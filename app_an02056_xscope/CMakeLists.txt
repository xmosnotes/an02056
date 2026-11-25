cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_an02056_xscope0)


set(APP_DEPENDENT_MODULES  "")


set(APP_INCLUDES           src/)

set(XMOS_SANDBOX_DIR       ${CMAKE_CURRENT_LIST_DIR}/../..)

set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board0.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope1)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board1.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope2)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board2.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope3)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board3.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope4)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board4.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope5)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board5.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope6)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board6.xn)
XMOS_REGISTER_APP()

project(app_an02056_xscope7)
set(APP_COMPILER_FLAGS     -g -fxscope)
set(APP_HW_TARGET          board7.xn)
XMOS_REGISTER_APP()
