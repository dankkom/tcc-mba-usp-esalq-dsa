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
  "output/plots/timeseries-plot.jpg",
  width = 10,
  height = 5,
  dpi = 100,
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
  "output/plots/seasonal-plot-subseries.jpg",
  width = 10,
  height = 6,
  dpi = 100,
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
# Decomposição aditiva com método X-13
ajuste <- seasonal::seas(ts_data)
summary(ajuste)
plot(ajuste)

dados_br2 <- dados_br |>
  dplyr::mutate(
    sazonal = seasonal::series(ajuste, "seats.seasonal"),
    irregular = seasonal::series(ajuste, "seats.irregular"),
    tendencia = seasonal::trend(ajuste),
    ajustada = seasonal::final(ajuste)
  )


# Gráfico das séries
plot_original_e_ajustada <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, notificacoes)) +
  ggplot2::geom_line(ggplot2::aes(color = "Notificações"), linetype = "solid") +
  ggplot2::geom_line(
    ggplot2::aes(anomes, ajustada, color = "Ajustada"),
    linetype = "dashed",
  ) +
  # Put the legend at the top
  ggplot2::theme(legend.position = "top")

plot_tendencia <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, tendencia)) +
  ggplot2::geom_line()

plot_sazonalidade <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, sazonal)) +
  ggplot2::geom_line()

plot_irregularidade <- dados_br2 |>
  ggplot2::ggplot(ggplot2::aes(anomes, irregular)) +
  ggplot2::geom_line()


# Plotar os gráficos numa única figura
plot_original_e_ajustada +
  plot_tendencia +
  plot_sazonalidade +
  plot_irregularidade +
  patchwork::plot_annotation(
    title = "Decomposição da série temporal de notificações de dengue no Brasil",
    caption = "Fonte: SINAN"
  ) +
  ggplot2::theme_minimal() +
  ggplot2::theme(legend.position = "bottom") +
  patchwork::plot_layout(ncol = 1, heights = c(2, 1, 1, 1))
ggplot2::ggsave(
  "output/plots/decomposition-plot.jpg",
  width = 10,
  height = 10,
  dpi = 100,
)
