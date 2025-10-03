import chromadb

print("Проверяем векторную базу...")

client = chromadb.PersistentClient(path="./doronichev_vectordb")
collection = client.get_collection("doronichev_knowledge")

count = collection.count()
print(f"Найдено {count} чанков в базе")

if count > 0:
    results = collection.query(query_texts=["продукт"], n_results=2)
    
    print("\nПоиск по слову 'продукт':")
    for i, doc in enumerate(results['documents'][0]):
        metadata = results['metadatas'][0][i] 
        print(f"\n{i+1}. Файл: {metadata['source_file']}")
        print(f"   Текст: {doc[:150]}...")
    
    print("\nВекторная база работает!")
else:
    print("База пуста")
