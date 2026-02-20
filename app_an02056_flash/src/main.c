// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <stdio.h>

#define UNTOUCHED_ADDRESS 0xf0000

int main()
{
    volatile int *a = (int *)UNTOUCHED_ADDRESS;
    *a = 0x5AA50FF0;
    printf("Written 0x%08X to address 0x%08X\n", *a, (unsigned int)a);
    asm("ecallf %0" : : "r"(0)); // Ensure program stops on thread 1.1
}
