cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_an02056_power_impulse_600)

set(APP_HW_TARGET          XK-EVK-XU316)

set(APP_DEPENDENT_MODULES  "")

set(APP_COMPILER_FLAGS_impulse_600 -O2 -DSLOPE=0 -DSPEED=600)
set(APP_COMPILER_FLAGS_slope_600   -O2 -DSLOPE=1 -DSPEED=600)

set(APP_INCLUDES           src/)

set(XMOS_SANDBOX_DIR       ${CMAKE_CURRENT_LIST_DIR}/../..)

XMOS_REGISTER_APP()
