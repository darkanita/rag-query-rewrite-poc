"""
Query Rewriter Module
Implements various strategies for query rewriting to improve RAG retrieval
Optimized for Spanish queries with semantic deduplication and caching
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from functools import lru_cache
import hashlib
from loguru import logger
from openai import OpenAI
from config import settings


class RewriteStrategy(Enum):
    """Available query rewrite strategies"""
    EXPANSION = "expansion"
    DECOMPOSITION = "decomposition"
    REFINEMENT = "refinement"
    HYBRID = "hybrid"


class QueryRewriter:
    """
    Rewrites user queries to improve retrieval performance in RAG systems
    Optimized with semantic deduplication and adaptive query generation
    """
    
    def __init__(self, strategy: str = "hybrid"):
        """
        Initialize the query rewriter
        
        Args:
            strategy: Rewrite strategy to use (expansion, decomposition, refinement, hybrid)
        """
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.strategy = RewriteStrategy(strategy)
        self.max_queries = 3  # Default to 3 queries for better performance
        self._query_cache = {}  # Simple cache for rewritten queries
        logger.info(f"QueryRewriter initialized with strategy: {self.strategy.value}")
    
    def _get_cache_key(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for query and context"""
        context_str = str(context) if context else ""
        combined = f"{query}:{self.strategy.value}:{self.max_queries}:{context_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _calculate_semantic_similarity(self, queries: List[str]) -> List[tuple]:
        """
        Calculate semantic similarity between queries using embeddings
        Returns list of (query1_idx, query2_idx, similarity) for similar pairs
        """
        if len(queries) <= 1:
            return []
        
        try:
            # Get embeddings for all queries
            response = self.client.embeddings.create(
                model=settings.openai_embedding_model,
                input=queries
            )
            
            embeddings = [item.embedding for item in response.data]
            
            # Calculate cosine similarity between all pairs
            similar_pairs = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    # Cosine similarity
                    dot_product = sum(a * b for a, b in zip(embeddings[i], embeddings[j]))
                    norm_i = sum(a * a for a in embeddings[i]) ** 0.5
                    norm_j = sum(a * a for a in embeddings[j]) ** 0.5
                    similarity = dot_product / (norm_i * norm_j) if norm_i and norm_j else 0
                    
                    # Threshold for considering queries too similar (0.95 = very similar)
                    if similarity > 0.95:
                        similar_pairs.append((i, j, similarity))
            
            return similar_pairs
        except Exception as e:
            logger.warning(f"Error calculating semantic similarity: {e}")
            return []
    
    def _deduplicate_queries(self, queries: List[str]) -> List[str]:
        """
        Remove semantically similar queries to avoid redundancy
        Keeps the shorter/simpler version when duplicates are found
        """
        if len(queries) <= 1:
            return queries
        
        # First, remove exact duplicates (case-insensitive)
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)
        
        if len(unique_queries) <= 1:
            return unique_queries
        
        # Then check semantic similarity
        similar_pairs = self._calculate_semantic_similarity(unique_queries)
        
        if not similar_pairs:
            return unique_queries
        
        # Mark queries to remove (keep shorter one)
        to_remove = set()
        for i, j, similarity in similar_pairs:
            # Keep the shorter/simpler query
            if len(unique_queries[i]) > len(unique_queries[j]):
                to_remove.add(i)
            else:
                to_remove.add(j)
        
        deduplicated = [q for idx, q in enumerate(unique_queries) if idx not in to_remove]
        
        if len(deduplicated) < len(unique_queries):
            logger.info(f"Removed {len(unique_queries) - len(deduplicated)} semantically similar queries")
        
        return deduplicated
    
    def _determine_query_complexity(self, query: str) -> str:
        """
        Determine if query is simple or complex to adjust number of variations
        Returns: 'simple', 'medium', or 'complex'
        """
        words = query.split()
        word_count = len(words)
        
        # Check for complexity indicators
        has_multiple_questions = query.count('?') > 1 or ' y ' in query.lower() or ' o ' in query.lower()
        has_comparisons = any(word in query.lower() for word in ['comparar', 'diferencia', 'versus', 'vs', 'mejor'])
        has_conditionals = any(word in query.lower() for word in ['si', 'cuando', 'cómo', 'por qué', 'dónde'])
        
        if word_count <= 5 and not has_multiple_questions:
            return 'simple'
        elif word_count > 15 or has_multiple_questions or has_comparisons:
            return 'complex'
        else:
            return 'medium'
    
    def _adjust_max_queries(self, query: str) -> int:
        """
        Dynamically adjust max_queries based on query complexity
        """
        complexity = self._determine_query_complexity(query)
        
        if complexity == 'simple':
            return min(2, self.max_queries)  # Simple queries need fewer variations
        elif complexity == 'complex':
            return min(5, max(3, self.max_queries))  # Complex queries benefit from more variations
        else:
            return self.max_queries  # Medium complexity uses default
    
    def rewrite(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Rewrite a query using the configured strategy
        
        Args:
            query: Original user query
            context: Optional context information (conversation history, user preferences, etc.)
        
        Returns:
            Dictionary containing rewritten queries and metadata
        """
        # Check cache first
        cache_key = self._get_cache_key(query, context)
        if cache_key in self._query_cache:
            logger.info(f"Using cached rewrite for query: '{query}'")
            return self._query_cache[cache_key]
        
        logger.info(f"Rewriting query: '{query}' with strategy: {self.strategy.value}")
        
        # Adjust max_queries based on query complexity
        original_max = self.max_queries
        adaptive_max = self._adjust_max_queries(query)
        if adaptive_max != original_max:
            logger.info(f"Adjusted max_queries from {original_max} to {adaptive_max} based on query complexity")
            self.max_queries = adaptive_max
        
        try:
            if self.strategy == RewriteStrategy.EXPANSION:
                result = self._expand_query(query, context)
            elif self.strategy == RewriteStrategy.DECOMPOSITION:
                result = self._decompose_query(query, context)
            elif self.strategy == RewriteStrategy.REFINEMENT:
                result = self._refine_query(query, context)
            elif self.strategy == RewriteStrategy.HYBRID:
                result = self._hybrid_rewrite(query, context)
            else:
                result = {"original": query, "rewritten": [query], "strategy": "none"}
            
            # Apply semantic deduplication
            if len(result["rewritten"]) > 1:
                original_count = len(result["rewritten"])
                result["rewritten"] = self._deduplicate_queries(result["rewritten"])
                if len(result["rewritten"]) < original_count:
                    result["metadata"]["deduplicated"] = True
                    result["metadata"]["removed_duplicates"] = original_count - len(result["rewritten"])
            
            # Cache the result
            self._query_cache[cache_key] = result
            
            # Limit cache size to prevent memory issues
            if len(self._query_cache) > 100:
                # Remove oldest entry (simple FIFO)
                self._query_cache.pop(next(iter(self._query_cache)))
            
            return result
        finally:
            # Restore original max_queries
            self.max_queries = original_max
    
    def _expand_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Expand query with synonyms, related terms, and alternative phrasings
        Optimized for Spanish queries with better focus
        """
        prompt = f"""Eres un experto en expansión de consultas para búsqueda de documentos. Tu objetivo es crear variaciones de búsqueda MUY ESPECÍFICAS que ayuden a encontrar información CONCRETA en documentos.

Consulta Original: {query}

Crea {self.max_queries} versiones ESPECÍFICAS de esta consulta que:

1. MANTENGAN TODOS los nombres propios, empresas, marcas y términos específicos EXACTAMENTE igual
2. AGREGUEN términos más específicos relacionados con la búsqueda
3. SE ENFOQUEN en detalles concretos y palabras clave que aparecerían en documentos reales
4. Usen vocabulario técnico o específico del dominio cuando sea apropiado
5. Sean preguntas o búsquedas que alguien haría para encontrar información ESPECÍFICA
6. NO sean vagas ni genéricas - deben buscar información concreta

CRÍTICO:
- Si la consulta original menciona nombres específicos (empresas, planes, productos), MANTENLOS en todas las variaciones
- NO uses placeholders genéricos como [Empresa], [Plan], [Compañía]
- NO hagas consultas más genéricas que la original - hazlas MÁS específicas
- Piensa: "¿Qué palabras clave buscaría en un documento para encontrar esta información?"
- Cada variación debe enfocarse en aspectos específicos o términos relacionados

Ejemplos de lo que NO hacer:
❌ "beneficios plan de salud" (muy genérico)
❌ "información general sobre seguros" (muy vago)

Ejemplos de lo que SÍ hacer:
✅ "cobertura médica hospitalización emergencias [Nombre Específico]"
✅ "deducibles copagos límites cobertura [Plan Específico]"
✅ "servicios preventivos incluidos vacunas chequeos [Nombre Específico]"

Devuelve SOLO las consultas expandidas, una por línea, sin numeración ni explicación."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en búsqueda de documentos que crea consultas específicas con palabras clave concretas, no generalizaciones."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Reduced from 0.6 for more focused, specific results
                max_tokens=350  # Reduced to encourage concise, keyword-focused queries
            )
            
            expanded_queries = response.choices[0].message.content.strip().split('\n')
            expanded_queries = [q.strip() for q in expanded_queries if q.strip() and len(q.strip()) > 10]
            
            # Limit to max_queries
            expanded_queries = expanded_queries[:self.max_queries]
            
            logger.info(f"Query expanded into {len(expanded_queries)} specific variations")
            
            return {
                "original": query,
                "rewritten": [query] + expanded_queries,
                "strategy": "expansion",
                "metadata": {
                    "num_variations": len(expanded_queries),
                    "temperature": 0.4
                }
            }
        except Exception as e:
            logger.error(f"Error expanding query: {e}")
            return {"original": query, "rewritten": [query], "strategy": "expansion", "error": str(e)}
    
    def _decompose_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Decompose complex queries into simpler sub-queries
        Optimized for Spanish with better complexity detection
        """
        prompt = f"""Eres un experto en descomposición de consultas complejas. Tu objetivo es dividir consultas complejas en sub-consultas ESPECÍFICAS que busquen información concreta.

Consulta Original: {query}

Si esta consulta es compleja y contiene múltiples partes:

1. Identifica las sub-preguntas ESPECÍFICAS que la componen
2. Crea {self.max_queries} o menos sub-consultas ENFOCADAS en detalles concretos
3. MANTÉN todos los nombres propios y términos específicos en cada sub-consulta
4. AGREGA palabras clave específicas para búsqueda en documentos
5. Cada sub-consulta debe buscar información CONCRETA, no general
6. USA vocabulario técnico y términos específicos del dominio

IMPORTANTE:
- NO crees sub-consultas genéricas como "información general sobre..."
- SÍ crea sub-consultas específicas con palabras clave concretas
- Mantén todos los nombres propios (empresas, planes, marcas) en cada sub-consulta
- Enfócate en aspectos medibles y concretos

Ejemplo de mala descomposición:
Original: "¿Qué diferencias hay entre Plan A y Plan B?"
❌ "información sobre Plan A"
❌ "información sobre Plan B"

Ejemplo de buena descomposición:
Original: "¿Qué diferencias hay entre Plan A y Plan B?"
✅ "cobertura servicios médicos hospitalización Plan A"
✅ "cobertura servicios médicos hospitalización Plan B"
✅ "deducibles copagos límites cobertura Plan A vs Plan B"

Si la consulta ya es simple y enfocada, devuélvela tal cual.

Devuelve SOLO las sub-consultas, una por línea, sin numeración ni explicación."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en descomposición que crea sub-consultas específicas con palabras clave concretas para búsqueda en documentos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Reduced from 0.4 for more consistent, specific decomposition
                max_tokens=350
            )
            
            sub_queries = response.choices[0].message.content.strip().split('\n')
            sub_queries = [q.strip() for q in sub_queries if q.strip() and len(q.strip()) > 10]
            
            # Limit to max_queries
            sub_queries = sub_queries[:self.max_queries]
            
            logger.info(f"Query decomposed into {len(sub_queries)} sub-queries")
            
            return {
                "original": query,
                "rewritten": sub_queries if len(sub_queries) > 1 else [query],
                "strategy": "decomposition",
                "metadata": {
                    "num_sub_queries": len(sub_queries),
                    "was_decomposed": len(sub_queries) > 1,
                    "temperature": 0.4
                }
            }
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            return {"original": query, "rewritten": [query], "strategy": "decomposition", "error": str(e)}
    
    def _refine_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refine query by clarifying intent and adding specificity
        Optimized for Spanish with better context handling
        """
        context_str = ""
        if context and context.get("conversation_history"):
            context_str = f"\n\nContexto de la Conversación:\n{context['conversation_history']}"
        
        prompt = f"""Eres un experto en optimización de consultas de búsqueda. Tu objetivo es hacer la consulta MÁS ESPECÍFICA y enfocada en encontrar información concreta en documentos.

Consulta Original: {query}{context_str}

Refina esta consulta para hacerla MÁS ESPECÍFICA:

1. MANTÉN todos los nombres propios, empresas, marcas y términos específicos EXACTAMENTE igual
2. AGREGA palabras clave específicas que ayuden a encontrar la información en documentos
3. ELIMINA palabras vagas o genéricas
4. ENFOCA la búsqueda en detalles concretos y medibles
5. USA vocabulario técnico o del dominio cuando sea apropiado
6. PIENSA: "¿Qué términos específicos aparecerían en un documento que responda esta pregunta?"

IMPORTANTE:
- NO hagas la consulta más genérica
- NO uses términos vagos como "información general", "detalles", "aspectos"
- SÍ agrega términos específicos como "cobertura", "deducibles", "límites", "procedimientos", "servicios incluidos"
- SÍ mantén todos los nombres propios intactos

Ejemplo de mal refinamiento:
Original: "¿Qué cubre el plan Northwind Health Plus?"
❌ Mal: "información sobre planes de salud"

Ejemplo de buen refinamiento:
Original: "¿Qué cubre el plan Northwind Health Plus?"
✅ Bien: "cobertura servicios médicos hospitalización medicamentos Northwind Health Plus"

Devuelve SOLO la consulta refinada, sin explicación ni comillas."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en búsqueda que hace consultas MÁS específicas agregando palabras clave concretas, no generalizando."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Reduced from 0.2 for very conservative, specific refinement
                max_tokens=150  # Reduced from 200 for more concise, keyword-focused output
            )
            
            refined_query = response.choices[0].message.content.strip()
            
            # Remove quotes if LLM added them
            refined_query = refined_query.strip('"').strip("'")
            
            logger.info(f"Query refined: '{query}' -> '{refined_query}'")
            
            return {
                "original": query,
                "rewritten": [refined_query] if refined_query and refined_query != query else [query],
                "strategy": "refinement",
                "metadata": {
                    "refined": refined_query != query,
                    "temperature": 0.2
                }
            }
        except Exception as e:
            logger.error(f"Error refining query: {e}")
            return {"original": query, "rewritten": [query], "strategy": "refinement", "error": str(e)}
    
    def _hybrid_rewrite(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Combine multiple strategies for comprehensive query rewriting
        Optimized to reduce redundant LLM calls and better balance strategies
        """
        logger.info("Applying optimized hybrid rewrite strategy")
        
        complexity = self._determine_query_complexity(query)
        logger.info(f"Query complexity: {complexity}")
        
        # Strategy selection based on complexity
        if complexity == 'simple':
            # For simple queries: just refine + 1-2 expansions
            refined_result = self._refine_query(query, context)
            refined_query = refined_result["rewritten"][0]
            
            if refined_query != query:
                # If refinement changed the query, use both
                all_queries = [query, refined_query]
            else:
                # If no change, just expand the original
                original_max = self.max_queries
                self.max_queries = 2  # Only 2 variations for simple queries
                expanded_result = self._expand_query(query, context)
                self.max_queries = original_max
                all_queries = expanded_result["rewritten"][:2]
            
            strategies_applied = ["refinement", "expansion"]
            
        elif complexity == 'complex':
            # For complex queries: decompose first, then refine the decomposed parts
            decomposed_result = self._decompose_query(query, context)
            
            if decomposed_result["metadata"].get("was_decomposed"):
                # Use decomposed queries directly
                all_queries = decomposed_result["rewritten"]
                strategies_applied = ["decomposition"]
            else:
                # If not decomposed, fall back to refine + expand
                refined_result = self._refine_query(query, context)
                refined_query = refined_result["rewritten"][0]
                
                original_max = self.max_queries
                self.max_queries = max(2, self.max_queries - 1)
                expanded_result = self._expand_query(refined_query, context)
                self.max_queries = original_max
                
                all_queries = [query, refined_query] + [q for q in expanded_result["rewritten"] if q not in [query, refined_query]]
                strategies_applied = ["refinement", "expansion"]
        
        else:  # medium complexity
            # Standard approach: refine + expand
            refined_result = self._refine_query(query, context)
            refined_query = refined_result["rewritten"][0]
            
            # Only expand if refinement changed the query significantly
            if refined_query != query and len(refined_query) > len(query) * 0.7:
                # Expand the refined version
                original_max = self.max_queries
                self.max_queries = max(2, self.max_queries - 1)
                expanded_result = self._expand_query(refined_query, context)
                self.max_queries = original_max
                
                expanded_queries = [q for q in expanded_result["rewritten"] if q not in [query, refined_query]]
                all_queries = [query, refined_query] + expanded_queries
            else:
                # Expand the original if refinement didn't help much
                original_max = self.max_queries
                self.max_queries = max(2, self.max_queries)
                expanded_result = self._expand_query(query, context)
                self.max_queries = original_max
                
                all_queries = expanded_result["rewritten"]
            
            strategies_applied = ["refinement", "expansion"]
        
        # Remove duplicates and limit to max_queries
        seen = set()
        unique_queries = []
        for q in all_queries:
            q_clean = q.strip().lower()
            if q_clean not in seen and len(q.strip()) > 10:
                seen.add(q_clean)
                unique_queries.append(q.strip())
                if len(unique_queries) >= self.max_queries:
                    break
        
        logger.info(f"Hybrid rewrite generated {len(unique_queries)} unique query variations using {strategies_applied}")
        
        return {
            "original": query,
            "rewritten": unique_queries,
            "strategy": "hybrid",
            "metadata": {
                "num_variations": len(unique_queries),
                "strategies_applied": strategies_applied,
                "complexity": complexity
            }
        }
    
    def batch_rewrite(self, queries: List[str], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Rewrite multiple queries in batch
        
        Args:
            queries: List of queries to rewrite
            context: Optional context for all queries
        
        Returns:
            List of rewrite results
        """
        logger.info(f"Batch rewriting {len(queries)} queries")
        return [self.rewrite(query, context) for query in queries]


def create_rewriter(strategy: Optional[str] = None, max_queries: int = 3) -> QueryRewriter:
    """
    Factory function to create a QueryRewriter instance
    
    Args:
        strategy: Optional strategy override (uses config default if not provided)
        max_queries: Maximum number of query variations to generate (default: 3)
    
    Returns:
        QueryRewriter instance
    """
    strategy = strategy or settings.rewrite_strategy
    rewriter = QueryRewriter(strategy=strategy)
    rewriter.max_queries = max_queries
    return rewriter
