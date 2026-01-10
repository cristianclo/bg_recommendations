# REQUERIMIENTOS FUNCIONALES
## Sistema de Recomendación de Juegos de Mesa - CJEI

---

## TABLA RESUMEN DE REQUERIMIENTOS

| Módulo | Código | Must | Should | Could | Total |
|--------|--------|------|--------|-------|-------|
| A - Ingesta y Normalización de Datos | ING | 2 | 1 | 0 | 3 |
| B - Caracterización de Contexto | CTX | 2 | 1 | 0 | 3 |
| C - Taxonomía de Habilidades | TAX | 3 | 1 | 1 | 5 |
| D - Motor de Recomendación | REC | 3 | 1 | 2 | 6 |
| E - Explicabilidad y Trazabilidad | EXP | 2 | 1 | 0 | 3 |
| F - Interfaz Web | UI | 3 | 3 | 0 | 6 |
| G - Retroalimentación y Conocimiento | RETRO | 2 | 1 | 2 | 5 |
| H - Administración | ADM | 2 | 0 | 1 | 3 |
| **TOTAL** | | **19** | **9** | **6** | **34** |

---

## MÓDULO A — INGESTA Y NORMALIZACIÓN DE DATOS

### RF-ING-01 | Must | Importación de catálogo base

**Descripción:** El sistema debe importar y almacenar el dataset de juegos de mesa con los atributos mínimos identificados: nombre, ID BGG, duración promedio, complejidad/dificultad, rango de jugadores (min-max), mecánicas, dependencia de idioma, ranking BGG, y disponibilidad en CJEI.

**Criterios de aceptación:**
- [ ] El sistema importa correctamente al menos el 95% de los juegos del catálogo CJEI
- [ ] Todos los atributos obligatorios (nombre, ID BGG, disponibilidad) están presentes en el 100% de registros importados
- [ ] Los juegos con atributos incompletos se marcan como "datos parciales" y no generan errores en el sistema
- [ ] Se genera un reporte de importación que indica: total importados, rechazados y advertencias

**Dependencias:** Ninguna (requisito base)

**Notas:** La fuente primaria es la API/archivos de BGG complementada con el inventario interno del CJEI. Este RF corresponde a la actividad 2 del Objetivo Específico 1.

---

### RF-ING-02 | Must | Normalización de atributos

**Descripción:** El sistema debe normalizar todos los atributos importados a escalas y formatos consistentes: duración en minutos (entero), complejidad en escala 1-5, rangos de jugadores validados, mecánicas en lista controlada, dependencia de idioma como enum (ninguna/baja/media/alta), ranking como entero, disponibilidad como booleano.

**Criterios de aceptación:**
- [ ] El 100% de los juegos válidos tienen duración expresada en minutos (rango: 5-360)
- [ ] El 100% de los juegos válidos tienen complejidad normalizada en escala 1.0-5.0
- [ ] Las mecánicas se normalizan contra un vocabulario controlado (mínimo 50 mecánicas estándar de BGG)
- [ ] Los valores fuera de rango o formato incorrecto se corrigen automáticamente o se marcan para revisión manual
- [ ] Se documenta el diccionario de datos con definición de cada escala/formato

**Dependencias:** RF-ING-01

**Notas:** Los criterios de normalización deben documentarse según la actividad 4 del Objetivo Específico 1. Se establecen valores por defecto para atributos ausentes (ej: duración=60, complejidad=2.5).

---

### RF-ING-03 | Should | Actualización incremental del catálogo

**Descripción:** El sistema debe permitir la actualización del catálogo mediante carga de archivos CSV/JSON sin modificar código, incluyendo validación de formato, detección de duplicados por ID BGG, y opciones de merge o reemplazo de datos existentes.

**Criterios de aceptación:**
- [ ] El sistema procesa archivos CSV y JSON con estructura predefinida
- [ ] Se detectan y reportan duplicados antes de importar (match por ID BGG)
- [ ] El usuario Admin puede elegir: (a) actualizar solo campos nuevos, (b) sobrescribir completo, o (c) rechazar duplicados
- [ ] Archivos con más del 20% de filas inválidas se rechazan completamente con reporte detallado de errores
- [ ] Se mantiene log de todas las actualizaciones (fecha, usuario, registros afectados)

**Dependencias:** RF-ING-01, RF-ING-02, RF-ADM-01

**Notas:** Facilita mantenimiento sin intervención técnica. Prioritario para escalabilidad post-MVP.

---

## MÓDULO B — CARACTERIZACIÓN DE CONTEXTO DE CLASE

### RF-CTX-01 | Must | Captura de perfil de sesión

**Descripción:** El sistema debe capturar el "perfil de sesión" mediante un formulario que incluya: objetivo(s) de clase (texto libre o selección múltiple), habilidad(es) a trabajar (primaria y opcionalmente secundaria), tiempo disponible en minutos, tamaño del grupo, restricción de idioma, preferencia de modalidad (competitivo/cooperativo/sin preferencia), y restricciones adicionales opcionales (ej: "reglas simples", "primera sesión").

**Criterios de aceptación:**
- [ ] El formulario valida que al menos 1 objetivo de clase y 1 habilidad primaria estén especificados
- [ ] El tiempo disponible debe estar entre 15-240 minutos
- [ ] El tamaño de grupo debe ser un número entero positivo (1-100)
- [ ] Todos los campos capturados se almacenan para trazabilidad (RF-EXP-02)
- [ ] El sistema guarda el perfil de sesión completo antes de generar recomendaciones

**Dependencias:** RF-TAX-01 (lista de habilidades disponibles)

**Notas:** Este RF implementa la caracterización definida en el Objetivo Específico 1, actividad 1. El objetivo de clase puede ser texto libre para flexibilidad, pero se sugiere complementar con categorías predefinidas.

---

### RF-CTX-02 | Must | Validación de coherencia operativa

