import bn
import re
from extract_data import pdf_to_images, extract_text_from_images
from chuck_text import chunk_and_vectorize_text,search_chunks_multiple_keywords
from ai_system import output_get


def firstly(pdf_file):
    images = pdf_to_images(pdf_file)
    bangla_text = extract_text_from_images(images)
    with open("extract_data2.txt", "w", encoding="utf-8") as f:
        f.write(bangla_text)

    print("✅ Done! Bangla text saved to 'extract_data2.txt'")

def secondly():
    # --- Example Usage ---
    file_path = "extract_data2.txt"
    chunks = chunk_and_vectorize_text(file_path)

    return chunks


def thirdly(question,chunks):
    st=bn.remove_stopwords(question)
    words = bn.tokenizer(st) # or bn.tokenizer(text, 'word')
    found_chunks = search_chunks_multiple_keywords(chunks, words)
    result_al = []
    for i, chunk in enumerate(found_chunks):
        result_al.append(chunk)
    result = output_get(result_al,question)
    print(result)

#give pdf file and question
pdf = "HSC.pdf"  
question = "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?"
chunks=secondly()
thirdly(question,chunks)


