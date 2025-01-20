"""Plotagem de mapas de dengue por ano.

Files dependencies:

- data/dengue-populacao-mun-ano.csv
- data/br_mun.gpkg
- data/br_uf.json

Output files:

- output/plots/dengue-ano/{ano}-points.png
- output/plots/dengue-ano/{ano}-hexbin.png
- output/plots/dengue-ano/{ano}-hexbin-pseudolog.png
- output/plots/dengue-ano/{ano}-coro.png
- output/plots/dengue-ano/{ano}-coro-pseudolog.png

"""


import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

warnings.filterwarnings("ignore")


def pseudolog(x):
    return np.sign(x) * np.log1p(abs(x))


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
    merged_data["incidencia"] = np.sqrt(merged_data["incidencia"])
    merged_data["pseudolog_incidencia"] = pseudolog(merged_data["incidencia"])
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
        dengue_populacao_br_mun = process_geo_data_year(
            geo=br_mun_p,
            data=dengue_populacao_ano,
            ano=ano,
        )

        # Plot mapa points
        print("Plotando mapa points para o ano", ano)
        f, ax = plt.subplots()
        f.set_size_inches(12, 12)
        br_uf.plot(ax=ax, facecolor="#e0e0e0", edgecolor="#ffffff", linewidth=2)
        dengue_populacao_br_mun.plot(
            markersize="incidencia",
            color="red",
            edgecolor="none",
            alpha=alpha,
            ax=ax,
        )
        ax.set_title(f"{ano}")
        # Legenda de bolhas
        # Adaptado de https://stackoverflow.com/a/73354795
        bins = np.array([10, 50, 100, 500])
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
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-points.png", dpi=300)
        plt.close(f)

        # Plot mapa HEXBIN
        print("Plotando mapa HEXBIN para o ano", ano)
        f, ax = plt.subplots()
        f.set_size_inches(12, 12)
        hb = ax.hexbin(
            dengue_populacao_br_mun.geometry.x,
            dengue_populacao_br_mun.geometry.y,
            C=dengue_populacao_br_mun["incidencia"],
            gridsize=100,
            bins="log",
            cmap="GnBu",
            alpha=1,
            mincnt=1,
            reduce_C_function=np.mean,
        )
        br_uf.plot(ax=ax, facecolor="none", edgecolor="#808080", linewidth=0.8)
        ax.set_title(f"{ano}")
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-hexbin.png", dpi=300)
        plt.close(f)

        # Plot mapa HEXBIN pseudolog
        print("Plotando mapa HEXBIN pseudolog para o ano", ano)
        f, ax = plt.subplots()
        f.set_size_inches(12, 12)
        hb = ax.hexbin(
            dengue_populacao_br_mun.geometry.x,
            dengue_populacao_br_mun.geometry.y,
            C=dengue_populacao_br_mun["pseudolog_incidencia"],
            gridsize=100,
            bins="log",
            cmap="GnBu",
            alpha=1,
            mincnt=1,
            reduce_C_function=np.mean,
        )
        br_uf.plot(ax=ax, legend=True, facecolor="none", edgecolor="#808080", linewidth=0.8)
        ax.set_title(f"{ano}")
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-hexbin-pseudolog.png", dpi=300)
        plt.close(f)

    # Mapas coropléticos
    for ano in dengue_populacao_ano["ano"].unique():
        dengue_populacao_br_mun = process_geo_data_year(
            geo=br_mun,
            data=dengue_populacao_ano,
            ano=ano,
        )

        # Plot mapa coroplético
        print("Plotando mapa para o ano", ano)
        f, ax = plt.subplots()
        f.set_size_inches(12, 12)
        data = dengue_populacao_br_mun[dengue_populacao_br_mun["ano"] == ano]
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="5%", pad=0.1)
        br_uf.plot(ax=ax, facecolor="#e0e0e0", edgecolor="#ffffff", linewidth=2)
        data.plot(
            column="incidencia",
            cmap="GnBu",
            ax=ax,
            legend=True,
            cax=cax,
            legend_kwds={
                "label": f"Taxa de Incidência de Dengue em {ano}",
                "orientation": "horizontal",
            },
        )
        ax.set_title(f"{ano}")
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-coro.png", dpi=300)
        plt.close(f)

        # Plot mapa coroplético pseudolog
        print("Plotando mapa pseudolog para o ano", ano)
        f, ax = plt.subplots()
        f.set_size_inches(12, 12)
        data = dengue_populacao_br_mun[dengue_populacao_br_mun["ano"] == ano]
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
        ax.set_title(f"{ano}")
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}-coro-pseudolog.png", dpi=300)
        plt.close(f)


if __name__ == "__main__":
    main()
