// Copyright 2024-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <stdio.h>
#include <xcore/hwtimer.h>

int main()
{
    hwtimer_t tmr = hwtimer_alloc();
    for(int i = 0; i < 1000; i++) {
        printf("hello %04d\n", i);
        
        int t = hwtimer_get_time(tmr);
        hwtimer_set_trigger_time(tmr, t+100); // give xtag a breather
        (void) hwtimer_get_time(tmr);
    }
    hwtimer_free(tmr);
}
