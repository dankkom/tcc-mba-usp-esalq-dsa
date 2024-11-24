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


data_dir <- "data/datasus"
dest_dir <- "data/datasus/parquet"
dir_create(dest_dir)


main <- function() {
  # Lista de arquivos DBC
  files <- dir_ls(
    data_dir,
    recurse = TRUE,
    glob = "*.dbc"
  )

  for (file in files) {
    dest_filepath <- path(dest_dir, glue::glue("{basename(dirname(file))}.parquet"))
    if (file_exists(dest_filepath)) {
      print(paste("Arquivo já processado:", file))
      next
    }
    print(paste("Lendo arquivo:", file))
    # Lendo arquivo DBC
    read.dbc(file, as.is = TRUE) |>
      as_tibble() |>
      arrow::write_parquet(dest_filepath)
    gc()  # Coleta de lixo
  }
}

main()
