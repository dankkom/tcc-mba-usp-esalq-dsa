"""Rotinas para limpeza e preparação dos dados do SINAN Dengue para análise."""

from pathlib import Path

import numpy as np
import pandas as pd

F_MINUTOS = 1 / (60 * 24 * 365)
F_HORAS = 1 / (24 * 365)
F_DIAS = 1 / 365
F_MESES = 1 / 12
UF = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}
COR_RACA = {
    "": "Ignorado",
    "1": "Branca",
    "2": "Preta",
    "4": "Parda",
    "5": "Indígena",
    "9": "Ignorado",
}
CLASSIFICACAO_FINAL = {
    "5": "Descartado",
    "10": "Dengue",
    "11": "Dengue com sinais de alarme",
    "12": "Dengue grave",
    "13": "Chikungunya",
}
CRITERIO = {
    "1": "Laboratório",
    "2": "Clínico epidemiológico",
    "3": "Em investigação",
}
EVOLUCAO = {
    "1": "Cura",
    "2": "Óbito por dengue",
    "3": "Óbito por outras causas",
    "4": "Óbito em investigação",
}
SOROTIPO = {
    "1": "DEN 1",
    "2": "DEN 2",
    "3": "DEN 3",
    "4": "DEN 4",
}


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


def convert_sexo(x: str) -> str:
    sexo = "Ignorado"
    if x == "M":
        sexo = "Masculino"
    elif x == "F":
        sexo = "Feminino"
    return sexo


def convert_raca(x: str) -> str:
    return COR_RACA.get(x, "Ignorado")


def convert_uf(x: str) -> str:
    return UF.get(x)


def convert_classificacao_final(x: str) -> str:
    return CLASSIFICACAO_FINAL.get(x, "Ignorado")


def convert_criterio(x: str) -> str:
    return CRITERIO.get(x, "Ignorado")


def convert_evolucao(x: str) -> str:
    return EVOLUCAO.get(x, "Ignorado")


def convert_sorotipo(x: str) -> str:
    return SOROTIPO.get(x, "Ignorado")


def main():
    data_dir = Path("data/datasus/parquet")

    # Carregando os dados do SINAN Dengue
    columns = [
        "DT_NOTIFIC",
        "SEM_NOT",
        "NU_ANO",
        "SG_UF_NOT",  # Convert using function 'convert_uf'
        "ID_MUNICIP",
        "NU_IDADE_N",  # Convert using function 'convert_idade'
        "CS_SEXO",  # Convert using function 'convert_sexo'
        "CS_RACA",  # Convert using function 'convert_raca'
        "SG_UF",  # Convert using function 'convert_uf'
        "ID_MN_RESI",
        "CLASSI_FIN",  # Convert using function 'convert_classificacao_final'
        "CRITERIO",  # Convert using function 'convert_criterio'
        "EVOLUCAO",  # Convert using function 'convert_evolucao'
        "DT_OBITO",
        "DT_ENCERRA",
        "SOROTIPO",  # Convert using function 'convert_sorotipo'
    ]
    sinan_deng = pd.DataFrame()
    for filepath in sorted(data_dir.glob("*.parquet")):
        print(filepath)
        d = pd.read_parquet(filepath, columns=columns)
        d = d[d["DT_NOTIFIC"] >= pd.to_datetime("2020-01-01").date()]
        d["NU_IDADE_N"] = d["NU_IDADE_N"].astype(str)
        d["NU_IDADE_N"] = d["NU_IDADE_N"].apply(convert_idade)
        d["CS_SEXO"] = d["CS_SEXO"].apply(convert_sexo)
        d["CS_RACA"] = d["CS_RACA"].apply(convert_raca)
        d["SG_UF"] = d["SG_UF"].apply(convert_uf)
        d["SG_UF_NOT"] = d["SG_UF_NOT"].apply(convert_uf)
        d["CLASSI_FIN"] = d["CLASSI_FIN"].apply(convert_classificacao_final)
        d["CRITERIO"] = d["CRITERIO"].apply(convert_criterio)
        d["EVOLUCAO"] = d["EVOLUCAO"].apply(convert_evolucao)
        d["SOROTIPO"] = d["SOROTIPO"].apply(convert_sorotipo)
        sinan_deng = pd.concat((sinan_deng, d), ignore_index=True)

    sinan_deng.to_csv("data/sinan-dengue.csv", index=False)


if __name__ == "__main__":
    main()
