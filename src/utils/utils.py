from pathlib import Path


def read_file(path: Path) -> str:
    """Reads a file and returns its content.

    Args:
        path (Path): The path to the file.
    Returns:
        str: The content of the file.
    """
    with open(path) as fp:
        return fp.read()
