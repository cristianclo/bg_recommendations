# CJEI Board Game Recommendations - Frontend

Sistema de recomendación de juegos de mesa para el Centro de Juegos y Experiencias Interactivas (CJEI).

## 🚀 Características Implementadas

### ✅ Módulo B - Session Profile Characterization
- **Creación de perfiles de sesión** con formulario completo
- **Validación operacional** con advertencias no bloqueantes
- Captura de: objetivos, habilidades, tiempo, grupo, idioma, modalidad
- Integración completa con backend API

### ✅ Módulo C - Skills Taxonomy Management
- **Visualización de taxonomía** de habilidades jerárquica
- Listado y búsqueda de habilidades
- Integración con formulario de sesión

### ✅ Módulo D - Recommendation Engine (Parcial)
- **Generación de recomendaciones** basadas en perfil de sesión
- Visualización de juegos rankeados con puntuaciones
- Explicaciones detalladas de cada recomendación
- Descomposición de scores (habilidades, mecánicas, dificultad, ranking)

### ✅ Módulo G - Feedback System (UI)
- **Formulario de feedback** completo
- Calificación por estrellas (1-5)
- Campos cualitativos para comentarios
- Ventana de edición de 7 días

### ✅ UI Components
- **Catálogo de juegos** con búsqueda y filtros
- **Visualización de habilidades** con jerarquía
- **Cards de recomendaciones** expandibles
- **Modales** para detalles de juegos y feedback
- Diseño responsive con Tailwind CSS

## 🛠️ Tecnologías

- **React 18+** con TypeScript 5+
- **Vite** para build y dev server
- **React Router v6** para navegación
- **TanStack Query** para state management del servidor
- **React Hook Form + Zod** para formularios y validación
- **Tailwind CSS** para estilos
- **Lucide React** para iconos
- **Axios** para llamadas HTTP

## 📋 Requisitos Previos

- Node.js 18+ 
- npm/yarn/pnpm
- Backend API ejecutándose en http://localhost:8000

## 🔧 Instalación

```bash
# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env

# Editar .env con la URL del backend si es diferente
# VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 Ejecución

```bash
# Modo desarrollo
npm run dev
# Acceder a: http://localhost:5173

# Build para producción
npm run build

# Preview de build de producción
npm run preview
```

## 📁 Estructura del Proyecto

```
src/
├── components/          # Componentes reutilizables
│   ├── common/         # LoadingSpinner, ErrorAlert, etc.
│   ├── layout/         # MainLayout, Navbar
│   ├── games/          # GameCard, GameList, GameDetailModal
│   ├── recommendations/ # SessionProfileForm, RecommendationCard
│   ├── feedback/       # FeedbackForm, FeedbackSummary
│   └── skills/         # SkillCard, SkillList
├── pages/              # Páginas de la aplicación
│   ├── HomePage.tsx
│   ├── SessionCreatePage.tsx
│   ├── RecommendationsPage.tsx
│   ├── GameCatalogPage.tsx
│   ├── SkillsPage.tsx
│   └── FeedbackPage.tsx
├── services/           # API clients
│   ├── games.service.ts
│   ├── sessions.service.ts
│   ├── skills.service.ts
│   └── recommendations.service.ts
├── types/              # TypeScript types
├── lib/                # Utilidades (api-client, utils)
└── App.tsx             # Componente raíz
```

## 🔌 Integración con Backend

### Endpoints Utilizados

**Módulo B - Sessions:**
- `POST /api/sessions` - Crear perfil de sesión
- `GET /api/sessions/{id}` - Obtener sesión por ID
- `GET /api/sessions` - Listar sesiones
- `PUT /api/sessions/{id}` - Actualizar sesión
- `DELETE /api/sessions/{id}` - Eliminar sesión

**Módulo C - Skills:**
- `GET /api/skills` - Listar habilidades
- `GET /api/skills/{id}` - Obtener habilidad por ID
- `GET /api/skills/tree` - Obtener árbol jerárquico

**Módulo D - Recommendations:**
- `POST /api/recommendations/generate` - Generar recomendaciones
- `GET /api/recommendations/session/{id}` - Obtener recomendaciones de sesión
- `POST /api/recommendations/{id}/feedback` - Enviar feedback

**Módulo Games:**
- `GET /api/games` - Listar juegos con filtros
- `GET /api/games/{id}` - Obtener juego por ID

### Configuración de API

El cliente API está configurado en `src/lib/api-client.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

## 🎯 Flujo de Usuario Principal

1. **Crear Sesión** (`/sessions/new`)
   - Usuario completa formulario con objetivos y características
   - Sistema valida y muestra advertencias si es necesario
   - Usuario confirma y genera recomendaciones

2. **Ver Recomendaciones** (`/recommendations/:sessionId`)
   - Sistema muestra juegos rankeados con scores
   - Usuario puede expandir explicaciones detalladas
   - Usuario puede dar feedback sobre juegos usados

3. **Explorar Catálogo** (`/games`)
   - Usuario puede buscar y filtrar juegos
   - Ver detalles completos de cada juego

4. **Ver Habilidades** (`/skills`)
   - Usuario puede explorar taxonomía de habilidades
   - Ver habilidades organizadas jerárquicamente

## ⚠️ Validaciones Implementadas

### Session Profile Form
- **Objetivos:** Mínimo 1 objetivo requerido
- **Habilidad primaria:** Requerida
- **Tiempo disponible:** 15-240 minutos
- **Tamaño de grupo:** 1-100 personas
- **Notas:** Máximo 500 caracteres

### Feedback Form
- **Was Used:** Campo requerido (checkbox)
- **Rating:** 1-5 estrellas (requerido)
- **Asesor:** Nombre requerido
- **Comentarios:** Máximo 500 caracteres cada uno

## 🐛 Troubleshooting

**Error: Cannot connect to backend**
- Verificar que el backend esté ejecutándose
- Verificar `VITE_API_BASE_URL` en `.env`
- Verificar configuración de CORS en backend

**Error: Module not found**
- Ejecutar `npm install`
- Limpiar caché: `rm -rf node_modules && npm install`

**Build fails**
- Verificar versión de Node.js (18+)
- Ejecutar `npm run build` para ver errores específicos

## 📝 Próximos Pasos

- [ ] Implementar autenticación (LoginPage)
- [ ] Agregar páginas de administración
- [ ] Implementar gestión de usuarios
- [ ] Agregar tests unitarios e integración
- [ ] Mejorar manejo de errores y loading states
- [ ] Implementar paginación en listas largas
- [ ] Agregar analytics y métricas

## 👥 Contribución

Este proyecto es parte del Sistema de Recomendación CJEI de la Pontificia Universidad Javeriana Cali.

## 📄 Licencia

Propiedad de la Pontificia Universidad Javeriana Cali - CJEI

---

**Última actualización:** Enero 2026  
**Estado:** MVP Funcional ✅  
**Módulos completados:** B, C (parcial), D (parcial), G (UI)
