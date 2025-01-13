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


dados <- arrow::read_parquet("data/sinan-dengue.parquet")


dados_agrupados <- dados %>%
  dplyr::filter(CLASSI_FIN != "Descartado") %>%
  dplyr::group_by(DT_NOTIFIC, SG_UF_NOT) %>%
  dplyr::summarise(notificacoes = dplyr::n(), .groups = "drop")


dados_br <- dados_agrupados %>%
  dplyr::group_by(anomes = lubridate::floor_date(DT_NOTIFIC, "month")) %>%
  dplyr::summarise(notificacoes = sum(notificacoes), .groups = "drop")


dados_br %>%
  ggplot2::ggplot(ggplot2::aes(anomes, notificacoes)) +
  ggplot2::geom_line(linewidth = 1) +
  ggplot2::labs(
    x = "Ano-Mês",
    y = "Notificações de Dengue",
  ) +
  ggplot2::theme_minimal() +
  scale_y_continuous(labels = scales::comma)
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
