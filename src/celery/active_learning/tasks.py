import base64
import copy
from io import BytesIO

import cv2
import httpx
import numpy as np
from geoalchemy2 import functions
from PIL import Image
from sqlalchemy import desc

import src.db_models as db_models
from celery import Task, shared_task, subtask
from celery.canvas import Signature
from celery.result import AsyncResult
from src.celery import AL_QUEUE, AL_QUEUE_1, READER_QUEUE
from src.celery.database import get_session
from src.celery.mc.tasks import _predict_mc_task
from src.celery.shared import dmap, expand_args
from src.core.celery import celery_app
from src.core.config import settings
from src.models.mc.custom_types import MitosisPrediction

from .definitions import GetSlideMetadataResponse
from .utils import convert_bbox_to_wkt, join_url, transform_label

MITOSIS_MEAN_LAB = np.array([52.357067, 29.037254, -30.11074], dtype=np.float32)


@shared_task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue=READER_QUEUE
)
def download_tile(
    level: int,
    slide_path: str,
    x: int,
    y: int,
    tile_size: int
) -> np.ndarray:
    """Download a tile from the reader service.

    Args:
        level (int): The level of the slide.
        slide_path (str): The path to the slide.
        x (int): The x coordinate of the tile.
        y (int): The y coordinate of the tile.
        tile_size (int): The size of the tile.

    Returns:
        np.ndarray: The tile as a numpy array.
    """
    response = httpx.get(
        join_url(settings.READER_URL, slide_path),
        params={
            'z': level,
            'x': x,
            'y': y,
            'w': tile_size,
            'h': tile_size
        }
    )
    return np.array(Image.open(BytesIO(response.content)))


@shared_task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue=READER_QUEUE
)
def crop_tile(
    slide_path: str,
    x: int,
    y: int,
    tile_size: int
) -> np.ndarray:
    """Crop a tile from the reader service.

    Args:
        slide_path (str): The path to the slide.
        x (int): The x coordinate of the tile.
        y (int): The y coordinate of the tile.
        tile_size (int): The size of the tile.

    Returns:
        np.ndarray: The cropped tile as a numpy array.
    """
    response = httpx.get(
        join_url(settings.READER_URL, f"/crop/{slide_path}"),
        params={
            'x': x,
            'y': y,
            'w': tile_size,
            'h': tile_size
        }
    )
    response = response.json()

    return np.array(Image.open(BytesIO(base64.b64decode(response['base64Image']))))


@shared_task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue=READER_QUEUE
)
def download_metadata(
    slide_path: str,
    level: int | None = None
) -> GetSlideMetadataResponse:
    """Download slide metadata from the reader service.

    Args:
        slide_path (str): The path to the slide.
        level (int | None): The level (magnification) of the slide.

    Returns:
        GetSlideMetadataResponse: The slide metadata.
    """
    response = httpx.get(
        join_url(
            settings.READER_URL,
            f"/metadata{slide_path}{'?z=' + str(level) if level is not None else ''}"
        )
    )
    response = response.json()

    return GetSlideMetadataResponse(**response)


@celery_app.task(ignore_result=True, queue=AL_QUEUE)
def create_tissue_mask(
    image: np.ndarray,
    median_blur: int = 5,
    slic_region_size: int = 32
) -> np.ndarray:
    """Create a tissue mask from an image.

    Args:
        image (np.ndarray): The image.
        median_blur (int): The median blur.
        slic_region_size (int): The slic region size.

    Returns:
        np.ndarray: The tissue mask (binary form).
    """
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    image_s = image_hsv[:, :, 1]

    image_s = cv2.medianBlur(image_s, median_blur)

    se3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    image_s = cv2.filter2D(image_s, -1, se3)

    # create superpixels
    slic = cv2.ximgproc.createSuperpixelSLIC(
        image_s, algorithm=cv2.ximgproc.SLICO, region_size=slic_region_size
    )
    slic.iterate()

    # threshold superpixels
    T = np.mean(image_s)
    output_image = np.zeros_like(image_s, dtype=bool)

    num_superpixels = slic.getNumberOfSuperpixels()
    labels = slic.getLabels()

    for label_val in range(num_superpixels):
        idx = np.uint8(labels == label_val)

        superpixel_coords = np.where(idx > 0)

        mean_val = np.mean(image_s[superpixel_coords])

        if mean_val > T:
            output_image[superpixel_coords] = 1

    return output_image


