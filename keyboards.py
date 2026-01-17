from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Основная клавиатура для меню"""
    keyboard = [
        ["🎫 Новая экскурсия"],
        ["📋 Мои бронирования", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_time_keyboard(booked_times=None):
    """Клавиатура с выбором времени"""
    if booked_times is None:
        booked_times = []
    
    all_times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]
    available_times = [t for t in all_times if t not in booked_times]
    
    # Разбиваем на строки по 3 кнопки
    keyboard = [available_times[i:i+3] for i in range(0, len(available_times), 3)]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def get_confirmation_keyboard():
    """Клавиатура для подтверждения"""
    keyboard = [["✅ Подтвердить", "❌ Отменить"]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def get_weekday_keyboard():
    """Клавиатура для выбора дня недели"""
    keyboard = [
        ["Вторник", "Среда", "Четверг"],
        ["📅 Ввести другую дату"]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)