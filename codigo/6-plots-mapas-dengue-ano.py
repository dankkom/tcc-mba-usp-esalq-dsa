from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import warnings

warnings.filterwarnings("ignore")


def pseudolog(x):
    return np.sign(x) * np.log1p(abs(x))


def create_legend(ax, color, bins):
    # Legenda de bolhas
    # Adaptado de https://stackoverflow.com/a/73354795
    # create second legend
    ax.add_artist(
        ax.legend(
            handles=[
                mlines.Line2D(
                    [],
                    [],
                    color=color,
                    lw=0,
                    marker="o",
                    markersize=np.sqrt(b),
                    label=f"{b} notificações/100 mil habitantes",
                )
                for i, b in enumerate(bins)
            ],
            loc=4,
            fontsize=16,
        )
    )


def plot_mapa(br_uf, dengue_data, ax, color, alpha):
    br_uf.plot(ax=ax, facecolor="#e0e0e0", edgecolor="#ffffff", linewidth=2)
    dengue_data.plot(
        markersize="incidencia",
        color=color,
        edgecolor="none",
        alpha=alpha,
        ax=ax,
    )

    create_legend(ax, color, bins=np.array([100, 500, 1_000]))

    return ax


def process_geo_data_year(geo, data, ano: int):
    merged_data = geo.merge(
        data[data["ano"] == ano],
        on=["id_municipio_6"],
        how="right",
    )
    merged_data["incidencia"] = merged_data["notificacoes"] / (
        merged_data["populacao_estimada"] / 100_000
    )
    # Fator de escalonamento para melhor visualização
    merged_data["incidencia"] = merged_data["incidencia"] / 60
    return merged_data


def main():
    data_dir = Path("data")
    dest_plots_dir = Path("output/plots/dengue-ano")
    dest_plots_dir.mkdir(parents=True, exist_ok=True)

    dengue_populacao_ano = pd.read_csv(
        data_dir / "dengue-populacao-mun-ano.csv",
        dtype={"id_municipio_6": str},
    )

    # Dados geográficos dos municípios
    br_mun_filepath = data_dir / "br_mun.gpkg"
    br_mun = gpd.read_file(br_mun_filepath, columns=["id_municipio_6"])
    br_mun.geometry = br_mun.centroid

    # Dados geográficos dos estados
    br_uf_filepath = data_dir / "br_uf.json"
    br_uf = gpd.GeoDataFrame.from_file(br_uf_filepath).drop(columns=["id"])

    # Plot
    plt.rcParams.update(
        {
            "font.size": 22,
            "font.family": "serif",
            "axes.facecolor": "#FFFFFF",
            "figure.facecolor": "#FFFFFF",
            "font.weight": "normal",
        },
    )
    color = "red"
    alpha = 0.25

    # Mapas
    for ano in dengue_populacao_ano["ano"].unique():
        print("Plotando mapa para o ano", ano)
        dengue_populacao_br_mun = process_geo_data_year(
            geo=br_mun,
            data=dengue_populacao_ano,
            ano=ano,
        )

        f, ax = plt.subplots()
        f.set_size_inches(12, 12)

        # Plot mapa
        ax = plot_mapa(br_uf, dengue_populacao_br_mun, ax, color, alpha)

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}.png", dpi=300)
        plt.close(f)


if __name__ == "__main__":
    main()