**Descripción:** El sistema debe validar la coherencia entre los parámetros ingresados y emitir advertencias cuando detecte potenciales problemas operativos, especialmente en casos de grupos grandes (>20 personas) o tiempos muy limitados (<30 min), sugiriendo ajustes o modalidades alternativas.

**Criterios de aceptación:**
- [ ] Si el grupo es mayor a 20 personas, el sistema advierte y sugiere: (a) juegos escalables, (b) modalidad por estaciones/mesas múltiples, o (c) ajustar expectativas
- [ ] Si el tiempo disponible es menor a 30 minutos, el sistema advierte sobre limitaciones de mecánicas complejas
- [ ] Si se solicita modalidad cooperativa con grupo grande (>30), el sistema sugiere considerar dinámica por equipos
- [ ] Las advertencias no bloquean la consulta, pero se registran en el perfil de sesión
- [ ] El asesor puede confirmar o modificar parámetros después de ver advertencias

**Dependencias:** RF-CTX-01

**Notas:** Este RF mejora la usabilidad y previene recomendaciones operacionalmente inviables. Corresponde a conocimiento experto del CJEI.

---

### RF-CTX-03 | Should | Plantillas de sesión reutilizables

**Descripción:** El sistema debe permitir guardar "plantillas de sesión" con configuraciones frecuentes (ej: "Ética Empresarial - 20 estudiantes - 90 min - Toma de decisiones") para reutilización rápida por parte de los asesores.

**Criterios de aceptación:**
- [ ] El asesor puede guardar un perfil de sesión como plantilla con nombre personalizado
- [ ] El sistema almacena mínimo 10 plantillas por usuario
- [ ] Al cargar una plantilla, todos los campos del formulario se pre-llenan
- [ ] El asesor puede modificar cualquier campo después de cargar la plantilla
- [ ] Las plantillas se pueden editar y eliminar

**Dependencias:** RF-CTX-01

**Notas:** Mejora significativamente la eficiencia para sesiones recurrentes. Implementación post-MVP.

---

## MÓDULO C — TAXONOMÍA DE HABILIDADES Y MAPEO

### RF-TAX-01 | Must | Gestión de taxonomía de habilidades

**Descripción:** El sistema debe gestionar una taxonomía de habilidades educativas con sus definiciones, categorías y ejemplos. Cada habilidad debe incluir: nombre, definición, categoría (ej: cognitiva, social, emocional), ejemplos de mecánicas asociadas, y contextos de aplicación típicos.

**Criterios de aceptación:**
- [ ] La taxonomía inicial incluye al menos 15 habilidades identificadas en la revisión de literatura (actividad 1, Objetivo Específico 2)
- [ ] Cada habilidad tiene definición clara (50-200 palabras) y al menos 2 ejemplos de mecánicas asociadas
- [ ] Las habilidades se organizan en mínimo 3 categorías (ej: cognitivas, sociales, emocionales)
- [ ] La taxonomía es editable por usuarios Admin
- [ ] El sistema valida que no haya nombres de habilidades duplicados

**Dependencias:** Ninguna (pero se construye según actividades 1-2 del Objetivo Específico 2)

**Notas:** La taxonomía es resultado de sesiones con asesores pedagógicos. Debe documentarse formalmente según actividad 3 del Objetivo Específico 2.

---

### RF-TAX-02 | Must | Asignación manual de habilidades a juegos

**Descripción:** El sistema debe permitir asignar manualmente a cada juego una habilidad primaria (obligatoria) y una habilidad secundaria (opcional), con justificación o notas sobre la asignación. Esta asignación puede realizarse por usuarios Admin o por asesores con permisos especiales.

**Criterios de aceptación:**
- [ ] Cada juego del catálogo puede tener asignada 1 habilidad primaria (obligatoria)
- [ ] Cada juego puede tener 0 o 1 habilidad secundaria
- [ ] El sistema permite agregar notas explicativas sobre por qué se asignó cada habilidad (texto libre, máx 500 caracteres)
- [ ] Se registra quién realizó la asignación y cuándo (auditoría)
- [ ] El sistema muestra advertencia si un juego no tiene habilidad primaria asignada

**Dependencias:** RF-TAX-01, RF-ING-01

**Notas:** Corresponde a la actividad 4 del Objetivo Específico 2. En MVP la asignación es completamente manual. RF-TAX-04 (NLP) complementa pero no reemplaza este proceso.

---

### RF-TAX-03 | Must | Documentación de criterios de asignación

**Descripción:** El sistema debe mantener documentación estructurada de los criterios y reglas pedagógicas utilizados para asignar habilidades a juegos, incluyendo casos de ejemplo y decisiones tomadas durante las sesiones de validación con asesores.

**Criterios de aceptación:**
- [ ] Existe un documento/sección en el sistema que describe los criterios de asignación de habilidades
- [ ] Se documentan al menos 10 casos de ejemplo (juego → habilidad con justificación)
- [ ] Se registran las decisiones tomadas en sesiones de validación con asesores (fechas, participantes, conclusiones)
- [ ] El documento es accesible desde la interfaz de administración
- [ ] El documento se actualiza cada vez que se modifican criterios o taxonomía

**Dependencias:** RF-TAX-01, RF-TAX-02

**Notas:** Esencial para preservación del conocimiento institucional y transferencia a nuevos asesores. Corresponde a actividad 3 del Objetivo Específico 2 y documentación del modelo de datos.

---

### RF-TAX-04 | Should | Asistencia NLP para sugerencia de habilidades

**Descripción:** El sistema debe analizar la descripción del juego y sus mecánicas mediante técnicas de NLP para sugerir hasta 3 habilidades candidatas con score de confianza. El asesor o Admin debe revisar y confirmar/modificar la asignación final.

**Criterios de aceptación:**
- [ ] El sistema procesa la descripción textual del juego (de BGG) y lista de mecánicas
- [ ] Se generan hasta 3 sugerencias de habilidades ordenadas por score de confianza (0.0-1.0)
- [ ] Las sugerencias con score >0.6 se marcan como "alta confianza"
- [ ] La sugerencia NLP nunca es definitiva; el usuario debe confirmar o elegir otra habilidad
- [ ] Se registra si la asignación final coincidió con la sugerencia NLP (métrica de calidad del modelo)
- [ ] En conjunto de validación (mínimo 50 juegos), las sugerencias coinciden con criterio experto en al menos 50% de los casos

