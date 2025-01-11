"""Carrega a malha municipal do Brasil.

Pacotes necessários:

- geopandas
- pyogrio
- requests

Documentação da API do IBGE:

https://servicodados.ibge.gov.br/api/docs/malhas?versao=3

Output files:

- data/br_mun.csv
- data/br_mun.gpkg
- data/br_regiao.json
- data/br_uf.json
- data/br_mesorregiao.json
- data/br_microrregiao.json

"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests


def download_malha(br_mun_filepath: Path, intrarregiao: str):
    url = (
        "https://servicodados.ibge.gov.br/api/v3"
        "/malhas/paises/BR"
        "?intrarregiao={intrarregiao}"
        "&qualidade=intermediaria"
        "&formato=application/json"
    )
    r = requests.get(
        url.format(intrarregiao=intrarregiao), allow_redirects=True, timeout=600
    )
    with open(br_mun_filepath, "wb") as f:
        f.write(r.content)


def load_br_mun():
    br_mun_filepath = Path("data", "br_mun.json")
    if not br_mun_filepath.exists():
        download_malha(br_mun_filepath, "municipio")
    br_mun = gpd.GeoDataFrame.from_file(br_mun_filepath).drop(columns=["id"])
    br_mun = br_mun.rename(columns={"codarea": "id_municipio"})
    # Calcula os centroides dos municípios
    br_mun = br_mun.assign(
        latitude=br_mun["geometry"].centroid.y,
        longitude=br_mun["geometry"].centroid.x,
    )
    return br_mun


def load_br_regiao():
    br_regiao_filepath = Path("data", "br_regiao.json")
    if not br_regiao_filepath.exists():
        download_malha(br_regiao_filepath, "regiao")
    br_regiao = gpd.GeoDataFrame.from_file(br_regiao_filepath).drop(columns=["id"])
    br_regiao = br_regiao.rename(columns={"codarea": "id_regiao"})
    return br_regiao


def load_br_uf():
    br_uf_filepath = Path("data", "br_uf.json")
    if not br_uf_filepath.exists():
        download_malha(br_uf_filepath, "UF")
    br_uf = gpd.GeoDataFrame.from_file(br_uf_filepath).drop(columns=["id"])
    br_uf = br_uf.rename(columns={"codarea": "id_uf"})
    return br_uf


def load_br_mesorregiao():
    br_mesorregiao_filepath = Path("data", "br_mesorregiao.json")
    if not br_mesorregiao_filepath.exists():
        download_malha(br_mesorregiao_filepath, "mesorregiao")
    br_mesorregiao = gpd.GeoDataFrame.from_file(br_mesorregiao_filepath).drop(
        columns=["id"]
    )
    br_mesorregiao = br_mesorregiao.rename(columns={"codarea": "id_mesorregiao"})
    return br_mesorregiao


def load_br_microrregiao():
    br_microrregiao_filepath = Path("data", "br_microrregiao.json")
    if not br_microrregiao_filepath.exists():
        download_malha(br_microrregiao_filepath, "microrregiao")
    br_microrregiao = gpd.GeoDataFrame.from_file(br_microrregiao_filepath).drop(
        columns=["id"]
    )
    br_microrregiao = br_microrregiao.rename(columns={"codarea": "id_microrregiao"})
    return br_microrregiao


def main():
    municipio = pd.read_csv(
        "data/br_bd_diretorios_brasil_municipio.csv",
        usecols=[
            "id_municipio",
            "id_municipio_6",
            "nome",
            "id_regiao_imediata",
            "nome_regiao_imediata",
            "id_regiao_intermediaria",
            "nome_regiao_intermediaria",
            "id_microrregiao",
            "nome_microrregiao",
            "id_mesorregiao",
            "nome_mesorregiao",
            "id_uf",
            "sigla_uf",
            "nome_uf",
            "nome_regiao",
        ],
        dtype=str,
    )
    br_mun = load_br_mun().merge(municipio, on="id_municipio")
    # Remove a columa geometry para não dar erro ao salvar em CSV
    br_mun.drop(columns=["geometry"]).to_csv(
        "data/br_mun.csv", decimal=",", index=False
    )
    # salvando em gpkg
    br_mun.to_file("data/br_mun.gpkg", driver="GPKG")

    load_br_regiao()
    load_br_uf()
    load_br_mesorregiao()
    load_br_microrregiao()


if __name__ == "__main__":
    main()
