"""Rotinas para limpeza e preparação dos dados do SINAN Dengue para análise."""

from pathlib import Path

import numpy as np
import pandas as pd

F_MINUTOS = 1 / (60 * 24 * 365)
F_HORAS = 1 / (24 * 365)
F_DIAS = 1 / 365
F_MESES = 1 / 12


def convert_idade(x: str) -> float:
    idade = np.nan
    len_x = len(x)
    if len_x < 4 and len_x != 0:
        x = f"{x:0>4}"
    idade_cod = x[0]
    idade_num = x[1:]
    if idade_num == "" or idade_num == "999" or idade_num == "000":
        return idade
    idade_num = int(idade_num)
    if idade_cod == "0":  # Minutos
        idade = idade_num * F_MINUTOS
    elif idade_cod == "1":  # Horas
        idade = idade_num * F_HORAS
    elif idade_cod == "2":  # Dias
        idade = idade_num * F_DIAS
    elif idade_cod == "3":  # Meses
        idade = idade_num * F_MESES
    elif idade_cod == "4":
        idade = idade_num
    elif idade_cod == "5":
        idade = idade_num + 100
    if idade > 120:
        idade = np.nan
    return idade


def main():
    data_dir = Path("data/datasus/parquet")

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
        d = pd.read_parquet(filepath, columns=columns)
        d["NU_IDADE_N"] = d["NU_IDADE_N"].astype(str)
        d["idade"] = d["NU_IDADE_N"].apply(convert_idade)
        print(d.idade.min(), d.idade.max(), d.idade.mean(), d.idade.median())
        sinan_deng = pd.concat((sinan_deng, d), ignore_index=True)
    sinan_deng.to_csv("data/sinan-dengue.csv", index=False)


if __name__ == "__main__":
    main()
