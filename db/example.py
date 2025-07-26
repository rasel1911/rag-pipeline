import requests
import json
import uuid

# Base URL of your FastAPI application
BASE_URL = "http://localhost:8000"

def create_sample_chunk():
    """Create a sample data chunk"""
    sample_data = {
        "chunk_id": 3,
        "source_file": "sample_document.pdf",
        "chunk_text": "This is a sample text chunk for testing purposes.",
        "token_count": 10,
        "start_unit": 0,
        "end_unit": 46,
        "embedding_model": "text-embedding-ada-002",
        "embedding": "[0.1, 0.2, 0.3, 0.4, 0.5]"
    }
    
    response = requests.post(f"{BASE_URL}/chunks/", json=sample_data)
    if response.status_code == 200:
        print("✅ Chunk created successfully!")
        chunk_data = response.json()
        print(f"Created chunk with ID: {chunk_data['id']}")
        return chunk_data['id']
    else:
        print(f"❌ Error creating chunk: {response.text}")
        return None

def get_all_chunks():
    """Get all data chunks"""
    response = requests.get(f"{BASE_URL}/chunks/")
    if response.status_code == 200:
        chunks = response.json()
        print(chunks)
        print(f"✅ Retrieved {len(chunks)} chunks")
        for chunk in chunks:
            print(f"  - ID: {chunk['id']}, Source: {chunk['source_file']}")
        return chunks
    else:
        print(f"❌ Error retrieving chunks: {response.text}")
        return []

def get_chunk_by_id(chunk_id):
    """Get a specific chunk by ID"""
    response = requests.get(f"{BASE_URL}/chunks/{chunk_id}")
    if response.status_code == 200:
        chunk = response.json()
        print(f"✅ Retrieved chunk: {chunk['source_file']}")
        return chunk
    else:
        print(f"❌ Error retrieving chunk: {response.text}")
        return None

def update_chunk(chunk_id):
    """Update a data chunk"""
    update_data = {
        "chunk_text": "This is an updated text chunk with new content.",
        "token_count": 12
    }
    
    response = requests.put(f"{BASE_URL}/chunks/{chunk_id}", json=update_data)
    if response.status_code == 200:
        chunk = response.json()
        print(f"✅ Chunk updated successfully!")
        print(f"New text: {chunk['chunk_text']}")
        return chunk
    else:
        print(f"❌ Error updating chunk: {response.text}")
        return None

def delete_chunk(chunk_id):
    """Delete a data chunk"""
    response = requests.delete(f"{BASE_URL}/chunks/{chunk_id}")
    if response.status_code == 200:
        print(f"✅ Chunk deleted successfully!")
        return True
    else:
        print(f"❌ Error deleting chunk: {response.text}")
        return False

def main():
    """Demonstrate all CRUD operations"""
    print("🚀 Testing Data Chunks API")
    print("-" * 40)
    
    # Create
    print("\n1. Creating a new chunk...")
    chunk_id = create_sample_chunk()
    
    if not chunk_id:
        print("Failed to create chunk. Exiting.")
        return
    
    # Read (single)
    print(f"\n2. Getting chunk by ID: {chunk_id}")
    get_chunk_by_id(chunk_id)
    
    # Read (all)
    print("\n3. Getting all chunks...")
    get_all_chunks()
    
    # Update
    #print(f"\n4. Updating chunk: {chunk_id}")
    #update_chunk(chunk_id)
    
    # Read (after update)
    #print(f"\n5. Getting updated chunk: {chunk_id}")
    #get_chunk_by_id(chunk_id)
    
    # Delete
    #print(f"\n6. Deleting chunk: {chunk_id}")
    #delete_chunk(chunk_id)
    
    # Verify deletion
    print("\n7. Verifying deletion...")
    get_all_chunks()
    
    print("\n✅ All operations completed!")

if __name__ == "__main__":
    main()

# Alternative using curl commands:
"""
# Create a chunk
curl -X POST "http://localhost:8000/chunks/" \
     -H "Content-Type: application/json" \
     -d '{
       "chunk_id": 1,
       "source_file": "test.pdf",
       "chunk_text": "Sample text",
       "token_count": 5,
       "start_unit": 0,
       "end_unit": 11,
       "embedding_model": "ada-002",
       "embedding": "[0.1, 0.2]"
     }'

# Get all chunks
curl -X GET "http://localhost:8000/chunks/"

# Get specific chunk
curl -X GET "http://localhost:8000/chunks/{chunk-id}"

# Update chunk
curl -X PUT "http://localhost:8000/chunks/{chunk-id}" \
     -H "Content-Type: application/json" \
     -d '{"chunk_text": "Updated text"}'

# Delete chunk
curl -X DELETE "http://localhost:8000/chunks/{chunk-id}"
"""