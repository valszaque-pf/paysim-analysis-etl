# PaySim Analytics y ETL Pipeline 

Proyecto de análisis de datos con consultas SQL y notebooks 
orientados a la investigación de patrones de fraude, evaluación de la 
regla de detección original y exploraciónde una regla alternativa del
dataset PaySim.

El proyecto también incluye Pipeline ETL en Python para 
descargar, validar, transformar y cargar en
PostgreSQL el dataset sintético de transacciones financieras.

El dataset original fue tomado desde kaggle en: 
https://www.kaggle.com/datasets/ealaxi/paysim1.

## Decisiones de diseño

- Originalmente un proyecto de análisis, este evolucionó para
  agregar un pipeline de transformación y carga a PostgreSQL
  dada la magnitud del dataset estudiado (más de 6 millones de filas).
- Se optó por un diseño de carga atómico, idempotente y por lotes
  dadas ciertas limitaciones de hardware, también para mantener
  un resultado consistente con cada ejecución del pipeline.
- También se agregó una migración de schema con alembic previo a la
  carga completa para asegurar que los datos lleguen correctamente.
- El pipeline podría ser construido como un ELT perfectamente, el diseño
  ETL fue elegido a razón de la necesidad de replicabilidad del proyecto.
- Las principales visualizaciones del proyecto se encuentran en los
  cuadernos y en la carpeta `/reports/`, los gráficos fueron creados
  utilizando matplotlib y seaborn. Originalmente estaban contempladas
  visualizaciones a través de herramientas BI, mas se decidió
  aplazar para la siguiente versión.

## Flujo del pipeline

El comando principal ejecuta las siguientes etapas:

1. Crea los directorios requeridos.
2. Descarga el archivo CSV desde Kaggle.
3. Se convierte el CSV a Parquet mediante DuckDB.
4. Valida el esquema y las restricciones de los datos crudos con Pandera.
5. Normaliza los nombres de columnas y genera `hour_of_day` y
   `simulation_day`.
6. Valida el resultado transformado y lo guarda en formato Parquet.
7. Carga el archivo transformado en PostgreSQL mediante `COPY FROM STDIN`.

## Tecnologías principales

- Python 3.12
- PyArrow
- pandas 
- DuckDB
- Pandera
- PostgreSQL y psycopg2
- SQLAlchemy
- Alembic
- KaggleHub
- JupyterLab
- VS Code
- DBeaver
- uv

## Requisitos

- Python 3.12
- uv
- PostgreSQL con una base de datos creada para el proyecto
- Acceso a internet para descargar el dataset desde Kaggle

La migración crea la tabla y sus índices, pero no crea los datos 
en PostgreSQL.

## Instalación

Clona el repositorio y entra en su directorio:

```
git clone (https://github.com/valszaque-pf/paysim-analysis-etl)
cd etl_pipeline
```

Instala las dependencias:

```
uv sync
```

## Configuración

El archivo .env de ejemplo sólo contiene una constante que es DB_URL,
la cual es utilizada en algunas partes del pipeline. los datos de 
la variable deben ser reemplazados por el usuario, contraseña y puerto 
de conexión que estén asignados a la instancia usada de postgreSQL
Para el funcionamiento integral del script.

## Ejecución

### Primera ejecución

Para aplicar la migración y ejecutar el pipeline completo:

```
uv run paysim-pipeline --migrate
```

La opción `--migrate` equivale a ejecutar `alembic upgrade head` antes 
de la orquestación del pipeline.

### Ejecuciones posteriores

Si el esquema de PostgreSQL ya está actualizado:

```
uv run paysim-pipeline
```

El tamaño de los lotes utilizados durante la carga puede configurarse:

```
uv run paysim-pipeline --batch-size 100000
```

El valor predeterminado es de 200.000 filas.

Para consultar todas las opciones:

```
uv run paysim-pipeline --help
```

## Ejecución por etapas

Las etapas también pueden ejecutarse individualmente:

```
uv run python -m src.paths
uv run python -m src.download
uv run python -m src.extract
uv run python -m src.transform
uv run python -m src.load
```

