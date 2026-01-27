#!/usr/bin/env python3.8
# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

import sys
import subprocess
import os
import time
import xtagctl

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

def test_fail(output='no output provided'):
  print(output)
  sys.exit(1)

def fmt_out(stdout='', stderr=''):
  return "STDOUT:\n{}\nSTDERR:\n{}".format(stdout, stderr)


def main():
    if len(sys.argv) > 1:
        regex = sys.argv[1]
    else:
        regex = '/.*/'
    with xtagctl.acquire(regex) as adapter_id:
        print('Adapter id ', adapter_id)
        xtagctl.reset_adapter(adapter_id)
        time.sleep(2) # Wait for adapter to enumerate

        try:
            result = subprocess.run(args=['python', 'test.py', adapter_id], timeout=120, cwd='..', capture_output=True, universal_newlines=True)
        except subprocess.TimeoutExpired as e:
            print('FAIL - TIMEOUT')
            test_fail(fmt_out(result.stdout, result.stderr))
            sys.exit(1)
        if big_pass in result.stdout:
            print('PASS')
            sys.exit(0)
        print('FAIL - WRONG OUTPUT')
        test_fail(fmt_out(result.stdout, result.stderr))
        sys.exit(1)

if __name__ == "__main__":
   main()
