
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