@celery_app.task(ignore_result=True, queue=AL_QUEUE)
def clean_data(
    mitoses: list[MitosisPrediction],
    image: np.ndarray
) -> list[MitosisPrediction]:
    """Clean the data by removing false positives.
    It compares the predicted mitoses and hard-negative mitoses to the reference image.

    Args:
        mitoses (list[MitosisPrediction]): The predicted mitoses and
        hard-negative mitoses.
        image (np.ndarray): The image.

    Returns:
        list[MitosisPrediction]: The cleaned predicted mitoses and
        hard-negative mitoses.
    """
    cleared_mitoses: list[MitosisPrediction] = []

    for mitos in mitoses:
        bbox = mitos['bbox']
        x1, y1, x2, y2 = bbox

        patch = image[y1:y2, x1:x2]
        patch = cv2.cvtColor(patch.astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)

        difference_image = np.sqrt(
            np.sum(np.power((patch - MITOSIS_MEAN_LAB), 2), axis=2)
        )

        difference_threshold = cv2.threshold(
            src=difference_image,
            thresh=20,
            maxval=255,
            type=cv2.THRESH_BINARY_INV
        )[1]

        if np.sum(difference_threshold == 255) / difference_threshold.size >= 0.02:
            cleared_mitoses.append(mitos)

    return cleared_mitoses


@celery_app.task(ignore_result=True, queue=AL_QUEUE)
def get_tiles_coords_from_tissue_mask(
    mask: np.ndarray,
    slide_width: int,
    slide_height: int,
    mask_magnification: int,
    slide_magnification: int,
    tile_size: int = 2048,
    overlap: float = 0.05
) -> list[tuple[int, int]]:
    """Get the coordinates of the tiles from the tissue mask. It extracts the tiles
    that contain more than 50% tissue.

    Args:
        mask (np.ndarray): The tissue mask.
        slide_width (int): The width of the slide.
        slide_height (int): The height of the slide.
        mask_magnification (int): The magnification of the mask.
        slide_magnification (int): The magnification of the slide.
        tile_size (int): The size of the tile.
        overlap (float): The overlap of the tiles.

    Returns:
        list[tuple[int, int]]: The coordinates of the tiles.
    """
    coords = []

    magnifier = 2**(slide_magnification - mask_magnification)
    step = int(tile_size * (1 - overlap))

    for y in range(0, slide_height, step):
        for x in range(0, slide_width, step):
            x_start = x // magnifier
            y_start = y // magnifier

            x_end = (x + tile_size) // magnifier
            y_end = (y + tile_size) // magnifier

            patch = mask[y_start:y_end, x_start:x_end]

            tissue_area = np.sum(patch == 1) / patch.size

            if tissue_area > 0.5:
                coords.append((x, y))

    return coords


@celery_app.task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue=AL_QUEUE
)
def store_predictions(
    predictions: list[MitosisPrediction],
    slide_path: str,
) -> None:
    """Store the predictions in the database.

    Args:
        predictions (list[MitosisPrediction]): The predictions.
        slide_path (str): The path to the slide.

    Raises:
        ValueError: If the whole slide image is not found.

    Returns:
        None
    """
    with get_session() as session:
        slide = session.query(
            db_models.WholeSlideImage
        ).filter_by(
            path=f"{slide_path}"
        ).first()

        if slide is None:
            raise ValueError(f'Whole slide image with path {slide_path} not found')

        for prediction in predictions:
            bbox = prediction['bbox']

            bbox_wkt = convert_bbox_to_wkt(bbox)

            intersecting_polygon_result = session.query(
                functions.ST_Area(
                    functions.ST_Intersection(db_models.Prediction.bbox, bbox_wkt)
                ).label('intersection_area')
            ).filter(
                functions.ST_Intersects(db_models.Prediction.bbox, bbox_wkt)
            ).order_by(desc('intersection_area')).first()

            if intersecting_polygon_result is not None:
                polygon_wkt_area = session.query(
                    functions.ST_Area(bbox_wkt)
                ).scalar()

                intersecting_polygon_area = intersecting_polygon_result[0]

                intersection = intersecting_polygon_area / polygon_wkt_area * 100

                if intersection >= 50:
                    continue

            prediction = db_models.Prediction(
                slide_id=slide.id, type='MC_TASK', bbox=bbox_wkt,
                probability=prediction['conf'],
                label=transform_label(str(prediction['label'])),
                model_hash=None
                if 'model_hash'
                not in prediction else
                prediction['model_hash']
                [: db_models.Prediction.model_hash.property.columns[0].type.length])

            session.add(prediction)

        session.commit()


