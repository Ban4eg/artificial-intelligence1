import re
import random
import datetime
import webbrowser
import requests
import spacy
from googletrans import Translator
from textblob import TextBlob


nlp = spacy.load("ru_core_news_sm")
translator = Translator()

API_KEY = "16096f9c40048c4f62d4bdba2b5f73ce"

DAYS_RU = {
    "Monday": "понедельник",
    "Tuesday": "вторник",
    "Wednesday": "среда",
    "Thursday": "четверг",
    "Friday": "пятница",
    "Saturday": "суббота",
    "Sunday": "воскресенье",
}


def log_dialog(user_input, bot_response):
    with open("chat_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"Пользователь: {user_input}\n")
        log_file.write(f"Бот: {bot_response}\n")
        log_file.write("-" * 40 + "\n")


def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Открываю браузер с результатами поиска: {query}"


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        return f"В городе {city} сейчас {weather_desc} и {temp}°C."
    else:
        return "Не удалось получить информацию о погоде. Попробуйте указать другой город."

def analyze_sentiment(text):
    try:
        translated = translator.translate(text, dest="en").text
        polarity = TextBlob(translated).sentiment.polarity
    except Exception:
        return "Хм... сложно понять твоё настроение. Но я здесь, если что 😊"

    if polarity > 0.3:
        return "Ты звучишь очень позитивно! 😄 Чем могу порадовать тебя ещё?"
    elif polarity < -0.3:
        return "Ты, похоже, не в настроении... 😔 Хочешь поговорить об этом?"
    else:
        return "Улавливаю нейтральный настрой. Спрашивай, если что-нибудь нужно!"

def process_text(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_punct]


responses = {
    r"\bпривет\b": [
        "Привет-привет! 😊 Как твои дела?",
        "Здравствуйте! Чем могу помочь сегодня?",
        "Йо! Рад тебя видеть!",
    ],
    r"\bкак\b.*\bзвать\b": [
        "Я Олег, твой виртуальный помощник. А тебя как зовут?",
        "Меня зовут Олег. В любой момент обращайся!",
    ],
    r"\bнастоящий\b|\bживой\b|\bчеловек\b": [
        "Я пока не человек... но уже с характером! 😏",
        "Почти! Только не пью чай и не хожу в магазин 😄",
    ],
    r"\bдело\b|\bновый\b": [
        "Всё отлично, спасибо что спросил! 😊 А у тебя как?",
        "Жизнь прекрасна, особенно когда ты пишешь мне! Как сам?",
    ],
    r"\bуметь\b": [
        "Я могу рассказать дату, время, узнать погоду, провести поиск и даже понять твоё настроение!",
        "Я здесь, чтобы помогать — погода, время, настроение, поиск... или просто поболтать 😊",
    ],
    r"\bспасибо\b|\bблагодарить\b": [
        "Рад помочь! Обращайся в любое время 😊",
        "Всегда пожалуйста! Чем ещё могу быть полезен?",
    ],
    r"\bпока\b|\bсвидание\b": [
        "До встречи! Надеюсь, скоро снова поболтаем 👋",
        "Пока! Береги себя!",
    ],
    r"\bвремя\b|\bчас\b": lambda _: datetime.datetime.now().strftime("Сейчас %H:%M."),
    r"\bчисло\b|\bдата\b": lambda _: datetime.datetime.now().strftime("Сегодня %d.%m.%Y."),
    r"\bдень\b.*\bнеделя\b": lambda _: f"Сегодня {DAYS_RU[datetime.datetime.now().strftime('%A')]}.",
    r"\bпогода\b.*\bв\b\s+(\w+)": lambda m: get_weather(m.group(1)),
    r"\bпоиск\b\s+(.+)": lambda m: search_web(m.group(1)),
}

def chatbot_response(text):
    original_text = text
    text = text.lower()
    lemmas = process_text(text)
    lemmatized_text = " ".join(lemmas)

    for pattern, response in responses.items():
        match = re.search(pattern, lemmatized_text)
        if match:
            if callable(response):
                reply = response(match)
            elif isinstance(response, list):
                reply = random.choice(response)
            else:
                reply = response
            log_dialog(original_text, reply)
            return reply

    reply = analyze_sentiment(original_text)
    log_dialog(original_text, reply)
    return reply

if __name__ == "__main__":
    print("Введите 'выход' для завершения диалога.")
    while True:
        user_input = input("Вы: ")
        if user_input.lower() in ("выход", "пока"):
            farewell = random.choice(["До свидания!", "Пока-пока!", "До скорого общения!"])
            print("Бот:", farewell)
            log_dialog(user_input, farewell)
            break
        bot_reply = chatbot_response(user_input)
        print("Бот:", bot_reply)
