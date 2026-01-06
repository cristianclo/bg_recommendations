# 🚀 Quick Start Guide - CJEI Frontend

Guía rápida para poner en marcha el frontend en menos de 5 minutos.

## ⚡ Setup Rápido

```bash
# 1. Clonar repositorio (si no lo has hecho)
cd bg_recommendations/frontend

# 2. Instalar dependencias
npm install

# 3. Configurar environment
cp .env.example .env
# Editar .env si tu backend está en otra URL

# 4. Iniciar servidor de desarrollo
npm run dev
```

**¡Listo!** Accede a http://localhost:5173

---

## 📋 Pre-requisitos

### Backend Running
El frontend necesita el backend ejecutándose:

```bash
# En otra terminal
cd bg_recommendations/backend
uvicorn app.main:app --reload

# Verifica que funcione:
curl http://localhost:8000/docs
```

### Base de Datos con Datos
Asegúrate de tener datos de prueba:

```bash
cd backend
python -m scripts.seed_data
```

---

## 🎯 Primera Prueba

### Test Completo del Flujo Principal

1. **Abre http://localhost:5173**
2. **Click en "Crear Nueva Consulta"**
3. **Llena el formulario:**
   - Objetivo: "Fomentar pensamiento crítico"
   - Habilidad primaria: Selecciona cualquiera
   - Tiempo: 60 minutos
   - Grupo: 8 personas
   - Idioma: Baja
4. **Click "Crear Sesión"**
5. **Verás recomendaciones rankeadas**
6. **Click "Ver Explicación" en cualquier juego**
7. **Click "Dar Feedback"** y llena el formulario

**Si todo funciona, ¡estás listo! ✅**

---

## 🔍 Verificación Rápida

### Checklist de 1 Minuto

- [ ] Frontend carga en http://localhost:5173
- [ ] Backend responde en http://localhost:8000/docs
- [ ] Página de inicio muestra hero section
- [ ] "Nueva Consulta" abre formulario
- [ ] Dropdown de habilidades carga
- [ ] Puedes crear una sesión
- [ ] Recomendaciones aparecen

**Si todo está ✅, el sistema funciona correctamente.**

---

## 🐛 Troubleshooting Express

### Error: Cannot connect to backend
```bash
# Verifica que el backend esté corriendo
curl http://localhost:8000/docs

# Si no responde, inicia el backend:
cd backend
uvicorn app.main:app --reload
```

### Error: Module not found
```bash
# Reinstala dependencias
rm -rf node_modules package-lock.json
npm install
```

### Error: Port already in use
```bash
# Cambia el puerto en vite.config.ts o mata el proceso:
lsof -ti:5173 | xargs kill
npm run dev
```

### Skills dropdown vacío
```bash
# Verifica que la BD tenga datos:
cd backend
python -m scripts.seed_data
```

---

## 📱 Navegación Rápida

### URLs Principales

- **Home:** http://localhost:5173/
- **Nueva Sesión:** http://localhost:5173/sessions/new
- **Catálogo:** http://localhost:5173/games
- **Habilidades:** http://localhost:5173/skills

### Backend API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 💡 Tips Útiles

### Hot Reload
- Los cambios en código se reflejan automáticamente
- Si algo falla, recarga la página (Cmd+R / Ctrl+R)

### DevTools
- Abre Chrome DevTools (F12)
- Pestaña **Network** para ver API calls
- Pestaña **Console** para ver errores

### Debugging
```typescript
// Agrega console.logs en el código:
console.log('Form data:', data);
console.log('API response:', response);
```

### React Query DevTools
- Están habilitadas en desarrollo
- Ver estado de queries en la esquina inferior izquierda

---

## 🎨 Modo de Desarrollo

### Build para Testing
```bash
# Build de producción
npm run build

# Preview del build
npm run preview
# Accede a http://localhost:4173
```

### Linting
```bash
# Ver problemas de código
npm run lint

# Auto-fix
npm run lint:fix
```

### Type Checking
```bash
# Verificar tipos sin compilar
npm run type-check
```

---

## 📚 Documentación Completa

Si necesitas más detalles:

1. **README_FRONTEND.md** - Overview completo
2. **TESTING_GUIDE.md** - Plan de testing detallado
3. **API_INTEGRATION.md** - Endpoints y ejemplos
4. **COMPONENTS_GUIDE.md** - Arquitectura de componentes
5. **EXECUTIVE_SUMMARY.md** - Resumen ejecutivo

---

## 🎓 Flujo de Usuario Típico

```
1. Inicio (/) 
   ↓
2. Click "Crear Nueva Consulta"
   ↓
3. Llenar formulario (/sessions/new)
   ↓
4. Ver advertencias (si existen)
   ↓
5. Confirmar y generar
   ↓
6. Ver recomendaciones (/recommendations/:id)
   ↓
7. Expandir explicación
   ↓
8. Dar feedback
   ↓
9. Explorar catálogo (/games)
```

---

## 🔧 Variables de Entorno

### .env
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_APP_NAME=CJEI Recommendations
```

**Nota:** Si cambias `.env`, reinicia el dev server.

---

## 🚀 Deploy (Opcional)

### Vercel
```bash
npm install -g vercel
vercel --prod
```

### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### Docker
```bash
docker build -t cjei-frontend .
docker run -p 3000:80 cjei-frontend
```

---

## 📞 Necesitas Ayuda?

1. **Revisa la consola del navegador** (F12)
2. **Revisa la terminal** donde corre `npm run dev`
3. **Verifica que el backend esté corriendo**
4. **Consulta TESTING_GUIDE.md** para tests específicos

---

## ✅ Checklist de Setup Completo

- [ ] Node.js 18+ instalado
- [ ] npm/yarn/pnpm disponible
- [ ] Backend ejecutándose (puerto 8000)
- [ ] Frontend ejecutándose (puerto 5173)
- [ ] Base de datos con datos de prueba
- [ ] .env configurado
- [ ] Primera sesión creada exitosamente

**Si todo está ✅, ¡felicidades! El sistema está operativo. 🎉**

---

**Tiempo estimado de setup:** 5-10 minutos  
**Dificultad:** Principiante  
**Última actualización:** Enero 2026
