import numpy as np
from imantics import Mask

from src.core.celery import celery_app
from src.models import predict_nuclick
from src.schemas.nuclick import Keypoint

from .definitions import NuclickTask


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=NuclickTask
)
def predict_nuclick_task(
    self: NuclickTask,
    image: np.ndarray,
    keypoints: list[Keypoint],
    offset: tuple[int, int]
) -> list[list[Keypoint]]:
    """Segments the nuclei in the input image based on the input keypoints
    using the NuClick model.

    Args:
        image (np.ndarray): The input image.
        keypoints (list[Keypoint]): The user-defined keypoints relative
        to the top left corner of the image.
        offset (tuple[int, int]): The offset to be added to the keypoints.
    Returns:
        list[list[Keypoint]]: The segmented nuclei in the form of a list of keypoints.
    """
    self.model.eval()

    result = predict_nuclick(
        model=self.model,
        image=image,
        keypoints=keypoints,
        device=self.device
    )

    polygons = Mask(result).polygons()

    return [
        [
            {
                "x": point[0] + offset[0],
                "y": point[1] + offset[1]
            }
            for point in nuclei_points
        ]
        for nuclei_points in polygons.points
    ]
