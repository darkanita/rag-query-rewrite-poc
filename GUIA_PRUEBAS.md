# 🧪 Guía de Pruebas: Query Rewriting Optimizado

## 🎯 Objetivo
Esta guía te ayudará a probar y verificar todas las optimizaciones del sistema de reescritura de consultas.

---

## 📋 Checklist de Pruebas

### ✅ 1. Deduplicación Semántica
**Objetivo:** Verificar que no genera queries redundantes

**Prueba:**
```
Query: "¿Qué cubre el plan de salud Northwind Health Plus?"
```

**Esperado:**
- ✅ 3 queries distintas con perspectivas diferentes
- ✅ NO deberías ver queries como:
  - "¿Cuál es la cobertura del plan de salud Northwind Health Plus?"
  - "¿Qué incluye el plan de salud Northwind Health Plus?"
  (Ambas son muy similares a la original)

**Verificar en logs:**
```
INFO: Removed X semantically similar queries
```

---

### ✅ 2. Ajuste Adaptativo de max_queries
**Objetivo:** Verificar que ajusta número de queries según complejidad

#### Prueba A: Query Simple
```
Query: "beneficios dentales"
```
**Esperado:**
- Complejidad: SIMPLE
- Queries generadas: 1-2 (no 3)
- Tiempo: ~1-1.5s

**Verificar en logs:**
```
INFO: Adjusted max_queries from 3 to 2 based on query complexity
INFO: Query complexity: simple
```

#### Prueba B: Query Media
```
Query: "¿Qué servicios médicos cubre el plan?"
```
**Esperado:**
- Complejidad: MEDIA
- Queries generadas: 3 (default)
- Estrategia: refinamiento + expansión

**Verificar en logs:**
```
INFO: Query complexity: medium
```

#### Prueba C: Query Compleja
```
Query: "¿Cuáles son las diferencias entre el plan básico y el plan premium en términos de cobertura dental, oftalmológica y de medicamentos recetados para el año 2023?"
```
**Esperado:**
- Complejidad: COMPLEJA
- Queries generadas: 4-5 (sub-consultas descompuestas)
- Estrategia: descomposición

**Verificar en logs:**
```
INFO: Adjusted max_queries from 3 to 5 based on query complexity
INFO: Query complexity: complex
```

---

### ✅ 3. Cache de Queries
**Objetivo:** Verificar que usa cache para queries repetidas

**Prueba:**
1. Ejecuta esta query:
```
Query: "¿Qué beneficios tiene el plan Northwind Health Plus?"
```
Tiempo esperado: ~1.8-2.5s

2. Ejecuta EXACTAMENTE la misma query de nuevo:
```
Query: "¿Qué beneficios tiene el plan Northwind Health Plus?"
```
Tiempo esperado: <50ms ⚡

**Verificar en logs:**
```
INFO: Using cached rewrite for query: '¿Qué beneficios tiene el plan Northwind Health Plus?'
```

**Verificar en UI:**
- Segunda respuesta debería ser casi instantánea
- Las queries reescritas deberían ser idénticas a la primera vez

---

### ✅ 4. Prompts en Español + Preservación de Nombres
**Objetivo:** Verificar que genera queries naturales en español y mantiene nombres propios

**Prueba:**
```
Query: "¿Cuáles son los beneficios del plan Northwind Health Plus para empleados de Microsoft?"
```

**Esperado:**
- ✅ Todas las queries en español natural
- ✅ "Northwind Health Plus" se mantiene en TODAS las queries
- ✅ "Microsoft" se mantiene en TODAS las queries
- ✅ NO deberías ver:
  - "[Nombre de la Compañía]"
  - "[Marca]"
  - "[Empresa]"
  - Cualquier otro placeholder genérico

