"""
Test Postprocessing
"""

from PyNumeca.postprocessing import mf, plan


def test_reading_plan():
    """Test reading a plan file"""
    plan.plan_to_dataframe("tests/data/FINAL_DOE_400_shuffled.plan", log_head=True)


def test_reading_mf():
    """Test reading a mf file"""
    mf.read_mf("tests/data/example.mf")
