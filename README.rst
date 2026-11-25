:orphan:

######################################
AN02056: Board test procedure and code
######################################

:vendor: XMOS
:version: 1.0.0
:scope: Example
:description: Methods and source code for smoke-testing a newly designed board
:category: General purpose
:keywords: Testing, Debug, Booting, Power
:hardware: XK-EVK-XU316

*******
Summary
*******

When designing a new board, it can be useful to put the board through a set
of tests to establish that the XCORE is fully functional, powered
correctly, etc. This app note contains a small collection of test programs.
Extra test programs may be added that are specific to your board design.

********
Features
********

* Tests JTAG connectivity
* Tests power
* Tests power impulse response
* Tests XSCOPE link

************
Known issues
************

* None

**************
Required tools
**************

* XMOS XTC Tools: 15.3.1

*********************************
Required libraries (dependencies)
*********************************

* None

*************************
Related application notes
*************************

* None

*******
Support
*******

This package is supported by XMOS Ltd. Issues can be raised against the software at
`www.xmos.com/support <https://www.xmos.com/support>`_ or using GitHub `issues <https://github.com/xmosnotes/an02056/issues>`_.
