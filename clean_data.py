"""
Скрипт для очистки данных перед индексацией в RAG.
1. Конвертирует RTF в plain text
2. Прогоняет грязные субтитры через GPT для очистки
3. Сохраняет чистые файлы в data_clean/
"""

import os
import re
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

DATA_DIR = "./data"
CLEAN_DIR = "./data_clean"


def rtf_to_text(filepath):
    """Конвертация RTF в plain text через textutil (macOS)."""
    try:
        result = subprocess.run(
            ["textutil", "-convert", "txt", "-stdout", filepath],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass

    # Фоллбэк: грубая очистка RTF-тегов
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Декодируем unicode escapes типа \u1051
    def decode_unicode(match):
        return chr(int(match.group(1)))
    content = re.sub(r'\\u(\d+)\s?', decode_unicode, content)
    # Убираем RTF-теги
    content = re.sub(r'\\[a-z]+\d*\s?', '', content)
    content = re.sub(r'[{}]', '', content)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()


def is_rtf(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read(5) == '{\\rtf'


def clean_subtitles_with_gpt(text, filename):
    """Очищает субтитры через GPT: убирает мусор, восстанавливает пунктуацию."""
    # Разбиваем на куски по ~8000 символов
    chunks = []
    for i in range(0, len(text), 8000):
        chunks.append(text[i:i+8000])

    cleaned_parts = []
    for i, chunk in enumerate(chunks):
        print(f"  Очистка части {i+1}/{len(chunks)}...")
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": (
                        "Ты получаешь фрагмент автоматических субтитров из YouTube-интервью. "
                        "Твоя задача:\n"
                        "1. Убрать мусор: [музыка], [аплодисменты], таймкоды, пометки\n"
                        "2. Восстановить пунктуацию и заглавные буквы\n"
                        "3. Убрать слова-паразиты (эм, ну, типа, вот) если они не несут смысла\n"
                        "4. Исправить очевидные ошибки распознавания речи\n"
                        "5. Разбить на абзацы по смыслу\n"
                        "6. Сохранить ВСЁ содержание — не сокращай, не пересказывай, не добавляй от себя\n"
                        "7. Если есть реплики разных спикеров — обозначь их (Интервьюер: / Андрей:)\n"
                        "Верни только очищенный текст, без комментариев."
                    )},
                    {"role": "user", "content": chunk}
                ],
                max_tokens=10000,
                temperature=0.1
            )
            cleaned_parts.append(response.choices[0].message.content)
        except Exception as e:
            print(f"  Ошибка GPT: {e}, оставляю как есть")
            cleaned_parts.append(chunk)

    return "\n\n".join(cleaned_parts)


def basic_clean(text):
    """Базовая очистка для уже чистых текстов."""
    text = re.sub(r'\[музыка\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[аплодисменты\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+:\d+:\d+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def is_dirty_subtitles(text):
    """Проверяет, похож ли текст на грязные субтитры."""
    lines = text.strip().split('\n')
    if not lines:
        return False
    # Субтитры: много коротких строк без пунктуации
    short_lines = sum(1 for l in lines[:50] if len(l.strip()) < 60)
    no_periods = sum(1 for l in lines[:50] if '.' not in l and '!' not in l and '?' not in l)
    return short_lines > 30 or no_periods > 35


def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
    print(f"Найдено {len(files)} файлов\n")

    for filename in sorted(files):
        filepath = os.path.join(DATA_DIR, filename)
        clean_path = os.path.join(CLEAN_DIR, filename)

        print(f"📄 {filename}")

        # Определяем тип файла
        if is_rtf(filepath):
            print("  → RTF, конвертирую...")
            text = rtf_to_text(filepath)
            text = basic_clean(text)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

        # Проверяем, нужна ли GPT-очистка
        if is_dirty_subtitles(text):
            print(f"  → Грязные субтитры ({len(text)} символов), очищаю через GPT...")
            text = clean_subtitles_with_gpt(text, filename)
        else:
            print("  → Текст чистый, базовая очистка")
            text = basic_clean(text)

        # Сохраняем
        with open(clean_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  ✅ Сохранено ({len(text)} символов)\n")

    print(f"Готово! Чистые файлы в {CLEAN_DIR}/")
    print("Теперь запусти rag_preparation.py с путём к data_clean/")


if __name__ == "__main__":
    main()
