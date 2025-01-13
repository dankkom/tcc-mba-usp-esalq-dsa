# Header -------------------------------------------------------------------
# Author: Daniel Kiyoyudi Komesu
# Date: 2025-01-12
# Purpose: Plot incidence rate by state

# Library Imports ----------------------------------------------------------
library(arrow)
library(dplyr)
library(ggplot2)
library(patchwork)
library(scales)


dengue_populacao_mun <- arrow::read_parquet("data/dengue-populacao-mun.parquet")


# Taxa de Incidência por UF
incidencia_uf <- dengue_populacao_mun %>%
  dplyr::group_by(ano = lubridate::year(data), sigla_uf, id_municipio_6) %>%
  dplyr::summarise(
    notificacoes = sum(notificacoes),
    populacao_estimada = mean(populacao_estimada),
    .groups = "drop"
  ) %>%
  dplyr::group_by(ano, sigla_uf) %>%
  dplyr::summarise(
    notificacoes = sum(notificacoes),
    populacao_estimada = sum(populacao_estimada),
    .groups = "drop"
  ) %>%
  dplyr::mutate(
    incidencia = (notificacoes / populacao_estimada) * 100000
  )


# Plot horizontal bar chart sorted by incidence, 2023
incidencia_uf_2023_plot <- incidencia_uf %>%
  filter(ano == 2023) %>%
  dplyr::arrange(desc(incidencia)) %>%
  ggplot2::ggplot(
    ggplot2::aes(
      x = incidencia,
      y = forcats::fct_reorder(sigla_uf, incidencia),
      fill = incidencia
    )
  ) +
  ggplot2::geom_col() +
  ggplot2::labs(
    title = "a) 2023",
    x = "Incidência de dengue por 100.000 habitantes",
    y = "Unidade Federativa",
  ) +
  ggplot2::scale_x_continuous(labels = scales::number) +
  ggplot2::theme_minimal() +
  # Add labels
  ggplot2::geom_text(
    ggplot2::aes(label = scales::number(incidencia, accuracy = 1)),
    hjust = -0.2,
    size = 4
  ) +
  # Adjust x limits and format x axis labels
  ggplot2::scale_x_continuous(
    limits = c(0, 2200),
    labels = scales::number
  ) +
  # Remove legend
  ggplot2::theme(legend.position = "none")
incidencia_uf_2023_plot
ggplot2::ggsave(
  "output/plots/incidencia-uf-2023.jpg",
  incidencia_uf_2023_plot,
  width = 6,
  height = 8,
  dpi = 100,
)


# Plot horizontal bar chart sorted by incidence, 2024
incidencia_uf_2024_plot <- incidencia_uf %>%
  filter(ano == 2024) %>%
  dplyr::arrange(desc(incidencia)) %>%
  ggplot2::ggplot(
    ggplot2::aes(
      x = incidencia,
      y = forcats::fct_reorder(sigla_uf, incidencia),
      fill = incidencia
    )
  ) +
  ggplot2::geom_col() +
  ggplot2::labs(
    title = "b) 2024",
    x = "Incidência de dengue por 100.000 habitantes",
    y = "Unidade Federativa",
  ) +
  ggplot2::theme_minimal() +
  # Add labels
  ggplot2::geom_text(
    ggplot2::aes(label = scales::number(incidencia, accuracy = 1)),
    hjust = -0.2,
    size = 4
  ) +
  # Adjust x limits and format x axis labels
  ggplot2::scale_x_continuous(
    limits = c(0, 10000),
    labels = scales::number
  ) +
  # Remove legend
  ggplot2::theme(legend.position = "none")
incidencia_uf_2024_plot
ggplot2::ggsave(
  "output/plots/incidencia-uf-2023-2024.jpg",
  incidencia_uf_2024_plot,
  width = 6,
  height = 8,
  dpi = 100,
)

incidencia_uf_2023_2024_plot <- incidencia_uf_2023_plot + incidencia_uf_2024_plot +
  patchwork::plot_layout(
    ncol = 2
  )
ggplot2::ggsave(
  "output/plots/incidencia-uf-2023-2024.jpg",
  incidencia_uf_2023_2024_plot,
  width = 12,
  height = 8,
  dpi = 100,
)



incidencia_uf_2023_2024_plot <-
  incidencia_uf_2023_plot +
  incidencia_uf_2024_plot +
  patchwork::plot_layout(
    ncol = 2
  )
ggplot2::ggsave(
  "output/plots/incidencia-uf-2023-2024.jpg",
  incidencia_uf_2023_2024_plot,
  width = 12,
  height = 8,
  dpi = 100,
)
