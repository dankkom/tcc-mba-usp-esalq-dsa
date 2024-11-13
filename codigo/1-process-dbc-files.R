# Conversão dos arquivos "DBC" do DATASUS para parquet

# Para instalar os pacotes necessários, execute:

# install.packages("arrow")
# install.packages("dplyr")
# install.packages("fs")
# install.packages("read.dbc")
# install.packages("tibble")
# pak::pak("https://github.com/dankkom/microdatasus.git")

# Carregando bibliotecas
library(arrow)
library(dplyr)
library(fs)
library(read.dbc)
library(tibble)
library(microdatasus)


data_dir <- "data/datasus"
dest_dir <- "data/datasus/csv"
dir_create(dest_dir)


main <- function() {
  # Lista de arquivos DBC
  files <- dir_ls(
    data_dir,
    recurse = TRUE,
    glob = "*.dbc"
  )

  for (file in files) {
    # dest_filepath <- path(glue::glue("{basename(dirname(file))}.parquet"))
    dest_filepath <- path(dest_dir, glue::glue("{basename(dirname(file))}.csv"))
    if (file_exists(dest_filepath)) {
      print(paste("Arquivo já processado:", file))
      next
    }
    print(paste("Lendo arquivo:", file))
    # Lendo arquivo DBC
    read.dbc(file, as.is = TRUE) |>
      process_sinan_dengue() |>
      as_tibble() |>
      # write_parquet(dest_filepath)
      readr::write_csv(dest_filepath)
    gc()  # Coleta de lixo
  }
}

main()
