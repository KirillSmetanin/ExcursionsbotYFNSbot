import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")

# Конфигурация базы данных
DB_PATH = "excursions.db"

# Конфигурация времени экскурсий
WORKING_DAYS = [1, 2, 3]  # 0=Понедельник, 1=Вторник, 2=Среда, 3=Четверг...
WORKING_HOURS_START = 10  # 10:00
WORKING_HOURS_END = 15    # 15:00

# Форматы даты и времени
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DISPLAY_DATE_FORMAT = "%d.%m.%Y"

# Сообщения об ошибках
ERROR_MESSAGES = {
    'invalid_day': "❌ Экскурсии проводятся только по вторникам, средам и четвергам. Выберите другой день.",
    'invalid_time': f"❌ Экскурсии проводятся с {WORKING_HOURS_START}:00 до {WORKING_HOURS_END}:00. Выберите другое время.",
    'time_taken': "⏰ Это время уже занято. Пожалуйста, выберите другое время.",
    'date_passed': "❌ Нельзя выбрать прошедшую дату.",
    'db_error': "⚠️ Произошла ошибка при сохранении данных. Попробуйте позже."
}