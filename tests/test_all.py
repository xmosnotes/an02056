#!/usr/bin/env python3.8
# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEST_PY_PATH = PROJECT_ROOT / "test.py"
spec = importlib.util.spec_from_file_location("an02056_test_py", TEST_PY_PATH)
dut = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(dut)


def test_fmt_out():
    out = dut.fmt_out("one", "two")
    assert "STDOUT:\none" in out
    assert "STDERR:\ntwo" in out


# Hardware-independent regression tests: when xflash or xgdb times out, the
# handler must report a failure rather than raise UnboundLocalError by reading
# the result of the subprocess.run call that never returned.
@pytest.mark.parametrize(
    "func",
    [dut.test_flash_program, dut.test_flash_ran],
    ids=["flash_program", "flash_ran"],
)
@pytest.mark.parametrize(
    "stdout, stderr",
    [("partial stdout", "partial stderr"), (None, None)],
    ids=["captured_output", "none_streams"],
)
def test_timeout_reports_failure(monkeypatch, capsys, func, stdout, stderr):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=kwargs.get("args", "fake"), timeout=1, output=stdout, stderr=stderr
        )

    monkeypatch.setattr(dut.subprocess, "run", fake_run)

    with pytest.raises(SystemExit) as excinfo:
        func("FAKEXTAG")

    assert excinfo.value.code == 1
    out = capsys.readouterr().out
    assert "TIMEOUT - FAIL" in out
    assert dut.big_fail in out
    if stdout is None:
        assert dut.fmt_out("", "") in out
    else:
        assert dut.fmt_out(stdout, stderr) in out


@pytest.fixture(scope="module")
def xtag_id():
    forced = os.getenv("XTAG_ID")
    if forced:
        return forced
    return dut.test_xtag(pick_first=True)


@pytest.fixture(scope="module")
def xscope_link(xtag_id):
    return dut.discover_xscope(xtag_id)


@pytest.fixture(scope="module", autouse=True)
def run_from_project_root():
    original_cwd = Path.cwd()
    os.chdir(PROJECT_ROOT)
    try:
        yield
    finally:
        os.chdir(original_cwd)


@pytest.mark.order(1)
def test_check_tools_version():
    dut.check_tools_version(15, 3, 1)


@pytest.mark.order(2)
def test_xtag(xtag_id):
    assert isinstance(xtag_id, str)
    assert len(xtag_id) > 0


@pytest.mark.order(3)
def test_hello(xtag_id):
    elapsed = dut.test_hello(xtag_id)
    assert elapsed >= 0


@pytest.mark.order(4)
def test_discover_xscope(xscope_link):
    assert isinstance(xscope_link, int)
    assert xscope_link >= 0


@pytest.mark.order(5)
def test_xscope(xtag_id, xscope_link):
    returned_link = dut.test_xscope(xtag_id, xscope_link)
    assert returned_link == xscope_link


@pytest.mark.order(6)
def test_frequency(xtag_id):
    elapsed_empty = dut.test_hello(xtag_id)
    dut.test_frequency(xtag_id, elapsed_empty)


@pytest.mark.order(7)
def test_power_slope(xtag_id):
    dut.test_power(xtag_id, True)


@pytest.mark.order(8)
def test_power_impulse(xtag_id):
    dut.test_power(xtag_id, False)


@pytest.mark.order(9)
def test_run_flash_command(xtag_id):
    output = dut.run_flash_command("0x9f", 3, dut.timeouts.xflash, xtag_id)
    assert isinstance(output, list)
    assert len(output) == 3


@pytest.mark.order(10)
def test_flash_ident(xtag_id):
    ident = dut.test_flash_ident(xtag_id)
    assert isinstance(ident, list)
    assert len(ident) == 3


@pytest.mark.order(11)
def test_flash_sfdp(xtag_id):
    sfdp = dut.test_flash_sfdp(xtag_id)
    assert isinstance(sfdp, list)
    assert len(sfdp) > 0


@pytest.mark.order(12)
def test_flash_program(xtag_id):
    dut.test_flash_program(xtag_id)


@pytest.mark.order(13)
def test_post_flash_run(xtag_id):
    dut.test_flash_ran(xtag_id)

