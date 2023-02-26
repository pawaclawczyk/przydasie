import datetime
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PATTERN = "StanRachunkuRejestrowego_*.xls"

date_pattern = re.compile(r"StanRachunkuRejestrowego_(.*).xls$")

COLUMNS = {
    "EMISJA": "emission",
    "DOSTĘPNA LICZBA OBLIGACJI": "available_count",
    "ZABLOKOWANA LICZBA OBLIGACJI": "blocked_count",
    "WARTOŚĆ NOMINALNA": "base_value",
    "WARTOŚĆ AKTUALNA": "current_value",
    "DATA WYKUPU": "redemption_date",
}

DTYPES = {
    "emission": "string",
    "available_count": "int64",
    "blocked_count": "int64",
    "base_value": "float64",
    "current_value": "float64",
    "redemption_date": "datetime64[ns]",
}

TERM_CLASSES = {
    "COI": "LONG",
    "EDO": "LONG",
}

REDEMPTION_COSTS = {
    "COI": 0.70,
    "EDO": 2.00,
}

NET_RATIO = 0.81


def find_all(directory: Path) -> list[Path]:
    return list(directory.rglob(PATTERN))


def find_latest(directory: Path) -> Path:
    return sorted(find_all(directory))[-1]


def read(path: Path) -> pd.DataFrame:
    captured_date = date_pattern.match(str(path.name)).group(1)
    df = pd.read_excel(path)
    df = df.rename(COLUMNS, axis="columns")
    df = df.astype(DTYPES)
    df["current_date"] = pd.Series(
        datetime.date.fromisoformat(captured_date), index=df.index
    ).astype("datetime64[ns]")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    count = df["available_count"] + df["blocked_count"]
    emission_class = df["emission"].str[:3]
    redemption_cost = emission_class.map(REDEMPTION_COSTS, na_action=None) * count
    profit = df["current_value"] - df["base_value"]
    current_profit = np.maximum(profit - redemption_cost, 0)
    current_net_profit = NET_RATIO * current_profit
    current_net_value = df["base_value"] + current_net_profit

    term_class = emission_class.map(TERM_CLASSES, na_action=None)

    return pd.DataFrame(
        {
            "current_date": df["current_date"],
            "term_class": term_class,
            "current_net_value": current_net_value,
        }
    )


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("term_class")
        .agg(
            current_date=("current_date", np.max),
            current_net_value=("current_net_value", np.sum),
        )
        .round(2)
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("usage: obligacje.py [path to data dir]")
    data_dir = sys.argv[1]
    latest = find_latest(Path(data_dir))
    df = read(latest)
    df = transform(df)
    df = aggregate(df)
    print(df)
