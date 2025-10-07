"""
Query Helper Script
Query the RAG system easily from command line
"""
import sys
from rag_pipeline import create_pipeline


def query(question: str, enable_rewrite: bool = True):
    """Query the RAG system"""
    print("\n" + "="*60)
    print("🔍 RAG Query System")
    print("="*60 + "\n")
    
    print(f"Question: {question}\n")
    print("Processing...\n")
    
    pipeline = create_pipeline(enable_rewrite=enable_rewrite)
    
    try:
        result = pipeline.query(
            question=question,
            top_k=5,
            return_sources=True
        )
        
        print("="*60)
        print("💡 ANSWER")
        print("="*60)
        print(result['answer'])
        print()
        
        if result.get('metadata', {}).get('query_rewrite'):
            rewrite_info = result['metadata']['query_rewrite']
            print("\n" + "="*60)
            print("🔄 Query Rewriting")
            print("="*60)
            print(f"Strategy: {rewrite_info['strategy']}")
            print(f"Queries generated: {rewrite_info['num_queries']}")
            if rewrite_info.get('queries'):
                print("\nRewritten queries:")
                for i, q in enumerate(rewrite_info['queries'][:3], 1):
                    print(f"  {i}. {q}")
        
        if result.get('sources'):
            print("\n" + "="*60)
            print("📚 Sources")
            print("="*60)
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"\n{i}. Score: {source['relevance_score']:.4f}")
                print(f"   Source: {source['metadata'].get('source', 'Unknown')}")
                print(f"   Content: {source['content'][:150]}...")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error querying system: {e}")
        sys.exit(1)


def main():
    """Main query interface"""
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("🔍 RAG Query Helper")
        print("="*60)
        print("\nUsage:")
        print('  python query_system.py "Your question here"')
        print("\nExamples:")
        print('  python query_system.py "What is machine learning?"')
        print('  python query_system.py "How does RAG work?"')
        print("\nOptions:")
        print("  Add --no-rewrite to disable query rewriting")
        print('  python query_system.py "Your question" --no-rewrite')
        sys.exit(1)
    
    question = sys.argv[1]
    enable_rewrite = "--no-rewrite" not in sys.argv
    
    query(question, enable_rewrite)


if __name__ == "__main__":
    main()
