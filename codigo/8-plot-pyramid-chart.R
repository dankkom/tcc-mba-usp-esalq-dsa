# Header -------------------------------------------------------------------
# Author: Daniel Kiyoyudi Komesu
# Date: 2025-01-12
# Purpose: Plot pyramid chart of dengue notifications in 2024

# Library Imports ----------------------------------------------------------
library(arrow)
library(dplyr)
library(ggplot2)
library(patchwork)
library(scales)


plot_pyramid_chart <- function(dados) {
  # Plot pyramid chart
  # ref: https://rfortherestofus.com/2024/07/population-pyramid-part-1
  dados_piramide <- dados %>%
    dplyr::filter(NU_ANO == 2024, CS_SEXO != "Ignorado") %>%
    # Create age groups with the NU_IDADE_N column, with intervals of 5 years
    dplyr::mutate(
      faixa_etaria = dplyr::case_when(
        NU_IDADE_N < 5 ~ "0-4",
        NU_IDADE_N < 10 ~ "5-9",
        NU_IDADE_N < 15 ~ "10-14",
        NU_IDADE_N < 20 ~ "15-19",
        NU_IDADE_N < 25 ~ "20-24",
        NU_IDADE_N < 30 ~ "25-29",
        NU_IDADE_N < 35 ~ "30-34",
        NU_IDADE_N < 40 ~ "35-39",
        NU_IDADE_N < 45 ~ "40-44",
        NU_IDADE_N < 50 ~ "45-49",
        NU_IDADE_N < 55 ~ "50-54",
        NU_IDADE_N < 60 ~ "55-59",
        NU_IDADE_N < 65 ~ "60-64",
        NU_IDADE_N < 70 ~ "65-69",
        NU_IDADE_N < 75 ~ "70-74",
        NU_IDADE_N < 80 ~ "75-79",
        NU_IDADE_N < 85 ~ "80-84",
        NU_IDADE_N < 90 ~ "85-89",
        NU_IDADE_N < 95 ~ "90-94",
        NU_IDADE_N < 100 ~ "95-99",
        TRUE ~ "100+"
      ),
      # Convert faixa_etaria to factor to keep the order
      faixa_etaria = factor(
        faixa_etaria,
        levels = c(
          "0-4",
          "5-9",
          "10-14",
          "15-19",
          "20-24",
          "25-29",
          "30-34",
          "35-39",
          "40-44",
          "45-49",
          "50-54",
          "55-59",
          "60-64",
          "65-69",
          "70-74",
          "75-79",
          "80-84",
          "85-89",
          "90-94",
          "95-99",
          "100+"
        )
      ),
    ) %>%
    dplyr::group_by(faixa_etaria, CS_SEXO) %>%
    dplyr::summarise(notificacoes = dplyr::n(), .groups = "drop") %>%
    dplyr::mutate(
      notificacoes = ifelse(CS_SEXO == "Feminino", -notificacoes, notificacoes)
    )


  piramide_feminino <- dados_piramide %>%
    dplyr::filter(CS_SEXO == "Feminino") %>%
    ggplot2::ggplot(
      ggplot2::aes(
        x = notificacoes,
        y = faixa_etaria,
      )
    ) +
    ggplot2::geom_col(fill = "#a00000") +
    ggplot2::annotate(
      geom = "label",
      x = -300000,
      y = 21,
      label = "Feminino",
      fill = "#a00000",
      color = "white",
      label.size = 0,
      label.padding = ggplot2::unit(0.5, "lines")
    ) +
    ggplot2::scale_x_continuous(
      labels = function(x) scales::label_number(accuracy = 1)(abs(x)),
      breaks = scales::breaks_pretty(),
      limits = c(-400000, 0)
    ) +
    ggplot2::theme_void() +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(),
      panel.grid.major.x = ggplot2::element_line(color = "grey90")
    )
  piramide_feminino

  piramide_masculino <- dados_piramide %>%
    dplyr::filter(CS_SEXO == "Masculino") %>%
    ggplot2::ggplot(
      ggplot2::aes(
        x = notificacoes,
        y = faixa_etaria,
      )
    ) +
    ggplot2::geom_col(fill = "#0000a0") +
    ggplot2::annotate(
      geom = "label",
      x = 250000,
      y = 21,
      label = "Masculino",
      fill = "#0000a0",
      color = "white",
      label.size = 0,
      label.padding = ggplot2::unit(0.5, "lines")
    ) +
    ggplot2::scale_x_continuous(
      labels = function(x) scales::label_number(accuracy = 1)(abs(x)),
      breaks = scales::breaks_pretty(),
      limits = c(0, 400000)
    ) +
    ggplot2::theme_void() +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(),
      panel.grid.major.x = ggplot2::element_line(color = "grey90")
    )
  piramide_masculino

  faixa_etaria_labels <- tibble::tibble(
    faixa_etaria = c(
      "0-4",
      "5-9",
      "10-14",
      "15-19",
      "20-24",
      "25-29",
      "30-34",
      "35-39",
      "40-44",
      "45-49",
      "50-54",
      "55-59",
      "60-64",
      "65-69",
      "70-74",
      "75-79",
      "80-84",
      "85-89",
      "90-94",
      "95-99",
      "100+"
    )
  ) %>%
    dplyr::mutate(faixa_etaria = forcats::fct_inorder(faixa_etaria))

  faixa_etaria_plot <- faixa_etaria_labels |>
    ggplot2::ggplot(
      ggplot2::aes(
        x = 1,
        y = faixa_etaria,
        label = faixa_etaria
      )
    ) +
    ggplot2::geom_text() +
    ggplot2::theme_void()

  piramide_feminino + faixa_etaria_plot + piramide_masculino +
    patchwork::plot_layout(
      widths = c(7.5, 0.75, 7.5)
    )
  ggplot2::ggsave(
    "output/plots/pyramid-chart.jpg",
    width = 12,
    height = 6,
    dpi = 100,
  )
}


# Read data
dados <- arrow::read_parquet("data/sinan-dengue.parquet")

# Plot pyramid chart
plot_pyramid_chart(dados)
