import numpy as np


def car2cil(x: np.ndarray):
    # assert x.shape[-1] == 3, f'car2cil: x.shape[-1] should be 3, but its {x.shape[-1]}'
    y = x.copy()
    y[..., 0] = np.sqrt(x[..., 0] ** 2 + x[..., 1] ** 2)
    y[..., 1] = np.arctan2(x[..., 0], x[..., 1])

    return y
