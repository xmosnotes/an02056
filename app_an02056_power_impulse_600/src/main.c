// Copyright 2024-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <stdio.h>
#include <string.h>
#include <xcore/parallel.h>
#include "iterations.h"

// These must all be less than EXTRA_ITERATIONS_FOR_SKIP in iterations.h
#if defined(SLOPE) && SLOPE == 1
#define skip0 0
#define skip1 10
#define skip2 20
#define skip3 30
#define skip4 40
#define skip5 50
#else
#define skip0 0
#define skip1 0
#define skip2 0
#define skip3 0
#define skip4 0
#define skip5 0
#endif

int vC0[8] = {0xf0f0f0f0,0xf0f0f0f0,0xf0f0f0f0,0xf0f0f0f0,0xf0f0f0f0,0xf0f0f0f0,0xf0f0f0f0,0xf0f0f0f0};
int vC1[8] = {0x0f0f0f0f,0x0f0f0f0f,0x0f0f0f0f,0x0f0f0f0f,0x0f0f0f0f,0x0f0f0f0f,0x0f0f0f0f,0x0f0f0f0f};
int multiplier0[8] = {0xAAAAAAAA,0xAAAAAAAA,0xAAAAAAAA,0xAAAAAAAA,0xAAAAAAAA,0xAAAAAAAA,0xAAAAAAAA,0xAAAAAAAA};
int multiplier1[8] = {0x55555555,0x55555555,0x55555555,0x55555555,0x55555555,0x55555555,0x55555555,0x55555555};
int answer0[16] = {0x347e347e,0x347e347e,0x347e347e,0x347e347e,0x347e347e,0x347e347e,0x347e347e,0x347e347e,
                   0xd800d800,0xd800d800,0xd800d800,0xd800d800,0xd800d800,0xd800d800,0xd800d800,0xd800d800};
int answer1[16] = {0x30a430a4,0x30a430a4,0x30a430a4,0x30a430a4,0x30a430a4,0x30a430a4,0x30a430a4,0x30a430a4,
                   0x6ac06ac0,0x6ac06ac0,0x6ac06ac0,0x6ac06ac0,0x6ac06ac0,0x6ac06ac0,0x6ac06ac0,0x6ac06ac0};

extern void vpu(int*, int*, int, int*);

DECLARE_JOB(run_vpu, (int*, int*, int, int*, synchronizer_t));
DECLARE_JOB(run_parent, (synchronizer_t));

void run_parent(synchronizer_t s) {
    for(int i = 0; i < ITERATIONS + EXTRA_ITERATIONS_FOR_SKIP; i++) {
        par_jobs_synchronize(s);
    }
    par_jobs_synchronize(s);
}

void run_vpu(int *multiplier, int *vC, int skips, int *ref_answer, synchronizer_t s) {
    if(s != 0) {
        printf("Unexpected non-zero synchronizer\n");
        asm("waiteu");
    }
    int answer[16];
    vpu(multiplier, vC, skips, answer);
    if (memcmp(answer, ref_answer, 64) != 0) {
        printf("FAIL Bad answer ");
        for(int i = 0; i < 16; i++) {
            printf("%08x ", answer[i]);
        }
        printf("\n");
        asm("waiteu");                 // Do not terminate - hang up and let time-out
    }
    par_jobs_synchronize(s);    
}

int main() {
    PAR_JOBS(
        PJOB(run_parent, (PAR_SYNC)),
        PJOB(run_vpu, (multiplier0, vC0, skip0, answer0, PAR_SYNC)),
        PJOB(run_vpu, (multiplier1, vC1, skip1, answer1, PAR_SYNC)),
        PJOB(run_vpu, (multiplier0, vC0, skip2, answer0, PAR_SYNC)),
        PJOB(run_vpu, (multiplier1, vC1, skip3, answer1, PAR_SYNC)),
        PJOB(run_vpu, (multiplier0, vC0, skip4, answer0, PAR_SYNC)),
        PJOB(run_vpu, (multiplier1, vC1, skip5, answer1, PAR_SYNC))
        );
    printf("PASS\n");
}
