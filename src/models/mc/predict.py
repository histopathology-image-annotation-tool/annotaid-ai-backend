import albumentations as A
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from monai.apps.pathology.transforms.stain.array import NormalizeHEStains
from patchify import patchify
from torch.nn import functional as F
from torchvision.models import EfficientNet
from ultralytics import YOLO
from ultralytics.engine.results import Results

from .custom_types import MitosisPrediction
from .transforms import NormalizeHEStainsWrapper

FIRST_STAGE_PATCH_SIZE = (512, 512, 3)


@torch.no_grad()
def predict_first_stage(
    model: YOLO,
    image: np.ndarray,
) -> list[np.ndarray]:
    """Predicts the mitotic candidates in the input image using the first stage model.

    Args:
        model (YOLO): The first stage model.
        image (np.ndarray): The input image.
    Returns:
        list[np.ndarray]: The bounding boxes of the mitotic candidates.
    """
    normalizer = NormalizeHEStains()

    patches = patchify(
        image,
        FIRST_STAGE_PATCH_SIZE,
        step=FIRST_STAGE_PATCH_SIZE[0]
    )

    n_rows, n_cols = patches.shape[:2]

    candidates: list[np.ndarray] = []

    for row_index in range(n_rows):
        for col_index in range(n_cols):
            patch = patches[row_index, col_index].squeeze()

            try:
                patch = normalizer(patch)
            except ValueError:
                continue

            prediction: Results = model.predict(patch)[0].cpu()

            patch_height, patch_width = FIRST_STAGE_PATCH_SIZE[:2]

            y_offset = row_index * patch_height
            x_offset = col_index * patch_width

            offset = np.array([y_offset, x_offset, y_offset, x_offset])
            bboxes = prediction.boxes.xyxy.numpy().astype(np.int32) + offset

            if len(bboxes) == 0:
                continue

            candidates.extend(bboxes)

    return candidates


def _extract_patch_second_stage(
    image: np.ndarray,
    bbox: np.ndarray,
    patch_size: int = 64
) -> np.ndarray:
    """Extracts a patch from the image centered around the bounding box coordinates.

    Args:
        image (np.ndarray): The input image.
        bbox (np.ndarray): The bounding box coordinates.
        patch_size (int): The size of the patch.
    Returns:
        np.ndarray: The extracted patch.
    """
    image_height, image_width = image.shape[:2]

    x1, y1, x2, y2 = bbox

    center_y = y1 + (y2 - y1) // 2
    center_x = x1 + (x2 - x1) // 2

    half_patch_size = patch_size // 2

    patch_x1 = center_x - half_patch_size
    patch_x2 = patch_x1 + patch_size
    patch_y1 = center_y - half_patch_size
    patch_y2 = patch_y1 + patch_size

    if patch_x1 < 0:
        patch_x1 = 0
        patch_x2 = patch_size
    if patch_y1 < 0:
        patch_y1 = 0
        patch_y2 = patch_size
    if patch_x2 > image_width:
        patch_x2 = image_width
        patch_x1 = image_width - patch_size
    if patch_y2 > image_height:
        patch_y2 = image_height
        patch_y1 = image_height - patch_size

    return image[patch_y1:patch_y2, patch_x1:patch_x2]


@torch.no_grad()
def predict_second_stage(
    model: EfficientNet,
    image: np.ndarray,
    bboxes: list[np.ndarray],
    device: torch.device
) -> list[MitosisPrediction]:
    """Classifies the mitotic candidates in the input image
    using the second stage model.

    Args:
        model (EfficientNet): The second stage model.
        image (np.ndarray): The input image.
        bboxes (list[np.ndarray]): The bounding boxes of the mitotic candidates.
        device (torch.device): The device to use for inference.
    Returns:
        list[MitosisPrediction]: The classification results.
    """
    stain_normalize = A.Compose(
        [
            A.Resize(64, 64),
            NormalizeHEStainsWrapper()
        ]
    )
    basic_transforms = A.Compose(
        [
            stain_normalize,
            A.Normalize(
                mean=(0.77986992, 0.54518602, 0.7211757),
                std=(0.10058567, 0.12314448, 0.07771834)
            ),
            ToTensorV2()
        ]
    )

    model.eval()
    model.to(device)

    patches = (
        _extract_patch_second_stage(
            image=image,
            bbox=bbox
        )
        for bbox in bboxes
    )

    results: list[MitosisPrediction] = []

    for patch, bbox in zip(patches, bboxes):
        try:
            patch = stain_normalize(image=patch)['image']
            patch = basic_transforms(image=patch)['image']
        except ValueError:
            continue

        tensor_patch: torch.Tensor = patch[None, ...]
        tensor_patch = tensor_patch.to(device)

        prediction = model(tensor_patch).cpu()
        label = prediction.argmax().numpy()
        prob = F.softmax(prediction, dim=-1).max().numpy()

        results.append({
            'bbox': bbox,
            'label': label.item(),
            'conf': prob.item()
        })

    return results
