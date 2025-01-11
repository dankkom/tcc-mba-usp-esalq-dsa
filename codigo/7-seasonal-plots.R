library(tidyverse)
library(arrow)


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
dados_br %>%
  ggplot2::ggplot(ggplot2::aes(x = anomes, y = notificacoes)) +
  ggplot2::geom_line() +
  ggplot2::labs(
    title = "Notificações de dengue no Brasil",
    x = "Ano-Mês",
    y = "Notificações de Dengue",
  ) +
  ggplot2::theme_minimal() +
  ggplot2::facet_wrap(~lubridate::month(anomes), scales = "free_y")
ggplot2::ggsave(
  "output/plots/seasonal-plot-facet.jpg",
  width = 10,
  height = 6,
  dpi = 100,
)


forecast::ggsubseriesplot(
  ts(dados_br$notificacoes, frequency = 12),
  ylab = "Notificações",
  xlab = "Mês",
  main = "Notificações de dengue no Brasil"
)
ggplot2::ggsave(
  "output/plots/seasonal-plot-subseries.jpg",
  width = 10,
  height = 6,
  dpi = 100,
)
