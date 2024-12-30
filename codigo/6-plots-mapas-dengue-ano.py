from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import warnings
from mpl_toolkits.axes_grid1 import make_axes_locatable

warnings.filterwarnings("ignore")


def pseudolog(x):
    return np.sign(x) * np.log1p(abs(x))


def plot_mapa_hexbin(
    br_uf,
    dengue_data,
    ax,
    column="notificacoes",
    cmap="GnBu",
    gridsize=100,
    bins="log",
    alpha=0.7,
):
    hb = ax.hexbin(
        dengue_data.geometry.x,
        dengue_data.geometry.y,
        C=dengue_data[column],
        gridsize=gridsize,
        bins=bins,
        cmap=cmap,
        alpha=alpha,
        mincnt=1,
        reduce_C_function=np.sum,
    )
    br_uf.plot(ax=ax, facecolor="none", edgecolor="#d0d0d0", linewidth=1)


def plot_mapa_coropletico(br_uf, dengue_data, ax, ano):
    data = dengue_data[dengue_data["ano"] == ano]
    data["pseudolog_incidencia"] = pseudolog(data.incidencia)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    br_uf.plot(ax=ax, facecolor="#e0e0e0", edgecolor="#ffffff", linewidth=2)
    data.plot(
        column="pseudolog_incidencia",
        cmap="GnBu",
        ax=ax,
        legend=True,
        cax=cax,
        legend_kwds={
            "label": f"Pseudo-Logaritmo da Taxa de Incidência de Dengue em {ano}",
            "orientation": "horizontal",
        },
    )


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

    br_mun_p = br_mun.copy()
    br_mun_p.geometry = br_mun_p.centroid

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
            geo=br_mun_p,
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

        # Mapa HEXBIN
        print("Plotando mapa HEXBIN para o ano", ano)

        f, ax = plt.subplots()
        f.set_size_inches(12, 12)

        # Plot mapa HEXBIN
        ax = plot_mapa_hexbin(br_uf, dengue_populacao_br_mun, ax)

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-hexbin.png", dpi=300)
        plt.close(f)

    # Mapas coropléticos
    for ano in dengue_populacao_ano["ano"].unique():
        print("Plotando mapa coroplético para o ano", ano)
        dengue_populacao_br_mun = process_geo_data_year(
            geo=br_mun,
            data=dengue_populacao_ano,
            ano=ano,
        )

        f, ax = plt.subplots()
        f.set_size_inches(12, 12)

        plot_mapa_coropletico(br_uf, dengue_populacao_br_mun, ax, ano)

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-coro.png", dpi=300)
        plt.close(f)


if __name__ == "__main__":
    main()
