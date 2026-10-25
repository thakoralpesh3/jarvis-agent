"""
Tests for Laptop Troubleshooter and Stuck-Point Problem Solver.
"""

from unittest.mock import patch
import pytest
from core.troubleshooter import LaptopTroubleshooter


def test_capture_environment_context():
    troubleshooter = LaptopTroubleshooter()
    ctx = troubleshooter.capture_environment_context()
    assert isinstance(ctx, dict)
    assert "active_windows" in ctx
    assert "clipboard" in ctx
    assert "recent_commands" in ctx
    assert "recent_errors" in ctx


def test_diagnose_and_solve_mocked():
    troubleshooter = LaptopTroubleshooter()
    with patch.object(troubleshooter, "_call_gemini", create=True, return_value=None):
        # Even without live model response, returns string
        res = troubleshooter.diagnose_and_solve_stuck_point("ModuleNotFoundError in python script")
        assert isinstance(res, str)
        assert len(res) > 10
