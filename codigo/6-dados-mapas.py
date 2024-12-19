from pathlib import Path

import pandas as pd
import warnings

warnings.filterwarnings("ignore")


def load_transform_dengue(data_dir: Path):
    # Dados Dengue
    dengue = (
        pd.read_csv(
            data_dir / "sinan-dengue.csv",
            usecols=["DT_NOTIFIC", "NU_ANO", "ID_MUNICIP", "CLASSI_FIN"],
            dtype=str,
        )
        .query("CLASSI_FIN != 'Descartado' and NU_ANO >= '2020'")
        .drop(columns="CLASSI_FIN")
        .assign(
            DT_NOTIFIC=lambda x: pd.to_datetime(x.DT_NOTIFIC),
            notificacoes=1,
        )
        .rename(columns={"DT_NOTIFIC": "data", "ID_MUNICIP": "id_municipio_6"})
    )
    dengue = dengue.loc[
        (dengue["id_municipio_6"].str.len() == 6) & (dengue["data"].notnull())
    ]
    dengue = (
        dengue.groupby(["data", "id_municipio_6"])
        .agg({"notificacoes": "sum"})
        .reset_index()
    )

    return dengue


def load_transform_populacao(data_dir: Path):
    # Dados População
    populacao = (
        pd.read_csv(
            data_dir / "populacao-municipios.csv",
            parse_dates=["data"],
            dtype={"municipio_id": str},
        )
        .assign(id_municipio_6=lambda x: x["municipio_id"].str[:6])
        .drop(columns="municipio_id")
    )

    return populacao


def main():
    data_dir = Path("data")

    dengue = load_transform_dengue(data_dir)

    populacao = load_transform_populacao(data_dir)

    # Merge Dengue e População
    dengue_populacao = dengue.merge(
        populacao,
        on=["data", "id_municipio_6"],
        how="left",
    )

    # Agregado por ano
    dengue_populacao_ano = (
        dengue_populacao.assign(ano=lambda x: x["data"].dt.year)
        .groupby(["ano", "id_municipio_6"])
        .agg(
            notificacoes=pd.NamedAgg(column="notificacoes", aggfunc="sum"),
            populacao_estimada=pd.NamedAgg(column="populacao_estimada", aggfunc="mean"),
        )
        .reset_index()
    )

    dengue_populacao_ano.to_csv(
        data_dir / "dengue-populacao-ano.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
