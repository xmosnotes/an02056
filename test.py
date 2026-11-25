#!/usr/bin/env python3.8
# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

import timeouts
import sys

MIN_PYTHON = (3, 7, 7)
# print(sys.version_info)
if sys.version_info < MIN_PYTHON:
    sys.exit('Python %s.%s.%s or later is required.\n' % MIN_PYTHON)

import subprocess
import time
import os
import re
from pathlib import Path


def format_hex_list(values):
  return ' '.join(f"0x{int(v, 16):02X}" for v in values)

def pretty_hex_lines(values, width=16):
  for offset in range(0, len(values), width):
    chunk = values[offset:offset + width]
    hex_bytes = ' '.join(f"{int(x, 16):02X}" for x in chunk)
    yield f"{offset:04X}: {hex_bytes}"


REPO_ROOT = Path(__file__).resolve().parent

HELLO_BIN = REPO_ROOT / "default_bin/app_an02056_hello_world.xe"
FREQUENCY_BIN = REPO_ROOT / "default_bin/app_an02056_frequency.xe"
POWER_BIN_IMPULSE = REPO_ROOT / "default_bin/app_an02056_power_impulse.xe"
POWER_BIN_SLOPE = REPO_ROOT / "default_bin/app_an02056_power_slope.xe"
XSCOPE_DISCOVERY_BIN = REPO_ROOT / "default_bin/app_an02056_xscope_discovery.xe"
XSCOPE_BIN_BASE = REPO_ROOT / "default_bin/"
FLASH_BIN = REPO_ROOT / "default_bin/app_an02056_flash.xe"
BOARD_XN = REPO_ROOT / "app_an02056_flash/board.xn"

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


