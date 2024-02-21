from typing import Any

import numpy as np
from albumentations.core.transforms_interface import ImageOnlyTransform
from monai.apps.pathology.transforms.stain.array import NormalizeHEStains


class NormalizeHEStainsWrapper(ImageOnlyTransform):
    """Wrapper for the NormalizeHEStains class from MONAI."""

    def __init__(self, always_apply: bool = True, p: float = 1.0) -> None:
        super().__init__(always_apply, p)
        self.normalizer = NormalizeHEStains()

    def apply(self, img: np.ndarray, **params: Any) -> np.ndarray:
        image = self.normalizer(np.array(img))
        return image
