import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
from typing import Generator
import time

from weaviate import WeaviateClient

from agentic.utils.rag_helper import (
    init_weaviate,
    create_collection,
    init_embedding_model,
    search_collection,
    prepare_document_metadata,
    check_document_exists,
    delete_document_from_index,
    get_document_metadata,
    list_documents_in_collection,
    rename_collection,
    list_collections
)
from agentic.utils.file_reader import read_file

@pytest.mark.rag
@pytest.fixture
def temp_weaviate_dir() -> Generator[Path, None, None]:
    """Create temporary directory for Weaviate data"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.mark.rag
@pytest.fixture
def weaviate_client(temp_weaviate_dir: Path) -> Generator[WeaviateClient, None, None]:
    """Initialize Weaviate client with temporary storage"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = init_weaviate()
            yield client
            client.close()
            return
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retry

@pytest.mark.rag
@pytest.fixture
def test_collection(weaviate_client: WeaviateClient) -> str:
    """Create test collection with sample documents"""
    collection_name = "test_collection"
    create_collection(weaviate_client, collection_name)
    collection = weaviate_client.collections.get(collection_name)
    
    # Sample documents for testing
    documents = [
        {
            "content": "Python is a popular programming language known for its simplicity.",
            "filename": "python_intro.txt",
            "document_id": "doc1",
            "chunk_index": 0,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mime_type": "text/plain",
            "source_url": "https://example.com/python",
            "fingerprint": "fp1"
        },
        {
            "content": "Machine learning models require significant training data.",
            "filename": "ml_basics.txt",
            "document_id": "doc2",
            "chunk_index": 0,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mime_type": "text/plain",
            "source_url": "https://example.com/ml",
            "fingerprint": "fp2"
        },
        {
            "content": "Deep learning is a subset of machine learning.",
            "filename": "deep_learning.txt",
            "document_id": "doc3",
            "chunk_index": 0,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mime_type": "text/plain",
            "source_url": "https://example.com/dl",
            "fingerprint": "fp3"
        }
    ]
    
    # Add test documents with vectors
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    with collection.batch.dynamic() as batch:
        for doc in documents:
            vector = list(embed_model.embed([doc["content"]]))[0].tolist()
            batch.add_object(
                properties=doc,
                vector=vector
            )
    
    return collection_name

