// Copyright 2024-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <stdio.h>

int main()
{
    int *a = (int *)0xa1234;
    *a = 0x5AA50FF0;
}
