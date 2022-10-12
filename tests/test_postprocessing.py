from PyNumeca.postprocessing import plan


def test_reading_plan():
    plan.plan_to_dataframe('data/FINAL_DOE_400_shuffled.plan', log_head=True)
