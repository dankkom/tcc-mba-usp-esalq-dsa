"""Interpolação do dados de população municipal anual para diária e projeção da população para 2025.

    pip install openpyxl scipy statsmodels


https://pandas.pydata.org/docs/reference/api/pandas.Series.interpolate.html
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html

"""

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt
from tqdm import tqdm


def load_municipality_population():
    # Carrega a população municipal
    pop_mun = pd.read_excel("data/populacao-municipios.xlsx")
    pop_mun = pop_mun.assign(
        municipio_id=pop_mun["municipio_id"].astype(str),
        data=pd.to_datetime(pop_mun["ano"].astype(str) + "-07-01", format="%Y-%m-%d"),
    )
    pop_mun = pop_mun.pivot(
        index="data",
        columns="municipio_id",
        values="populacao_estimada",
    )
    return pop_mun


def interpolate_population(pop_mun, method="akima"):
    # Interpolação para dias
    # quadratic: Quadratic interpolation. Not recommended for most common use cases.
    # akima: Akima interpolation. This is recommended for a smooth interpolation.
    print("Interpolation using", method)
    if method == "akima":
        pop_mun_interp = pop_mun.resample("D").interpolate(method="akima")
    elif method == "quadratic":
        pop_mun_interp = pop_mun.resample("D").interpolate(method="quadratic")
    return pop_mun_interp


def make_exponential_smoothing_forecast(series, horizon):
    print("Making exponential smoothing forecast in", series.name)
    return (
        ExponentialSmoothing(series, trend="mul", seasonal=None, damped_trend=True)
        .fit()
        .forecast(horizon)
    )


def make_holt_forecast(series, horizon):
    print("Making Holt forecast in", series.name)
    return Holt(series, exponential=True, damped_trend=True).fit().forecast(horizon)


def main():
    pop_mun = load_municipality_population()
    pop_mun_interp = interpolate_population(
        pop_mun.loc[["2019-07-01", "2020-07-01", "2021-07-01", "2024-07-01"]],
        method="akima",
    )

    # Make projections for each municipality
    horizon = 183
    pop_mun_fcst_wide = pd.DataFrame()
    for column in tqdm(pop_mun_interp.columns):
        series = pop_mun_interp[column]
        forecast = make_exponential_smoothing_forecast(series, horizon)
        forecast = forecast.rename(column)
        pop_mun_fcst_wide = pd.concat([pop_mun_fcst_wide, forecast], axis=1)
    pop_mun_fcst_wide = pop_mun_fcst_wide.reset_index()
    pop_mun_fcst_wide = pop_mun_fcst_wide.rename(columns={"index": "data"})

    pop_mun_fcst = (
        pd.concat(
            (pop_mun_interp.reset_index(), pop_mun_fcst_wide),
            ignore_index=True,
        )
        .melt(
            id_vars="data",
            var_name="municipio_id",
            value_name="populacao_estimada",
        )
        .assign(
            populacao_estimada=lambda x: x["populacao_estimada"].round(0).astype(int),
        )
    )
    pop_mun_fcst.to_csv("data/populacao-municipios.csv", index=False)


if __name__ == "__main__":
    main()
