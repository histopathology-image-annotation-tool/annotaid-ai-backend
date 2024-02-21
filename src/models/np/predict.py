import albumentations as A
import numpy as np
import torch
import torch.nn as nn
from albumentations.pytorch import ToTensorV2
from patchify import patchify

from src.models.mc.transforms import NormalizeHEStainsWrapper

PATCH_SIZE = (256, 256, 3)


@torch.no_grad()
def predict_nuclear_pleomorphism(
    model: nn.Module,
    image: np.ndarray,
    device: torch.device
) -> int | None:
    """Predicts the nuclear pleomorphism score of a given image.

    Args:
        model (nn.Module): The nuclear pleomorphism model.
        image (np.ndarray): The input image.
        device (torch.device): The device to use for the prediction.
    Returns:
        int | None: The predicted nuclear pleomorphism score.
    """
    model.eval()
    model.to(device)

    transforms = A.Compose([
        A.Resize(260, 260),
        NormalizeHEStainsWrapper(),
        A.Normalize(
            mean=(0.7869035601615906, 0.6227355599403381, 0.7037901878356934),
            std=(0.16848863661289215, 0.21331951022148132, 0.15994398295879364)
        ),
        ToTensorV2()
    ])

    patches = patchify(
        image,
        PATCH_SIZE,
        step=PATCH_SIZE[0]
    )

    predicted_labels = []

    n_rows, n_cols = patches.shape[:2]

    for row_index in range(n_rows):
        for col_index in range(n_cols):
            patch = patches[row_index, col_index].squeeze()

            try:
                patch = transforms(image=patch)['image']
            except ValueError:
                continue

            tensor_patch: torch.Tensor = patch[None, ...]
            tensor_patch = tensor_patch.to(device)

            prediction = model(tensor_patch).cpu()
            label = prediction.argmax().numpy()

            predicted_labels.append(label)

    if len(predicted_labels) == 0:
        return None

    return np.bincount(predicted_labels).argmax()