def check_tools_version(tools_major, tools_minor, tools_sub):
  print('Checking XMOS Tools version ............ ', end='', flush=True)
  try:
    result = subprocess.run(args=['xcc', '--version'], timeout=timeouts.xcc, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  lines = result.stdout.splitlines()
  if len(lines) < 2:
    print(f'ERROR: Incorrect XMOS Tools version string too short')
    test_fail(fmt_out(result.stdout, result.stderr))
  words = lines[1].split()
  if len(words) < 3:
    print(f'ERROR: Incorrect XMOS Tools version string is short')
    test_fail(fmt_out(result.stdout, result.stderr))
  version = words[2].split('.')
  if len(version) != 3:
    print(f'ERROR: Incorrect XMOS Tools version does not have three components')
    test_fail(fmt_out(result.stdout, result.stderr))
  compatible = (int(version[0]) == tools_major and
                int(version[1]) == tools_minor and
                int(version[2]) >= tools_sub)
  if not compatible:
    print('Requires version %d.%d.x (x >= %d), not %s\n' % (tools_major, tools_minor, tools_sub, words[2]))
    test_fail(fmt_out(result.stdout, result.stderr))
  print('PASS')


def test_hello(xt):
  print('Testing hello world .................... ', end='', flush=True)
  try:
    start = time.time()
    result = subprocess.run(args=['xrun', '--adapter-id', xt, '--io', str(HELLO_BIN)], timeout=timeouts.xtag, capture_output=True, universal_newlines=True)
    elapsed = time.time() - start
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'Hello world!\n' == result.stdout:
    print('PASS')
  else:
    print(f'Hello world did not print Hello World!')
    test_fail(fmt_out(result.stdout, result.stderr))
  return elapsed

def discover_xscope(xt):
  print('Discover xscope ........................ ', end='', flush=True)
  try:
    result = subprocess.run(args=['xrun', '--adapter-id', xt, '--xscope', str(XSCOPE_DISCOVERY_BIN)], timeout=timeouts.xrun, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  output = f"{result.stdout}\n{result.stderr}"
  link_match = re.search(r'\blink\s+(\d+)\b', output, re.IGNORECASE)
  if link_match:
    link_nr = int(link_match.group(1))
  else:
    print('No xscope link found')
    test_fail(fmt_out(result.stdout, result.stderr))
  print('Found XSCOPE on link %d ... PASS'%link_nr)
  return link_nr

def test_xscope(xt, link_nr):
  print('Testing xscope ......................... ', end='', flush=True)
  try:
    bin_path = XSCOPE_BIN_BASE / f"app_an02056_xscope{link_nr}.xe"
    result = subprocess.run(args=['xrun', '--adapter-id', xt, '--xscope', str(bin_path)], timeout=timeouts.xrun, capture_output=True, universal_newlines=True)
    the_link_nr = link_nr
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()

  expected = ''
  for i in range(1000):
    expected += 'hello %04d\n' % i

  if expected == result.stdout:
    print('Successfully found 1000 messages .... PASS')
  else:
    print(f'Hello world did not print 1000 times hello %04d')
    test_fail(fmt_out(result.stdout, result.stderr))

  return the_link_nr

def test_frequency(xt, elapsed_empty):
  print('Testing frequency (takes 1 minute) ..... ', end='', flush=True)
  try:
    start = time.time()
    result = subprocess.run(args=['xrun', '--adapter-id', xt, '--io', str(FREQUENCY_BIN)], timeout=60+timeouts.xrun, capture_output=True, universal_newlines=True)
    elapsed = time.time() - start - elapsed_empty
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if abs(elapsed - 60) < 5:
    if abs(elapsed - 60) < 1:
      print('PASS')
    else:
      print('Timings are slightly off 60 seconds: ', elapsed)      
  else:
    print(f'Frequency test took wrong time ', elapsed)
    test_fail(fmt_out(result.stdout, result.stderr))

def test_power(xt, slope):
  if slope:
    binary = POWER_BIN_SLOPE
    print('Testing power steady max supply ........ ', end='', flush=True)
  else:
    binary = POWER_BIN_IMPULSE
    print('Testing power sudden change in load .... ', end='', flush=True)
  try:
    result = subprocess.run(args=['xrun', '--adapter-id', xt, '--io', str(binary)], timeout=timeouts.xrun, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'PASS\n' == result.stdout:
    print('PASS')
  else:
    print(f'Power test failed ')
    test_fail(fmt_out(result.stdout, result.stderr))

def run_flash_command(arg0, output_len, timeout, xt):
  try:
    proc = subprocess.run(args=['xflash', '--adapter-id', xt, '--spi-command', arg0, str(output_len), '0',
                                '--target-file', str(BOARD_XN)],
                                timeout=timeout, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()
  if proc.stderr != '':
    print(' FAIL')
    test_fail(fmt_out(proc.stdout, proc.stderr))
  response = proc.stdout.split()
  if len(response) != output_len + 7:
    print(' FAIL response too short ', proc.stdout)
    test_fail()
  output = []
  for i in response[7:]:
    output += [i[0:4]]
  return output

def test_flash_ident(xt):
  print('Reading flash ID ....................... ', end='', flush=True)
  ident = run_flash_command('0x9f', 3, timeouts.xflash, xt)
  print('PASS')
  return ident

def test_flash_sfdp(xt):
  print('Reading flash parameters ............... ', end='', flush=True)
  sfdp = run_flash_command('0x5A', 259, timeouts.xflash, xt)
  sfdp = sfdp[3:]
  zeroes = ['0x00'] * 8
  while len(sfdp) > 8 and sfdp[len(sfdp)-8:] == zeroes:
    sfdp = sfdp[:len(sfdp)-8]
  
  
  # TODO trim dummy bytes and parse
  print('PASS')
  return sfdp

def test_flash_program(xt):
  print('Trying to write program to flash ....... ', end='', flush=True)
  try:
    proc = subprocess.run(args=['xflash', '--adapter-id', xt, '-f', str(FLASH_BIN)],
                          timeout=timeouts.xflash, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print('TIMEOUT - FAIL')
    test_fail(fmt_out(e.stdout or '', e.stderr or ''))

  if 'Site 0 has finished successfully' in proc.stdout:
    print('PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def test_flash_ran(xt):
  print('Check xCORE booted from flash .......... ', end='', flush=True)
  try:
    xgdb_args = (
        f"xgdb|--batch|--eval-command=attach --adapter-id {xt}|--eval-command=thread 1.1|--eval-command=p/x *(0xf0000)"
    )
    proc = subprocess.run(args=xgdb_args.split('|'),
                                timeout=timeouts.xrun, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail(fmt_out(e.stdout or '', e.stderr or ''))

  if ' = 0x5aa50ff0' in proc.stdout:
    print('PASS')
  else:
    print(' FAIL, expected 0x5aa50ff0')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def test_xtag(pick_first=False):
  print('Finding xcore device ................... ', end='')
  try:
    result = subprocess.run(args=['xrun', '-l'], timeout=timeouts.xtag, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'No Available Devices Found' in result.stdout:
    print('No XTAG connected, check connections!')
    test_fail(fmt_out(result.stdout, result.stderr))

  # parse xrun -l output and return adapter id if only 1 found,
  # otherwise ask user to specify, or fail if more than 1 adapter
  # and the -x command-line option wasn't set
  adapters = []
  adapter_list = result.stdout.splitlines()
  for i, j in enumerate(adapter_list):
    # Create list of indexes to lines containing adapters
    if 'XTAG-4' in j:
      adapters.append(i)
  if len(adapters) == 0:
    print('FAIL - no xTAG found!')
    test_fail(fmt_out(result.stdout, result.stderr))
  if len(adapters) > 1:
    if pick_first:
      print('Multiple xTAGs found, picking first one, ', end='')
      adapters = [adapters[0]]
    else:
      print('FAIL - more than 1 xTAG found!')
      print('Please pass xTAG id as argument eg. python test.py <Adapter ID>')
      test_fail(fmt_out(result.stdout, result.stderr))

  # Extract adapter id - the 4th string along the line
  tmp = adapter_list[adapters[0]].split()

  if len(tmp) < 5 or len(tmp[3]) != 8:
    print('FAIL - wrong number of lines in xrun -l output')
    test_fail(fmt_out(result.stdout, result.stderr))

  test_xtag_id = tmp[3]
  if tmp[4] != 'XS3A[0]':
    print('FAIL - no XCORE found')
    test_fail(fmt_out(result.stdout, result.stderr))
  print(f'Adapter ID: {test_xtag_id} .... PASS')

  return test_xtag_id


def main():
    print('*** XCORE.AI board test ***')

    check_tools_version(15, 3, 1)

    if len(sys.argv) < 2:
        xt = test_xtag()        # Test for presence of chip
    else:
        xt = sys.argv[1]

    e = test_hello(xt)         # Print hello world, this may pause booting xtag
    e = test_hello(xt)         # Print hello world, now quickly
    test_frequency(xt,e)       # Frequency check
    l = discover_xscope(xt )   # Discover XSCOPE link
    test_xscope(xt,l)          # Print hello over xscope 1000 times
    test_power(xt,True)        # Test max power requirements
    test_power(xt,False)       # Test sudden load change in power

    i = test_flash_ident(xt)   # Read identifier
    s = test_flash_sfdp(xt)    # Read SFDP string
    test_flash_program(xt)     # Try and write a program
    test_flash_ran(xt)         # Execute the program and check that it ran

    print(big_pass)

    print('''Summary:
  - XTAG: %s
  - XSCOPE Link: %d
  - Flash ID: %s
  - Flash SFDP %d records:'''
        % (xt, l, format_hex_list(i), len(s)//8))
    for line in pretty_hex_lines(s):
      print('  ' + line)
    
if __name__ == "__main__":
   main()
