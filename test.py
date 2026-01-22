#!/usr/bin/env python3.8

# Python 3
# xcore.ai Explorer Board Test Script

import sys
MIN_PYTHON = (3, 7, 7)
# print(sys.version_info)
if sys.version_info < MIN_PYTHON:
    sys.exit('Python %s.%s.%s or later is required.\n' % MIN_PYTHON)

import subprocess
import time
import os
import getopt
from datetime import datetime

# from pylab import*
# from scipy.io import wavfile

header_string = '''
* * * MANUFACTURING TEST FOR xcore.ai vision explorer Board 1V1 * * *

See instructions document for test setup.
'''

big_pass = '''
#######################################
#                                     #
#   ######     #     #####   #####    #
#   #     #   # #   #     # #     #   #
#   #     #  #   #  #       #         #
#   ######  #     #  #####   #####    #
#   #       #######       #       #   #
#   #       #     # #     # #     #   #
#   #       #     #  #####   #####    #
#                                     #
#######################################
'''

big_fail = '''
#######################################
#                                     #
#   #######    #      ###   #         #
#   #         # #      #    #         #
#   #        #   #     #    #         #
#   #####   #     #    #    #         #
#   #       #######    #    #         #
#   #       #     #    #    #         #
#   #       #     #   ###   #######   #
#                                     #
#######################################
'''

#DEBUG = os.environ.get("PRODTEST_DEBUG", None) is not None

DEBUG = 1

def test_fail(output='no output provided'):
  print(big_fail)
  if DEBUG:
    print(output)
  quit()

def fmt_out(stdout='', stderr=''):
  return "STDOUT:\n{}\nSTDERR:\n{}".format(stdout, stderr)


