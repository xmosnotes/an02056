cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)

project(app_an02056)

add_subdirectory(app_an02056_hello_world)
add_subdirectory(app_an02056_power)
add_subdirectory(app_an02056_xscope)
