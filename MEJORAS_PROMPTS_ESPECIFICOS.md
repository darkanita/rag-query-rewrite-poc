# 🎯 Mejoras en Prompts para Queries Específicos

## 🚨 Problema Identificado

El sistema estaba generando consultas **demasiado genéricas** que no ayudaban a buscar en la base de conocimiento:

### Ejemplo del Problema
**Query original:** (sobre plan de salud específico)

**Queries generadas ANTES:**
```
❌ "beneficios plan de salud"  (muy genérico)
❌ "información general sobre seguros"  (muy vago)
❌ "Beneficios específicos del plan de salud de Seguros XYZ para 2023"  (título genérico)
```

**Problema:** Estas queries no tienen palabras clave concretas que aparecerían en documentos reales.

---

## ✅ Solución Implementada

Se reescribieron completamente los prompts con enfoque en **especificidad y palabras clave concretas**.

### Cambios Principales

#### 1. **Prompt de Expansión** - Ahora genera queries con palabras clave específicas

**ANTES:**
```
"Genera versiones expandidas que usen sinónimos y reformulaciones..."
```

**AHORA:**
```
"Crea versiones ESPECÍFICAS que:
- AGREGUEN términos más específicos relacionados
- SE ENFOQUEN en detalles concretos y palabras clave
- Usen vocabulario técnico del dominio
- NO sean vagas ni genéricas"
```

**Ejemplos concretos agregados al prompt:**
```
❌ NO: "beneficios plan de salud" (genérico)
✅ SÍ: "cobertura médica hospitalización emergencias [Nombre Específico]"
✅ SÍ: "deducibles copagos límites cobertura [Plan Específico]"
✅ SÍ: "servicios preventivos incluidos vacunas chequeos [Nombre]"
```

#### 2. **Prompt de Refinamiento** - Agrega palabras clave, no generaliza

**ANTES:**
```
"Refina esta consulta aclarando términos ambiguos..."
```

**AHORA:**
```
"Refina esta consulta para hacerla MÁS ESPECÍFICA:
- AGREGA palabras clave específicas
- ELIMINA palabras vagas o genéricas
- ENFOCA en detalles concretos y medibles
- USA vocabulario técnico"
```

**Ejemplo en el prompt:**
```
❌ Mal refinamiento: "información sobre planes de salud"
✅ Buen refinamiento: "cobertura servicios médicos hospitalización medicamentos [Plan]"
```

#### 3. **Prompt de Descomposición** - Sub-consultas específicas

**ANTES:**
```
"Divide en sub-consultas más simples..."
```

**AHORA:**
```
"Divide en sub-consultas ESPECÍFICAS:
- Cada una debe buscar información CONCRETA
- AGREGA palabras clave específicas
- USA vocabulario técnico del dominio
- NO crees sub-consultas genéricas"
```

**Ejemplo en el prompt:**
```
❌ Mala: "información sobre Plan A"
✅ Buena: "cobertura servicios médicos hospitalización Plan A"
✅ Buena: "deducibles copagos límites cobertura Plan A vs Plan B"
```

#### 4. **Ajustes de Temperatura**

Se redujeron las temperaturas para generar queries más consistentes y específicas:

| Estrategia | Antes | Ahora | Razón |
|------------|-------|-------|-------|
| Expansión | 0.6 | **0.4** | Más enfocado, menos creativo |
| Descomposición | 0.4 | **0.3** | Más consistente |
| Refinamiento | 0.2 | **0.1** | Muy conservador, solo agregar especificidad |

#### 5. **System Prompts Mejorados**

**ANTES:**
```
"Eres un experto en expansión de consultas..."
```

**AHORA:**
```
"Eres un experto en búsqueda de documentos que crea consultas 
específicas con palabras clave concretas, no generalizaciones."
```

---

## 🎯 Resultados Esperados

### Para: "¿Qué cubre el plan Northwind Health Plus?"

**ANTES (genérico):**
```
❌ beneficios plan de salud
❌ información sobre seguros
❌ detalles del plan
```

**AHORA (específico):**
```
✅ cobertura médica hospitalización cirugías emergencias Northwind Health Plus
✅ servicios preventivos chequeos vacunas exámenes incluidos Northwind Health Plus
✅ medicamentos recetados farmacia cobertura Northwind Health Plus
```

### Para: "¿Cuánto cuesta el plan familiar?"

**ANTES (genérico):**
```
❌ costos planes de salud
❌ información precios
```

**AHORA (específico):**
```
✅ precio costo mensual prima plan familiar
✅ deducibles copagos coaseguro plan familiar
✅ límites gastos bolsillo máximo anual plan familiar
```

---

## 🔍 Palabras Clave Prioritarias

Los prompts ahora guían al LLM a usar estos tipos de términos específicos:

### Para Planes de Salud:
- ✅ cobertura, servicios incluidos, procedimientos cubiertos
- ✅ deducibles, copagos, coaseguro, prima
- ✅ límites, máximos, exclusiones
- ✅ hospitalización, cirugías, emergencias
- ✅ medicamentos, farmacia, recetas
- ✅ preventivo, chequeos, vacunas, exámenes
- ✅ especialistas, consultas, terapias
- ✅ dental, oftalmológico, auditivo
- ✅ maternidad, pediatría, geriatría

