# CJEI Board Game Recommendations - Frontend

Sistema web para recomendación de juegos de mesa basado en objetivos pedagógicos y contexto de clase.

## 🎯 Proyecto

**Sistema de Recomendación de Juegos de Mesa** para el Centro de Juegos y Experiencias Interactivas (CJEI) de la Pontificia Universidad Javeriana Cali.

Ayuda a asesores pedagógicos a seleccionar juegos apropiados basándose en:
- Objetivos de aprendizaje
- Habilidades a desarrollar (taxonomía jerárquica)
- Restricciones operacionales (tiempo, grupo, idioma)
- Preferencias de modalidad (cooperativo/competitivo)

## ✨ Características

### ✅ Implementadas (MVP)
- **Creación de sesiones** con validación operacional
- **Generación de recomendaciones** rankeadas con scores
- **Explicaciones detalladas** de por qué se recomienda cada juego
- **Sistema de feedback** post-sesión
- **Catálogo de juegos** con búsqueda y filtros
- **Taxonomía de habilidades** jerárquica (4 niveles)
- **Diseño responsive** (mobile + desktop)
- **Integración completa con backend** via REST API

## 🚀 Quick Start

```bash
# Instalar dependencias
npm install

# Configurar environment
cp .env.example .env

# Iniciar servidor de desarrollo
npm run dev
```

Accede a: **http://localhost:5173**

**⚠️ Importante:** El backend debe estar corriendo en http://localhost:8000

Consulta [QUICK_START.md](QUICK_START.md) para más detalles.

## 🛠️ Tecnologías

- **React** 19.2.0 con TypeScript 5.9.3
- **Vite** 7.2.4 (build tool)
- **TanStack React Query** 5.90.16 (server state)
- **React Hook Form** 7.70.0 + **Zod** 4.3.5 (forms + validation)
- **React Router** 7.11.0 (routing)
- **Tailwind CSS** 4.1.18 (styling)
- **Axios** 1.13.2 (HTTP client)
- **Lucide React** 0.562.0 (icons)

## 📁 Estructura del Proyecto

```
src/
├── components/          # 16 componentes reutilizables
│   ├── common/         # LoadingSpinner, ErrorAlert, ConfirmDialog, PageHeader
│   ├── layout/         # MainLayout, Navbar
│   ├── games/          # GameCard, GameList, GameDetailModal
│   ├── recommendations/ # SessionProfileForm, RecommendationCard, etc.
│   ├── feedback/       # FeedbackForm, FeedbackSummary
│   └── skills/         # SkillCard, SkillList
├── pages/              # 6 páginas principales
├── services/           # API clients (games, sessions, skills, recommendations)
├── types/              # TypeScript types
├── lib/                # api-client.ts, utils.ts
├── App.tsx             # Routing principal
└── main.tsx            # Entry point
```

## 🎯 Flujo de Usuario

1. **Crear Sesión** (`/sessions/new`)
   - Llenar formulario con objetivos y características
   - Sistema valida y muestra advertencias si es necesario
   - Generar recomendaciones

2. **Ver Recomendaciones** (`/recommendations/:sessionId`)
   - Lista de juegos rankeados con scores
   - Expandir explicaciones detalladas
   - Dar feedback sobre juegos usados

3. **Explorar Catálogo** (`/games`)
   - Buscar y filtrar juegos
   - Ver detalles completos

4. **Consultar Habilidades** (`/skills`)
   - Explorar taxonomía jerárquica
   - Ver definiciones y ejemplos

## 📚 Documentación

- **[README_FRONTEND.md](README_FRONTEND.md)** - Documentación completa del proyecto
- **[QUICK_START.md](QUICK_START.md)** - Guía rápida de inicio (5 minutos)
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Manual de testing completo
- **[API_INTEGRATION.md](API_INTEGRATION.md)** - Documentación de endpoints
- **[COMPONENTS_GUIDE.md](COMPONENTS_GUIDE.md)** - Arquitectura de componentes
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Resumen ejecutivo

## 🧪 Comandos Disponibles

