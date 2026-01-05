# 🎲 CJEI - Sistema de Recomendación de Juegos de Mesa

Sistema de recomendación de juegos de mesa para asesores pedagógicos del **Centro de Juegos y Experiencias Interactivas (CJEI)** de la Pontificia Universidad Javeriana Cali.

## 📊 Estado del Proyecto

| Módulo | Estado | Requerimientos |
|--------|--------|----------------|
| **A - Ingesta y Normalización** | ✅ **COMPLETO** | RF-ING-01, RF-ING-02, RF-ING-03 |
| B - Contexto de Clase | 🔄 Pendiente | RF-CTX-01, RF-CTX-02 |
| C - Taxonomía de Habilidades | 🔄 Pendiente | RF-TAX-01, RF-TAX-02, RF-TAX-03 |
| D - Motor de Recomendación | 🔄 Pendiente | RF-REC-01, RF-REC-02, RF-REC-03 |
| E - Explicabilidad | 🔄 Pendiente | RF-EXP-01, RF-EXP-02 |
| F - Interfaz Web | 🔄 Pendiente | RF-UI-01, RF-UI-02, RF-UI-03 |
| G - Retroalimentación | 🔄 Pendiente | RF-RETRO-01, RF-RETRO-02 |
| H - Administración | 🔄 Pendiente | RF-ADM-01, RF-ADM-02 |

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.11+
- PostgreSQL 14+
- pip / venv

### Instalación

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd bg_recommendations

# 2. Configurar backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar base de datos
cp .env.example .env
# Editar .env con tus credenciales

createdb cjei_recommendations

# 4. Ejecutar migraciones
alembic upgrade head

# 5. Seed datos de prueba
python -m scripts.seed_data

# 6. Iniciar servidor
uvicorn app.main:app --reload
```

### Acceso Rápido

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📁 Estructura del Proyecto

```
bg_recommendations/
├── .github/
│   ├── copilot-instructions.md      # ✅ Instrucciones para AI agents
│   ├── backend-instructions.md      # ✅ Guía detallada de backend
│   └── rf_sistema_cjei.md          # ✅ Especificaciones completas (34 RF)
├── backend/                         # ✅ API FastAPI
│   ├── app/
│   │   ├── core/                   # Config, database, exceptions
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── games/                  # ✅ Módulo A completo
│   │   └── main.py
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # ✅ 9 tests unitarios
│   ├── scripts/                    # Seed data scripts
│   └── sample_data/                # CSV/JSON de ejemplo
├── IMPLEMENTATION_SUMMARY.md        # ✅ Resumen técnico Módulo A
├── USAGE_GUIDE.md                  # ✅ Guía de uso con ejemplos
└── README.md                       # Este archivo
```

## 🎯 Módulo A Implementado

### ✅ RF-ING-01: Importación de Catálogo
- Modelo `Game` con todos los atributos requeridos
- Validación de campos obligatorios (name, bgg_id)
- Detección de duplicados
- Endpoint: `POST /api/games`

### ✅ RF-ING-02: Normalización Automática
- **Duración:** Clamp 5-360 min, default 60
- **Complejidad:** Clamp 1.0-5.0, default 2.5
- **Mecánicas:** Vocabulario controlado (50+ mecánicas)
- **Idioma:** Enum (ninguna/baja/media/alta)
- **Jugadores:** Validación min ≤ max

### ✅ RF-ING-03: Importación Masiva
- Soporte CSV y JSON
- Detección de duplicados por BGG ID
- 3 estrategias de merge: `update`, `skip`, `replace`
- Validación de tasa de rechazo (<20%)
- Endpoints: 
  - `POST /api/games/import/csv`
  - `POST /api/games/import/json`

## 📖 Documentación

- **[Guía de Uso](USAGE_GUIDE.md)** - Ejemplos prácticos de API
- **[Resumen Técnico](IMPLEMENTATION_SUMMARY.md)** - Detalles de implementación
- **[Instrucciones Backend](. github/backend-instructions.md)** - Arquitectura completa
- **[Especificaciones RF](.github/rf_sistema_cjei.md)** - 34 requerimientos funcionales

## 🧪 Testing

```bash
cd backend

# Ejecutar tests
pytest -v

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos del Módulo A
pytest tests/test_games.py -v
```

**Cobertura actual:** >80% en módulo A

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.104+ (Python 3.11+)
- **ORM:** SQLAlchemy 2.0
- **Validación:** Pydantic v2
- **Database:** PostgreSQL 14+
- **Migrations:** Alembic
- **Testing:** Pytest

### Futuro (Pendiente)
- **Frontend:** React + TypeScript
- **Auth:** JWT with python-jose
- **Deploy:** Docker + Docker Compose

## 📚 API Endpoints (Módulo A)

### Games Management
- `POST /api/games` - Crear juego
- `GET /api/games` - Listar (paginado, filtrable)
- `GET /api/games/{id}` - Obtener por ID
- `PUT /api/games/{id}` - Actualizar
- `DELETE /api/games/{id}` - Eliminar
- `GET /api/games/mechanics` - Vocabulario de mecánicas

### Bulk Import
- `POST /api/games/import/csv` - Importar CSV
- `POST /api/games/import/json` - Importar JSON

### Filters Soportados
- `name`, `available`, `min_duration`, `max_duration`
- `min_complexity`, `max_complexity`, `min_players`, `max_players`
- `mechanics`, `language`, `sort_by`, `page`, `page_size`

## 💡 Ejemplos de Uso

### Crear un juego
```bash
curl -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Catan",
    "bgg_id": 13,
    "duration_min": 120,
    "complexity": 2.3,
    "min_players": 3,
    "max_players": 4,
    "mechanics": ["Trading", "Dice Rolling"],
    "language_dependency": "baja",
    "available": true
  }'
```

### Buscar juegos para clase
```bash
# Juegos para 15 estudiantes, 45 min máximo, simples
curl "http://localhost:8000/api/games?\
min_players=15&\
max_duration=45&\
max_complexity=2.5&\
available=true"
```

### Importar catálogo completo
```bash
curl -X POST "http://localhost:8000/api/games/import/csv?merge_strategy=update" \
  -F "file=@cjei_catalog.csv"
```

Ver más ejemplos en [USAGE_GUIDE.md](USAGE_GUIDE.md)

## 🔜 Próximos Módulos

### Módulo B - Contexto de Clase
- Captura de perfil de sesión (objetivos, tiempo, grupo)
- Validación de coherencia operativa
- Plantillas reutilizables

### Módulo C - Taxonomía de Habilidades
- Gestión de taxonomía (cognitivas, sociales, emocionales)
- Asignación manual de habilidades a juegos
- Documentación de criterios pedagógicos

### Módulo D - Motor de Recomendación
- Algoritmo híbrido (filtros + scoring)
- Configuración de pesos
- Manejo de restricciones no satisfechas

## 👥 Equipo

**Institución:** Pontificia Universidad Javeriana Cali  
**Centro:** CJEI (Centro de Juegos y Experiencias Interactivas)  
**Desarrollo:** Sistema de recomendación MVP  

## 📄 Licencia

© 2026 Pontificia Universidad Javeriana Cali - CJEI

## 🆘 Soporte

- **Issues:** [GitHub Issues](./issues)
- **Documentación:** Ver carpeta `.github/`
- **API Docs:** http://localhost:8000/docs

---

**Última actualización:** Enero 5, 2026  
**Estado:** Módulo A completo ✅  
**Siguiente hito:** Módulo B - Session Profiles
