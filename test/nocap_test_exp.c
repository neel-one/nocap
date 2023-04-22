#include <stdio.h>
#include "../build/src/nocap_exp.h"

int main() {
for (int j = 0; j < 1e9; j++) {
    for (int i = 0; i <= 20; i++) {
        double x = i;
        double y = nocap_exp(-x);
    }
}
    return 0;
}
