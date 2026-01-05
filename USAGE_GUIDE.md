# 📖 Guía de Uso - Módulo A

## Inicio Rápido (5 minutos)

```bash
# 1. Clonar y entrar al directorio
cd bg_recommendations/backend

# 2. Setup completo (automático)
make setup

# 3. Iniciar servidor
make run

# 4. Abrir documentación
open http://localhost:8000/docs
```

## Ejemplos de API

### 1. Crear un juego manualmente

**Request:**
```bash
curl -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pandemic Legacy: Season 1",
    "bgg_id": 161936,
    "duration_min": 60,
    "complexity": 2.8,
    "min_players": 2,
    "max_players": 4,
    "mechanics": ["Cooperative Play", "Campaign / Battle Card Driven", "Legacy"],
    "language_dependency": "alta",
    "bgg_rank": 3,
    "description": "Pandemic Legacy is a co-operative campaign game...",
    "image_url": "https://cf.geekdo-images.com/...",
    "year_published": 2015,
    "available": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Pandemic Legacy: Season 1",
  "bgg_id": 161936,
  "duration_min": 60,
  "complexity": 2.8,
  "min_players": 2,
  "max_players": 4,
  "mechanics": ["Cooperative Play", "Campaign / Battle Card Driven", "Legacy"],
  "language_dependency": "alta",
  "bgg_rank": 3,
  "description": "Pandemic Legacy is a co-operative campaign game...",
  "image_url": "https://cf.geekdo-images.com/...",
  "year_published": 2015,
  "available": true,
  "has_partial_data": false,
  "created_at": "2026-01-05T10:30:00",
  "updated_at": "2026-01-05T10:30:00"
}
```

### 2. Listar todos los juegos disponibles

**Request:**
```bash
curl "http://localhost:8000/api/games?available=true&page=1&page_size=20"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Catan",
      "bgg_id": 13,
      "duration_min": 120,
      "complexity": 2.3,
      ...
    },
    {
      "id": 2,
      "name": "Pandemic",
      ...
    }
  ],
  "total": 8,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### 3. Buscar juegos por nombre

**Request:**
```bash
curl "http://localhost:8000/api/games?name=pandemic"
```

### 4. Filtrar juegos por características

**Juegos para 2-4 jugadores, duración 30-90 min, complejidad baja-media:**
```bash
curl "http://localhost:8000/api/games?min_players=2&max_players=4&min_duration=30&max_duration=90&max_complexity=3.0"
```

**Juegos cooperativos disponibles:**
```bash
curl "http://localhost:8000/api/games?mechanics=Cooperative%20Play&available=true"
```

**Juegos sin dependencia de idioma:**
```bash
curl "http://localhost:8000/api/games?language=ninguna"
```

### 5. Obtener un juego específico

**Request:**
```bash
curl "http://localhost:8000/api/games/1"
```

### 6. Actualizar un juego

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/games/1" \
  -H "Content-Type: application/json" \
  -d '{
    "available": false,
    "description": "Updated description..."
  }'
```

### 7. Eliminar un juego

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/games/1"
```

### 8. Obtener vocabulario de mecánicas

**Request:**
```bash
curl "http://localhost:8000/api/games/mechanics"
```

**Response:**
```json
[
  "Action Points",
  "Area Control",
  "Auction/Bidding",
  "Card Drafting",
  "Cooperative Play",
  ...
]
```

## Importación Masiva

### CSV Import

**1. Preparar archivo CSV:**

`my_games.csv`:
```csv
name,bgg_id,duration_min,complexity,min_players,max_players,mechanics,language_dependency,bgg_rank,year_published,available
Wingspan,266192,70,2.4,1,5,Set Collection;Hand Management;Dice Rolling,baja,25,2019,true
Splendor,148228,30,1.8,2,4,Set Collection;Card Drafting,ninguna,120,2014,true
```

**2. Importar con estrategia UPDATE (default):**
```bash
curl -X POST "http://localhost:8000/api/games/import/csv?merge_strategy=update" \
  -F "file=@my_games.csv"
```

**3. Importar con estrategia SKIP (solo nuevos):**
```bash
curl -X POST "http://localhost:8000/api/games/import/csv?merge_strategy=skip" \
  -F "file=@my_games.csv"
```

**4. Importar con estrategia REPLACE (reemplazar):**
```bash
curl -X POST "http://localhost:8000/api/games/import/csv?merge_strategy=replace" \
  -F "file=@my_games.csv"
```

**Response:**
```json
{
  "total_processed": 2,
  "imported": 2,
  "updated": 0,
  "rejected": 0,
  "warnings": [],
  "errors": [],
  "success_rate": 100.0
}
```

### JSON Import

**1. Preparar archivo JSON:**

`my_games.json`:
```json
[
  {
    "name": "Wingspan",
    "bgg_id": 266192,
    "duration_min": 70,
    "complexity": 2.4,
    "min_players": 1,
    "max_players": 5,
    "mechanics": ["Set Collection", "Hand Management", "Dice Rolling"],
    "language_dependency": "baja",
    "bgg_rank": 25,
    "year_published": 2019,
    "available": true
  },
  {
    "name": "Splendor",
    "bgg_id": 148228,
    "duration_min": 30,
    "complexity": 1.8,
    "min_players": 2,
    "max_players": 4,
    "mechanics": ["Set Collection", "Card Drafting"],
    "language_dependency": "ninguna",
    "bgg_rank": 120,
    "year_published": 2014,
    "available": true
  }
]
```

**2. Importar:**
```bash
curl -X POST "http://localhost:8000/api/games/import/json?merge_strategy=update" \
  -F "file=@my_games.json"
