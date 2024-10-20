# Conversão dos arquivos "DBC" do DATASUS para parquet

# Carregando bibliotecas
library(arrow)
library(dplyr)
library(read.dbc)


data_dir <- "output"

# Lista de arquivos DBC
files <- list.files(data_dir, pattern = ".dbc$", full.names = TRUE)

# Função para converter DBC para parquet
convert_dbc_to_parquet <- function(file) {
  # Lendo DBC
  df <- read.dbc(file)
  df
}

