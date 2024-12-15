from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    sinan_deng = pd.read_csv("data/sinan-dengue.csv")

    timeseries_daily = (
        sinan_deng.set_index("DT_NOTIFIC")
        .resample("D")["nu_notific"]
        .count()
        .reset_index(name="nu_notific")
    )

    # Gráfico da série temporal diária de casos de dengue
    f, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=timeseries_daily, x="DT_NOTIFIC", y="nu_notific", ax=ax)
    plt.savefig("dengue-timeseries-daily.png", dpi=300)
    plt.close()

    for sg_uf in sinan_deng["SG_UF"].unique():
        print(sg_uf)
        timeseries_daily = (
            sinan_deng[sinan_deng["SG_UF"] == sg_uf]
            .set_index("DT_NOTIFIC")
            .resample("D")["nu_notific"]
            .count()
            .reset_index(name="nu_notific")
        )

        # Gráfico da série temporal diária de casos de dengue
        f, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=timeseries_daily, x="DT_NOTIFIC", y="nu_notific", ax=ax)
        plt.savefig(f"output/dengue-timeseries-daily-{sg_uf}.png", dpi=300)
        plt.close()


    timeseries_monthly = (
        sinan_deng.set_index("DT_NOTIFIC")
        .resample("ME")["nu_notific"]
        .count()
        .reset_index(name="nu_notific")
    )

    # Gráfico da série temporal mensal de casos de dengue
    f, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=timeseries_monthly, x="DT_NOTIFIC", y="nu_notific", ax=ax)
    plt.savefig("output/dengue-timeseries-monthly.png", dpi=300)
    plt.close()

    for sg_uf in sinan_deng["SG_UF"].unique():
        print(sg_uf)
        timeseries_monthly = (
            sinan_deng[sinan_deng["SG_UF"] == sg_uf]
            .set_index("DT_NOTIFIC")
            .resample("ME")["nu_notific"]
            .count()
            .reset_index(name="nu_notific")
        )

        # Gráfico da série temporal mensal de casos de dengue
        f, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=timeseries_monthly, x="DT_NOTIFIC", y="nu_notific", ax=ax)
        plt.savefig(f"output/dengue-timeseries-monthly-{sg_uf}.png", dpi=300)
        plt.close()


if __name__ == "__main__":
    main()
