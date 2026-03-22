import random

QUESTIONS_RU = [
    {
        "teaser": "Чему учиться, чтобы AI не сожрал",
        "full": "Какие навыки останутся ценными в ближайшие 10 лет, когда AI умеет почти всё — и как их тренировать?"
    },
    {
        "teaser": "AI вместо сотрудников — реально?",
        "full": "Можно ли уже сейчас заменить часть команды AI-сотрудниками? Какие роли первыми и как оценивать результат?"
    },
    {
        "teaser": "Почему ты боишься хотеть большего",
        "full": "Как воспитывать в себе внутреннее право хотеть большего и перестать занижать планку?"
    },
    {
        "teaser": "Ты оптимист или врёшь себе?",
        "full": "Где проходит граница между стратегическим оптимизмом и самообманом?"
    },
    {
        "teaser": "Где маленькая команда порвёт корпорацию",
        "full": "В каких сферах сегодня малая команда с AI может обойти крупных игроков и почему те туда не дойдут?"
    },
    {
        "teaser": "Отмазки или реальные проблемы?",
        "full": "Как отличить реальные ограничения от отмазок, за которыми ты прячешься?"
    },
    {
        "teaser": "Как понять, что продукт нужен",
        "full": "Как найти и проверить must-have в своём продукте до запуска?"
    },
    {
        "teaser": "Первые деньги за 30 дней",
        "full": "Как пройти путь от идеи до первых платящих пользователей за 30 дней?"
    }
]

QUESTIONS_EN = [
    {
        "teaser": "What to learn before AI eats your job",
        "full": "What skills will remain valuable in the next 10 years when AI can do almost everything — and how to train them?"
    },
    {
        "teaser": "AI replacing employees — real?",
        "full": "Can you already replace part of your team with AI employees? Which roles first and how to measure results?"
    },
    {
        "teaser": "Why you're afraid to want more",
        "full": "How to cultivate the internal right to want more and stop lowering the bar for yourself?"
    },
    {
        "teaser": "Optimist or lying to yourself?",
        "full": "Where do you draw the line between strategic optimism and self-deception?"
    },
    {
        "teaser": "Where small teams beat corporations",
        "full": "What areas can a small team with AI outcompete big players in, and why won't they get there?"
    },
    {
        "teaser": "Excuses or real problems?",
        "full": "How to tell real constraints from excuses you're hiding behind?"
    },
    {
        "teaser": "How to know your product is needed",
        "full": "How to find and validate must-have in your product before launch?"
    },
    {
        "teaser": "First revenue in 30 days",
        "full": "How to go from idea to first paying users in 30 days?"
    }
]

def get_random_questions(lang="ru", count=3):
    """Возвращает случайные вопросы"""
    questions = QUESTIONS_RU if lang == "ru" else QUESTIONS_EN
    selected = random.sample(questions, min(count, len(questions)))
    return selected