**Dependencias:** RF-TAX-01, RF-TAX-02, RF-ING-01

**Notas:** Implementa el modelado de habilidades mediante NLP mencionado en el Objetivo Específico 4. Requiere entrenamiento/ajuste con conjunto de juegos ya etiquetados. Prioridad reducida a Should porque el MVP funciona con asignación manual.

---

### RF-TAX-05 | Could | Análisis de co-ocurrencias de habilidades

**Descripción:** El sistema debe analizar patrones de habilidades frecuentemente trabajadas juntas (primaria+secundaria) y sugerir combinaciones coherentes basadas en el uso histórico y feedback de asesores.

**Criterios de aceptación:**
- [ ] El sistema identifica las 10 combinaciones más frecuentes de habilidad primaria-secundaria
- [ ] Al asignar una habilidad primaria, el sistema sugiere habilidades secundarias comúnmente asociadas
- [ ] Los patrones se actualizan automáticamente cada vez que se registra nuevo feedback
- [ ] Se visualiza en dashboard para asesores (ej: "80% de juegos con pensamiento crítico también trabajan resolución de problemas")

**Dependencias:** RF-TAX-02, RF-RETRO-01

**Notas:** Funcionalidad analítica avanzada. Implementación post-MVP.

---

## MÓDULO D — MOTOR DE RECOMENDACIÓN HÍBRIDO

### RF-REC-01 | Must | Generación de recomendaciones Top-N

**Descripción:** El sistema debe generar una lista rankeada de Top-N recomendaciones (configurable, por defecto N=10) aplicando filtros duros (disponibilidad, jugadores, tiempo, idioma), scoring por contenido (similitud de mecánicas, dificultad, habilidades), y reglas pedagógicas validadas con asesores del CJEI.

**Criterios de aceptación:**
- [ ] El sistema devuelve al menos 3 recomendaciones válidas en el 85% de consultas en dataset de prueba
- [ ] Si no hay suficientes juegos que cumplan filtros duros, el sistema muestra mensaje explicativo indicando qué restricciones no se pudieron satisfacer
- [ ] Los filtros duros se aplican en orden: disponibilidad → jugadores → tiempo → idioma
- [ ] El scoring combina: similitud de habilidad (40%), adecuación de mecánicas (30%), dificultad apropiada (20%), ranking BGG (10%) (pesos configurables)
- [ ] Las recomendaciones se ordenan por score total descendente
- [ ] El tiempo de generación es <5 segundos para el 95% de consultas

**Dependencias:** RF-ING-01, RF-ING-02, RF-CTX-01, RF-TAX-02

**Notas:** Núcleo del sistema. Implementa filtrado basado en contenido + reglas pedagógicas (Objetivo Específico 4). El algoritmo debe documentarse formalmente.

---

### RF-REC-02 | Must | Configuración de pesos del scoring

**Descripción:** El sistema debe permitir a usuarios Admin ajustar los pesos de los componentes del scoring (habilidad, mecánicas, dificultad, ranking) mediante una interfaz simple de administración, para priorizar diferentes criterios según evolucione el conocimiento pedagógico del CJEI.

**Criterios de aceptación:**
- [ ] Existe interfaz de administración con sliders o campos numéricos para ajustar 4 pesos
- [ ] La suma de los pesos debe ser 100% (el sistema normaliza automáticamente)
- [ ] Los cambios de pesos se aplican inmediatamente a nuevas consultas
- [ ] Se mantiene historial de configuraciones de pesos (fecha, usuario, valores)
- [ ] Existe configuración "por defecto" restaurable

**Dependencias:** RF-REC-01, RF-ADM-01

**Notas:** Permite iteración y ajuste fino sin modificar código. Los pesos iniciales se establecen en conjunto con asesores durante el diseño (Objetivo Específico 3).

---

### RF-REC-03 | Must | Manejo de restricciones no satisfechas

**Descripción:** El sistema debe detectar cuando no existan juegos disponibles que cumplan todos los filtros duros y debe sugerir de forma inteligente qué restricciones podrían relajarse, priorizando mantener las más críticas (disponibilidad, habilidad) y relajar las operativas (tiempo, jugadores).

**Criterios de aceptación:**
- [ ] Si no hay resultados, el sistema identifica qué filtro(s) causaron la exclusión total
- [ ] Se genera mensaje específico: "No hay juegos disponibles para 40 jugadores en 45 minutos con habilidad X. Sugerencias: (a) extender tiempo a 90 min, (b) considerar modalidad por estaciones"
- [ ] El sistema ofrece botón "Relajar restricción automáticamente" que aplica el cambio más razonable
- [ ] Se priorizan sugerencias en orden: modificar tiempo → modificar rango de jugadores → considerar juegos similares de habilidad secundaria → relajar dependencia de idioma
- [ ] Nunca se relaja automáticamente la disponibilidad (juego debe estar físicamente en CJEI)

**Dependencias:** RF-REC-01, RF-CTX-02

**Notas:** Mejora dramáticamente la experiencia cuando las restricciones son muy estrictas. Usa conocimiento experto de qué restricciones son negociables.

---

### RF-REC-04 | Should | Priorización por feedback histórico

**Descripción:** El sistema debe utilizar el feedback histórico de utilidad (RF-RETRO-01) para ajustar el ranking de recomendaciones, dando boost a juegos que han funcionado bien en contextos similares (misma habilidad, rango de tiempo, tamaño de grupo similar).

