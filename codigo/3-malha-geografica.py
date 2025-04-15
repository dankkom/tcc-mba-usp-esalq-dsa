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


def load_br_uf():
    br_uf_filepath = Path("data", "br_uf.json")
    if not br_uf_filepath.exists():
        download_malha(br_uf_filepath, "UF")
    br_uf = gpd.GeoDataFrame.from_file(br_uf_filepath).drop(columns=["id"])
    br_uf = br_uf.rename(columns={"codarea": "id_uf"})
    return br_uf


def load_br_regiao_intermediaria():
    br_regiao_intermediaria_filepath = Path("data", "br_regiao_intermediaria.json")
    if not br_regiao_intermediaria_filepath.exists():
        download_malha(br_regiao_intermediaria_filepath, "regiao_intermediaria")
    br_regiao_intermediaria = gpd.GeoDataFrame.from_file(
        br_regiao_intermediaria_filepath
    ).drop(columns=["id"])
    br_regiao_intermediaria = br_regiao_intermediaria.rename(
        columns={"codarea": "id_regiao_intermediaria"}
    )
    return br_regiao_intermediaria


def load_br_regiao_imediata():
    br_regiao_imediata_filepath = Path("data", "br_regiao_imediata.json")
    if not br_regiao_imediata_filepath.exists():
        download_malha(br_regiao_imediata_filepath, "regiao-imediata")
    br_regiao_imediata = gpd.GeoDataFrame.from_file(br_regiao_imediata_filepath).drop(
        columns=["id"]
    )
    br_regiao_imediata = br_regiao_imediata.rename(
        columns={"codarea": "id_regiao_imediata"}
    )
    return br_regiao_imediata


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
    br_mun = load_br_mun()
    br_mun = br_mun.merge(municipio, on="id_municipio")
    br_regiao_intermediaria = load_br_regiao_intermediaria()
    br_regiao_intermediaria = br_regiao_intermediaria.assign(
        longitude_regiao_intermediaria=br_regiao_intermediaria.geometry.centroid.x,
        latitude_regiao_intermediaria=br_regiao_intermediaria.geometry.centroid.y,
    ).drop(columns=["geometry"])
    br_mun = br_mun.merge(
        br_regiao_intermediaria, on="id_regiao_intermediaria", how="left"
    )
    br_regiao_imediata = load_br_regiao_imediata()
    br_regiao_imediata = br_regiao_imediata.assign(
        longitude_regiao_imediata=br_regiao_imediata.geometry.centroid.x,
        latitude_regiao_imediata=br_regiao_imediata.geometry.centroid.y,
    ).drop(columns=["geometry"])
    br_mun = br_mun.merge(br_regiao_imediata, on="id_regiao_imediata", how="left")

    # Remove a columa geometry para não dar erro ao salvar em CSV
    br_mun.drop(columns=["geometry"]).to_csv(
        "data/br_mun.csv", decimal=",", index=False
    )
    # salvando em gpkg
    br_mun.to_file(
        "data/br_mun.gpkg",
        driver="GPKG",
        layer="br_mun",
        mode="a",
        overwrite=True,
    )

    br_uf = load_br_uf()

    br_uf.to_file(
        "data/br_mun.gpkg",
        driver="GPKG",
        layer="br_uf",
        mode="a",
        overwrite=True,
    )


if __name__ == "__main__":
    main()