**Ejemplo de queries correctas:**
```
1. ¿Cuáles son los beneficios del plan Northwind Health Plus para empleados de Microsoft?
2. ¿Qué cobertura ofrece el plan Northwind Health Plus a trabajadores de Microsoft?
3. ¿Qué ventajas tiene el plan de salud Northwind Health Plus para personal de Microsoft?
```

**Ejemplo de queries INCORRECTAS (no deberías ver):**
```
❌ ¿Cuáles son los beneficios del plan [Nombre del Plan] para empleados de [Empresa]?
❌ ¿Qué cubre el plan de [Compañía] para trabajadores de [Organización]?
```

---

### ✅ 5. Estrategia Híbrida Inteligente
**Objetivo:** Verificar que elige la mejor estrategia según el caso

#### Caso A: Query Simple → Solo Refinamiento Mínimo
```
Query: "cobertura dental"
```
**Esperado:**
- Estrategia aplicada: refinamiento mínimo o expansión ligera
- Queries: 1-2

**Verificar en logs:**
```
INFO: Hybrid rewrite generated X unique variations using ['refinement']
```

#### Caso B: Query Compleja → Descomposición
```
Query: "Quiero saber qué diferencias hay entre los planes y cuál me conviene más según mi situación familiar"
```
**Esperado:**
- Estrategia aplicada: descomposición
- Queries: 4-5 sub-consultas

**Verificar en logs:**
```
INFO: Hybrid rewrite generated X unique variations using ['decomposition']
```

#### Caso C: Query Media → Refinamiento + Expansión
```
Query: "¿Qué servicios preventivos cubre el plan?"
```
**Esperado:**
- Estrategia aplicada: refinamiento + expansión
- Queries: 3

**Verificar en logs:**
```
INFO: Hybrid rewrite generated X unique variations using ['refinement', 'expansion']
```

---

## 🔬 Pruebas Específicas de Edge Cases

### Edge Case 1: Query con Múltiples Nombres Propios
```
Query: "Comparar Northwind Health Plus y Contoso Medical Premium para empleados de Microsoft"
```

**Verificar:**
- ✅ "Northwind Health Plus" preservado
- ✅ "Contoso Medical Premium" preservado
- ✅ "Microsoft" preservado
- ✅ No se reemplazan con genéricos

---

### Edge Case 2: Query con Números y Fechas
```
Query: "¿Cuánto cuesta el plan para una familia de 4 personas en 2023?"
```

**Verificar:**
- ✅ "4 personas" se mantiene (no se generaliza a "X personas")
- ✅ "2023" se mantiene
- ✅ Contexto numérico preservado

---

### Edge Case 3: Query Muy Corta
```
Query: "dental"
```

**Verificar:**
- ✅ Complejidad: SIMPLE
- ✅ Queries: 1-2
- ✅ Sistema no falla con queries de 1 palabra

---

### Edge Case 4: Query Extremadamente Larga
```
Query: "Necesito información completa y detallada sobre todos los beneficios de salud que ofrece el plan Northwind Health Plus incluyendo cobertura dental, oftalmológica, servicios preventivos, medicamentos recetados, hospitalización, cirugías, emergencias, maternidad y salud mental para mi familia de 5 personas considerando que tenemos condiciones preexistentes"
```

**Verificar:**
- ✅ Complejidad: COMPLEJA
- ✅ Se descompone en sub-consultas manejables
- ✅ Queries: 5-7 sub-consultas específicas
- ✅ Cada sub-consulta enfocada en un aspecto

---

## 📊 Métricas a Observar

### En Primera Ejecución
```
Tiempo total: 1.5-2.5s
Queries generadas: 1-5 (según complejidad)
Llamadas API: 1-2
Cache: Miss
```

### En Segunda Ejecución (misma query)
```
Tiempo total: <50ms ⚡
Queries generadas: Mismo número
Llamadas API: 0 (usa cache)
Cache: Hit ✅
```

---

## 🎨 Verificación Visual en UI

### 1. Activar "Show Query Rewriting"
- Ve a http://localhost:8000
- Marca el checkbox "Show Query Rewriting"

