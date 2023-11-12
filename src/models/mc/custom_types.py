from typing import TypedDict

import numpy as np


class MitosisPrediction(TypedDict):
    bbox: np.ndarray
    conf: float
    label: int