@pytest.mark.rag
def test_vector_search(weaviate_client: WeaviateClient, test_collection: str):
    """Test vector search functionality"""
    collection = weaviate_client.collections.get(test_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    # Test basic vector search
    results = search_collection(
        collection=collection,
        query="What is Python?",
        embed_model=embed_model,
        limit=2
    )
    
    assert len(results) <= 2
    assert any("Python" in result["content"] for result in results)
    assert all("distance" in result for result in results)
    assert all(result["distance"] is not None for result in results)

@pytest.mark.rag
def test_hybrid_search(weaviate_client: WeaviateClient, test_collection: str):
    """Test hybrid search functionality"""
    collection = weaviate_client.collections.get(test_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    # Test hybrid search
    results = search_collection(
        collection=collection,
        query="machine learning",
        embed_model=embed_model,
        limit=3,
        hybrid=True,
        alpha=0.5
    )
    
    assert len(results) > 0
    assert any("machine learning" in result["content"].lower() for result in results)
    assert all("score" in result for result in results)
    assert all(result["score"] is not None for result in results)

@pytest.mark.rag
def test_filtered_search(weaviate_client: WeaviateClient, test_collection: str):
    """Test search with filters"""
    collection = weaviate_client.collections.get(test_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    # Test search with filename filter
    results = search_collection(
        collection=collection,
        query="learning",
        embed_model=embed_model,
        filters={"filename": "ml_basics.txt"}
    )
    
    assert len(results) > 0
    assert all(result["filename"] == "ml_basics.txt" for result in results)

@pytest.mark.rag
def test_search_empty_collection(weaviate_client: WeaviateClient):
    """Test search on empty collection"""
    empty_collection = "empty_test"
    create_collection(weaviate_client, empty_collection)
    collection = weaviate_client.collections.get(empty_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    results = search_collection(
        collection=collection,
        query="test query",
        embed_model=embed_model
    )
    
    assert len(results) == 0

@pytest.mark.rag
def test_search_with_invalid_filter(weaviate_client: WeaviateClient, test_collection: str):
    """Test search with invalid filter"""
    collection = weaviate_client.collections.get(test_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    # Test with non-existent property
    results = search_collection(
        collection=collection,
        query="test",
        embed_model=embed_model,
        filters={"non_existent_field": "value"}
    )
    
    assert len(results) == 1
    assert "error" in results[0]
    assert "Invalid filter" in results[0]["error"] or "Search failed" in results[0]["error"]

@pytest.mark.rag
def test_hybrid_search_parameters(weaviate_client: WeaviateClient, test_collection: str):
    """Test hybrid search with different alpha values"""
    collection = weaviate_client.collections.get(test_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    # Test with different alpha values
    vector_biased = search_collection(
        collection=collection,
        query="machine learning",
        embed_model=embed_model,
        hybrid=True,
        alpha=0.8
    )
    
    keyword_biased = search_collection(
        collection=collection,
        query="machine learning",
        embed_model=embed_model,
        hybrid=True,
        alpha=0.2
    )
    
    # Results should be different due to different alpha values
    assert vector_biased != keyword_biased

@pytest.mark.rag
def test_search_result_metadata(weaviate_client: WeaviateClient, test_collection: str):
    """Test completeness of search result metadata"""
    collection = weaviate_client.collections.get(test_collection)
    embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
    
    results = search_collection(
        collection=collection,
        query="Python programming",
        embed_model=embed_model,
        limit=1
    )
    
    assert len(results) > 0
    result = results[0]
    
    # Check all required fields are present
    required_fields = [
        "filename",
        "content",
        "source_url",
        "timestamp",
        "distance"
    ]
    
    for field in required_fields:
        assert field in result
        assert result[field] is not None

@pytest.mark.rag
@pytest.fixture
def sample_text_file(tmp_path):
    """Create a sample text file for testing"""
    file_path = tmp_path / "test_doc.txt"
    content = "This is a test document for indexing."
    file_path.write_text(content)
    return str(file_path)

@pytest.mark.rag
@pytest.fixture
def sample_url_content():
    """Mock URL content for testing"""
    return "This is content from a URL"

@pytest.mark.rag
def test_prepare_document_metadata(sample_text_file):
    """Test document metadata preparation"""
    text = "Sample content"
    metadata = prepare_document_metadata(
        file_path=sample_text_file,
        text=text,
        mime_type="text/plain",
        model="test-model"
    )
    
    assert "filename" in metadata
    assert metadata["filename"] == "test_doc.txt"
    assert "document_id" in metadata
    assert "fingerprint" in metadata
    assert metadata["mime_type"] == "text/plain"
    assert metadata["source_url"] == "None"

@pytest.mark.rag
def test_prepare_url_metadata(sample_url_content):
    """Test URL metadata preparation"""
    url = "https://example.com/doc.pdf"
    metadata = prepare_document_metadata(
        file_path=url,
        text=sample_url_content,
        mime_type="application/pdf",
        model="test-model"
    )
    
    assert metadata["filename"] == "doc.pdf"
    assert metadata["source_url"] == url
    assert metadata["mime_type"] == "application/pdf"

@pytest.mark.rag
def test_document_existence_check(weaviate_client: WeaviateClient, test_collection: str):
    """Test document existence checking"""
    collection = weaviate_client.collections.get(test_collection)
    doc_id = "test_doc_id"
    fingerprint = "test_fingerprint"
    
    # Check non-existent document
    exists, status = check_document_exists(collection, doc_id, fingerprint)
    assert not exists
    assert status == "new"
    
    # Add document and check again
    with collection.batch.dynamic() as batch:
        batch.add_object(
            properties={
                "document_id": doc_id,
                "fingerprint": fingerprint,
                "content": "test content"
            },
            vector=[0.1] * 384  # Dummy vector
        )
    
    exists, status = check_document_exists(collection, doc_id, fingerprint)
    assert exists
    assert status == "unchanged"

@pytest.mark.rag
def test_delete_document(weaviate_client: WeaviateClient, test_collection: str):
    """Test document deletion"""
    collection = weaviate_client.collections.get(test_collection)
    doc_id = "doc1"  # From test_collection fixture
    
    # Verify document exists
    assert get_document_metadata(collection, doc_id) is not None
    
    # Delete document
    deleted_count = delete_document_from_index(collection, doc_id, "python_intro.txt")
    assert deleted_count > 0
    
    # Verify deletion
    assert get_document_metadata(collection, doc_id) is None

@pytest.mark.rag
def test_list_documents(weaviate_client: WeaviateClient, test_collection: str):
    """Test document listing"""
    collection = weaviate_client.collections.get(test_collection)
    documents = list_documents_in_collection(collection)
    
    assert len(documents) > 0
    for doc in documents:
        assert "document_id" in doc
        assert "filename" in doc
        assert "timestamp" in doc
        assert "chunk_count" in doc
        assert doc["chunk_count"] > 0

@pytest.mark.rag
def test_show_document(weaviate_client: WeaviateClient, test_collection: str):
    """Test document metadata retrieval"""
    collection = weaviate_client.collections.get(test_collection)
    doc_id = "doc1"  # From test_collection fixture
    
    metadata = get_document_metadata(collection, doc_id)
    assert metadata is not None
    assert metadata["document_id"] == doc_id
    assert metadata["filename"] == "python_intro.txt"
    assert "mime_type" in metadata
    assert "fingerprint" in metadata
    assert "total_chunks" in metadata
    assert metadata["total_chunks"] > 0

@pytest.mark.rag
def test_rename_index(weaviate_client: WeaviateClient, test_collection: str):
    """Test index renaming"""
    new_name = "renamed_collection"
    
    # Ensure target doesn't exist
    if weaviate_client.collections.exists(new_name):
        weaviate_client.collections.delete(new_name)
    
    # Rename collection
    success = rename_collection(weaviate_client, test_collection, new_name)
    assert success
    
    # Verify rename
    assert not weaviate_client.collections.exists(test_collection)
    assert weaviate_client.collections.exists(new_name)
    
    # Check data preservation
    collection = weaviate_client.collections.get(new_name)
    documents = list_documents_in_collection(collection)
    assert len(documents) > 0

@pytest.mark.rag
@pytest.fixture
def test_url() -> str:
    """URL fixture for testing"""
    return "https://raw.githubusercontent.com/deepseek-ai/DeepSeek-R1/refs/heads/main/README.md"

@pytest.mark.rag
def test_list_indexes(weaviate_client: WeaviateClient, test_collection: str):
    """Test index listing"""
    indexes = list_collections(weaviate_client)
    assert len(indexes) > 0
    # Collection names are case-sensitive
    assert test_collection.lower() in [idx.lower() for idx in indexes]

@pytest.mark.rag
def test_url_document_operations(weaviate_client: WeaviateClient, test_collection: str, test_url: str):
    """Test URL document operations including metadata, existence check, and indexing"""
    from agentic.cli import index_file
    
    # Test metadata preparation
    content, mime_type = read_file(test_url)
    assert content is not None
    if test_url.endswith('.md'):
        mime_type = "text/plain"
    
    metadata = prepare_document_metadata(
        file_path=test_url,
        text=content,
        mime_type=mime_type,
        model="openai/gpt-4o-mini"
    )
    
    # Verify metadata
    assert metadata["filename"] == "README.md"
    assert metadata["source_url"] == test_url
    assert metadata["mime_type"] == "text/plain"
    assert "document_id" in metadata
    assert "fingerprint" in metadata
    assert "timestamp" in metadata
    
    # Close the test client before using index_file
    weaviate_client.close()
    
    index_file(
        index_name=test_collection,
        file_path=test_url,
        embedding_model="BAAI/bge-small-en-v1.5",
        chunk_threshold=0.5,
        chunk_delimiters=". ,! ,? ,\n"
    )
    
    client = None
    try:
        client = init_weaviate()
        collection = client.collections.get(test_collection)
        
        # Verify document was indexed
        doc_metadata = get_document_metadata(collection, metadata["document_id"])
        assert doc_metadata is not None
        assert doc_metadata["filename"] == "README.md"
        assert doc_metadata["source_url"] == test_url
        assert doc_metadata["mime_type"] == "text/plain"
        
        # Test searching
        embed_model = init_embedding_model("BAAI/bge-small-en-v1.5")
        results = search_collection(
            collection=collection,
            query="What is DeepSeek-R1?",
            embed_model=embed_model,
            limit=1
        )
        
        assert len(results) > 0
        assert results[0]["source_url"] == test_url
        assert "DeepSeek" in results[0]["content"]
    finally:
        if client:
            client.close() 