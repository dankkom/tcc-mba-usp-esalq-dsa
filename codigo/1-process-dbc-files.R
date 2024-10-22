# Conversão dos arquivos "DBC" do DATASUS para parquet

# Para instalar os pacotes necessários, execute:

# install.packages("arrow")
# install.packages("dplyr")
# install.packages("fs")
# install.packages("read.dbc")
# install.packages("tibble")

# Carregando bibliotecas
library(arrow)
library(dplyr)
library(fs)
library(read.dbc)
library(tibble)


data_dir <- "C:\\data\\datasus"
dest_dir <- "C:\\data\\datasus\\parquet"
dir_create(dest_dir)

# Lista de arquivos DBC
files <- dir_ls(
  data_dir,
  recurse = TRUE,
  glob = "*.dbc"
)

dados <- tibble()
for (file in files) {
  print(paste("Lendo arquivo:", file))
  # Lendo arquivo DBC
  d <- read.dbc(file, as.is = TRUE) |> as_tibble()
  dados <- bind_rows(dados, d)
  rm(d)  # Liberando memória
  gc()  # Coleta de lixo
}

write_parquet(dados, path(dest_dir, "sinan-deng_2020-2024.parquet"))
