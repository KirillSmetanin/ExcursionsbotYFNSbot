# В bot.py добавьте импорт
from database import db, init_db
from config import BOT_TOKEN, WORKING_DAYS, WORKING_HOURS_START, WORKING_HOURS_END

# В функции main() или перед запуском бота
async def main():
    # Инициализируем базу данных
    await init_db()
    
    # Пример использования функций
    is_available = await db.is_time_available("2024-12-25", "14:30")
    
    # Добавление брони
    success = await db.add_booking(
        user_id=123456789,
        username="user123",
        school_name="Гимназия №1",
        class_number="10А",
        class_profile="Физико-математический",
        excursion_date="2024-12-25",
        excursion_time="14:30",
        contact_person="Иванов Иван Иванович",
        contact_phone="+79161234567",
        participants_count=25
    )