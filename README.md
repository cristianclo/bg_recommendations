# 🎲 Sistema de Recomendación Inteligente de Juegos de Mesa

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema inteligente de recomendación de juegos de mesa para asesores pedagógicos del Centro de Juegos y Experiencias Interactivas (CJEI) de la Pontificia Universidad Javeriana Cali.

---

## 📚 Información Académica

**Trabajo de Grado** - Ingeniería de Sistemas y Computación  
**Pontificia Universidad Javeriana Cali**

- **Estudiante:** Cristian Carabalí
- **Director:** David Baldeón
- **Codirector:** Juan Carlos Martínez

---

## 🎯 Descripción del Proyecto

Este sistema proporciona recomendaciones inteligentes de juegos de mesa para asesores pedagógicos del CJEI, utilizando un motor de recomendación híbrido que combina filtrado colaborativo y basado en contenido. El sistema incluye explicabilidad de recomendaciones, sistema de feedback loop para mejora continua, y gestión completa del catálogo de juegos.

### ✨ Características Principales

- 🤖 **Motor de Recomendación Híbrido**: Combina múltiples técnicas para sugerencias precisas
- 📊 **Explicabilidad**: Justificación clara de cada recomendación
- 🔄 **Feedback Loop**: Mejora continua basada en retroalimentación de usuarios
- 📦 **Gestión de Catálogo**: Administración completa de juegos de mesa
- 👥 **Perfiles de Usuario**: Personalización basada en preferencias pedagógicas
- 📈 **Analytics**: Métricas y estadísticas de uso

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI**: Framework web moderno y rápido para Python
- **PostgreSQL**: Base de datos relacional robusta
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validación de datos

### Frontend
- **React**: Librería para interfaces de usuario
- **TypeScript**: JavaScript con tipado estático
- **Vite**: Build tool ultrarrápido
- **Material-UI (MUI)**: Componentes de UI modernos

### DevOps
- **Docker & Docker Compose**: Contenerización
- **Alembic**: Migraciones de base de datos

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker y Docker Compose (opcional)

### Instalación con Docker

```bash
# Clonar el repositorio
git clone https://github.com/cristianclo/bg_recommendations.git
cd bg_recommendations

# Iniciar servicios con Docker Compose
docker-compose up -d

# El backend estará disponible en http://localhost:8000
# El frontend estará disponible en http://localhost:3000
```

### Instalación Manual

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar servidor de desarrollo
npm run dev
```

---

## 📁 Estructura del Proyecto

```
bg_recommendations/
├── backend/                 # Aplicación FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints de la API
│   │   ├── core/           # Configuración y seguridad
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Esquemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   └── main.py         # Punto de entrada
│   ├── alembic/            # Migraciones de BD
│   ├── tests/              # Tests unitarios
│   └── requirements.txt    # Dependencias Python
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── pages/         # Páginas de la aplicación
│   │   ├── services/      # Llamadas a API
│   │   ├── hooks/         # Custom hooks
│   │   └── App.tsx        # Componente principal
│   ├── public/            # Archivos estáticos
│   └── package.json       # Dependencias Node.js
├── docker-compose.yml     # Orquestación de servicios
└── README.md             # Este archivo
```

---

## 🧠 Arquitectura del Motor de Recomendación

El sistema utiliza un enfoque híbrido que combina:

1. **Filtrado Colaborativo**: Basado en similitudes entre usuarios y sus valoraciones
2. **Filtrado Basado en Contenido**: Basado en características de los juegos (mecánicas, categorías, duración, etc.)
3. **Filtrado Basado en Conocimiento**: Reglas pedagógicas específicas del CJEI

### Explicabilidad

Cada recomendación incluye:
- Score de relevancia
- Razones pedagógicas
- Juegos similares considerados
- Factores de coincidencia

---

## 📊 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario

### Juegos
- `GET /api/games` - Listar juegos
- `GET /api/games/{id}` - Obtener detalle de juego
- `POST /api/games` - Crear juego (admin)
- `PUT /api/games/{id}` - Actualizar juego (admin)

### Recomendaciones
- `GET /api/recommendations` - Obtener recomendaciones personalizadas
- `POST /api/recommendations/feedback` - Enviar feedback

### Usuarios
- `GET /api/users/profile` - Perfil del usuario
- `PUT /api/users/profile` - Actualizar perfil

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

**Nota Académica**: Este proyecto es parte de un trabajo de grado para la Pontificia Universidad Javeriana Cali.

---

## 👥 Contribución

Este es un proyecto académico. Para consultas o sugerencias, contactar a los autores mencionados.

---

## 📧 Contacto

Para más información sobre el proyecto, contactar a:
- **Estudiante**: Cristian Carabalí
- **Institución**: Pontificia Universidad Javeriana Cali
- **Programa**: Ingeniería de Sistemas y Computación

---

**Desarrollado con ❤️ para el CJEI - Pontificia Universidad Javeriana Cali**
