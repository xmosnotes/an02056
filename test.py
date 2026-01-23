#!/usr/bin/env python3.8
# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.


import sys
MIN_PYTHON = (3, 7, 7)
# print(sys.version_info)
if sys.version_info < MIN_PYTHON:
    sys.exit('Python %s.%s.%s or later is required.\n' % MIN_PYTHON)

import subprocess
import time
import os


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
    result = subprocess.run(args=['xcc', '--version'], timeout=2, capture_output=True, universal_newlines=True)
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
  compatible = True
  compatible = compatible and int(version[0]) == tools_major
  if int(version[1]) == tools_minor:
    compatible = compatible and int(version[2]) >= tools_sub
  elif int(version[1]) < tools_major:
    compatible = False
  if not compatible:
    print('Requires version %d.%d.%d not %s\n' % (tools_major, tools_minor, tools_sub, words[2]))
    test_fail(fmt_out(result.stdout, result.stderr))
  print('PASS')


def test_hello():
  print('Testing hello world .................... ', end='', flush=True)
  try:
    start = time.time()
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin','app_an02056_hello_world.xe')], timeout=5, capture_output=True, universal_newlines=True)
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

def discover_xscope():
  print('Discover xscope ........................ ', end='', flush=True)
  try:
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin','app_an02056_xscope_discovery.xe')], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  words = result.stdout.split()
  if len(words) != 4:
    print(f'No xcsope link found')
    test_fail(fmt_out(result.stdout, result.stderr))
  link_nr = int(words[3])
  print('Found XSCOPE on link %d... PASS'%link_nr)
  return link_nr

def test_xscope(link_nr):
  print('Testing xscope ......................... ', end='', flush=True)
  try:
    result = subprocess.run(args=['xrun', '--xscope', os.path.join('default_bin','app_an02056_xscope%d.xe' % link_nr)], timeout=5, capture_output=True, universal_newlines=True)
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

def test_frequency(elapsed_empty):
  print('Testing frequency (takes 1 minute) ..... ', end='', flush=True)
  try:
    start = time.time()
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin','app_an02056_frequency.xe')], timeout=65, capture_output=True, universal_newlines=True)
    elapsed = time.time() - start - elapsed_empty
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if abs(elapsed - 60) < 1:
    print('PASS')
  else:
    print(f'Frequency test took wrong time ', elapsed)
    test_fail(fmt_out(result.stdout, result.stderr))

def test_power(slope):
  if slope:
    binary = 'app_an02056_power_slope.xe'
    print('Testing power steady max supply ........ ', end='', flush=True)
  else:
    binary = 'app_an02056_power_impulse.xe'
    print('Testing power sudden change in load .... ', end='', flush=True)
  try:
    result = subprocess.run(args=['xrun', '--io', os.path.join('default_bin', binary)], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' FAIL - TIMEOUT')
    test_fail()
  if 'PASS\n' == result.stdout:
    print('PASS')
  else:
    print(f'Power test failed ')
    test_fail(fmt_out(result.stdout, result.stderr))

def test_usb():
  # NOTE DUT must be connected to PC with USB cable for this test...
  print('Testing USB .............', end='', flush=True)
  result = subprocess.run(args=['xrun', os.path.join('default_bin','app_hid_mouse_demo_AI.xe')], timeout=12, capture_output=True, universal_newlines=True)
  # wait 2 seconds for device to enumerate
  for i in range(2):
    time.sleep(1)
    print('....', end='', flush=True)
  # do lsusb see if device in tree.
  result = subprocess.run(args=['lsusb'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
  if 'ID 20b1:1010 XMOS Ltd' in result.stdout:
    print('PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(result.stdout, result.stderr))

def test_mipi():
  print('Testing MIPI ....................', end='', flush=True)
  try:
    proc = subprocess.run(args=['xrun', '--xscope', os.path.join('default_bin','app_characterisation_VISION_EXPLORER.xe')], timeout=20, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()
  out = proc.stderr
  if 'PASS' in out:
    print('PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def run_flash_command(arg0, output_len, timeout):
  try:
    proc = subprocess.run(args=['xflash', '--spi-command', arg0, str(output_len), '0',
                                '--target-file', os.path.join('default_bin','board.xn')],
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

def test_flash_ident():
  print('Reading flash ID ....................... ', end='', flush=True)
  ident = run_flash_command('0x9f', 3, 10)
  print('PASS')
  return ident

def test_flash_sfdp():
  print('Reading flash parameters ............... ', end='', flush=True)
  sfdp = run_flash_command('0x5A', 259, 20)
  sfdp = sfdp[3:]
  zeroes = ['0x00'] * 8
  while len(sfdp) > 8 and sfdp[len(sfdp)-8:] == zeroes:
    sfdp = sfdp[:len(sfdp)-8]
  
  
  # TODO trim dummy bytes and parse
  print('PASS')
  return sfdp

def test_flash_program():
  print('Trying to write program to flash ....... ', end='', flush=True)
  try:
    proc = subprocess.run(args=['xflash', '-f', os.path.join('default_bin','app_an02056_flash.xe')],
                          timeout=30, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()

  if 'Site 0 has finished successfully' in proc.stdout:
    print('PASS')
  else:
    print(' FAIL')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def test_flash_run():
  print('Check xCORE booted from flash .......... ', end='', flush=True)
  try:
    proc = subprocess.run(args=['xgdb',
                                  '--batch',
                                  '--eval-command=connect',
                                  '--eval-command=p/x *(0xa1234)'], timeout=5, capture_output=True, universal_newlines=True)
  except subprocess.TimeoutExpired as e:
    print(' TIMEOUT - FAIL')
    test_fail()

  if ' = 0x5aa50ff0' in proc.stdout:
    print('PASS')
  else:
    print(' FAIL, expected 0x5aa50ff0')
    test_fail(fmt_out(proc.stdout, proc.stderr))

def test_xtag():
  print('Finding xcore device ................... ', end='')
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
  print('Found xTAG Adapter ID... ' + test_xtag_id, end = '', flush=True)
  if tmp[4] != 'XS3A[0]':
    print('FAIL - no XCORE found')
    test_fail(fmt_out(result.stdout, result.stderr))
  print(' Found XCORE.AI... PASS')


def main():
    print('*** XCORE.AI board test ***')

    check_tools_version(15, 3, 1)

    test_xtag()             # Test for presence of chip

    e = test_hello()        # Print hello world
    test_frequency(e)       # Frequency check
    l = discover_xscope()   # Dioscover XSCOPE link
    test_xscope(l)          # Print hello over xscope 1000 times
    test_power(True)        # Test max power requirements
    test_power(False)       # Test sudden load change in power

    i = test_flash_ident()  # Read identifier
    s = test_flash_sfdp()   # Read SFDP string
    test_flash_program()    # Try and write a program
    test_flash_run()        # Execute the program and check that it ran

#    test_usb()
#    test_mipi()

    print(big_pass)

    print('''Summary:
- XSCOPE Link: %d
- Flash ID: %s
- Flash SDFP %d records: %s''' % (l, str(i), len(s)//8, str(s)))
    
if __name__ == "__main__":
   main()
