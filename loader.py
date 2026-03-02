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


def load_csv(conn: psycopg2.extensions.connection) -> int:
    """Загрузка CSV в таблицу support_tickets."""
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM support_tickets;")
    if cur.fetchone()[0] > 0:
        print("[loader] Таблица уже содержит данные — пропуск загрузки.")
        return 0

    count = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:

            rating = row["user_rating"]
            if rating == "" or rating is None:
                rating = None
            else:
                rating = int(float(rating))
            
            cur.execute(
                """
                INSERT INTO support_tickets
                    (ticket_id, created_at, response_time_minutes, 
                     resolution_time_minutes, user_rating, category)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticket_id) DO NOTHING;
                """,
                (
                    int(row["ticket_id"]),
                    row["created_at"],
                    int(row["response_time_minutes"]),
                    int(row["resolution_time_minutes"]),
                    rating,
                    row["category"],
                ),
            )
            count += 1

    conn.commit()
    cur.close()
    print(f"[loader] Загружено {count} строк в таблицу support_tickets.")
    return count


def main() -> None:
    conn = wait_for_db()
    try:
        load_csv(conn)
    finally:
        conn.close()
    print("[loader] Готово.")


if __name__ == "__main__":
    main()