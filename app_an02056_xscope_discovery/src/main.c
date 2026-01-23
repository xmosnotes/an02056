// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xs1.h>
#include <stdio.h>
#include <xscope.h>
#include <xcore/hwtimer.h>

#define LINK_ENABLE 0x80008010
#define LINK_HELLO  0x81808010

#define HAS_CREDIT  0x02000000

int main()
{
    for(int i = 0; i < 8; i++) {
        write_sswitch_reg(get_local_tile_id(), 0x80 + i, LINK_ENABLE);
    }
    for(int i = 0; i < 8; i++) {
        write_sswitch_reg(get_local_tile_id(), 0x80 + i, LINK_HELLO);
    }
    for(int i = 0; i < 8; i++) {
        unsigned x;
        read_sswitch_reg(get_local_tile_id(), 0x80 + i, &x);
        if (x & HAS_CREDIT) {
            printf("XSCOPE on link %d\n", i);
        }
    }
}