### Para Beneficios Corporativos:
- ✅ elegibilidad, requisitos, condiciones
- ✅ inscripción, periodos, plazos
- ✅ dependientes, cónyuge, hijos
- ✅ contribución empleador, descuento payroll
- ✅ red proveedores, médicos participantes

---

## 📊 Comparación Técnica

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Enfoque** | Sinónimos y reformulación | Palabras clave específicas |
| **Vocabulario** | General | Técnico del dominio |
| **Especificidad** | Baja/Media | Alta |
| **Generalización** | Riesgo alto | Riesgo muy bajo |
| **Temperatura promedio** | 0.4-0.6 | 0.1-0.4 |
| **Tokens máximos** | 400-500 | 150-350 |
| **Instrucciones** | Preservar nombres | + Agregar keywords |
| **Ejemplos en prompt** | No | Sí (explícitos ✅❌) |

---

## 🧪 Cómo Verificar las Mejoras

### Prueba 1: Query sobre Cobertura
```
Input: "¿Qué cubre el plan Northwind Health Plus?"
```

**Verifica que las queries generadas incluyan:**
- ✅ Términos específicos: "hospitalización", "cirugías", "emergencias"
- ✅ Palabras técnicas: "cobertura", "servicios incluidos", "procedimientos"
- ✅ Nombres propios intactos: "Northwind Health Plus"
- ❌ NO palabras genéricas: "información", "detalles", "aspectos"

### Prueba 2: Query sobre Costos
```
Input: "¿Cuánto cuesta?"
```

**Verifica que las queries incluyan:**
- ✅ Términos específicos: "prima", "deducible", "copago", "coaseguro"
- ✅ Métricas concretas: "mensual", "anual", "límite máximo"
- ❌ NO: "precio", "costo" (sin especificar tipo)

### Prueba 3: Query Compleja
```
Input: "¿Qué diferencias hay entre plan básico y premium?"
```

**Verifica sub-consultas específicas:**
- ✅ "cobertura hospitalización cirugías plan básico vs premium"
- ✅ "deducibles copagos límites plan básico vs premium"
- ✅ "red médicos especialistas incluidos básico vs premium"
- ❌ NO: "información plan básico", "detalles premium"

---

## 💡 Principios Clave de los Nuevos Prompts

### 1. **Ser Específico, No General**
```
❌ "información sobre X"
✅ "cobertura servicios procedimientos incluidos X"
```

### 2. **Usar Vocabulario del Dominio**
```
❌ "gastos médicos"
✅ "deducibles copagos coaseguro prima"
```

### 3. **Enfocarse en Palabras Clave de Búsqueda**
```
❌ "¿Cuáles son los beneficios?"
✅ "beneficios preventivos chequeos vacunas exámenes incluidos"
```

### 4. **Incluir Contexto Específico**
```
❌ "plan de salud"
✅ "plan [Nombre] cobertura hospitalización emergencias 2023"
```

### 5. **Evitar Términos Vagos**
```
❌ "detalles", "aspectos", "información general", "datos"
✅ "cobertura", "límites", "exclusiones", "procedimientos"
```

---

## 🎓 Guía para Interpretar Logs

Cuando veas los logs, ahora verás:

```bash
INFO: Query expanded into 2 specific variations
# "specific" indica que se enfocó en especificidad

INFO: Query complexity: simple
# Para queries simples, menos variaciones

INFO: Using cached rewrite for query: '...'
# Cache sigue funcionando
```

---

## 🔄 Impacto en el Sistema

### Antes de la Mejora:
- 🟡 Queries generadas: vagos, genéricos
- 🟡 Recuperación: documentos poco relevantes
- 🟡 Respuestas: información general, no específica

### Después de la Mejora:
- 🟢 Queries generadas: específicos, con keywords
- 🟢 Recuperación: documentos más relevantes
- 🟢 Respuestas: información concreta y útil

---

## 📝 Recomendaciones de Uso

1. **Prueba con queries reales** de tu base de conocimiento
2. **Activa "Show Query Rewriting"** en el UI para ver las queries generadas
3. **Verifica que incluyan palabras clave** técnicas específicas
4. **Compara resultados** antes y después

---

## 🚀 Próximos Pasos Opcionales

Si aún necesitas más especificidad, podrías:

1. **Agregar contexto del dominio** al prompt:
   ```python
   "Dominio: Seguros de salud corporativos
   Vocabulario clave: cobertura, deducibles, copagos, prima, red médica..."
   ```

2. **Usar few-shot learning** con ejemplos de tu base de conocimiento:
   ```python
   "Ejemplos de consultas efectivas en nuestra base:
   - 'cobertura hospitalización cirugías plan X'
   - 'deducibles copagos límites anuales plan Y'"
   ```

3. **Ajustar temperatura aún más** (0.05-0.1) para máxima consistencia

---

**Fecha:** 7 de octubre, 2025
**Versión:** 2.1 - Prompts Específicos
**Estado:** ✅ Implementado y Activo