**Criterios de aceptación:**
- [ ] Juegos con promedio de utilidad >4.0 en contextos similares reciben +10% en score final
- [ ] "Contexto similar" se define como: misma habilidad primaria Y (tiempo ±30min O tamaño grupo ±5 personas)
- [ ] Juegos sin feedback se tratan neutralmente (sin penalización)
- [ ] El boost se activa solo si hay mínimo 3 registros de feedback para ese juego
- [ ] Se documenta en la explicación (RF-EXP-01) cuando un juego fue boosted por feedback positivo

**Dependencias:** RF-REC-01, RF-RETRO-01

**Notas:** Implementa el aprendizaje del sistema a partir de uso real. Prioridad Should porque requiere acumular feedback inicial. Corresponde a "retroalimentación de uso" en Objetivo Específico 4.

---

### RF-REC-05 | Could | Recomendación por juego semilla

**Descripción:** El sistema debe permitir recomendar juegos similares a un "juego semilla" específico (ej: "Quiero juegos similares a Catan"), útil cuando un asesor sabe que un juego funcionó bien y busca alternativas con mecánicas/habilidades parecidas.

**Criterios de aceptación:**
- [ ] El asesor puede seleccionar un juego del catálogo como referencia
- [ ] El sistema genera Top-10 juegos más similares según: mecánicas compartidas (50%), misma habilidad primaria (30%), dificultad similar ±0.5 (20%)
- [ ] Los juegos recomendados deben estar disponibles en CJEI
- [ ] Se puede combinar con filtros adicionales (tiempo, jugadores)
- [ ] La lista incluye score de similitud (0-100%) para cada recomendación

**Dependencias:** RF-REC-01, RF-ING-02

**Notas:** Funcionalidad de "búsqueda por similitud" tipo content-based puro. Útil para diversificar uso del catálogo. Implementación post-MVP.

---

### RF-REC-06 | Could | Favoritos y exclusiones por asesor

**Descripción:** El sistema debe permitir a cada asesor marcar juegos como "favoritos" (prioritarios en futuras recomendaciones) o "no recomendables para mí" (excluidos de sus recomendaciones), creando perfiles personalizados que coexistan con las reglas generales del sistema.

**Criterios de aceptación:**
- [ ] Cada asesor puede marcar hasta 20 juegos como favoritos
- [ ] Los juegos favoritos reciben +15% en score cuando ese asesor hace consultas
- [ ] Cada asesor puede marcar juegos como "no recomendar" sin límite
- [ ] Los juegos marcados así se excluyen automáticamente de recomendaciones de ese asesor (pero siguen disponibles para otros)
- [ ] El asesor puede revertir estas marcas en cualquier momento

**Dependencias:** RF-REC-01, RF-UI-01 (autenticación de usuario)

**Notas:** Personalización avanzada. Útil cuando asesores tienen experiencias muy positivas/negativas específicas. Post-MVP.

---

## MÓDULO E — EXPLICABILIDAD Y TRAZABILIDAD

### RF-EXP-01 | Must | Explicación de recomendaciones

**Descripción:** Cada juego recomendado debe incluir una explicación textual clara y estructurada que indique por qué fue sugerido, citando específicamente: coincidencia de habilidad, cumplimiento de restricciones operativas, mecánicas relevantes, y cualquier factor de boost aplicado.

**Criterios de aceptación:**
- [ ] La explicación incluye mínimo 3 razones de selección específicas
- [ ] Se citan explícitamente: habilidad primaria coincidente, rango de jugadores y tiempo cumplidos, y al menos 1 mecánica relevante
- [ ] Si se aplicó boost por feedback, se menciona: "Recomendado altamente por asesores en contextos similares (utilidad promedio: 4.5/5)"
- [ ] Si la dificultad está en el límite de lo apropiado, se incluye nota: "Advertencia: complejidad alta, considerar grupo experimentado"
- [ ] La explicación es legible en lenguaje natural (no códigos técnicos)
- [ ] Máximo 200 palabras por explicación

**Dependencias:** RF-REC-01

**Notas:** Esencial para transparencia y confianza del asesor. Permite entender la lógica del sistema y tomar decisiones informadas. Corresponde a "trazabilidad de criterios de selección" en Objetivo Específico 3.

---

### RF-EXP-02 | Must | Registro de trazabilidad completa

**Descripción:** El sistema debe almacenar permanentemente el "rastro de decisión" completo de cada consulta realizada, incluyendo: perfil de sesión ingresado, timestamp, usuario, lista de recomendaciones generadas con sus scores, explicaciones, y configuración de pesos vigente en ese momento.

**Criterios de aceptación:**
- [ ] Cada consulta genera un registro único con ID secuencial
- [ ] Se almacenan todos los parámetros del perfil de sesión (RF-CTX-01)
- [ ] Se guardan las Top-10 recomendaciones con sus scores individuales y explicaciones completas
- [ ] Se registra la configuración de pesos del motor vigente al momento de la consulta
- [ ] Se almacena timestamp (fecha/hora) y usuario que realizó la consulta
- [ ] El sistema mantiene historial de al menos las últimas 1000 consultas (configurable)
- [ ] Los registros no son editables (solo lectura para auditoría)

**Dependencias:** RF-CTX-01, RF-REC-01, RF-EXP-01

**Notas:** Crítico para evaluación del sistema, auditoría, y posibles ajustes futuros. Permite responder "¿por qué recomendamos X en la clase de Y hace 3 meses?". Relacionado con preservación de conocimiento institucional (Objetivo General).

---

### RF-EXP-03 | Should | Visualización de rastros históricos

**Descripción:** El sistema debe permitir a usuarios Admin y asesores consultar el historial de recomendaciones pasadas, con filtros por fecha, asesor, habilidad o juego recomendado, para análisis y aprendizaje organizacional.

**Criterios de aceptación:**
- [ ] Interfaz de "Historial" accesible desde menú principal
- [ ] Filtros disponibles: rango de fechas, asesor, habilidad primaria, juego específico
- [ ] Cada registro del historial muestra resumen: fecha, asesor, objetivo de clase, habilidades, juegos recomendados (Top 3)
- [ ] Al hacer clic en un registro se despliega el detalle completo (perfil de sesión + todas las recomendaciones + explicaciones)
- [ ] Opción de exportar resultados filtrados a CSV
- [ ] La consulta de historial no afecta el rendimiento del motor de recomendación

