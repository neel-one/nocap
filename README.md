# NOCAP
**N**earby-**o**perand **C**ontinuous **Ap**proximation (NOCAP) is a project created by Neel Shah, Owen Goebel, Peter Ly, Zhixiang Teoh for EECS 583 Advanced Compilers at the University of Michigan.

We implement an algorithm that approximates continuous functions with a lookup table with the goal of sacrificing significant memory usage and some accuracy for speed. Specifically, we:
1. Gather profile data (we can omit this step for periodic functions)
2. Use the profile data to build intervals of input to approximate the function
3. Use the profile data to estimate the granularity of the intervals and build input buckets
4. Build a lookup table.
5. Replace all calls to function of interest with a call to the lookup table.
