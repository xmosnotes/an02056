// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xs1.h>
#include <platform.h>

extern void main0(chanend);
extern void main1(chanend);

int main(void) {
    chan c;
    par {
        on tile[0]: main0(c);
        on tile[1]: main1(c);
    }
    return 0;
}
