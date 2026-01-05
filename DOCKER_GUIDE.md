# Guía de Docker - Sistema CJEI

Esta guía explica cómo usar Docker para ejecutar el Sistema de Recomendaciones de Juegos de Mesa del CJEI.

## Requisitos Previos

- Docker Desktop instalado ([Descargar](https://www.docker.com/products/docker-desktop))
- Docker Compose v3.8+ (incluido con Docker Desktop)

## Estructura de Archivos Docker

```
bg_recommendations/
├── docker-compose.yml           # Orquestación de servicios
├── .dockerignore               # Archivos a ignorar en el build
├── backend/
│   ├── Dockerfile              # Imagen del backend FastAPI
│   ├── .dockerignore           # Archivos a ignorar específicos del backend
│   └── .env.docker             # Variables de entorno para Docker
```

## Comandos Rápidos

### Iniciar el proyecto (primera vez)

```bash
# Construir imágenes y levantar servicios
docker-compose up --build

# O en modo detached (segundo plano)
docker-compose up --build -d
```

### Uso diario

```bash
# Iniciar servicios
docker-compose up

# Iniciar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f db

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra la base de datos)
docker-compose down -v
```

## Servicios Disponibles

### Backend FastAPI
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Container:** `cjei_backend`

### PostgreSQL Database
- **Host:** localhost
- **Puerto:** 5432
- **Usuario:** cjei
- **Password:** cjei
- **Base de datos:** cjei_recommendations
- **Container:** `cjei_db`

## Configuración

### Variables de Entorno

Las variables de entorno se configuran en `docker-compose.yml` o en `backend/.env.docker`.

**Para producción**, asegúrate de cambiar:
- `SECRET_KEY` - Genera una clave segura con `openssl rand -hex 32`
- Credenciales de la base de datos

### Hot Reload en Desarrollo

El docker-compose está configurado para desarrollo con hot reload:
- Los cambios en el código se reflejan automáticamente
- No necesitas reconstruir la imagen para cambios en el código Python

Si necesitas desactivar el hot reload:
```yaml
# En docker-compose.yml, cambia:
command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Gestión de la Base de Datos

### Aplicar Migraciones

```bash
# Ejecutar migraciones dentro del contenedor
docker-compose exec backend alembic upgrade head
```

### Crear una Nueva Migración

```bash
# Generar migración automáticamente
docker-compose exec backend alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar la migración
docker-compose exec backend alembic upgrade head
```

### Sembrar Datos de Prueba

```bash
docker-compose exec backend python -m scripts.seed_data
```

### Acceder a PostgreSQL

```bash
# Conectarse a la base de datos
docker-compose exec db psql -U cjei -d cjei_recommendations

# O desde tu máquina local (si tienes psql instalado)
psql -h localhost -U cjei -d cjei_recommendations
```

### Backup y Restore

```bash
# Crear backup
docker-compose exec db pg_dump -U cjei cjei_recommendations > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U cjei cjei_recommendations < backup.sql
```

## Comandos Útiles de Docker

### Inspeccionar Contenedores

```bash
# Listar contenedores activos
docker-compose ps

# Ver recursos utilizados
docker stats

# Acceder a una shell en el backend
docker-compose exec backend bash

# Acceder a una shell en la base de datos
docker-compose exec db bash
```

### Limpiar Recursos

```bash
# Eliminar contenedores detenidos, redes, volúmenes e imágenes sin usar
docker system prune -a --volumes

# Eliminar solo volúmenes no utilizados
docker volume prune
```

## Solución de Problemas

### El backend no puede conectarse a la base de datos

1. Verifica que el servicio `db` esté saludable:
   ```bash
   docker-compose ps
   ```

2. Revisa los logs de la base de datos:
   ```bash
   docker-compose logs db
   ```

3. Espera a que el healthcheck de PostgreSQL pase (puede tomar 10-20 segundos).

### Puerto ya en uso

Si el puerto 8000 o 5432 ya está en uso:

1. **Detener servicios locales:**
   ```bash
   # En macOS/Linux, encuentra el proceso
   lsof -ti:8000 | xargs kill -9
   lsof -ti:5432 | xargs kill -9
   ```

2. **O cambiar los puertos en docker-compose.yml:**
   ```yaml
   ports:
     - "8001:8000"  # Usar puerto 8001 en el host
   ```

### Reconstruir desde cero

Si algo está muy roto:

```bash
# Detener todo y eliminar volúmenes
docker-compose down -v

# Eliminar imágenes
docker-compose rm -f
docker rmi cjei_backend

# Reconstruir
docker-compose up --build
```

### Ver logs detallados

```bash
# Logs de todos los servicios
docker-compose logs -f --tail=100

# Solo errores
docker-compose logs -f | grep -i error
```

## Producción

Para desplegar en producción:

1. **Crear un docker-compose.prod.yml:**
   - Eliminar los volúmenes de código
   - Remover el flag `--reload`
   - Configurar variables de entorno seguras
   - Usar secretos de Docker

2. **Configurar un proxy reverso (Nginx/Traefik)**

3. **Usar certificados SSL/TLS**

4. **Configurar logging y monitoreo**

Ejemplo de comando para producción:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Desarrollo sin Docker

Si prefieres desarrollo local sin Docker, consulta el [README.md](README.md) para instrucciones de configuración manual.

## Referencias

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)

---

**Última actualización:** Enero 5, 2026