Cada etapa presupone que los artefactos requeridos por la etapa anterior ya
existen. La carga también requiere que la tabla haya sido creada mediante
Alembic.

Para aplicar solamente las migraciones:

```
uv run alembic upgrade head
```

## Datos generados

Durante la ejecución se crean los siguientes artefactos:

```
data/
├── csv/
│   └── PS_20174392719_1491204439457_log.csv
├── raw/
│   └── paysim_raw.parquet
└── transformed/
    └── paysim_clean.parquet
```

Los datos descargados y transformados no se incluyen en el repositorio.

## Modelo de datos

La tabla `paysim` contiene las columnas originales normalizadas y dos columnas
derivadas:

| Columna | Descripción |
| --- | --- |
| `id` | clave primaria |
| `step` | Hora secuencial de la simulación |
| `type` | Tipo de transacción |
| `amount` | Monto de la operación |
| `name_orig` | Identificador de la cuenta de origen |
| `oldbalance_orig` | Saldo de origen antes de la transacción |
| `newbalance_orig` | Saldo de origen después de la transacción |
| `name_dest` | Identificador de la cuenta de destino |
| `oldbalance_dest` | Saldo de destino antes de la transacción |
| `newbalance_dest` | Saldo de destino después de la transacción |
| `is_fraud` | Etiqueta real de fraude |
| `is_flagged_fraud` | Alerta generada por la regla original |
| `hour_of_day` | Hora derivada, entre 0 y 23 |
| `simulation_day` | Día derivado de la simulación |

La tabla incorpora una clave primaria y diversos índices para
facilitar las consultas.

## Análisis

La carpeta `/SQL/` contiene consultas para:

- Analizar fraude por día y hora.
- Comparar fraudes reales y alertas originales.
- Explorar sucesiones entre transferencias y retiros.
- Analizar cardinalidades por monto y hora de simulación.
- Evaluar una nueva regla de detección.
- Calcular matrices de confusión, precisión, recall, especificidad y F1.
- Comparar el monto fraudulento recuperado por ambas reglas.

Los notebooks principales son:

- `notebooks/Exploracion.ipynb`: exploración y calidad del dataset original.
- `notebooks/Consultas.ipynb`: análisis sobre los datos cargados en PostgreSQL.

Para abrirlos basta con ejecutar los archivos en VS code o jupyter lab o notebook

## Estructura del proyecto

```
├── SQL/                    # Consultas analíticas
├── data/                   # Datos descargados y transformados
├── migrations/             # Migraciones de Alembic
├── notebooks/              # Exploración y análisis
├── reports/                # Gráficos y resultados generados
├── src/
│   ├── db.py               # Conexiones a PostgreSQL
│   ├── download.py         # Descarga del dataset
│   ├── extract.py          # Conversión CSV a Parquet
│   ├── load.py             # Carga por lotes a PostgreSQL
│   ├── paths.py            # Rutas y directorios
│   ├── pipeline.py         # Orquestador y CLI principal
│   ├── schema.py           # Schema SQLAlchemy
│   ├── transform.py        # Transformaciones
│   ├── utils.py            # Funciones auxiliares
│   └── validate.py         # Contratos Pandera
├── .env.example
├── alembic.ini
├── pyproject.toml
└── uv.lock
```

## Limitaciones actuales

- PaySim es un dataset sintético y no representa toda la complejidad de un
  sistema financiero real.
- Las dimensiones temporales se derivan del campo `step`; el dataset no
  contiene fechas reales de calendario.
- Las visualizaciones son creadas sólo a través de python y notebooks,
  no tiene una presentación clara con herramientas de BI.
- El pipeline no es escalable actualmente, con ciertos cambios en el
  diseño podría serlo, no está en los planes de futuras versiones.

## Planes futuros

- actualizaciones para dependencias como pandas y psycopg2 están
  previstas para la próxima versión, reemplazando por polars y
  psycopg3 respectivamente.
- Visualizaciones con herramientas de BI.