**Dependencias:** RF-EXP-02, RF-ADM-01

**Notas:** Facilita meta-análisis y mejora continua. Permite identificar patrones de uso y oportunidades de optimización. Implementación prioritaria post-MVP.

---

## MÓDULO F — INTERFAZ WEB PARA ASESORES

### RF-UI-01 | Must | Autenticación y roles de usuario

**Descripción:** El sistema debe implementar autenticación básica de usuarios con dos roles: "Asesor" (puede crear consultas y dar feedback) y "Admin" (puede además gestionar catálogo, taxonomía y configuraciones).

**Criterios de aceptación:**
- [ ] Sistema de login con usuario y contraseña
- [ ] Las sesiones expiran después de 2 horas de inactividad
- [ ] Los asesores solo pueden acceder a: crear consultas, ver recomendaciones, dar feedback, ver su historial
- [ ] Los Admin pueden acceder a todas las funciones del sistema
- [ ] Las contraseñas se almacenan encriptadas (bcrypt o similar)
- [ ] Existe función "recuperar contraseña" básica

**Dependencias:** Ninguna (requisito base para UI)

**Notas:** Seguridad básica necesaria para preservación de conocimiento institucional y auditoría. Relacionado con requerimiento no funcional de seguridad.

---

### RF-UI-02 | Must | Pantalla de creación de consulta

**Descripción:** El sistema debe proveer una interfaz web intuitiva para que los asesores ingresen el perfil de sesión (RF-CTX-01) mediante formulario con validaciones en tiempo real, y generen recomendaciones con un solo clic.

**Criterios de aceptación:**
- [ ] Formulario implementa todos los campos de RF-CTX-01
- [ ] Validaciones en tiempo real (ej: tiempo entre 15-240 min, grupo >0)
- [ ] Campos obligatorios marcados claramente con asterisco
- [ ] Ayudas contextuales (tooltips) en cada campo explicando qué ingresar
- [ ] Botón "Generar Recomendaciones" visible y destacado
- [ ] Al enviar, se muestra indicador de carga mientras el motor procesa
- [ ] Mensajes de error claros si faltan campos obligatorios
- [ ] Opción de cargar plantilla guardada (RF-CTX-03)

**Dependencias:** RF-UI-01, RF-CTX-01

**Notas:** Interfaz principal del sistema. Debe ser simple, rápida y sin fricción. Priorizar usabilidad sobre estética en MVP. Corresponde al diseño de interfaz mencionado en Objetivo Específico 3, actividad 4.

---

### RF-UI-03 | Must | Visualización de recomendaciones rankeadas

**Descripción:** El sistema debe mostrar la lista de recomendaciones en formato de tarjetas ordenadas por ranking, con información clave visible (nombre, imagen, habilidades, jugadores, tiempo, score) y acceso a detalle completo al hacer clic.

**Criterios de aceptación:**
- [ ] Las recomendaciones se muestran en lista ordenada del #1 al #N
- [ ] Cada tarjeta incluye: posición en ranking, nombre del juego, imagen (si disponible), habilidad primaria, rango de jugadores, duración, score de recomendación (0-100)
- [ ] Indicadores visuales de advertencias (ej: ícono si requiere explicación compleja de reglas)
- [ ] Al hacer clic en una tarjeta se abre vista detallada (RF-UI-04)
- [ ] Botón "Dar Feedback" visible en cada tarjeta
- [ ] Si no hay resultados, se muestra mensaje de RF-REC-03
- [ ] Tiempo de carga de resultados <3 segundos

**Dependencias:** RF-UI-02, RF-REC-01

**Notas:** Visualización debe ser escaneable rápidamente. Asesores suelen revisar Top 3-5. Usar principios de diseño de información. Relacionado con identidad visual CJEI (Objetivo Específico 3).

---

### RF-UI-04 | Should | Vista detallada del juego

**Descripción:** El sistema debe proveer una vista de detalle completa para cada juego recomendado, mostrando todos sus atributos normalizados, la explicación de por qué fue recomendado (RF-EXP-01), habilidades asignadas, mecánicas, advertencias operativas, y feedback histórico si existe.

**Criterios de aceptación:**
- [ ] La vista detalle muestra: nombre, imagen ampliada, descripción completa, ID BGG con enlace externo, duración, complejidad, jugadores (min-max), mecánicas, dependencia de idioma, ranking BGG, disponibilidad en CJEI
- [ ] Se muestra la explicación completa de por qué fue recomendado (RF-EXP-01)
- [ ] Se muestran las habilidades primaria y secundaria con sus definiciones
- [ ] Se incluye sección de "Consideraciones Operativas" con advertencias si aplican (ej: "Requiere mesa grande", "Primera partida toma más tiempo")
- [ ] Si el juego tiene feedback histórico, se muestra resumen: utilidad promedio (X/5), número de usos registrados, comentarios destacados
- [ ] Botón prominente "Dar Feedback sobre este juego"
- [ ] Opción de "Compartir" (generar enlace a esta recomendación específica)

**Dependencias:** RF-UI-03, RF-REC-01, RF-EXP-01, RF-RETRO-01

**Notas:** Provee toda la información necesaria para que el asesor tome decisión informada. Prioridad Should porque en MVP puede funcionar con vista resumida en tarjetas.

---

### RF-UI-05 | Should | Búsqueda y filtros rápidos

**Descripción:** El sistema debe permitir búsqueda directa por nombre de juego, mecánica o habilidad, y aplicar filtros rápidos (duración, jugadores, complejidad) sin pasar por el formulario completo de consulta, para usuarios que ya conocen parte de lo que buscan.

