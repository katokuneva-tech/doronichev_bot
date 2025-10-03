import chromadb
import openai
import os
from dotenv import load_dotenv

load_dotenv()

print("Проверяем векторную базу...")

# Настройка OpenAI  
openai.api_key = os.getenv("OPENAI_API_KEY")
client_openai = openai.OpenAI()

# Подключение к базе
client_chroma = chromadb.PersistentClient(path="./doronichev_vectordb")
collection = client_chroma.get_collection("doronichev_knowledge")

count = collection.count()
print(f"Найдено {count} чанков в базе")

if count > 0:
    # Создаем эмбеддинг с той же моделью что использовалась при создании базы
    response = client_openai.embeddings.create(
        input="продукт",
        model="text-embedding-3-large"  # Та же модель что в rag_preparation.py
    )
    query_embedding = response.data[0].embedding
    
    # Поиск с использованием эмбеддинга
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    print("\nПоиск по слову 'продукт':")
    for i, doc in enumerate(results['documents'][0]):
        metadata = results['metadatas'][0][i]
        print(f"\n{i+1}. Файл: {metadata['source_file']}")
        print(f"   Текст: {doc[:200]}...")
    
    print("\nВекторная база работает!")
else:
    print("База пуста")
