#!/usr/bin/env python3.8
# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

import sys
import subprocess

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


def main():
    try:
        result = subprocess.run(args=['python3', os.path.join('..','test.py')], timeout=120, capture_output=True, universal_newlines=True)
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
