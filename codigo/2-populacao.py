"""Interpolação do dados de população municipal anual para diária e projeção da população para 2025.

    pip install openpyxl scipy statsmodels


https://pandas.pydata.org/docs/reference/api/pandas.Series.interpolate.html
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html

"""

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt


def load_municipality_population():
    # Carrega a população municipal
    pop_mun = pd.read_excel("data/populacao-municipios.xlsx")
    pop_mun = pop_mun.assign(
        municipio_id=pop_mun["municipio_id"].astype(str),
        data=pd.to_datetime(pop_mun["ano"].astype(str) + "-07-01", format="%Y-%m-%d"),
    )
    #       municipio_id                   nome  populacao_estimada   ano sg_uf       data
    # 0          1100015  Alta Floresta D'Oeste               22728  2020    RO 2020-07-01
    # 1          1100023              Ariquemes              109523  2020    RO 2020-07-01
    # 2          1100031                 Cabixi                5188  2020    RO 2020-07-01
    # 3          1100049                 Cacoal               85893  2020    RO 2020-07-01
    # 4          1100056             Cerejeiras               16204  2020    RO 2020-07-01
    # ...            ...                    ...                 ...   ...   ...        ...
    # 27845      5222005             Vianópolis               13863  2019    GO 2019-07-01
    # 27846      5222054         Vicentinópolis                8743  2019    GO 2019-07-01
    # 27847      5222203               Vila Boa                6171  2019    GO 2019-07-01
    # 27848      5222302          Vila Propício                5821  2019    GO 2019-07-01
    # 27849      5300108               Brasília             3015268  2019    DF 2019-07-01

    pop_mun = pop_mun.pivot(
        index="data",
        columns="municipio_id",
        values="populacao_estimada",
    )
    # municipio_id  1100015  1100023  1100031  1100049  1100056  1100064  1100072  1100080  ...  5221809  5221858  5221908  5222005  5222054  5222203  5222302  5300108
    # data                                                                                  ...
    # 2019-07-01      22945   107863     5312    85359    16323    15882     7391    18331  ...     3072   168468     3827    13863     8743     6171     5821  3015268
    # 2020-07-01      22728   109523     5188    85893    16204    15544     7220    18798  ...     3066   172135     3838    13977     8873     6312     5882  3055149
    # 2021-07-01      22516   111148     5067    86416    16088    15213     7052    19255  ...     3056   175720     3848    14088     9002     6451     5941  3094325
    # 2022-07-01      21494    96833     5351    86887    15890    15663     7519    12627  ...     3553   198861     3716    14956     8768     4215     5815  2817381
    # 2024-07-01      22853   108573     5690    97637    16975    16588     8001    13522  ...     3667   213506     3768    15476     9077     4185     5982  2982818

    return pop_mun


def interpolate_population(pop_mun, method="akima"):
    # Interpolação para dias
    # quadratic: Quadratic interpolation. Not recommended for most common use cases.
    # akima: Akima interpolation. This is recommended for a smooth interpolation.
    if method == "akima":
        pop_mun_interp = pop_mun.resample("D").interpolate(method="akima")
    elif method == "quadratic":
        pop_mun_interp = pop_mun.resample("D").interpolate(method="quadratic")
    return pop_mun_interp


def make_exponential_smoothing_forecast(series, horizon):
    return (
        ExponentialSmoothing(series, trend="mul", seasonal=None, damped_trend=True)
        .fit()
        .forecast(horizon)
    )


def make_holt_forecast(series, horizon):
    return Holt(series, exponential=True, damped_trend=True).fit().forecast(horizon)


def pivot_long_forecasted(forecasted):
    return forecasted.reset_index().melt(
        id_vars="index",
        var_name="municipio_id",
        value_name="populacao_estimada",
    )


def make_plot(**series):
    try:
        for name, data in series.items():
            plt.plot(data.index, data, "o-", label=name)
        plt.legend()
        plt.show()
    finally:
        plt.clf()
        plt.close()


def main():
    pop_mun = load_municipality_population()
    pop_mun_interp_quadratic = interpolate_population(pop_mun, method="quadratic")
    pop_mun_interp_akima = interpolate_population(pop_mun, method="akima")

    make_plot(
        quadratic=pop_mun_interp_quadratic["1100015"],
        akima=pop_mun_interp_akima["1100015"],
        original=pop_mun["1100015"],
    )

    # # -------Projeção da população diária para 2025 para todos os municípios sem o censo-------
    pop_mun_without_census = pop_mun.loc[
        ["2019-07-01", "2020-07-01", "2021-07-01", "2024-07-01"]
    ]

    pop_mun_wo_c_akima = pop_mun_without_census.resample("D").interpolate(method="akima")
    make_plot(
        akima=pop_mun_wo_c_akima["5300108"],
        original=pop_mun["5300108"],
    )

    # Make forecasts for all municipalities without census
    horizon = 365

    exponential_smoothing_forecast_wo_census = pop_mun_wo_c_akima.apply(
        lambda series: make_exponential_smoothing_forecast(series, horizon)
    )
    (
        pivot_long_forecasted(exponential_smoothing_forecast_wo_census)
        .query("index <= '2024-12-31'")
        .to_csv("data/populacao-municipios-exponential_smoothing-sem-censo.csv", index=False)
    )

    holt_forecast_wo_census = pop_mun_wo_c_akima.apply(
        lambda series: make_holt_forecast(series, horizon)
    )
    (
        pivot_long_forecasted(holt_forecast_wo_census)
        .query("index <= '2024-12-31'")
        .to_csv("data/populacao-municipios-holt-sem-censo.csv", index=False)
    )


if __name__ == "__main__":
    main()
