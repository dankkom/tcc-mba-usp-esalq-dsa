
# Header -------------------------------------------------------------------
# Author: Daniel Kiyoyudi Komesu
# Date: 2025-01-12
# Purpose: Boxplot incidence rate by region

# Library Imports ----------------------------------------------------------
library(arrow)
library(dplyr)
library(ggplot2)
library(patchwork)
library(scales)
library(forcats)


dengue_populacao_mun <- arrow::read_parquet("data/dengue-populacao-mun.parquet")

# Adiciona a região de cada UF
norte <- c("AC", "AM", "AP", "PA", "RO", "RR", "TO")
nordeste <- c("AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE")
centro_oeste <- c("DF", "GO", "MT", "MS")
sudeste <- c("ES", "MG", "RJ", "SP")
sul <- c("PR", "RS", "SC")
dengue_populacao_mun <- dengue_populacao_mun %>%
  dplyr::mutate(
    regiao = dplyr::case_when(
      sigla_uf %in% norte ~ "Norte",
      sigla_uf %in% nordeste ~ "Nordeste",
      sigla_uf %in% centro_oeste ~ "Centro-Oeste",
      sigla_uf %in% sudeste ~ "Sudeste",
      sigla_uf %in% sul ~ "Sul",
      TRUE ~ NA_character_
    ),
    regiao = forcats::fct_reorder(regiao, incidencia, .fun = median)
  )

dengue_populacao_mun_2024 <- dengue_populacao_mun %>%
  dplyr::filter(lubridate::year(data) == 2024) %>%
  dplyr::group_by(regiao, id_municipio_6) %>%
  dplyr::summarise(
    notificacoes = sum(notificacoes),
    populacao_estimada = mean(populacao_estimada),
    .groups = "drop"
  ) %>%
  dplyr::mutate(
    incidencia = (notificacoes / populacao_estimada) * 100000
  )


# Sumariza a mediana da incidência por região
dengue_populacao_mun_2024 %>%
  dplyr::group_by(regiao) %>%
  dplyr::summarise(
    mediana_incidencia = median(incidencia, na.rm = TRUE)
  ) %>%
  dplyr::arrange(desc(mediana_incidencia))


# Boxplot da incidência por UF, com orientação horizontal
# e ordenado pela mediana
dengue_populacao_mun_2024 %>%
  ggplot2::ggplot(
    ggplot2::aes(
      x = forcats::fct_reorder(regiao, incidencia, .fun = median),
      y = incidencia,
    )
  ) +
  ggplot2::geom_boxplot(
    ggplot2::aes(
      fill = forcats::fct_reorder(regiao, incidencia, .fun = median),
    )
  ) +
  ggplot2::geom_jitter(
    position = ggplot2::position_jitter(0.3),
    colour = "black",
    alpha = 0.1,
  ) +
  ggplot2::labs(
    x = "Grande Região",
    y = "Incidência de dengue por 100.000 habitantes",
    fill = "Grande Região",
  ) +
  ggplot2::theme_minimal() +
  ggplot2::theme(
    legend.position = "none",
  )
ggplot2::ggsave(
  "output/plots/incidencia-regiao-boxplot.png",
  width = 8,
  height = 6,
  dpi = 300,
  bg = "white",
)
