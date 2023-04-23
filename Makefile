setup:
	./setup.sh

# Example usage: 
#   $ make setup
#   $ python3 nocap.py -t blackscholes -f log -args "1 test/blackscholes/in_100M.txt /dev/null" build
#   $ make compare_exp_log FUNC=log

BUILD_DIR=build/src
OUTPUT_DIR=outputs

reg_%: test/%/*.c
	gcc -o $(OUTPUT_DIR)/$@ $^ -lm

# TODO: Fix this target
nocap_%: $(BUILD_DIR)/%_lookups.c
	C_FILES=()
	$(foreach func, $(FUNCS), C_FILES+=(build/src/nocap_$(func).c);)
	gcc -o $(OUTPUT_DIR)/$@ $^ $(C_FILES) -lm

# TODO: Fix this target
compare_%: nocap_% reg_%
	@echo "Comparing nocap_$* with (baseline) reg_$*"
	@echo "-------------------------------------"
	@echo "------------- nocap_$* --------------"
	@time $(OUTPUT_DIR)/nocap_$*
	@echo "------------- reg_$* --------------"
	@time $(OUTPUT_DIR)/reg_$*

clean: 
	rm -rf outputs/*