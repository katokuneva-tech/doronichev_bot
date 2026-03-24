# Установи зависимости:
# pip install openai chromadb langchain langchain-text-splitters python-dotenv

import os
import re
import json
from datetime import datetime
from typing import List, Dict
import openai
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class DoronichevRAGPreparation:
    def __init__(self):
        # Настройка OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        
        # Настройка ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./doronichev_vectordb")
        
        # Создание или получение коллекции
        try:
            self.collection = self.chroma_client.get_collection("doronichev_knowledge")
        except:
            self.collection = self.chroma_client.create_collection(
                name="doronichev_knowledge",
                metadata={"description": "Knowledge base from Andrey Doronichev interviews and content"}
            )
        
        # Настройка сплиттера текста
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    
    def clean_transcription_text(self, text: str) -> str:
        """Очистка текста от артефактов транскрибации"""
        # Удаление временных меток
        text = re.sub(r'\d+:\d+:\d+', '', text)
        text = re.sub(r'\[\d+:\d+:\d+\]', '', text)
        
        # Удаление заполнителей речи
        text = re.sub(r'\b(эм|мм|хм|э-э-э|м-м-м)\b', '', text, flags=re.IGNORECASE)
        
        # Удаление повторяющихся знаков препинания
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\?{2,}', '?', text)
        text = re.sub(r'!{2,}', '!', text)
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        # Удаление скобок с пометками типа [неразборчиво], [смех]
        text = re.sub(r'\[.*?\]', '', text)
        
        return text.strip()
    
    def determine_content_type(self, filename: str, text: str) -> str:
        """Определение типа контента по имени файла и содержимому"""
        filename_lower = filename.lower()
        
        if 'interview' in filename_lower or 'интервью' in filename_lower:
            return 'interview'
        elif 'telegram' in filename_lower or 'tg' in filename_lower or 'канал' in filename_lower:
            return 'telegram'
        elif 'post' in filename_lower or 'пост' in filename_lower:
            return 'social_media'
        else:
            # Попытка определить по содержимому
            if len(text) > 10000:  # Длинные тексты скорее всего интервью
                return 'interview'
            else:
                return 'other'
    
    def extract_metadata_from_filename(self, filename: str) -> Dict:
        """Извлечение метаданных из имени файла"""
        metadata = {
            'source_file': filename,
            'processed_date': datetime.now().isoformat()
        }
        
        # Попытка извлечь дату из имени файла
        date_patterns = [
            r'(\d{4}[-_]\d{2}[-_]\d{2})',  # 2024-01-01 или 2024_01_01
            r'(\d{2}[-_]\d{2}[-_]\d{4})',  # 01-01-2024 или 01_01_2024
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                metadata['content_date'] = match.group(1)
                break
        
        # Попытка извлечь номер интервью
        interview_match = re.search(r'interview[_\-]?(\d+)|интервью[_\-]?(\d+)', filename, re.IGNORECASE)
        if interview_match:
            metadata['interview_number'] = interview_match.group(1) or interview_match.group(2)
        
        return metadata
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Создание эмбеддингов с помощью OpenAI"""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model="text-embedding-3-large"  # или "text-embedding-ada-002" для экономии
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Ошибка создания эмбеддингов: {e}")
            return []
    
    def process_file(self, file_path: str) -> List[Dict]:
        """Обработка одного файла"""
        filename = os.path.basename(file_path)
        print(f"Обрабатываю файл: {filename}")
        
        # Чтение файла
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Пробуем другую кодировку
            with open(file_path, 'r', encoding='cp1251') as f:
                content = f.read()
        
        # Очистка текста
        cleaned_content = self.clean_transcription_text(content)
        
        # Определение типа контента
        content_type = self.determine_content_type(filename, cleaned_content)
        
        # Извлечение базовых метаданных
        base_metadata = self.extract_metadata_from_filename(filename)
        base_metadata['content_type'] = content_type
        
        # Разбивка на чанки
        chunks = self.text_splitter.split_text(cleaned_content)
        
        # Подготовка данных для векторизации
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['chunk_id'] = f"{filename}_chunk_{i}"
            
            processed_chunks.append({
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        print(f"Файл {filename} разбит на {len(chunks)} чанков")
        return processed_chunks
    
    def add_to_vectordb(self, processed_chunks: List[Dict]):
        """Добавление чанков в векторную базу"""
        if not processed_chunks:
            return
        
        # Подготовка данных для ChromaDB
        texts = [chunk['text'] for chunk in processed_chunks]
        metadatas = [chunk['metadata'] for chunk in processed_chunks]
        ids = [metadata['chunk_id'] for metadata in metadatas]
        
        # Создание эмбеддингов
        print("Создаю эмбеддинги...")
        embeddings = self.create_embeddings(texts)
        
        if not embeddings:
            print("Ошибка создания эмбеддингов!")
            return
        
        # Добавление в ChromaDB
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Добавлено {len(texts)} чанков в векторную базу")
        except Exception as e:
            print(f"Ошибка добавления в векторную базу: {e}")
    
    def process_directory(self, directory_path: str):
        """Обработка всех txt файлов в директории"""
        txt_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
        
        if not txt_files:
            print(f"В директории {directory_path} не найдено txt файлов")
            return
        
        print(f"Найдено {len(txt_files)} txt файлов")
        
        all_chunks = []
        for filename in txt_files:
            file_path = os.path.join(directory_path, filename)
            chunks = self.process_file(file_path)
            all_chunks.extend(chunks)
        
        # Добавление всех чанков в векторную базу батчами
        batch_size = 50  # Обрабатываем по 50 чанков за раз
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            print(f"Обрабатываю батч {i//batch_size + 1}/{(len(all_chunks)-1)//batch_size + 1}")
            self.add_to_vectordb(batch)
        
        print(f"Обработка завершена! Всего обработано {len(all_chunks)} чанков")
    
    def get_collection_stats(self):
        """Получение статистики по коллекции"""
        count = self.collection.count()
        print(f"В векторной базе содержится {count} чанков")
        
        # Получение примера данных для проверки
        if count > 0:
            sample = self.collection.peek(limit=1)
            print("Пример чанка:")
            print(f"ID: {sample['ids'][0]}")
            print(f"Метаданные: {sample['metadatas'][0]}")
            print(f"Первые 200 символов: {sample['documents'][0][:200]}...")

def main():
    """Основная функция для запуска обработки"""
    import sys

    # Флаг --rebuild для пересоздания коллекции с нуля
    rebuild = "--rebuild" in sys.argv

    # Создаем экземпляр класса
    rag_prep = DoronichevRAGPreparation()

    if rebuild:
        print("🗑️  Удаляю старую коллекцию...")
        try:
            rag_prep.chroma_client.delete_collection("doronichev_knowledge")
            rag_prep.collection = rag_prep.chroma_client.create_collection(
                name="doronichev_knowledge",
                metadata={"description": "Knowledge base from Andrey Doronichev interviews and content"}
            )
            print("✅ Коллекция пересоздана")
        except Exception as e:
            print(f"Ошибка: {e}")

    # Используем очищенные данные если есть, иначе оригинальные
    data_directory = "./data_clean" if os.path.exists("./data_clean") else "./data"
    print(f"Используем данные из: {data_directory}")
    
    # Проверяем существование директории
    if not os.path.exists(data_directory):
        print(f"Директория {data_directory} не существует!")
        print("Создай папку 'data' и помести туда свои txt файлы")
        return
    
    # Обрабатываем все файлы
    rag_prep.process_directory(data_directory)
    
    # Показываем статистику
    rag_prep.get_collection_stats()

if __name__ == "__main__":
    main()