### 2. Observa la Sección de Metadata
Deberías ver algo como:
```
🔄 Query Rewriting: hybrid
Queries Generated: 3

Rewritten Queries:
1. [Query 1]
2. [Query 2]
3. [Query 3]

📊 Metadata:
- Strategy: hybrid
- Complexity: medium
- Strategies applied: refinement, expansion
- Deduplicated: true
- Removed duplicates: 1
```

---

## 🐛 Troubleshooting

### Problema: Cache no funciona
**Síntoma:** Queries repetidas tardan lo mismo

**Verificar:**
1. Que la query sea EXACTAMENTE igual (espacios, mayúsculas, puntuación)
2. Que la estrategia sea la misma
3. Que max_queries no haya cambiado

**Solución:**
- Cache es case-sensitive y exacto
- Prueba con copy-paste de la misma query

---

### Problema: Genera demasiadas queries
**Síntoma:** Siempre genera 5+ queries

**Verificar:**
1. Que max_queries esté en 3 (default)
2. Que no estés forzando un número alto en la UI

**Solución:**
- Revisa slider "Max Queries" en UI (debe estar en 3)
- El sistema puede generar hasta 5 solo para queries muy complejas

---

### Problema: Queries siguen siendo redundantes
**Síntoma:** Ve queries muy similares

**Verificar:**
1. Threshold de similitud (actual: 0.95)
2. Que deduplicación esté activa

**Logs esperados:**
```
INFO: Removed X semantically similar queries
```

**Si no ves ese log:**
- Puede ser que las queries no sean lo suficientemente similares (>95%)
- O que solo haya 1-2 queries (no hay qué deduplicar)

---

## 📝 Template de Reporte de Pruebas

```markdown
## Prueba: [Nombre]
**Query probada:** [Tu query]
**Fecha:** [Fecha]

### Resultados
- Complejidad detectada: [simple/medium/complex]
- Queries generadas: [número]
- Tiempo (primera vez): [tiempo]
- Tiempo (con cache): [tiempo]
- Nombres preservados: ✅/❌
- Redundancia eliminada: ✅/❌

### Queries Generadas
1. [Query 1]
2. [Query 2]
3. [Query 3]

### Observaciones
[Tus comentarios]

### ✅ Pasa / ❌ Falla
```

---

## 🎯 Casos de Prueba Recomendados (Top 10)

1. ✅ **Simple:** "beneficios dentales"
2. ✅ **Media:** "¿Qué cubre el plan Northwind Health Plus?"
3. ✅ **Compleja:** "Diferencias entre plan básico y premium en dental, oftalmología y medicamentos"
4. ✅ **Con nombres propios:** "Plan Northwind Health para empleados Microsoft"
5. ✅ **Con números:** "Costo para familia de 4 personas"
6. ✅ **Con fechas:** "Beneficios disponibles en 2023"
7. ✅ **Comparativa:** "Comparar plan A y plan B"
8. ✅ **Muy corta:** "dental"
9. ✅ **Muy larga:** [Query de 50+ palabras]
10. ✅ **Cache test:** Repetir cualquier query 2 veces

---

## 📈 Criterios de Éxito

Una implementación exitosa debería:

✅ **Calidad:**
- 100% preservación de nombres propios
- <5% de redundancia en queries
- Queries naturales en español

✅ **Performance:**
- <2.5s en primera ejecución
- <50ms con cache
- 25-30% menos llamadas API

✅ **Adaptabilidad:**
- Queries simples: 1-2 variaciones
- Queries medias: 3 variaciones
- Queries complejas: 4-5 variaciones

✅ **Inteligencia:**
- Estrategia correcta según complejidad
- Deduplicación efectiva
- Cache funcionando

---

**¡Buenas pruebas!** 🚀

Si encuentras algún problema, revisa los logs en la consola donde corre `api.py` para más detalles.