```bash
# Desarrollo
npm run dev              # Iniciar dev server (http://localhost:5173)
npm run build            # Build de producción
npm run preview          # Preview de build

# Calidad de código
npm run lint             # Ejecutar ESLint
npm run lint:fix         # Auto-fix de issues
npm run type-check       # Verificar tipos TypeScript

# Testing (pendiente implementación completa)
npm run test             # Ejecutar tests
npm run test:coverage    # Tests con coverage
```

## 🔌 Backend Integration

### Endpoints Principales

**Sessions:**
- `POST /api/sessions` - Crear perfil de sesión
- `GET /api/sessions/{id}` - Obtener sesión

**Recommendations:**
- `POST /api/recommendations/generate` - Generar recomendaciones
- `POST /api/recommendations/{id}/feedback` - Enviar feedback

**Skills:**
- `GET /api/skills` - Listar habilidades
- `GET /api/skills/tree` - Árbol jerárquico

**Games:**
- `GET /api/games` - Listar juegos con filtros
- `GET /api/games/{id}` - Obtener juego

Consulta [API_INTEGRATION.md](API_INTEGRATION.md) para documentación completa.

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_APP_NAME=CJEI Recommendations
```

### CORS (Backend)

Asegúrate de que el backend permita el origen del frontend:

```python
# backend/app/core/config.py
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

## 🧩 Componentes Principales

### SessionProfileForm
Formulario completo para crear sesiones con:
- Objetivos de clase (array dinámico)
- Habilidades primaria/secundaria
- Tiempo y tamaño de grupo
- Restricciones de idioma y modalidad
- Validación en tiempo real con Zod

### RecommendationCard
Card expandible que muestra:
- Rank y score del juego
- Información básica (jugadores, duración, complejidad)
- Explicación detallada (skill match, operational fit, mechanics)
- Desglose de puntuación
- Botón de feedback

### FeedbackForm
Modal para enviar retroalimentación:
- Rating por estrellas (1-5)
- ¿Se usó el juego? (checkbox)
- Campos cualitativos (qué funcionó, qué no)
- Ventana de edición de 7 días

Consulta [COMPONENTS_GUIDE.md](COMPONENTS_GUIDE.md) para documentación completa.

## 🐛 Troubleshooting

### Backend no responde
```bash
# Verifica que el backend esté corriendo
curl http://localhost:8000/docs
```

### Dropdown de habilidades vacío
```bash
# Verifica que la BD tenga datos
cd backend
python -m scripts.seed_data
```

### Port already in use
```bash
# Mata el proceso en el puerto 5173
lsof -ti:5173 | xargs kill
```

Consulta [QUICK_START.md](QUICK_START.md) para más soluciones.

## 📊 Estado del Proyecto

**MVP:** ✅ Completo (100%)  
**Build:** ✅ Exitoso (441KB JS, 28KB CSS)  
**Componentes:** 16/16 implementados  
**Páginas:** 5/6 completas (FeedbackPage pendiente)  
**Backend Integration:** ✅ Completa

### Módulos Implementados
- ✅ Módulo B - Session Profile Characterization
- ✅ Módulo C - Skills Taxonomy Management
- ✅ Módulo D - Recommendation Engine (UI)
- ✅ Módulo E - Explainability (UI)
- ✅ Módulo F - Web Interface Components
- ✅ Módulo G - Feedback System (UI)

## 🚧 Pendientes (Post-MVP)

- [ ] Autenticación (LoginPage)
- [ ] Páginas de administración
- [ ] Tests automatizados (unit + E2E)
- [ ] Toast notifications
- [ ] FeedbackPage completa

## 👥 Contribución

Este proyecto es parte del Sistema de Recomendación CJEI de la Pontificia Universidad Javeriana Cali.

## 📄 Licencia

Propiedad de la Pontificia Universidad Javeriana Cali - CJEI

---

**Versión:** 1.0 MVP  
**Última actualización:** Enero 2026  
**Status:** ✅ Listo para demo y testing con usuarios reales
