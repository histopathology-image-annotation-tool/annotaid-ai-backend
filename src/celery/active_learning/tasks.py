import base64
import copy
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import cv2
import httpx
import numpy as np
from geoalchemy2 import WKTElement, functions
from PIL import Image
from pydantic import AnyHttpUrl, BaseModel, NonNegativeFloat, NonNegativeInt
from sqlalchemy import desc

import src.db_models as db_models
from celery import shared_task
from src.celery.database import get_session
from src.celery.mc.tasks import _predict_mc_task
from src.celery.shared import dmap, expand_args, residual
from src.core.celery import celery_app
from src.core.config import settings
from src.models.mc.custom_types import MitosisPrediction

MITOSIS_MEAN_LAB = np.array([52.357067, 29.037254, -30.11074], dtype=np.float32)


class PixelsPerMeter(BaseModel):
    avg: NonNegativeFloat
    x: NonNegativeFloat
    y: NonNegativeFloat


class MetadataDimSize(BaseModel):
    micro: NonNegativeFloat
    pixel: NonNegativeFloat


class Size(BaseModel):
    c: NonNegativeInt
    t: NonNegativeInt
    z: NonNegativeInt
    width: MetadataDimSize
    height: MetadataDimSize


class FileSize(BaseModel):
    uncompressed: NonNegativeInt
    compressed: NonNegativeInt


class GetSlideMetadataResponse(BaseModel):
    magnification: NonNegativeInt
    format: str
    domains: list[str]
    resolution: NonNegativeInt
    fillColor: NonNegativeInt
    path: Path
    pixelsPerMeter: PixelsPerMeter
    size: Size
    fileSize: FileSize
    hash: str
    levels: NonNegativeInt


def join_url(base_url: str | AnyHttpUrl, path: str) -> str:
    url_parts = list(urlparse(str(base_url)))
    url_parts[2] = path
    return urlunparse(url_parts)


@shared_task(
    ignore_result=True,
    acks_late=True,
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=500,
    retry_jitter=True,
    queue="reader"
)
def download_tile(
    level: int,
    slide_path: str,
    x: int,
    y: int,
    tile_size: int
) -> np.ndarray:
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
    queue="reader"
)
def crop_tile(
    slide_path: str,
    x: int,
    y: int,
    tile_size: int
) -> np.ndarray:
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
    queue="reader"
)
def download_metadata(
    slide_path: str,
    level: int | None = None
) -> GetSlideMetadataResponse:
    response = httpx.get(
        join_url(
            settings.READER_URL,
            f"/metadata{slide_path}{'?z=' + str(level) if level is not None else ''}"
        )
    )
    response = response.json()

    return GetSlideMetadataResponse(**response)


@celery_app.task(ignore_result=True)
def create_tissue_mask(
    image: np.ndarray,
    median_blur: int = 5,
    slic_region_size: int = 32
) -> np.ndarray:
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


@celery_app.task(ignore_result=True)
def clean_data(
    image: np.ndarray,
    mitoses: list[MitosisPrediction]
) -> list[MitosisPrediction]:
    cleared_mitoses: list[MitosisPrediction] = []

    for index, mitos in enumerate(mitoses):
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
        else:
            patch_pil = Image.fromarray(image[y1:y2, x1:x2])
            patch_pil.save(f"pokuss/{index}_{mitos['label']}.png")

    return cleared_mitoses


@celery_app.task(ignore_result=True)
def get_tiles_coords_from_tissue_mask(
    mask: np.ndarray,
    slide_width: int,
    slide_height: int,
    mask_magnification: int,
    slide_magnification: int,
    tile_size: int = 2048,
    overlap: float = 0.05
) -> list[tuple[int, int]]:
    coords = []

    magnifier = 2**(slide_magnification - mask_magnification)
    step = int(tile_size * (1 - overlap))

    for y in range(20000, slide_height, step):
        for x in range(20000, slide_width, step):
            x_start = x // magnifier
            y_start = y // magnifier

            x_end = (x + tile_size) // magnifier
            y_end = (y + tile_size) // magnifier

            patch = mask[y_start:y_end, x_start:x_end]

            tissue_area = np.sum(patch == 1) / patch.size

            if tissue_area > 0.5:
                coords.append((x, y))

    return coords


@celery_app.task(ignore_result=True)
def store_annotations(
    annotations: list[MitosisPrediction],
    slide_path: str,
) -> None:
    with get_session() as session:
        wsi = session.query(db_models.WholeSlideImage).filter_by(path=slide_path).first()

        if wsi is None:
            raise ValueError(f'Whole slide image with path {slide_path} not found')

        for annotation in annotations:
            bbox = annotation['bbox']

            bbox_wkt = WKTElement(f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, {bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))", srid=4326)

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
                wsi_id=wsi.id,
                type='MC_TASK',
                bbox=bbox_wkt,
                probability=annotation['conf'],
                label=str(annotation['label'])
            )

            session.add(prediction)

        session.commit()


