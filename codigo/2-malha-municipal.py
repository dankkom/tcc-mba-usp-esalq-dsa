"""Carrega a malha municipal do Brasil.

Pacotes necessários:

- geopandas
- pyogrio
- requests

"""

from pathlib import Path

import geopandas as gpd
import requests


def download_br_mun(br_mun_filepath: Path):
    url = (
        "https://servicodados.ibge.gov.br/api/v3"
        "/malhas/paises/BR"
        "?intrarregiao=municipio"
        "&qualidade=intermediaria"
        "&formato=application/json"
    )
    r = requests.get(url, allow_redirects=True, timeout=600)
    with open(br_mun_filepath, "wb") as f:
        f.write(r.content)


def load_br_mun():
    br_mun_filepath = Path("data", "br_mun.json")
    if not br_mun_filepath.exists():
        download_br_mun(br_mun_filepath)
    br_mun = gpd.GeoDataFrame.from_file(br_mun_filepath).drop(columns=["id"])
    br_mun = br_mun.rename(columns={"codarea": "id_municipio"})
    # Calcula os centroides dos municípios
    br_mun = br_mun.assign(
        latitude=br_mun["geometry"].centroid.y,
        longitude=br_mun["geometry"].centroid.x,
    )
    br_mun = br_mun.assign(
        id_municipio_6=br_mun["id_municipio"].str[:6],
    )
    return br_mun


def main():
    br_mun = load_br_mun()

    # Remove a columa geometry para não dar erro ao salvar em CSV
    br_mun.drop(columns=["geometry"]).to_csv("data/br_mun.csv", index=False)

    # salvando em gpkg
    br_mun.to_file("data/br_mun.gpkg", driver="GPKG")


if __name__ == '__main__':
    main()
