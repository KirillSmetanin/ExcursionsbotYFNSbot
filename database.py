import aiosqlite
import datetime
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Путь к файлу базы данных
DB_PATH = "excursions.db"

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        
    async def init_db(self) -> None:
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    school_name TEXT NOT NULL,
                    class_number TEXT NOT NULL,
                    class_profile TEXT,
                    excursion_date DATE NOT NULL,
                    excursion_time TEXT NOT NULL,
                    contact_person TEXT NOT NULL,
                    contact_phone TEXT NOT NULL,
                    participants_count INTEGER NOT NULL,
                    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(excursion_date, excursion_time)
                )
            ''')
            
            # Создаем индекс для быстрого поиска по дате
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_excursion_date 
                ON bookings(excursion_date)
            ''')
            
            await db.commit()
            logger.info("База данных инициализирована")

    async def add_booking(
        self,
        user_id: int,
        username: str,
        school_name: str,
        class_number: str,
        class_profile: str,
        excursion_date: str,  # В формате 'YYYY-MM-DD'
        excursion_time: str,  # В формате 'HH:MM'
        contact_person: str,
        contact_phone: str,
        participants_count: int
    ) -> bool:
        """
        Добавление новой брони экскурсии.
        Возвращает True если успешно, False если время на эту дату уже занято.
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, свободно ли время на эту дату
                is_available = await self.is_time_available(excursion_date, excursion_time)
                
                if not is_available:
                    return False
                
                # Добавляем новую запись
                await db.execute('''
                    INSERT INTO bookings (
                        user_id, username, school_name, class_number, class_profile,
                        excursion_date, excursion_time, contact_person, 
                        contact_phone, participants_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, username, school_name, class_number, class_profile,
                    excursion_date, excursion_time, contact_person,
                    contact_phone, participants_count
                ))
                
                await db.commit()
                logger.info(f"Добавлена новая бронь от пользователя {username} на {excursion_date} {excursion_time}")
                return True
                
        except aiosqlite.IntegrityError:
            logger.warning(f"Попытка добавить дублирующую бронь на {excursion_date} {excursion_time}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении брони: {e}")
            return False

    async def is_time_available(self, excursion_date: str, excursion_time: str) -> bool:
        """
        Проверяет, свободно ли время на указанную дату.
        Возвращает True если время свободно.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM bookings 
                WHERE excursion_date = ? AND excursion_time = ?
            ''', (excursion_date, excursion_time))
            
            result = await cursor.fetchone()
            count = result[0] if result else 0
            
            return count == 0
        
    async def is_date_available(self, date_str):
        """Проверяет, свободна ли дата (может быть только одна экскурсия в день)"""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT COUNT(*) FROM bookings WHERE excursion_date = ?",
                (date_str,)
            )
            result = await cursor.fetchone()
            return result[0] == 0

    async def get_booked_slots_for_date(self, date: str) -> List[str]:
        """
        Возвращает список занятых временных слотов на указанную дату.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT excursion_time FROM bookings 
                WHERE excursion_date = ?
                ORDER BY excursion_time
            ''', (date,))
            
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        
    async def get_booking_by_date(self, date_str):
        """Получает бронирование по дате (только одно на дату)"""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                """SELECT * FROM bookings 
                WHERE excursion_date = ? 
                ORDER BY booking_date DESC 
                LIMIT 1""",
                (date_str,)
            )
            return await cursor.fetchone()

    async def get_booked_dates(self) -> List[str]:
        """
        Возвращает список дат, на которые есть бронирования.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT DISTINCT excursion_date FROM bookings 
                WHERE excursion_date >= date('now')
                ORDER BY excursion_date
            ''')
            
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_user_bookings(self, user_id: int) -> List[Tuple]:
        """
        Возвращает список бронирований пользователя.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT 
                    id, school_name, class_number, excursion_date, 
                    excursion_time, contact_person, participants_count
                FROM bookings 
                WHERE user_id = ? AND excursion_date >= date('now')
                ORDER BY excursion_date, excursion_time
            ''', (user_id,))
            
            return await cursor.fetchall()

    async def cancel_booking(self, booking_id: int, user_id: int) -> bool:
        """
        Отмена бронирования пользователем.
        Возвращает True если отмена успешна.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                DELETE FROM bookings 
                WHERE id = ? AND user_id = ?
            ''', (booking_id, user_id))
            
            await db.commit()
            return cursor.rowcount > 0

    async def get_all_bookings(self) -> List[Tuple]:
        """
        Получение всех бронирований (для админки).
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT 
                    id, username, school_name, class_number, class_profile,
                    excursion_date, excursion_time, contact_person, 
                    contact_phone, participants_count, booking_date
                FROM bookings 
                WHERE excursion_date >= date('now')
                ORDER BY excursion_date, excursion_time
            ''')
            
            return await cursor.fetchall()

    async def get_booking_stats(self) -> dict:
        """
        Получение статистики по бронированиям.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Общее количество броней
            cursor = await db.execute('SELECT COUNT(*) FROM bookings')
            total = (await cursor.fetchone())[0]
            
            # Брони на сегодня
            cursor = await db.execute('''
                SELECT COUNT(*) FROM bookings 
                WHERE excursion_date = date('now')
            ''')
            today = (await cursor.fetchone())[0]
            
            # Брони на будущее
            cursor = await db.execute('''
                SELECT COUNT(*) FROM bookings 
                WHERE excursion_date > date('now')
            ''')
            future = (await cursor.fetchone())[0]
            
            # Общее количество участников
            cursor = await db.execute('SELECT SUM(participants_count) FROM bookings')
            total_participants = (await cursor.fetchone())[0] or 0
            
            return {
                'total_bookings': total,
                'today_bookings': today,
                'future_bookings': future,
                'total_participants': total_participants
            }


# Создаем глобальный экземпляр базы данных для удобства использования
db = Database()


async def init_db():
    """Функция для инициализации базы данных (используется в основном файле)"""
    await db.init_db()


async def test_connection():
    """Тест соединения с базой данных"""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.execute("SELECT 1")
            result = await cursor.fetchone()
            return result[0] == 1 if result else False
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return False