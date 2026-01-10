# CJEI Board Game Recommendation System - Backend

Sistema de recomendación de juegos de mesa para asesores pedagógicos del Centro de Juegos y Experiencias Interactivas (CJEI) de la Pontificia Universidad Javeriana Cali.

## Módulo A - Ingesta y Normalización de Datos ✅

Este backend implementa los requerimientos funcionales del Módulo A:

- **RF-ING-01** ✅ Importación de catálogo base
- **RF-ING-02** ✅ Normalización de atributos
- **RF-ING-03** ✅ Actualización incremental del catálogo

## Requisitos

- Python 3.11+
- PostgreSQL 14+

## Instalación

```bash
# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración
```

## Configuración de Base de Datos

```bash
# Crear base de datos PostgreSQL
createdb cjei_recommendations

# O usando psql:
psql -U postgres
CREATE DATABASE cjei_recommendations;
CREATE USER cjei WITH PASSWORD 'cjei';
GRANT ALL PRIVILEGES ON DATABASE cjei_recommendations TO cjei;
\q
```

## Migraciones

```bash
# Inicializar Alembic (solo primera vez)
alembic init alembic

# Crear migración inicial
alembic revision --autogenerate -m "Initial migration with Game model"

# Aplicar migraciones
alembic upgrade head
```

## Ejecución

```bash
# Modo desarrollo con auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Acceder a:
# API: http://localhost:8000
# Documentación interactiva: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── core/                      # Core utilities
│   │   ├── config.py             # Settings with pydantic-settings
│   │   ├── database.py           # SQLAlchemy setup
│   │   └── exceptions.py         # Custom HTTP exceptions
│   ├── models/                    # SQLAlchemy ORM models
│   │   └── game.py               # Game model (RF-ING-01)
│   ├── schemas/                   # Pydantic schemas
│   │   └── game.py               # Game request/response models
│   └── games/                     # Games module (Módulo A)
│       ├── router.py             # CRUD endpoints
│       ├── service.py            # Business logic + normalization
│       └── import_handler.py     # CSV/JSON import (RF-ING-03)
├── alembic/                       # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints (Módulo A)

### Juegos

- `POST /api/games` - Crear juego (RF-ING-01)
- `GET /api/games` - Listar juegos con filtros y paginación
- `GET /api/games/{id}` - Obtener juego por ID
- `PUT /api/games/{id}` - Actualizar juego
- `DELETE /api/games/{id}` - Eliminar juego
- `GET /api/games/mechanics` - Vocabulario de mecánicas (RF-ING-02)

### Importación (RF-ING-03)

- `POST /api/games/import/csv` - Importar desde CSV
- `POST /api/games/import/json` - Importar desde JSON

**Estrategias de merge:**
- `update`: Actualizar campos nuevos, agregar juegos nuevos (default)
- `skip`: Solo agregar juegos nuevos, omitir duplicados
- `replace`: Reemplazar juegos existentes completamente

## Normalización de Datos (RF-ING-02)

El sistema aplica automáticamente las siguientes reglas:

- **Duración:** Clamped a 5-360 minutos, default 60
- **Complejidad:** Clamped a 1.0-5.0, default 2.5
- **Mecánicas:** Validación contra vocabulario controlado (50+ mecánicas estándar)
- **Dependencia de idioma:** Enum (ninguna/baja/media/alta)
- **Rangos de jugadores:** Validación min ≤ max

## Formato de Importación CSV

```csv
name,bgg_id,duration_min,complexity,min_players,max_players,mechanics,language_dependency,bgg_rank,description,image_url,year_published,available
Catan,13,120,2.3,3,4,"Trading;Resource Management;Dice Rolling",baja,15,A game about...,http://...,1995,true
```

**Columnas requeridas:** `name`, `bgg_id`

**Mecánicas:** Separadas por punto y coma (`;`)

## Formato de Importación JSON

```json
[
  {
    "name": "Catan",
    "bgg_id": 13,
    "duration_min": 120,
    "complexity": 2.3,
    "min_players": 3,
    "max_players": 4,
    "mechanics": ["Trading", "Resource Management", "Dice Rolling"],
    "language_dependency": "baja",
    "bgg_rank": 15,
    "description": "A game about...",
    "image_url": "http://...",
    "year_published": 1995,
    "available": true
  }
]
```

## Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html
```

## Próximos Pasos

Módulos pendientes según especificaciones:

- **Módulo B:** Caracterización de contexto de clase
- **Módulo C:** Taxonomía de habilidades
- **Módulo D:** Motor de recomendación
- **Módulo E:** Explicabilidad y trazabilidad
- **Módulo F:** Interfaz web
- **Módulo G:** Retroalimentación
- **Módulo H:** Administración

## Licencia

Pontificia Universidad Javeriana Cali - CJEI © 2026
