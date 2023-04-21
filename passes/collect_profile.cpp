#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/Pass.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {
struct FunctionProfilePass : public FunctionPass {
    static char ID;
    FunctionProfilePass() : FunctionPass(ID) {
    }

    FunctionProfilePass(const std::string &funcName) : FunctionProfilePass() {
        this->funcName = funcName;
    }

    bool runOnFunction(Function &F) override {
        Module *M = F.getParent();
        // TODO: figure out how to not need to hardcode the function.
        bool modified = false;
        modified = modified || getProfileInfo(F, M, funcName);
        return modified;
    }

   private:
    std::string funcName = "log";

    bool getProfileInfo(Function &F, Module *M, std::string funcName) {
        Function *func = M->getFunction(funcName);
        LLVMContext &context = M->getContext();
        Type *intType = Type::getInt32Ty(context);
        // Declare C standard library printf
        std::vector<Type *> printfArgsTypes({Type::getInt8PtrTy(context)});
        FunctionType *printfType =
            FunctionType::get(intType, printfArgsTypes, true);
        auto print = M->getOrInsertFunction("printf", printfType);
        if (!func) {
            errs() << "Error\n";
            return false;  // funcName not found, so function not modified
        }

        for (BasicBlock &BB : F) {
            for (Instruction &I : BB) {
                if (CallInst *call = dyn_cast<CallInst>(&I)) {
                    if (call->getCalledFunction() == func) {
                        // Assume single input.
                        Value *x = call->getArgOperand(0);
                        // Assume single output.
                        Value *y = dyn_cast<Value>(call);
                        IRBuilder<> builder(call);
                        builder.SetInsertPoint(call);
                        builder.CreateCall(
                            print, {builder.CreateGlobalStringPtr("@@%f "), x});
                        builder.SetInsertPoint(
                            call->getNextNonDebugInstruction());
                        builder.CreateCall(
                            print, {builder.CreateGlobalStringPtr("@@%f "), y});
                    }
                }
            }
        }
        return true;  // function modified
    }
};  // end of struct FunctionProfilePass
}  // end of anonymous namespace

static cl::opt<std::string> FPPassFuncName(
    "fppass-func-name", cl::desc("Name of function to approximate"),
    cl::value_desc("func-name"), cl::Required);

char FunctionProfilePass::ID = 0;
static RegisterPass<FunctionProfilePass> X("fppass", "Function profile pass",
                                           false /* Only looks at CFG */,
                                           false /* Analysis Pass */);
