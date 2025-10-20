"""
Document Upload Helper Script
Upload documents to the RAG system easily
"""
import sys
import os
from pathlib import Path
from rag_pipeline import create_pipeline
from loguru import logger

def upload_file(file_path: str):
    """Upload a single file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    pipeline = create_pipeline(enable_rewrite=True)
    
    try:
        result = pipeline.ingest_documents(
            source=file_path,
            source_type="file"
        )
        
        if result["success"]:
            print(f"✅ Successfully uploaded: {file_path}")
            print(f"   Chunks created: {result['chunks_added']}")
            return True
        else:
            print(f"❌ Failed to upload: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {e}")
        return False


def upload_directory(directory_path: str):
    """Upload all supported files from a directory"""
    if not os.path.exists(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        return
    
    pipeline = create_pipeline(enable_rewrite=True)
    
    try:
        result = pipeline.ingest_documents(
            source=directory_path,
            source_type="directory"
        )
        
        if result["success"]:
            print(f"✅ Successfully uploaded directory: {directory_path}")
            print(f"   Total chunks created: {result['chunks_added']}")
        else:
            print(f"❌ Failed to upload directory: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error uploading directory: {e}")


def upload_text(text: str, metadata: dict = None):
    """Upload raw text"""
    pipeline = create_pipeline(enable_rewrite=True)
    
    try:
        result = pipeline.ingest_documents(
            source=text,
            source_type="text"
        )
        
        if result["success"]:
            print(f"✅ Successfully uploaded text")
            print(f"   Chunks created: {result['chunks_added']}")
        else:
            print(f"❌ Failed to upload text: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error uploading text: {e}")


def main():
    """Main upload interface"""
    print("\n" + "="*60)
    print("📄 RAG Document Upload Helper")
    print("="*60 + "\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python upload_documents.py <file_or_directory_path>")
        print("\nExamples:")
        print("  python upload_documents.py document.pdf")
        print("  python upload_documents.py ./documents/")
        print("  python upload_documents.py \"C:/Users/Name/Documents/file.docx\"")
        print("\nSupported formats: PDF, TXT, DOCX, Markdown")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        print(f"📄 Uploading file: {path}\n")
        upload_file(path)
    elif os.path.isdir(path):
        print(f"📁 Uploading directory: {path}\n")
        upload_directory(path)
    else:
        print(f"❌ Path not found: {path}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✨ Upload complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