**Criterios de aceptación:**
- [ ] Barra de búsqueda siempre visible en navegación superior
- [ ] La búsqueda funciona sobre: nombre del juego, mecánicas, habilidades (búsqueda fuzzy con tolerancia a errores)
- [ ] Filtros laterales o superiores para: rango de duración (slider), rango de jugadores (slider), complejidad (1-5), disponibilidad (solo disponibles/todos)
- [ ] Los resultados se actualizan en tiempo real al ajustar filtros
- [ ] Se muestra contador de "X juegos encontrados"
- [ ] Opción de "Limpiar todos los filtros"
- [ ] Los resultados de búsqueda muestran tarjetas similares a RF-UI-03

**Dependencias:** RF-UI-01, RF-ING-02

**Notas:** Complementa el flujo principal de recomendación. Útil para asesores experimentados que buscan juego específico. Implementación post-MVP.

---

### RF-UI-06 | Should | Identidad visual CJEI

**Descripción:** El sistema debe implementar lineamientos básicos de identidad visual alineados con la marca del CJEI, incluyendo logo oficial, paleta de colores institucional, tipografía consistente, y elementos gráficos que reflejen la naturaleza lúdica del centro.

**Criterios de aceptación:**
- [ ] Logo del CJEI visible en encabezado de todas las páginas
- [ ] Uso de paleta de colores institucional del CJEI (si existe documentada)
- [ ] Tipografía consistente en todo el sistema
- [ ] Elementos gráficos (íconos, ilustraciones) alineados con estética lúdica/educativa
- [ ] Diseño responsivo básico (funcional en desktop y tablet, mínimo)
- [ ] Accesibilidad: contraste de colores WCAG AA, textos legibles (mínimo 14px)

**Dependencias:** RF-UI-01

**Notas:** Diseño debe coordinarse con equipo del CJEI. Objetivo Específico 3, actividad 4 menciona "identidad visual acorde al CJEI". Prioridad Should porque funcionalidad prima sobre estética en MVP, pero es importante para adopción institucional.

---

## MÓDULO G — RETROALIMENTACIÓN Y PRESERVACIÓN DE CONOCIMIENTO

### RF-RETRO-01 | Must | Registro de feedback post-sesión

**Descripción:** El sistema debe permitir a los asesores registrar feedback sobre juegos recomendados que efectivamente usaron en clase, capturando: calificación de utilidad (escala 1-5), si se usó o no el juego, qué funcionó bien, qué no funcionó, habilidad realmente trabajada, y notas cualitativas adicionales.

**Criterios de aceptación:**
- [ ] Formulario de feedback accesible desde: (a) tarjeta de recomendación, (b) vista detalle de juego, (c) historial de consultas
- [ ] Campos obligatorios: juego (pre-llenado), se usó (sí/no), calificación de utilidad (1-5 estrellas)
- [ ] Campos opcionales: habilidad realmente trabajada (puede diferir de la asignada), qué funcionó bien (texto libre, máx 500 caracteres), qué no funcionó (texto libre, máx 500 caracteres), notas adicionales (texto libre, máx 500 caracteres)
- [ ] El feedback se asocia automáticamente a: juego, asesor, fecha, perfil de sesión original (si viene de consulta específica)
- [ ] Se genera confirmación visual al guardar: "¡Gracias! Tu feedback ayuda a mejorar las recomendaciones"
- [ ] El feedback se puede editar hasta 7 días después de creado

**Dependencias:** RF-UI-03, RF-EXP-02

**Notas:** Núcleo de la preservación de conocimiento institucional. Objetivo Específico 5, actividad 1. El feedback alimenta RF-REC-04 (priorización) y RF-RETRO-03 (análisis).

---

### RF-RETRO-02 | Must | Visualización de feedback histórico

**Descripción:** El sistema debe mostrar el feedback histórico acumulado de cada juego en su vista detallada, incluyendo estadísticas agregadas (utilidad promedio, número de usos, distribución de calificaciones) y comentarios cualitativos destacados.

**Criterios de aceptación:**
- [ ] En la vista detalle de cada juego (RF-UI-04) se muestra sección "Experiencias de Uso"
- [ ] Estadísticas visibles: utilidad promedio (X.X/5.0), número total de veces usado, distribución de calificaciones (ej: 60% 5 estrellas, 30% 4 estrellas, 10% 3 estrellas)
- [ ] Se muestran hasta 3 comentarios cualitativos más útiles/recientes (votos de utilidad si se implementa RF-RETRO-05)
- [ ] Si hay discrepancias entre habilidad asignada y reportada por asesores, se muestra advertencia: "Nota: Algunos asesores reportan que trabaja principalmente [habilidad Y]"
- [ ] Si el juego nunca se ha usado, se indica: "Este juego aún no tiene feedback de uso en el CJEI"

**Dependencias:** RF-RETRO-01, RF-UI-04

**Notas:** Transparencia del conocimiento acumulado. Ayuda a asesores nuevos a aprender de experiencias de colegas. Relacionado con meta de preservación de conocimiento institucional (Objetivo General).

---

### RF-RETRO-03 | Should | Análisis de patrones de uso

**Descripción:** El sistema debe generar reportes analíticos sobre patrones de uso del catálogo, identificando: juegos más/menos utilizados, habilidades más trabajadas, contextos de uso frecuentes, y brechas (juegos subutilizados con buen ranking).

**Criterios de aceptación:**
- [ ] Dashboard de "Analíticas de Uso" accesible para Admins y opcionalmente para asesores
- [ ] Visualizaciones incluyen: Top 10 juegos más usados (con número de sesiones), distribución de uso por habilidad (gráfico de barras), contextos frecuentes (ej: "60% de sesiones son 15-30 estudiantes, 90 min")
- [ ] Identificación de "joyas ocultas": juegos con alta utilidad promedio (>4.5) pero menos de 5 usos totales
- [ ] Identificación de "candidatos a revisión": juegos con baja utilidad (<3.0) en múltiples usos
- [ ] Rango de fechas configurable para análisis
- [ ] Opción de exportar reporte a PDF

**Dependencias:** RF-RETRO-01, RF-EXP-02

