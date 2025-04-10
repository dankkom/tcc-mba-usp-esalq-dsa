"""
This script loads and transforms the dengue, population and municipalities data.

Files dependencies:

- data/sinan-dengue.parquet
- data/populacao-municipios.parquet
- data/br_mun.gpkg

Files output:

- data/dengue-populacao-mun.csv
- data/dengue-populacao-mun.parquet

"""

import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")


def load_transform_dengue(data_dir: Path):
    # Dados Dengue
    dengue = (
        pd.read_parquet(
            data_dir / "sinan-dengue.parquet",
            columns=["DT_NOTIFIC", "NU_ANO", "SG_UF_NOT", "ID_MUNICIP", "CLASSI_FIN"],
        )
        .query("CLASSI_FIN != 'Descartado' and NU_ANO >= '2020'")
        .drop(columns="CLASSI_FIN")
        .assign(
            DT_NOTIFIC=lambda x: pd.to_datetime(x.DT_NOTIFIC),
            notificacoes=1,
        )
        .rename(columns={"DT_NOTIFIC": "data", "SG_UF_NOT": "sigla_uf", "ID_MUNICIP": "id_municipio_6"})
    )
    dengue = dengue.loc[
        (dengue["id_municipio_6"].str.len() == 6) & (dengue["data"].notnull())
    ]
    dengue = (
        dengue.groupby(["data", "sigla_uf", "id_municipio_6"])
        .agg({"notificacoes": "sum"})
        .reset_index()
    )

    return dengue


def load_transform_populacao(data_dir: Path):
    # Dados População
    populacao = (
        pd.read_parquet(data_dir / "populacao-municipios.parquet")
        .assign(
            data=lambda x: pd.to_datetime(x["data"]),
            id_municipio_6=lambda x: x["municipio_id"].str[:6],
        )
        .drop(columns="municipio_id")
    )

    return populacao


def load_transform_br_mun(data_dir: Path):
    # Dados geográficos dos municípios
    br_mun_filepath = data_dir / "br_mun.gpkg"
    br_mun = gpd.read_file(br_mun_filepath, columns=["id_municipio_6"])
    br_mun.geometry = br_mun.centroid
    br_mun["longitude"] = br_mun.geometry.x
    br_mun["latitude"] = br_mun.geometry.y
    # Drop geometry
    br_mun = br_mun.drop(columns="geometry")

    return br_mun


def main():
    data_dir = Path("data")

    dengue = load_transform_dengue(data_dir)

    populacao = load_transform_populacao(data_dir)

    # Dados geográficos dos municípios
    br_mun = load_transform_br_mun(data_dir)

    # Merge Dengue, População e Municípios
    dengue_populacao_mun = (
        dengue.merge(
            populacao,
            on=["data", "id_municipio_6"],
            how="left",
        )
        .merge(
            br_mun,
            on="id_municipio_6",
            how="left",
        )
        .assign(
            data=lambda x: x["data"] + pd.DateOffset(hours=12),
            incidencia=lambda x: x["notificacoes"] / x["populacao_estimada"] * 100_000,
        )
    )

    dengue_populacao_mun.to_csv(
        data_dir / "dengue-populacao-mun.csv",
        index=False,
    )
    dengue_populacao_mun.to_parquet(data_dir / "dengue-populacao-mun.parquet")


if __name__ == "__main__":
    main()
