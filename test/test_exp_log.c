#include <math.h>
#include <stdio.h>

int main() {
    for (int i = 1; i <= 20; i++) {
        double x = i;
        double expx = exp(x);
        double logx = log(x);
        double explogx = exp(log(x));
    }
    return 0;
}