@shared_task(ignore_result=True, queue=AL_QUEUE)
def add_offset(
    mitosis: list[MitosisPrediction],
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    """Add an offset to the predicted mitoses.

    Args:
        mitosis (list[MitosisPrediction]): The predicted mitoses.
        offset (tuple[int, int]): The offset.

    Returns:
        list[MitosisPrediction]: The predicted mitoses with the offset.
    """
    copied_mitosis = copy.deepcopy(mitosis)

    bbox_offset = np.array([*offset, *offset], dtype=np.int32)

    for mitos in copied_mitosis:
        mitos['bbox'] += bbox_offset

    return copied_mitosis


@celery_app.task(bind=True, ignore_result=True, queue=AL_QUEUE)
def predict_mitoses_and_clean_result(
    self: Task,
    image: np.ndarray
) -> list[MitosisPrediction]:
    """Predict mitoses and clean the false positive results.

    Args:
        image (np.ndarray): The image.

    Returns:
        list[MitosisPrediction]: The cleaned predictions as Signature.
    """
    sig = subtask(
        _predict_mc_task.s(image=image, offset=(0, 0)),
        queue=AL_QUEUE
    ) | clean_data.s(
        image=image
    )

    return self.replace(sig)


@celery_app.task(bind=True, ignore_result=True, queue=AL_QUEUE_1)
def process_tile(
    self: Task,
    coords: np.ndarray,
    slide_path: str,
    tile_size: int
) -> Signature:
    """Process a tile. It crops the tile, predicts mitoses, cleans the results,
    adds an offset, and stores the predictions in the database.

    Args:
        coords (np.ndarray): The coordinates of the tile.
        slide_path (str): The path to the slide.
        tile_size (int): The size of the tile.

    Returns:
        Signature: The signature of the task.
    """
    sig = crop_tile.s(
        slide_path=slide_path,
        x=coords[0],
        y=coords[1],
        tile_size=tile_size
    ) | predict_mitoses_and_clean_result.s() | add_offset.s(
        offset=(coords[0], coords[1])
    ) | store_predictions.s(
        slide_path=slide_path
    )

    return self.replace(sig)


@shared_task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue=READER_QUEUE
)
def get_slide_best_magnification(
    slide_path: str,
    tile_size: int = 2048
) -> tuple[int, GetSlideMetadataResponse, GetSlideMetadataResponse]:
    """Get the best magnification of the slide.
    It iterates over the magnifications from the biggest to the smallest one and
    stops when the size of the slide is smaller than the tile size.

    Args:
        slide_path (str): The path to the slide.
        tile_size (int): The size of the tile.

    Returns:
        tuple[int, GetSlideMetadataResponse, GetSlideMetadataResponse]:
        The best magnification, the mask metadata, and the slide metadata."""
    current_magnification = 0
    max_magnification: int | None = None
    mask_metadata = None
    slide_metadata = None

    with httpx.Client() as client:
        while max_magnification is None or current_magnification < max_magnification:
            response = client.get(
                join_url(settings.READER_URL, f"/metadata/{slide_path}"),
                params={
                    'z': current_magnification
                }
            )
            response = response.json()
            mask_metadata = GetSlideMetadataResponse(**response)

            if slide_metadata is None:
                slide_metadata = mask_metadata

            if max_magnification is None:
                max_magnification = mask_metadata.levels

            if mask_metadata.size.width.pixel <= tile_size or mask_metadata.size.\
                height.pixel <= tile_size:  # noqa: E125
                break

            current_magnification += 1

    return (
        max_magnification - current_magnification,
        mask_metadata,
        slide_metadata
    )