**Notas:** Apoya toma de decisiones sobre adquisiciones, retiro de juegos, y ajustes de taxonomía. Objetivo Específico 5, actividad 4 (análisis de información). Implementación post-MVP.

---

### RF-RETRO-04 | Could | Exportación de reportes de uso

**Descripción:** El sistema debe permitir exportar reportes personalizados de uso del catálogo en formato CSV y PDF, con filtros por período, asesor, habilidad o juego, para documentación y presentación a stakeholders.

**Criterios de aceptación:**
- [ ] Interfaz de "Generar Reporte" con opciones de filtro: rango de fechas, asesor(es), habilidad(es), juego(s)
- [ ] Formatos de exportación: CSV (datos tabulares) y PDF (reporte visual con gráficos)
- [ ] El reporte CSV incluye todos los campos de feedback sin resumen
- [ ] El reporte PDF incluye: resumen ejecutivo, estadísticas clave, gráficos de distribución, comentarios cualitativos destacados
- [ ] Generación de reporte toma <30 segundos para datasets de hasta 1000 registros
- [ ] Los reportes generados incluyen timestamp y usuario que los generó

**Dependencias:** RF-RETRO-03, RF-ADM-01

**Notas:** Útil para memoria anual del CJEI, presentaciones a facultades, y documentación de impacto. Post-MVP.

---

### RF-RETRO-05 | Could | Sistema de votos en comentarios

**Descripción:** El sistema debe permitir que los asesores marquen comentarios de feedback de otros asesores como "útiles" o "no útiles", para priorizar los comentarios más valiosos en la visualización de feedback histórico.

**Criterios de aceptación:**
- [ ] Cada comentario de feedback muestra botones "👍 Útil" y "👎 No útil"
- [ ] Se muestra contador de votos útiles netos (útiles - no útiles)
- [ ] Los comentarios se ordenan por votos útiles descendente en RF-RETRO-02
- [ ] Un asesor puede votar una sola vez por comentario (puede cambiar su voto)
- [ ] El autor del comentario no puede votar su propio comentario

**Dependencias:** RF-RETRO-01, RF-RETRO-02

**Notas:** Crowdsourcing de calidad de feedback. Mejora la utilidad de comentarios cualitativos. Post-MVP.

---

## MÓDULO H — ADMINISTRACIÓN DEL SISTEMA

### RF-ADM-01 | Must | Gestión de catálogo de juegos

**Descripción:** El sistema debe permitir a usuarios Admin realizar operaciones CRUD (crear, leer, actualizar, eliminar) sobre el catálogo de juegos, incluyendo carga masiva por archivo (RF-ING-03) y edición individual de atributos.

**Criterios de aceptación:**
- [ ] Interfaz de "Gestión de Catálogo" con lista completa de juegos (paginada, 50 por página)
- [ ] Funciones: agregar juego individual (formulario), editar juego existente, eliminar juego (con confirmación), marcar disponibilidad
- [ ] Búsqueda y filtros para localizar juegos rápidamente
- [ ] Carga masiva mediante archivo CSV/JSON (RF-ING-03)
- [ ] Cada operación requiere confirmación para cambios destructivos (eliminar, sobrescribir)
- [ ] Log de auditoría: quién modificó qué y cuándo

**Dependencias:** RF-ING-01, RF-ING-02, RF-ING-03

**Notas:** Esencial para mantenimiento del sistema. Relacionado con actividades 2-3 del Objetivo Específico 1 (extracción y normalización de datos).

---

### RF-ADM-02 | Must | Gestión de taxonomía

**Descripción:** El sistema debe permitir a usuarios Admin realizar operaciones CRUD sobre la taxonomía de habilidades, incluyendo agregar nuevas habilidades, editar definiciones, reorganizar categorías, y eliminar habilidades (solo si no están asignadas a juegos).

**Criterios de aceptación:**
- [ ] Interfaz de "Gestión de Taxonomía" con vista de árbol o lista de habilidades por categoría
- [ ] Funciones: agregar habilidad (nombre, definición, categoría, ejemplos), editar habilidad, eliminar habilidad (validación: no debe estar asignada a juegos activos)
- [ ] Reorganizar habilidades entre categorías (drag-and-drop o dropdown)
- [ ] Previsualización de impacto al eliminar: "Esta habilidad está asignada a 12 juegos. Reasigna primero"
- [ ] Versionado de taxonomía: se guarda snapshot al hacer cambios significativos
- [ ] Exportación de taxonomía completa a JSON o PDF para documentación

**Dependencias:** RF-TAX-01

**Notas:** Permite evolución de la taxonomía conforme el CJEI refina su comprensión pedagógica. Relacionado con actividades 2-3 del Objetivo Específico 2 (elaboración y validación de taxonomía).

---

### RF-ADM-03 | Could | Gestión de usuarios

**Descripción:** El sistema debe permitir a usuarios Admin gestionar cuentas de usuarios (asesores y otros admins), incluyendo crear, editar, desactivar y asignar roles.

**Criterios de aceptación:**
- [ ] Interfaz de "Gestión de Usuarios" con lista completa (nombre, email, rol, estado activo/inactivo)
- [ ] Funciones: crear usuario (email, nombre, rol inicial, contraseña temporal), editar información, cambiar rol, desactivar/reactivar cuenta
- [ ] Al crear usuario, se envía email con credenciales temporales (si sistema de email está configurado, sino se muestra en pantalla)
- [ ] Validación: no se puede eliminar el último usuario Admin activo
- [ ] Log de auditoría de cambios en usuarios

**Dependencias:** RF-UI-01

**Notas:** Importante para escalabilidad del sistema conforme el CJEI crece. Prioridad Could porque en MVP puede manejarse manualmente por BD o script. Post-MVP.

---

## MATRIZ DE TRAZABILIDAD: REQUERIMIENTOS FUNCIONALES → OBJETIVOS ESPECÍFICOS

