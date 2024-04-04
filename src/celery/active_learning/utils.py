from urllib.parse import urlparse, urlunparse

import numpy as np
from geoalchemy2 import WKTElement
from pydantic import AnyHttpUrl


def join_url(base_url: str | AnyHttpUrl, path: str) -> str:
    url_parts = list(urlparse(str(base_url)))
    url_parts[2] = path
    return urlunparse(url_parts)


def convert_bbox_to_wkt(bbox: np.ndarray) -> WKTElement:
    return WKTElement(
        f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, "
        f"{bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))", srid=4326)
