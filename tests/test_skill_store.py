"""
Tests for Dynamic Skill Store and Tool Synthesis.
"""

import tempfile
from pathlib import Path
import pytest

from memory.database import DatabaseManager
from memory.skill_store import SkillStore


@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        db = DatabaseManager(base / "test.db")
        skills_dir = base / "skills"
        store = SkillStore(skills_dir=skills_dir, db=db)
        yield store


def test_syntax_validation(temp_store):
    valid_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    is_valid, err = temp_store.validate_code_syntax(valid_code)
    assert is_valid is True
    assert err is None

    invalid_code = "def broken(:\n    return"
    is_valid, err = temp_store.validate_code_syntax(invalid_code)
    assert is_valid is False
    assert "Syntax Error" in err


def test_register_and_execute_skill(temp_store):
    skill_code = """
def calculate_vat(amount: float, rate: float = 0.2) -> float:
    \"\"\"Calculates the VAT on a given monetary amount.\"\"\"
    return round(amount * rate, 2)
"""
    success, msg = temp_store.register_new_skill(
        name="calculate_vat",
        code_content=skill_code,
        description="Calculates the VAT on a given monetary amount."
    )
    assert success is True
    assert "successfully created" in msg

    # Verify tool is loaded in store
    assert "calculate_vat" in temp_store.loaded_tools
    vat_fn = temp_store.loaded_tools["calculate_vat"]
    assert vat_fn(100.0, 0.15) == 15.0

    # Verify formatting in prompt
    formatted = temp_store.format_skills_for_prompt()
    assert "calculate_vat" in formatted
    assert "VAT" in formatted
