def chunk_and_vectorize_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

        # --- Chunking ---
        # Tokenize the text into individual sentences
        text_content = text_content.replace("\n"," ")
        sentences = text_content.split("।")
        print(len(sentences))
        sum_sentence = []
        for i in range(0,len(sentences),8):
            chunk = sentences[i:i+8]
            sum_sentence.append("".join(chunk))
        return sum_sentence
    except:
        print("error")

def search_chunks_multiple_keywords(chunks, keywords):
    # Normalize keywords to lowercase
    keywords = [k.lower() for k in keywords]
    
    # Search for any of the keywords in each chunk
    result = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        if any(k in chunk_lower for k in keywords):
            result.append(chunk)
    return result

