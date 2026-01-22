// Copyright 2024-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <stdio.h>
#include <xcore/hwtimer.h>

int main()
{
    hwtimer_t tmr = hwtimer_alloc();
    int t = hwtimer_get_time(tmr);
    for(int i = 0; i < 60; i++) {
        printf("00:00:%02d\n", i);
        t += 100000000;
        hwtimer_set_trigger_time(tmr, t);
        (void) hwtimer_get_time(tmr);
    }
    hwtimer_free(tmr);
}
