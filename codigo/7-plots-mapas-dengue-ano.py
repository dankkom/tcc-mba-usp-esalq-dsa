from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import warnings

warnings.filterwarnings("ignore")


def main():
    data_dir = Path("data")
    dest_plots_dir = Path("output/plots/dengue-ano")
    dest_plots_dir.mkdir(parents=True, exist_ok=True)

    dengue_populacao_ano = pd.read_csv(
        data_dir / "dengue-populacao-ano.csv",
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
        dengue_populacao_br_mun = br_mun.merge(
            dengue_populacao_ano[dengue_populacao_ano["ano"] == ano],
            on=["id_municipio_6"],
            how="right",
        )
        dengue_populacao_br_mun["size"] = dengue_populacao_br_mun["notificacoes"] / (
            dengue_populacao_br_mun["populacao_estimada"] / 100_000
        )
        # Fator de escalonamento para melhor visualização
        dengue_populacao_br_mun["size"] = dengue_populacao_br_mun["size"] / 60

        f, ax = plt.subplots()
        f.set_size_inches(12, 12)
        br_uf.plot(ax=ax, facecolor="#e0e0e0", edgecolor="#ffffff", linewidth=2)
        dengue_populacao_br_mun.plot(
            markersize="size",
            color=color,
            edgecolor="none",
            alpha=alpha,
            ax=ax,
        )

        # Legenda de bolhas
        # Adaptado de https://stackoverflow.com/a/73354795
        bins = np.array([100, 500, 1_000])
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
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(dest_plots_dir / f"{ano}.png", dpi=300)
        plt.close(f)


if __name__ == "__main__":
    main()