@celery_app.task(bind=True, ignore_result=True, queue=AL_QUEUE)
def get_coords(
    self: Task,
    mask_magnification: int,
    mask_metadata: GetSlideMetadataResponse,
    slide_metadata: GetSlideMetadataResponse,
    path: str,
    tile_size: int = 2048
) -> list[tuple[int, int]]:
    """Get the coordinates of the tiles from the best magnification of the slide.
    It downloads the tiles, creates a tissue mask,
    and extracts the tiles that contain more than 50% tissue.

    Args:
        mask_magnification (int): The magnification of the mask.
        mask_metadata (GetSlideMetadataResponse): The mask metadata.
        slide_metadata (GetSlideMetadataResponse): The slide metadata.
        path (str): The path to the slide.
        tile_size (int): The size of the tile.

    Returns:
        list[tuple[int, int]]: The coordinates of the tiles as Signature.
    """
    sig = download_tile.s(
        level=mask_magnification,
        slide_path=path,
        x=0,
        y=0,
        tile_size=tile_size
    ) | create_tissue_mask.s() | get_tiles_coords_from_tissue_mask.s(
        slide_width=int(slide_metadata.size.width.pixel),
        slide_height=int(slide_metadata.size.height.pixel),
        mask_magnification=mask_magnification,
        slide_magnification=slide_metadata.levels,
        tile_size=tile_size
    )

    return self.replace(sig)


@celery_app.task(ignore_result=True, track_started=True, queue=AL_QUEUE)
def process_slide(
    path: str,
    tile_size: int = 2048
) -> AsyncResult:
    """Process a slide. It gets the best magnification of the slide,
    the mask metadata, and the slide metadata.
    Then, it gets the coordinates of the tiles and processes them.

    Args:
        path (str): The path to the slide.
        tile_size (int): The size of the tile.

    Returns:
        AsyncResult: The result of the task.
    """
    chain = get_slide_best_magnification.s(
        slide_path=path,
        tile_size=tile_size
    ) | subtask(
        expand_args.s(
            get_coords.s(
                path=path,
                tile_size=tile_size
            )
        ),
        queue=AL_QUEUE
    ) | dmap.s(
        process_tile.s(
            slide_path=path,
            tile_size=tile_size
        )
    )

    return chain()


@shared_task(ignore_result=True, queue=READER_QUEUE)
def get_list_of_slide_files() -> list[str]:
    """Get the list of slide files from the reader service.

    Returns:
        list[str]: The list of slide files.
    """
    response = httpx.get(
        join_url(settings.READER_URL, "/ls/mnt"),
        params={
            'ext': 'vsi'
        }
    )
    json_response: list[str] = response.json()

    return [
        file
        for file in json_response
        if file.find("_HE") != -1
    ]


@shared_task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue=AL_QUEUE
)
def store_metadata(metadatas: list[GetSlideMetadataResponse]) -> None:
    """Store slide metadata in the database.
    If the slide is already in the database, it updates it.

    Args:
        metadatas (list[GetSlideMetadataResponse]): The slide metadata.

    Raises:
        ValueError: If the slide is not found.

    Returns:
        None
    """
    with get_session() as session:
        hashes = [metadata.hash for metadata in metadatas]

        existing_slides_query = session.query(db_models.WholeSlideImage).where(
            db_models.WholeSlideImage.hash.in_(hashes)
        )

        existing_slides_result = session.execute(existing_slides_query).fetchall()
        existing_slides: dict[str, db_models.WholeSlideImage] = {
            slide[0].hash: slide[0]
            for slide in existing_slides_result
        }

        for metadata in metadatas:
            if metadata.hash in existing_slides:
                slide = existing_slides[metadata.hash]
                slide.format = metadata.format
                slide.hash = metadata.hash
                slide.path = metadata.path.as_posix()
            else:
                slide = db_models.WholeSlideImage(
                    hash=metadata.hash,
                    path=metadata.path.as_posix(),
                    format=metadata.format
                )

                session.add(slide)

        session.commit()


@shared_task(ignore_result=True, queue=READER_QUEUE)
def synchronize_slides() -> AsyncResult:
    """Synchronize the slides.
    It gets the list of slide files, downloads the metadata, and stores it.

    Returns:
        AsyncResult: The result of the task (None).
    """
    chain = get_list_of_slide_files.s() | subtask(
        dmap.s(
            download_metadata.s()
        ),
        queue=READER_QUEUE
    ) | store_metadata.s()

    return chain()
