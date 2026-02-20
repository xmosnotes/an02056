// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <stdio.h>

int main()
{
    int *a = (int *)0xa1234;
    *a = 0x5AA50FF0;
    // If debugger is attached in xrun, inform user that they need to manually exit
    printf("Written 0x%08X to address 0x%08X, press ctrl-c to exit\n", *a, (unsigned int)a);
    // Note we do not exit because it can leave the chip in an unknown thread which will
    // cause the next test to fail. This thread (t1.1) will pause forever and be available for inspection by the debugger.
    asm("waiteu");
}
