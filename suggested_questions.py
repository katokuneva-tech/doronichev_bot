import random

QUESTIONS_RU = [
    {
        "teaser": "Антихрупкие навыки",
        "full": "Какие навыки останутся антихрупкими в ближайшие 10 лет — и как их тренировать еженедельно?"
    },
    {
        "teaser": "Твоя первая AI-команда",
        "full": "Если человек — менеджер виртуальных сотрудников, какие три роли нанять первыми и по каким метрикам их оценивать?"
    },
    {
        "teaser": "Permission to dare",
        "full": "Как воспитывать в себе permission to dare — внутреннее право хотеть большего — и какие маркеры указывают, что оно ослабло?"
    },
    {
        "teaser": "Оптимизм vs самообман",
        "full": "Где для тебя проходит граница между стратегическим оптимизмом и самообманом?"
    },
    {
        "teaser": "Непаханые ниши",
        "full": "В каких сферах сегодня «непаханая целина» для малых команд с ИИ и почему крупные игроки туда не дойдут?"
    },
    {
        "teaser": "Отмазки vs ограничения",
        "full": "Где ты прячешься за «отмазками», а где real constraint?"
    },
    {
        "teaser": "Must-have продукта",
        "full": "Как найти и проверить must-have в своём продукте до запуска?"
    },
    {
        "teaser": "От идеи до первых клиентов",
        "full": "Как пройти путь от идеи до первых платящих пользователей за 30 дней?"
    }
]

QUESTIONS_EN = [
    {
        "teaser": "Antifragile skills",
        "full": "What skills will remain antifragile in the next 10 years — and how to train them weekly?"
    },
    {
        "teaser": "Your first AI team",
        "full": "If you're a manager of virtual employees, which three roles to hire first and what metrics to evaluate them by?"
    },
    {
        "teaser": "Permission to dare",
        "full": "How to cultivate permission to dare — the internal right to want more — and what markers indicate it has weakened?"
    },
    {
        "teaser": "Optimism vs self-deception",
        "full": "Where do you draw the line between strategic optimism and self-deception?"
    },
    {
        "teaser": "Untapped niches",
        "full": "What areas are 'virgin territory' today for small teams with AI and why won't big players reach them?"
    },
    {
        "teaser": "Excuses vs constraints",
        "full": "Where are you hiding behind 'excuses' and where are real constraints?"
    },
    {
        "teaser": "Product must-have",
        "full": "How to find and validate must-have in your product before launch?"
    },
    {
        "teaser": "Idea to first customers",
        "full": "How to go from idea to first paying users in 30 days?"
    }
]

def get_random_questions(lang="ru", count=3):
    """Возвращает случайные вопросы"""
    questions = QUESTIONS_RU if lang == "ru" else QUESTIONS_EN
    selected = random.sample(questions, min(count, len(questions)))
    return selected