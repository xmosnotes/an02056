// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include "iterations.h"
    
    .globl vpu
    .globl vpu.nstackwords
    .linkset vpu.nstackwords, 0

    .issue_mode dual
    .align 16
vpu:
    dualentsp 0
    vclrdr
    ldc r11, 0x200
    vsetc   r11
    ldc    r11, EXTRA_ITERATIONS_FOR_SKIP
    sub    r11, r11, r2
    bf     r2, go
skiploop:   
    { sub    r2, r2, 1            ; ssync }
    bt      r2, skiploop
go:
    add     r2, r11, 0
    ldc     r11, ITERATIONS
loop:
    ssync
    vldc    r1[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    vlmaccr r0[0]
    { bt r11, loop                 ; sub r11, r11, 1 }
    ldc r11, 32
    { vstd    r3[0]                ; add r3, r3, r11 }
    { vstr    r3[0]                ; nop            }
skiploopend:   
    { sub    r2, r2, 1            ; ssync }
    bt      r2, skiploopend
    retsp 0
