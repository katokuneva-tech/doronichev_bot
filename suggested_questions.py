import random

QUESTIONS_RU = [
    "Где для тебя проходит граница между стратегическим оптимизмом и самообманом?",
    "Как ты отличаешь «игру» как среду обучения от дофаминовой прокрастинации?",
    "Какие навыки останутся антихрупкими в ближайшие 10 лет — и как их тренировать еженедельно?",
    "Если человек — менеджер виртуальных сотрудников, какие три роли нанять первыми и по каким метрикам их оценивать?",
    "В каких сферах сегодня «непаханая целина» для малых команд с ИИ и почему крупные игроки туда не дойдут?",
    "Как воспитывать в себе permission to dare — внутреннее право хотеть большего — и какие маркеры указывают, что оно ослабло?",
    "Где ты прячешься за «отмазками», а где реально двигаешься?"
]

QUESTIONS_EN = [
    "Where do you draw the line between strategic optimism and self-deception?",
    "How do you distinguish 'play' as a learning environment from dopamine-driven procrastination?",
    "What skills will remain antifragile in the next 10 years — and how to train them weekly?",
    "If you're managing virtual employees, which three roles to hire first and what metrics to evaluate them by?",
    "Which areas are 'untapped territory' for small AI-powered teams today, and why won't big players reach them?",
    "How to cultivate permission to dare — the internal right to want more — and what markers show it's weakening?",
    "Where are you hiding behind excuses, and where are you actually moving forward?"
]

def get_random_questions(language="ru", count=3):
    """Получить случайные вопросы на указанном языке"""
    questions = QUESTIONS_RU if language == "ru" else QUESTIONS_EN
    return random.sample(questions, min(count, len(questions)))
