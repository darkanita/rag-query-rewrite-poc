"""
Example Usage Script
Demonstrates how to use the RAG Query Rewrite POC
"""
import asyncio
from pathlib import Path
from loguru import logger

from rag_pipeline import create_pipeline
from document_processor import DocumentProcessor
from query_rewriter import create_rewriter


def example_basic_usage():
    """Basic example of using the RAG pipeline"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic RAG Usage")
    print("="*80 + "\n")
    
    # Create pipeline
    pipeline = create_pipeline(enable_rewrite=False)
    
    # Sample documents
    sample_docs = [
        """
        Python is a high-level, interpreted programming language known for its simplicity 
        and readability. It was created by Guido van Rossum and first released in 1991. 
        Python supports multiple programming paradigms including procedural, object-oriented, 
        and functional programming.
        """,
        """
        Machine Learning is a subset of artificial intelligence that enables systems to learn 
        and improve from experience without being explicitly programmed. Popular ML frameworks 
        include TensorFlow, PyTorch, and scikit-learn. Python is the dominant language for 
        machine learning due to its extensive libraries and ease of use.
        """,
        """
        FastAPI is a modern, fast web framework for building APIs with Python. It's based on 
        standard Python type hints and provides automatic interactive API documentation. 
        FastAPI is known for its high performance, rivaling NodeJS and Go.
        """
    ]
    
    # Ingest documents
    print("Ingesting sample documents...")
    for i, doc in enumerate(sample_docs, 1):
        pipeline.ingest_documents(source=doc, source_type="text")
    print(f"✓ Ingested {len(sample_docs)} documents\n")
    
    # Query without rewriting
    question = "What is Python used for?"
    print(f"Question: {question}")
    print("-" * 80)
    
    result = pipeline.query(question, top_k=3)
    print(f"Answer: {result['answer']}\n")
    print(f"Documents retrieved: {result['metadata']['documents_retrieved']}")
    print()


def example_with_query_rewriting():
    """Example using different query rewriting strategies"""
    print("\n" + "="*80)
    print("EXAMPLE 2: RAG with Query Rewriting")
    print("="*80 + "\n")
    
    # Sample documents about climate change
    sample_docs = [
        """
        Climate change refers to long-term shifts in temperatures and weather patterns. 
        Since the 1800s, human activities have been the main driver of climate change, 
        primarily due to burning fossil fuels like coal, oil, and gas. This produces 
        greenhouse gases that trap heat in the atmosphere.
        """,
        """
        The effects of climate change include rising sea levels, more extreme weather events, 
        ocean acidification, and loss of biodiversity. Global temperatures have risen by 
        approximately 1.1°C since pre-industrial times. Scientists warn that we must limit 
        warming to 1.5°C to avoid catastrophic consequences.
        """,
        """
        Solutions to climate change include transitioning to renewable energy sources like 
        solar and wind power, improving energy efficiency, protecting and restoring forests, 
        and changing agricultural practices. Individual actions like reducing consumption, 
        using public transport, and eating less meat also contribute to mitigation efforts.
        """
    ]
    
    # Test different rewrite strategies
    strategies = ["expansion", "refinement", "hybrid"]
    question = "How can we stop global warming?"
    
    for strategy in strategies:
        print(f"\n{'='*80}")
        print(f"Strategy: {strategy.upper()}")
        print('='*80)
        
        # Create pipeline with specific strategy
        pipeline = create_pipeline(
            enable_rewrite=True,
            rewrite_strategy=strategy
        )
        
        # Ingest documents
        for doc in sample_docs:
            pipeline.ingest_documents(source=doc, source_type="text")
        
        # Query with rewriting
        result = pipeline.query(question, top_k=2)
        
        print(f"\nOriginal Question: {question}")
        
        if result['metadata'].get('query_rewrite'):
            rewrite_info = result['metadata']['query_rewrite']
            print(f"Rewrite Strategy: {rewrite_info['strategy']}")
            print(f"Generated Queries: {rewrite_info['num_queries']}")
            print("\nRewritten Queries:")
            for i, q in enumerate(rewrite_info['queries'][:3], 1):
                print(f"  {i}. {q}")
        
        print(f"\nAnswer:\n{result['answer']}")
        print()


def example_query_rewriter_only():
    """Example of using just the query rewriter"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Query Rewriting Only")
    print("="*80 + "\n")
    
    rewriter = create_rewriter(strategy="hybrid")
    
    test_queries = [
        "What is AI?",
        "How do I learn Python and what are the best resources?",
        "machine learning vs deep learning"
    ]
    
    for query in test_queries:
        print(f"Original: {query}")
        print("-" * 80)
        
        result = rewriter.rewrite(query)
        
        print(f"Strategy: {result['strategy']}")
        print("Rewritten variations:")
        for i, rewritten in enumerate(result['rewritten'], 1):
            print(f"  {i}. {rewritten}")
        print()