| RF ID | Nombre Corto | Objetivo(s) Específico(s) | Actividad(es) Relacionada(s) |
|-------|--------------|---------------------------|------------------------------|
| RF-ING-01 | Importación catálogo | OE1 | Actividad 2: Consultas y extracción de datos |
| RF-ING-02 | Normalización atributos | OE1 | Actividad 3: Normalización y limpieza |
| RF-ING-03 | Actualización incremental | OE1 | Actividad 2: Consultas y extracción (mantenimiento) |
| RF-CTX-01 | Captura perfil sesión | OE1, OE3 | OE1-Act1: Identificación de atributos; OE3: Requerimientos funcionales |
| RF-CTX-02 | Validación coherencia | OE1, OE3 | OE1-Act1: Condiciones operativas; OE3: Necesidades de asesores |
| RF-CTX-03 | Plantillas reutilizables | OE3, OE5 | OE3: Requerimientos funcionales; OE5: Eficiencia de preparación |
| RF-TAX-01 | Taxonomía de habilidades | OE2 | Actividad 1-2: Categorías de habilidades, taxonomía |
| RF-TAX-02 | Asignación manual habilidades | OE2 | Actividad 4: Asignación de habilidades a juegos |
| RF-TAX-03 | Documentación criterios | OE2 | Actividad 3-4: Validación y registro de decisiones |
| RF-TAX-04 | Asistencia NLP | OE2, OE4 | OE2-Act4: Asignación; OE4: NLP para habilidades |
| RF-TAX-05 | Co-ocurrencias habilidades | OE2, OE5 | OE2: Taxonomía; OE5: Preservación de conocimiento |
| RF-REC-01 | Generación Top-N | OE4 | Motor de recomendación híbrido |
| RF-REC-02 | Configuración pesos | OE4 | Implementación motor + ajuste |
| RF-REC-03 | Manejo restricciones | OE4, OE3 | OE4: Reglas pedagógicas; OE3: Necesidades asesores |
| RF-REC-04 | Priorización por feedback | OE4, OE5 | OE4: Retroalimentación de uso; OE5: Mejora continua |
| RF-REC-05 | Recomendación por semilla | OE4 | Filtrado basado en contenido |
| RF-REC-06 | Favoritos/exclusiones | OE3, OE5 | OE3: Necesidades asesores; OE5: Personalización |
| RF-EXP-01 | Explicación recomendaciones | OE3 | Trazabilidad de criterios de selección |
| RF-EXP-02 | Registro trazabilidad | OE5, Obj.Gral | OE5: Preservación conocimiento; Obj.Gral: Fortalecer transferencia |
| RF-EXP-03 | Visualización rastros | OE5 | Análisis y mejora continua |
| RF-UI-01 | Autenticación y roles | OE3 | Requerimientos no funcionales (seguridad) |
| RF-UI-02 | Creación de consulta | OE3, OE4 | OE3-Act4: Interfaz herramienta; OE4: Prototipo funcional |
| RF-UI-03 | Visualización recomendaciones | OE3, OE4 | OE3-Act4: Interfaz; OE4: Prototipo |
| RF-UI-04 | Vista detallada juego | OE3 | Diseño interfaz |
| RF-UI-05 | Búsqueda y filtros | OE3 | Necesidades de uso asesores |
| RF-UI-06 | Identidad visual CJEI | OE3 | Actividad 4: Lineamientos identidad visual |
| RF-RETRO-01 | Registro feedback | OE5 | Actividad 1-2: Esquema retroalimentación, registro |
| RF-RETRO-02 | Visualización feedback | OE5 | Preservación conocimiento |
| RF-RETRO-03 | Análisis patrones uso | OE5 | Actividad 4: Análisis de información |
| RF-RETRO-04 | Exportación reportes | OE5 | Documentación y evaluación |
| RF-RETRO-05 | Votos en comentarios | OE5 | Mejora calidad feedback |
| RF-ADM-01 | Gestión catálogo | OE1 | Consolidación repositorio único |
| RF-ADM-02 | Gestión taxonomía | OE2 | Actividad 2-3: Elaboración y validación taxonomía |
| RF-ADM-03 | Gestión usuarios | OE3 | Requerimientos no funcionales |

---

## LEYENDA DE OBJETIVOS ESPECÍFICOS

- **OE1**: Caracterizar el uso actual de juegos de mesa en el CJEI
- **OE2**: Diseñar y documentar taxonomía de juegos, habilidades y objetivos
- **OE3**: Especificar requerimientos funcionales y no funcionales del prototipo
- **OE4**: Desarrollar e implementar prototipo del sistema de recomendación
- **OE5**: Evaluar precisión, utilidad, usabilidad e impacto del prototipo
- **Obj.Gral**: Objetivo General (desarrollar sistema que preserve conocimiento y mejore eficiencia)

---

## NOTAS FINALES SOBRE COHERENCIA CON METODOLOGÍA

Este conjunto de requerimientos funcionales se alinea con las actividades descritas en la metodología del anteproyecto de la siguiente manera:

1. **Módulos A-B** implementan las actividades del **Objetivo Específico 1** (caracterización y extracción de datos).

2. **Módulo C** implementa las actividades del **Objetivo Específico 2** (taxonomía de habilidades).

3. **Módulos E-F** implementan las actividades del **Objetivo Específico 3** (especificación de requerimientos e interfaz).

4. **Módulo D** implementa las actividades del **Objetivo Específico 4** (desarrollo del motor de recomendación).

5. **Módulo G** implementa las actividades del **Objetivo Específico 5** (evaluación y retroalimentación).

6. **Módulo H** provee funcionalidades administrativas transversales necesarias para la operación del sistema.

La priorización MoSCoW refleja el alcance de MVP definido en el proyecto de grado, enfocándose en funcionalidades "Must" que demuestren el concepto central, mientras que "Should" y "Could" quedan para iteraciones post-validación inicial o trabajos futuros.

---

**Versión del documento:** 1.0  
**Fecha:** Enero 2026  
**Autor:** Cristian Andrés Carabalí Loboa  
**Proyecto:** Sistema de Recomendación de Juegos de Mesa - CJEI