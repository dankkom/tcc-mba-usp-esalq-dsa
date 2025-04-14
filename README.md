# TCC

## Projeto de Pesquisa

2024-10-31 a 2024-11-07

./projeto-de-pesquisa.qmd

## Resultados Preliminares

2025-01-30 a 2025-02-06

./resultados-preliminares.qmd

## Entrega Final

2025-04-15 a 2025-04-29

./entrega-final.qmd

## Slides

2025-05-01 a 2025-05-29

./slides.qmd

## Output Data Files

codigo/0-collect-datasus-sinan-dengue.py

- data/datasus/sinan-deng/*.dbc

codigo/1-process-dbc-files.R

- data/datasus/parquet/*.parquet

codigo/2-data-wrangling.py

- data/sinan-dengue.csv (PBI)
- data/sinan-dengue.parquet

codigo/3-malha-geografica.py

- data/br_mun.csv (PBI)
- data/br_mun.gpkg
- data/br_uf.json

codigo/4-populacao.py

- data/populacao-municipios.csv (PBI)
- data/populacao-municipios.parquet

codigo/5-dados-mapas.py

- data/dengue-populacao-mun.parquet
