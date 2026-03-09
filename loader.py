#!/usr/bin/env python3
"""
ETL-загрузчик: читает support_tickets.csv и загружает в PostgreSQL.
Запускается как init-контейнер (loader) после healthy-статуса БД.
"""

import csv
import os
import sys
import time

import psycopg2

# --- Настройки из переменных окружения ---
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "support")
DB_USER = os.getenv("POSTGRES_USER", "support_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "changeme")
CSV_PATH = os.getenv("CSV_PATH", "/data/support_tickets.csv")


DDL = """
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id                INT PRIMARY KEY,
    created_at               TIMESTAMP NOT NULL,
    response_time_minutes    INT NOT NULL,
    resolution_time_minutes  INT NOT NULL,
    user_rating              INT,
    category                 VARCHAR(50) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_created_at ON support_tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_category ON support_tickets(category);
CREATE INDEX IF NOT EXISTS idx_user_rating ON support_tickets(user_rating);
"""


def wait_for_db(max_retries: int = 30, delay: int = 2) -> psycopg2.extensions.connection:
    """Ожидание готовности PostgreSQL."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT,
                dbname=DB_NAME, user=DB_USER, password=DB_PASS,
            )
            print(f"[loader] БД доступна (попытка {attempt})")
            return conn
        except psycopg2.OperationalError:
            print(f"[loader] Ожидание БД... ({attempt}/{max_retries})")
            time.sleep(delay)
    print("[loader] БД недоступна, завершение.")
    sys.exit(1)


def create_table_if_not_exists(conn: psycopg2.extensions.connection) -> None:
    """Создание таблицы, если она не существует."""
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    cur.close()
    print("[loader] Таблица создана (если не существовала)")


def clear_table(conn: psycopg2.extensions.connection) -> None:
    """Очистка таблицы перед загрузкой."""
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE support_tickets RESTART IDENTITY CASCADE;")
    conn.commit()
    cur.close()
    print("[loader] Таблица очищена")


def load_csv(conn: psycopg2.extensions.connection) -> int:
    """Загрузка CSV в таблицу support_tickets."""
    cur = conn.cursor()
    
    clear_table(conn)
    
    loaded_count = 0
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            expected_fields = ['ticket_id', 'created_at', 'response_time_minutes', 
                              'resolution_time_minutes', 'user_rating', 'category']
            
            if reader.fieldnames != expected_fields:
                print(f"[loader] Предупреждение: поля CSV {reader.fieldnames} отличаются от ожидаемых {expected_fields}")
            
            for row in reader:
                rating = row["user_rating"]
                if rating == "" or rating is None or rating.strip() == "":
                    rating = None
                else:
                    try:
                        rating = int(float(rating))
                    except (ValueError, TypeError):
                        print(f"[loader] Ошибка преобразования rating '{rating}' для ticket_id {row['ticket_id']}, устанавливаю NULL")
                        rating = None
                
                try:
                    ticket_id = int(row["ticket_id"])
                    response_time = int(row["response_time_minutes"])
                    resolution_time = int(row["resolution_time_minutes"])
                except (ValueError, KeyError) as e:
                    print(f"[loader] Ошибка в данных для ticket_id {row.get('ticket_id', 'unknown')}: {e}")
                    continue
                
                cur.execute(
                    """
                    INSERT INTO support_tickets
                        (ticket_id, created_at, response_time_minutes, 
                         resolution_time_minutes, user_rating, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        ticket_id,
                        row["created_at"],
                        response_time,
                        resolution_time,
                        rating,
                        row["category"],
                    ),
                )
                loaded_count += 1
                
                if loaded_count % 1000 == 0:
                    print(f"[loader] Загружено {loaded_count} записей...")
                    conn.commit()

    except FileNotFoundError:
        print(f"[loader] Файл {CSV_PATH} не найден!")
        cur.close()
        return 0
    except Exception as e:
        print(f"[loader] Ошибка при чтении CSV: {e}")
        conn.rollback()
        cur.close()
        raise

    conn.commit()
    cur.close()
    print(f"[loader] Загружено {loaded_count} строк в таблицу support_tickets.")
    return loaded_count


def verify_data(conn: psycopg2.extensions.connection) -> None:
    """Проверка загруженных данных."""
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM support_tickets;")
    total = cur.fetchone()[0]
    print(f"[loader] Всего записей в таблице: {total}")
    
    cur.execute("""
        SELECT category, COUNT(*) as count 
        FROM support_tickets 
        GROUP BY category 
        ORDER BY count DESC;
    """)
    categories = cur.fetchall()
    if categories:
        print("[loader] Распределение по категориям:")
        for cat, cnt in categories:
            print(f"  - {cat}: {cnt}")
    
    cur.execute("""
        SELECT 
            MIN(response_time_minutes) as min_resp,
            MAX(response_time_minutes) as max_resp,
            AVG(response_time_minutes) as avg_resp
        FROM support_tickets;
    """)
    min_r, max_r, avg_r = cur.fetchone()
    print(f"[loader] Время ответа: мин={min_r}, макс={max_r}, ср={avg_r:.1f}")
    
    cur.close()


def main() -> None:
    print("[loader] Запуск ETL-загрузчика...")
    print(f"[loader] Подключение к {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"[loader] Файл данных: {CSV_PATH}")
    
    conn = wait_for_db()
    try:
        create_table_if_not_exists(conn)
        
        loaded = load_csv(conn)
        
        verify_data(conn)
        
        print(f"[loader] Загрузка завершена. Загружено записей: {loaded}")
    except Exception as e:
        print(f"[loader] Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        conn.close()
    
    print("[loader] Готово.")


if __name__ == "__main__":
    main()
