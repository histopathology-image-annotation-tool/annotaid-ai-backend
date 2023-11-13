from pathlib import Path


def read_file(path: Path) -> str:
    with open(path) as fp:
        return fp.read()
