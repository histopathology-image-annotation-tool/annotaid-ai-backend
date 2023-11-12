from typing import Any

import numpy as np
import torch
from skimage.morphology import (
    reconstruction,
    remove_small_holes,
    remove_small_objects,
)

from src.schemas.nuclick import Keypoint

from .architecture import NuClick_NN

bb = 128

BoundingBox = tuple[int, int, int, int]


def get_clickmap_boundingbox(
    keypoints: list[Keypoint],
    image_shape: tuple[int, int]
) -> tuple[np.ndarray[Any, np.dtype[np.uint8]], list[BoundingBox]]:
    image_height, image_width = image_shape

    click_map = np.zeros((image_height, image_width), dtype=np.uint8)

    x_coords = np.array([keypoint.x for keypoint in keypoints], dtype=np.int32)
    y_coords = np.array([keypoint.y for keypoint in keypoints], dtype=np.int32)

    # Remove points out of image dimension
    x_coords = x_coords[np.where((x_coords >= 0) & (x_coords <= image_width))]
    y_coords = y_coords[np.where((y_coords >= 0) & (y_coords <= image_height))]

    click_map[y_coords, x_coords] = 1

    bounding_boxes: list[BoundingBox] = []

    for x, y in zip(x_coords, y_coords):
        x_start = x - bb // 2
        y_start = y - bb // 2

        if x_start < 0:
            x_start = 0
        if y_start < 0:
            y_start = 0

        x_end = x_start + bb - 1
        y_end = y_start + bb - 1

        if x_end > image_width - 1:
            x_end = image_width - 1
            x_start = x_end - bb + 1
        if y_end > image_height - 1:
            y_end = image_height - 1
            y_start = y_end - bb + 1

        bounding_boxes.append((x_start, y_start, x_end, y_end))

    return click_map, bounding_boxes


def get_patches_and_signals(
    image: np.ndarray,
    click_map: np.ndarray,
    bounding_boxes: list[BoundingBox],
    keypoints: list[Keypoint],
    image_shape: tuple[int, int]
) -> tuple[
    np.ndarray[Any, np.dtype[np.uint8]],
    np.ndarray[Any, np.dtype[np.uint8]],
    np.ndarray[Any, np.dtype[np.uint8]]
]:
    image_height, image_width = image_shape

    total = len(bounding_boxes)
    image = np.array([image])
    click_map = np.array([click_map])
    click_map = click_map[:, np.newaxis, ...]

    patches: np.ndarray[Any, np.dtype[np.uint8]] = np.ndarray(
        (total, 3, bb, bb),
        dtype=np.uint8
    )
    nuc_points: np.ndarray[Any, np.dtype[np.uint8]] = np.ndarray(
        (total, 1, bb, bb),
        dtype=np.uint8
    )
    other_points: np.ndarray[Any, np.dtype[np.uint8]] = np.ndarray(
        (total, 1, bb, bb),
        dtype=np.uint8
    )

    x_coords = np.array([keypoint.x for keypoint in keypoints], dtype=np.int32)
    y_coords = np.array([keypoint.y for keypoint in keypoints], dtype=np.int32)

    # Remove points out of image dimension
    x_coords = x_coords[np.where((x_coords >= 0) & (x_coords <= image_width))]
    y_coords = y_coords[np.where((y_coords >= 0) & (y_coords <= image_height))]

    for index in range(total):
        bounding_box = bounding_boxes[index]

        x_start, y_start, x_end, y_end = bounding_box

        patches[index] = image[0, :, y_start:y_end + 1,
                               x_start:x_end + 1]

        this_click_map = np.zeros((1, 1, image_height, image_width), dtype=np.uint8)
        this_click_map[0, 0, y_coords[index], x_coords[index]] = 1

        others_click_map = np.uint8((click_map - this_click_map) > 0)

        nuc_points[index] = this_click_map[
            0, :,
            y_start:y_end + 1, x_start:x_end + 1
        ]
        other_points[index] = others_click_map[  # type: ignore
            0, :,
            y_start:y_end + 1, x_start:x_end + 1
        ]

    return patches, nuc_points, other_points


def post_processing(
    preds: np.ndarray,
    thresh: float = 0.33,
    min_size: int = 10,
    min_hole: int = 30,
    do_reconstruction: bool = False,
    nuc_points: np.ndarray | None = None
) -> np.ndarray:
    masks = preds > thresh
    masks: np.ndarray = remove_small_objects(masks, min_size=min_size)  # type: ignore
    masks: np.ndarray = remove_small_holes(  # type: ignore
        masks,
        area_threshold=min_hole
    )

    if do_reconstruction:
        for i in range(len(masks)):
            this_mask = masks[i]
            this_marker = nuc_points[i, 0, :, :] > 0  # type: ignore
            try:
                this_mask = reconstruction(this_marker, this_mask)
                masks[i] = np.array([this_mask])
            except Exception as e:
                print(e)

    return masks


def get_instance_map(
    masks: np.ndarray,
    bounding_boxes: list[BoundingBox],
    image_shape: tuple[int, int]
) -> np.ndarray:
    image_height, image_width = image_shape

    instance_map = np.zeros((image_height, image_width), dtype=np.uint16)

    for i in range(len(masks)):
        this_bb = bounding_boxes[i]
        this_mask_pos = np.argwhere(masks[i] > 0)
        this_mask_pos[:, 0] = this_mask_pos[:, 0] + this_bb[1]
        this_mask_pos[:, 1] = this_mask_pos[:, 1] + this_bb[0]
        instance_map[this_mask_pos[:, 0], this_mask_pos[:, 1]] = i + 1
    return instance_map


@torch.no_grad()
def predict(
    model: NuClick_NN,
    image: np.ndarray,
    keypoints: list[Keypoint],
    device: torch.device
) -> np.ndarray[Any, np.dtype[np.uint8]]:
    model.eval()

    image_shape = image.shape[:2]

    click_map, bounding_boxes = get_clickmap_boundingbox(
        keypoints=keypoints,
        image_shape=image_shape
    )

    image = np.asarray(image)[:, :, :3]
    image = np.moveaxis(image, 2, 0)

    patches, nuc_points, other_points = get_patches_and_signals(
        image=image,
        click_map=click_map,
        bounding_boxes=bounding_boxes,
        keypoints=keypoints,
        image_shape=image_shape
    )

    patches = patches.astype(np.float32) / 255

    input = np.concatenate(
        (patches, nuc_points, other_points),
        axis=1, dtype=np.float32)
    input = torch.from_numpy(input)
    input = input.to(device=device, dtype=torch.float32, non_blocking=True)

    output = model(input)
    output = torch.sigmoid(output)
    output = torch.squeeze(output, 1)
    preds = output.cpu().numpy()

    masks = post_processing(
        preds=preds,
        do_reconstruction=True,
        nuc_points=nuc_points
    )

    return get_instance_map(
        masks=masks,
        bounding_boxes=bounding_boxes,
        image_shape=image_shape
    )
