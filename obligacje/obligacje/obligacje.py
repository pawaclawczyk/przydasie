import sys
from pathlib import Path

import pandas as pd

PATTERN = "StanRachunkuRejestrowego_*.xls"

DTYPES = {
    "EMISJA": "string",
    "DOSTĘPNA LICZBA OBLIGACJI": "int64",
    "ZABLOKOWANA LICZBA OBLIGACJI": "int64",
    "WARTOŚĆ NOMINALNA": "float64",
    "WARTOŚĆ AKTUALNA": "float64",
    "DATA WYKUPU": "datetime64[ns]",
}


def find_all(directory: Path) -> list[Path]:
    return list(directory.rglob(PATTERN))


def find_latest(directory: Path) -> Path:
    return sorted(find_all(directory))[-1]


def read(path: Path):
    df = pd.read_excel(path, dtype=DTYPES)
    print(df)
    print(df.info())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("usage: obligacje.py [path to data dir]")
    data_dir = sys.argv[1]
    latest = find_latest(Path(data_dir))
    print("latest:", latest)
    read(latest)
