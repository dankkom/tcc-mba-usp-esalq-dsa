"""Rotinas para limpeza e preparação dos dados do SINAN Dengue para análise."""

from pathlib import Path

import pandas as pd


def main():
    data_dir = Path("data/datasus/csv")

    # Carregando os dados do SINAN Dengue
    columns = [
        "TP_NOT",
        "ID_AGRAVO",
        "DT_NOTIFIC",
        "SEM_NOT",
        "NU_ANO",
        "SG_UF_NOT",
        "ID_MUNICIP",
        "NU_IDADE_N",
        "CS_SEXO",
        "CS_RACA",
        "CS_ESCOL_N",
        "SG_UF",
        "ID_MN_RESI",
        "EVOLUCAO",
        "DT_OBITO",
    ]
    sinan_deng = pd.DataFrame()
    for filepath in data_dir.iterdir():
        print(filepath)
        d = pd.read_csv(filepath, usecols=columns)
        print(d)
        sinan_deng = pd.concat((sinan_deng, d), ignore_index=True)
    sinan_deng.to_csv("data/sinan-dengue.csv", index=False)


if __name__ == "__main__":
    main()
