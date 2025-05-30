# Header -------------------------------------------------------------------
# Author: Daniel Kiyoyudi Komesu
# Date: 2025-01-12
# Purpose: Plot seasonal plots and incidence rate by state

# Library Imports ----------------------------------------------------------
library(arrow)
library(dplyr)
library(ggplot2)
library(patchwork)
library(scales)
library(forecast)
library(seasonal)
library(fpp3)


dados <- arrow::read_parquet(
  "data/sinan-dengue.parquet",
  col_select = c("DT_NOTIFIC", "SG_UF_NOT", "CLASSI_FIN"),
)


dados_agrupados <- dados |>
  dplyr::filter(CLASSI_FIN != "Descartado") |>
  dplyr::group_by(DT_NOTIFIC, SG_UF_NOT) |>
  dplyr::summarise(notificacoes = dplyr::n(), .groups = "drop")


dados_br <- dados_agrupados |>
  dplyr::group_by(anomes = lubridate::floor_date(DT_NOTIFIC, "month")) |>
  dplyr::summarise(notificacoes = sum(notificacoes), .groups = "drop")


dados_br |>
  ggplot2::ggplot(ggplot2::aes(anomes, notificacoes)) +
  ggplot2::geom_line(linewidth = 1) +
  ggplot2::labs(
    x = "Ano-Mês",
    y = "Notificações de Dengue",
  ) +
  ggplot2::theme_minimal() +
  ggplot2::scale_y_continuous(labels = scales::comma)
ggplot2::ggsave(
  "output/plots/timeseries-plot.png",
  width = 10,
  height = 5,
  dpi = 100,
  bg = "white",
)

# Análise de sazonalidade
forecast::ggsubseriesplot(
  ts(dados_br$notificacoes, frequency = 12),
  ylab = "Notificações",
  xlab = "Mês",
  main = "Notificações de dengue no Brasil"
) +
  # Format y axis labels
  ggplot2::scale_y_continuous(labels = scales::number) +
  ggplot2::theme_minimal()
ggplot2::ggsave(
  "output/plots/seasonal-plot-subseries.png",
  width = 10,
  height = 6,
  dpi = 100,
  bg = "white",
)


dados_br |>
  readr::write_csv("output/dados_br.csv")


# Criar uma Série Temporal
ts_data <- ts(
  dados_br$notificacoes,
  start = c(2020, 1),
  frequency = 12
)
ts_data

# Decomposição da Série
# Decomposição aditiva com decompose
ajuste <- decompose(ts_data)
summary(ajuste)
plot(ajuste)

# Data Frame com os dados de sazonalidade
dados_br2 <- dados_br |>
  dplyr::mutate(
    sazonal = ajuste$seasonal,
    irregular = ajuste$random,
    tendencia = ajuste$trend,
  )

# Gráfico das séries
plot_original <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, notificacoes)) +
  ggplot2::geom_line() +
  ggplot2::scale_y_continuous(labels = scales::number) +
  ggplot2::theme_minimal() +
  ggplot2::labs(
    x = "Ano-Mês",
    y = "Notificações de Dengue",
  )

plot_tendencia <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, tendencia)) +
  ggplot2::geom_line() +
  ggplot2::scale_y_continuous(labels = scales::number) +
  ggplot2::theme_minimal() +
  ggplot2::labs(
    x = "Ano-Mês",
    y = "Tendência",
  )

plot_sazonalidade <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, sazonal)) +
  ggplot2::geom_line() +
  ggplot2::scale_y_continuous(labels = scales::number) +
  ggplot2::theme_minimal() +
  ggplot2::labs(
    x = "Ano-Mês",
    y = "Sazonalidade",
  )

plot_irregularidade <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, irregular)) +
  ggplot2::geom_line() +
  ggplot2::scale_y_continuous(labels = scales::number) +
  ggplot2::theme_minimal() +
  ggplot2::labs(
    x = "Ano-Mês",
    y = "Irregularidade",
  )


# Plotar os gráficos numa única figura
plot_original +
  plot_tendencia +
  plot_sazonalidade +
  plot_irregularidade +
  ggplot2::theme_minimal() +
  ggplot2::theme(legend.position = "bottom") +
  patchwork::plot_layout(ncol = 1, heights = c(2, 1, 1, 1))
ggplot2::ggsave(
  "output/plots/decomposition-plot.png",
  width = 10,
  height = 10,
  dpi = 100,
  bg = "white",
)
