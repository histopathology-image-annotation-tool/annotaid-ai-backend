from typing import NotRequired, TypedDict

import numpy as np


class MitosisPrediction(TypedDict):
    bbox: np.ndarray
    conf: float
    label: int
    model_hash: NotRequired[str]