def example_document_ingestion():
    """Example of ingesting documents from files"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Document Ingestion from Files")
    print("="*80 + "\n")
    
    pipeline = create_pipeline(enable_rewrite=True)
    processor = DocumentProcessor()
    
    # Create a sample document
    sample_file = Path("sample_document.txt")
    sample_content = """
    Artificial Intelligence Overview
    
    Artificial Intelligence (AI) is the simulation of human intelligence by machines. 
    AI systems can perform tasks that typically require human intelligence, such as 
    visual perception, speech recognition, decision-making, and language translation.
    
    Types of AI:
    1. Narrow AI: Designed for specific tasks (e.g., spam filters, voice assistants)
    2. General AI: Theoretical AI with human-like intelligence across all domains
    3. Super AI: Hypothetical AI that surpasses human intelligence
    
    Key AI Technologies:
    - Machine Learning: Systems that learn from data
    - Deep Learning: Neural networks with multiple layers
    - Natural Language Processing: Understanding and generating human language
    - Computer Vision: Interpreting and analyzing visual information
    
    Applications of AI include autonomous vehicles, medical diagnosis, financial trading,
    customer service chatbots, recommendation systems, and many more areas that continue
    to expand as the technology advances.
    """
    
    # Write sample file
    sample_file.write_text(sample_content)
    print(f"Created sample document: {sample_file}")
    
    try:
        # Ingest the document
        result = pipeline.ingest_documents(
            source=str(sample_file),
            source_type="file"
        )
        
        print(f"✓ Ingestion successful!")
        print(f"  Chunks created: {result['chunks_added']}")
        
        # Query the ingested document
        question = "What are the types of AI?"
        print(f"\nQuerying: {question}")
        print("-" * 80)
        
        answer = pipeline.query(question, top_k=2)
        print(f"Answer:\n{answer['answer']}")
        
        # Get pipeline statistics
        print("\n" + "="*80)
        print("Pipeline Statistics")
        print("="*80)
        stats = pipeline.get_stats()
        print(f"Vector Store Type: {stats['vector_store']['store_type']}")
        print(f"Documents Indexed: {stats['vector_store']['document_count']}")
        print(f"Rewrite Enabled: {stats['rewrite_enabled']}")
        print(f"Rewrite Strategy: {stats['rewrite_strategy']}")
        
    finally:
        # Clean up
        if sample_file.exists():
            sample_file.unlink()
            print(f"\nCleaned up: {sample_file}")


def example_batch_processing():
    """Example of batch query processing"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Batch Query Processing")
    print("="*80 + "\n")
    
    pipeline = create_pipeline(enable_rewrite=True)
    
    # Ingest sample data
    docs = [
        "Python is a versatile programming language used for web development, data science, and automation.",
        "JavaScript is the language of the web, used for both frontend and backend development.",
        "SQL is used for managing and querying relational databases.",
        "Git is a version control system used for tracking changes in source code."
    ]
    
    for doc in docs:
        pipeline.ingest_documents(source=doc, source_type="text")
    
    # Batch queries
    questions = [
        "What is Python?",
        "Which language is used for databases?",
        "What is version control?"
    ]
    
    print("Processing batch queries...")
    results = pipeline.batch_query(questions, top_k=2, return_sources=False)
    
    for i, (question, result) in enumerate(zip(questions, results), 1):
        print(f"\n{i}. Q: {question}")
        print(f"   A: {result['answer'][:150]}...")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("RAG QUERY REWRITE POC - EXAMPLE USAGE")
    print("="*80)
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Query Rewriting Strategies", example_with_query_rewriting),
        ("Query Rewriter Only", example_query_rewriter_only),
        ("Document Ingestion", example_document_ingestion),
        ("Batch Processing", example_batch_processing)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "="*80)
    choice = input("Select example (1-5) or 'all' to run all: ").strip().lower()
    
    if choice == "all":
        for name, func in examples:
            try:
                func()
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
    else:
        print("Invalid choice. Please run again and select 1-5 or 'all'.")
    
    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
