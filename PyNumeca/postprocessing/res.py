import numpy as np
import pandas as pd

__res_cols = [
    "Iteration number",
    "Work unit",
    "CPU time",
    "Lift",
    "Drag",
    "Torque",
    "Qmax",
    "Tmax",
    "Mass flow in",
    "Mass flow out",
]


def read_resfile(path: str):
    with open(path, "r") as f:
        res_content = f.readlines()
    extract = []
    index_ = 0
    for line in res_content:
        if f" {index_} " in line:
            extract.append(
                np.array(
                    [item for item in line.replace("\n", "").split(" ") if item != ""],
                    dtype=np.float32,
                )
            )
            index_ += 1
    dataframe = pd.DataFrame(extract, columns=__res_cols)
    return dataframe
