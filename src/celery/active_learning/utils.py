from enum import Enum
from urllib.parse import urlparse, urlunparse

import numpy as np
from geoalchemy2 import WKTElement
from pydantic import AnyHttpUrl


class MitosisLabel(str, Enum):
    """Represents possible labels for mitosis."""
    mitosis = 'mitosis'
    hard_negative_mitosis = 'hard_negative_mitosis'


def join_url(base_url: str | AnyHttpUrl, path: str) -> str:
    """Joins a base URL with a path.

    Args:
        base_url (str | AnyHttpUrl): The base URL.
        path (str): The path to join.

    Returns:
        str: The joined URL.
    """
    url_parts = list(urlparse(str(base_url)))
    url_parts[2] = path
    return urlunparse(url_parts)


def convert_bbox_to_wkt(bbox: np.ndarray) -> WKTElement:
    """Converts a bounding box to a WKT element.

    Args:
        bbox (np.ndarray): The bounding box (x_min, y_min, x_max, y_max).

    Returns:
        WKTElement: The WKT element.
    """
    return WKTElement(
        f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, "
        f"{bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))", srid=4326)


def transform_label(label: str) -> MitosisLabel | str:
    """Transforms a label to a MitosisLabel.

    Args:
        label (str): The label to transform (0 or 1).

    Returns:
        MitosisLabel | str: The transformed label.
    """
    _mapping: dict[str, MitosisLabel] = {
        "0": MitosisLabel.mitosis,
        "1": MitosisLabel.hard_negative_mitosis
    }

    return _mapping.get(label, label)
