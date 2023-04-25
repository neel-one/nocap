#include <math.h>
#include <stdio.h>

int main() {
    for (int j = 0; j < 1e7; j++) {
        for (int i = 0; i <= 20; i++) {
            double x = i;
            double y = exp(-x);
        }
    }
    return 0;
}