```

## Casos de Uso Comunes

### Caso 1: Buscar juegos para clase de 15 estudiantes, 45 minutos

```bash
# Juegos que soportan 15 jugadores, duración máxima 45 min
curl "http://localhost:8000/api/games?min_players=15&max_players=15&max_duration=45&available=true"
```

### Caso 2: Juegos cooperativos simples

```bash
# Complejidad baja (≤2.0), cooperativos
curl "http://localhost:8000/api/games?mechanics=Cooperative%20Play&max_complexity=2.0&available=true"
```

### Caso 3: Juegos sin barreras de idioma

```bash
# Language dependency = ninguna
curl "http://localhost:8000/api/games?language=ninguna&available=true"
```

### Caso 4: Actualizar disponibilidad después de préstamo

```bash
# Marcar juego como no disponible
curl -X PUT "http://localhost:8000/api/games/5" \
  -H "Content-Type: application/json" \
  -d '{"available": false}'

# Más tarde, marcarlo como disponible nuevamente
curl -X PUT "http://localhost:8000/api/games/5" \
  -H "Content-Type: application/json" \
  -d '{"available": true}'
```

### Caso 5: Importación inicial del catálogo completo

```bash
# 1. Exportar desde BGG o fuente interna
# 2. Formatear como CSV/JSON
# 3. Importar con estrategia UPDATE
curl -X POST "http://localhost:8000/api/games/import/csv?merge_strategy=update" \
  -F "file=@cjei_catalog_2026.csv"

# 4. Verificar resultados
# Si success_rate < 80%, revisar errores y corregir archivo
```

## Normalización Automática en Acción

### Ejemplo 1: Duración fuera de rango

**Input:**
```json
{
  "name": "Quick Game",
  "bgg_id": 999,
  "duration_min": 2,  // Menor que mínimo (5)
  ...
}
```

**Output:**
```json
{
  "id": 10,
  "name": "Quick Game",
  "duration_min": 5,  // ✅ Normalizado a mínimo
  ...
}
```

### Ejemplo 2: Complejidad fuera de rango

**Input:**
```json
{
  "name": "Super Complex",
  "bgg_id": 1000,
  "complexity": 7.5,  // Mayor que máximo (5.0)
  ...
}
```

**Output:**
```json
{
  "id": 11,
  "name": "Super Complex",
  "complexity": 5.0,  // ✅ Normalizado a máximo
  ...
}
```

### Ejemplo 3: Jugadores min > max

**Input:**
```json
{
  "name": "Confusing Game",
  "bgg_id": 1001,
  "min_players": 6,
  "max_players": 2,  // ❌ min > max
  ...
}
```

**Output:**
```json
{
  "id": 12,
  "name": "Confusing Game",
  "min_players": 2,  // ✅ Corregido automáticamente
  "max_players": 6,
  ...
}
```

## Troubleshooting

### Error: Duplicate BGG ID

**Problema:**
```json
{
  "detail": "Game with BGG ID 13 already exists"
}
```

**Solución:**
1. Verificar si el juego ya existe: `GET /api/games?bgg_id=13`
2. Si quieres actualizar, usa `PUT /api/games/{id}`
3. Si quieres reemplazar, elimina primero o usa importación con strategy=replace

### Error: File has too many invalid rows

**Problema:**
```json
{
  "errors": [
    "Import rejected: 25% of rows invalid (threshold: 20%)"
  ]
}
```

**Solución:**
1. Revisar el array `errors` en la respuesta para identificar filas problemáticas
2. Corregir el archivo CSV/JSON
3. Volver a intentar la importación

### Error: Unknown mechanics

**Comportamiento:**
- Las mecánicas desconocidas NO rechazan el juego
- Se aceptan pero se genera warning en logs
- Aparecen en el vocabulario de mecánicas

**Verificar vocabulario:**
```bash
curl "http://localhost:8000/api/games/mechanics"
```

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Crear cliente
class CJEIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def create_game(self, game_data):
        response = requests.post(f"{self.base_url}/games", json=game_data)
        response.raise_for_status()
        return response.json()
    
    def list_games(self, **filters):
        response = requests.get(f"{self.base_url}/games", params=filters)
        response.raise_for_status()
        return response.json()
    
    def get_game(self, game_id):
        response = requests.get(f"{self.base_url}/games/{game_id}")
        response.raise_for_status()
        return response.json()
    
    def import_csv(self, file_path, strategy="update"):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'merge_strategy': strategy}
            response = requests.post(
                f"{self.base_url}/games/import/csv",
                files=files,
                params=params
            )
        response.raise_for_status()
        return response.json()

# Uso
client = CJEIClient()

# Listar juegos cooperativos disponibles
games = client.list_games(
    mechanics="Cooperative Play",
    available=True,
    max_complexity=3.0
)

print(f"Found {games['total']} cooperative games")
for game in games['items']:
    print(f"- {game['name']} (complexity: {game['complexity']})")
```

## Testing

```bash
# Ejecutar todos los tests
make test

# Ejecutar con cobertura
make test-cov

# Ejecutar test específico
pytest tests/test_games.py::test_create_game -v

# Ver reporte de cobertura
open htmlcov/index.html
```

---

**📚 Más información:**
- OpenAPI Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Especificaciones completas: [.github/rf_sistema_cjei.md](.github/rf_sistema_cjei.md)