def check_tools_ver(tools_str):
  print('Checking XMOS Tools version ..... ', end='')
  try:
    result = subprocess.run(args=['xrun', '-v'], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if tools_str in result.stderr:
    print('OK')
  else:
    print(f'ERROR: Incorrect XMOS Tools version. Expected {tools_str}.')
    test_fail(fmt_out(result.stdout, result.stderr))


def test_hello():
  print('Testing hello world ..... ', end='')
  try:
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin','app_an02056_hello_world.xe')], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'Hello world!\n' == result.stdout:
    print('OK')
  else:
    print(f'Hello world did not print Hello World!')
    test_fail(fmt_out(result.stdout, result.stderr))

def test_xscope():
  print('Testing xscope ..... ', end='')
  success = False
  for link_nr in range(8):
    try:
      result = subprocess.run(args=['xrun', '--xscope', os.path.join('default_bin','app_an02056_xscope%d.xe' % link_nr)], timeout=5, capture_output=True, universal_newlines=True)
      success = True
    except subprocess.TimeoutExpired as e:
      pass
    if success:
      break

  expected = ''
  for i in range(1000):
    expected += 'hello %04d\n' % i
    
  if expected == result.stdout:
    print('OK')
  else:
    print(f'Hello world did not print 1000 times hello %04d')
    test_fail(fmt_out(result.stdout, result.stderr))


def test_frequency():
  print('Testing frequency ..... ', end='')
  try:
    start = time.time()
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin','app_an02056_frequency.xe')], timeout=65, capture_output=True, universal_newlines=True)
    elapsed = time.time() - start
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if abs(elapsed - 60) < 0.1:
    print('OK')
  else:
    print(f'Hello world took wrong time ', elapsed)
    test_fail(fmt_out(result.stdout, result.stderr))

def test_power(slope):
  if slope:
    binary = 'app_an02056_power_slope.xe'
    print('Testing power steady max supply ..... ', end='')
  else:
    binary = 'app_an02056_power_impulse.xe'
    print('Testing power suddent change in load ..... ', end='')
  try:
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin', binary)], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'PASS\n' == result.stdout:
    print('OK')
  else:
    print(f'Power test failed ')
    test_fail(fmt_out(result.stdout, result.stderr))

def test_usb():
  # NOTE DUT must be connected to PC with USB cable for this test...
  print('Testing USB .............', end='', flush=True)
  result = subprocess.run(args=['xrun', 'bin/app_hid_mouse_demo_AI.xe'], timeout=12, capture_output=True, universal_newlines=True)
  # wait 2 seconds for device to enumerate
  for i in range(2):
    time.sleep(1)
    print('....', end='', flush=True)
  # do lsusb see if device in tree.
  result = subprocess.run(args=['lsusb'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
  if 'ID 20b1:1010 XMOS Ltd' in result.stdout:
    print(' PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(result.stdout, result.stderr))

def test_mipi():
  print('Testing MIPI ....................', end='', flush=True)
  try:
    proc = subprocess.run(args=['xrun', '--xscope', 'bin/app_characterisation_VISION_EXPLORER.xe'], timeout=20, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()
  out = proc.stderr
  if 'PASS' in out:
    print(' PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def run_flash_command(arg0, output_len):
  try:
    proc = subprocess.run(args=['xflash', '--spi-command', arg0, '0', output_len,
                                '--target-file', os.path.join('default_bin','board.xn')],
                                timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()
  return proc.stdout[0:output_len]

def test_flash_ident():
  print('Reading flash parameters: ')
  ident = run_flash_command('0x9f', '3')
  print(' PASS <', str(ident), '>')

def test_flash_sfdp():
  print('Reading flash parameters: ')
  sfdp = run_flash_command('0x5A', '256')
  print(' PASS <', str(sfdp), '>')

def test_flash_program():
  print('Testing programming flash:')
  try:
    proc = subprocess.run(args=['xflash', '-f', os.path.join('default_bin','app_an02056_flash.xe')],
                          timeout=30, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()

  if True:
    print(proc.stdout)
    print(proc.stderr)
    print(' PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def test_flash_run():
  print('Testing running program in flash:')
  try:
    proc = subprocess.run(args=['xgdb',
                                  '--batch',
                                  '--eval-command=connect',
                                  '--eval-command=p/x *(0xa1234)'], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()

  if '5AA50FF0' in proc.stdout:
    print(' PASS')
  else:
    print(' FAIL, expected 5AA50FF0')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def test_xtag():
  try:
    result = subprocess.run(args=['xrun', '-l'], timeout=20, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'No Available Devices Found' in result.stdout:
    print('No XTAG connected, check connections!')
    test_fail(fmt_out(result.stdout, result.stderr))

  # parse xrun -l output and return adapter id if only 1 found,
  # otherwise ask user to select, or fail if more than 1 adapter
  # and the -x command-line option wasn't set
  adapters = []
  adapter_list = result.stdout.splitlines()
  for i, j in enumerate(adapter_list):
    # Create list of indexes to lines containing adapters
    if 'XTAG-4' in j:
      adapters.append(i)
  if len(adapters) != 1:
    print('FAIL - more than 1 xTAG found!')
    test_fail(fmt_out(result.stdout, result.stderr))
    
  # Extract adapter id - the 4th string along the line
  tmp = adapter_list[adapters[0]].split()

  if len(tmp) < 5 or len(tmp[3]) != 8:
    print('FAIL - wrong number of lines')
    test_fail(fmt_out(result.stdout, result.stderr))
    
  test_xtag_id = tmp[3]
  print('Found xTAG Adapter ID ' + test_xtag_id)
  if tmp[4] != 'P[0]':
    print('FAIL - no XCORE found')
    test_fail(fmt_out(result.stdout, result.stderr))
    print(' PASS')


def main():
    tools_str = 'a77caa1' # 15.3.1

    print(header_string)
    check_tools_ver(tools_str)

    test_xtag()             # Test for presence of chip
    
    test_hello()            # Print hello world
    test_frequency()        # Frequency check
    test_xscope()           # Print hello over xscope 1000 times; try which xscope link
    test_power(True)        # Test max power requirements
    test_power(False)       # Test sudden load change in power

    test_flash_ident()      # Read identifier
    test_flash_sfdp()       # Read SFDP string
    test_flash_program()    # Try and write a program
    test_flash_run()        # Execute the program and check that it ran
    
    test_usb()
    test_mipi()
    
    print(big_pass)

if __name__ == "__main__":
   main()