@shared_task(ignore_result=True)
def add_offset(
    mitosis: list[MitosisPrediction],
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    copied_mitosis = copy.deepcopy(mitosis)

    bbox_offset = np.array([*offset, *offset], dtype=np.int32)

    for mitos in copied_mitosis:
        mitos['bbox'] += bbox_offset

    return copied_mitosis


@celery_app.task(bind=True, ignore_result=True)
def process_tile(self, coords: np.ndarray, slide_path: str, tile_size: int):
    sig = crop_tile.s(
        slide_path=slide_path,
        x=coords[0],
        y=coords[1],
        tile_size=tile_size
    ) | residual.s(
        _predict_mc_task.s(offset=(0, 0))
    ) | expand_args.s(
        clean_data.s()
    ) | add_offset.s(
        offset=(coords[0], coords[1])
    ) | store_annotations.s(
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
    queue="reader"
)
def get_slide_best_magnification(
    slide_path: str,
    tile_size: int = 2048
) -> tuple[int, GetSlideMetadataResponse]:
    current_magnification = 0
    max_magnification = None
    metadata = None

    with httpx.Client() as client:
        while max_magnification is None or current_magnification < max_magnification:
            response = client.get(
                join_url(settings.READER_URL, f"/metadata/{slide_path}"),
                params={
                    'z': current_magnification
                }
            )
            response = response.json()
            metadata = GetSlideMetadataResponse(**response)

            if max_magnification is None:
                max_magnification = metadata.levels

            if metadata.size.width.pixel <= tile_size or metadata.size.height.pixel <= tile_size:
                break

            current_magnification += 1

    return max_magnification - current_magnification, metadata


@celery_app.task(bind=True, ignore_result=True)
def get_coords(
    self,
    mask_magnification: int,
    metadata: GetSlideMetadataResponse,
    path: str,
    tile_size: int = 2048
):
    sig = download_tile.s(
        level=mask_magnification,
        slide_path=path,
        x=0,
        y=0,
        tile_size=tile_size
    ) | create_tissue_mask.s(

    ) | get_tiles_coords_from_tissue_mask.s(
        # slide_width=int(metadata.size.width.pixel),
        # slide_height=int(metadata.size.height.pixel),
        slide_width=22000,
        slide_height=22000,
        mask_magnification=mask_magnification,
        slide_magnification=metadata.levels,
        tile_size=tile_size
    )

    return self.replace(sig)


@celery_app.task(ignore_result=True, track_started=True)
def process_wsi(
    path: str,
    tile_size: int = 2048
):
    chain = get_slide_best_magnification.s(
        slide_path=path,
        tile_size=tile_size
    ) | expand_args.s(
        get_coords.s(
            path=path,
            tile_size=tile_size
        )
    ) | dmap.s(
        process_tile.s(
            slide_path=path,
            tile_size=tile_size
        )
    )

    return chain()


@shared_task(ignore_result=True, queue="reader")
def get_list_of_wsi_files() -> list[str]:
    response = httpx.get(
        join_url(settings.READER_URL, "/ls/mnt"),
        params={
            'ext': 'vsi'
        }
    )
    response: list[str] = response.json()

    return [
        file
        for file in response
        if file.find("_HE") != -1
    ]


@shared_task(ignore_result=True)
def store_metadata(metadatas: list[GetSlideMetadataResponse]) -> None:
    with get_session() as session:
        for metadata in metadatas:
            wsi = db_models.WholeSlideImage(
                hash=metadata.hash,
                path=metadata.path.as_posix(),
                format=metadata.format
            )

            session.add(wsi)

        session.commit()


@shared_task(ignore_result=True, queue="reader")
def discover_wsi_files() -> None:
    chain = get_list_of_wsi_files.s() | dmap.s(
        download_metadata.s()
    ) | store_metadata.s()

    return chain()

# TODO: Create endpoints for the frontend to get the data for annotation
# TODO: Create alembic migrations for the database
# TODO: Update docker-compose to include the database and have persistent storage
# TODO: Update script at the server to include the database and have persistent storage
# TODO: Create multiple queues where the prediction tasks from the frontend will be prioritized
# TODO: Update dockerfile of the worker to have configurable CMD
# TODO: Save the softmax probabilities to the database
# TODO: Save the hash of the model with which the annotations were created