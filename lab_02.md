## **Тематики данных — Вариант 9.**

#### **Предметная область — примерные поля**

Customer Support — ID тикета, время реакции, время решения, оценка пользователя, категория проблемы.

#### **Индивидуальное задание — Python CLI Arguments**

Скрипт принимает аргументы при запуске (через sys.argv или argparse), например --count 100, генерирует указанное число строк и сохраняет в CSV.

## **Реализация индивидуального задания**

### **Шаг №1. Настройка файла generate_data.py**

Изменения затронули почти весь файл, т.к. была другая тема и нужно было "подбить" генератор данных под поставленную предметную область, а также добавить обработку CLI аргументов.

<details>
  <summary> __Код Python-файла__ </summary>
  
  ```py
  #!/usr/bin/env python3
"""
Генератор синтетических данных: поездки такси-парка.
Вариант 19 — Customer Support	
Columns: ticket_id, created_at, response_time_minutes, resolution_time_minutes, user_rating, category.

Запуск: python generate_data.py
Результат: data/support_tickets.csv
"""

import csv
import os
import random
import sys
import argparse
from datetime import datetime, timedelta

SEED = 42
NUM_ROWS = 5_000
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "support_tickets.csv")

CATEGORIES = {
    "Техническая проблема": 35,
    "Вопрос по оплате": 25,
    "Консультация": 20,
    "Жалоба на качество": 12,
    "Предложение": 5,
    "Другое": 3,
}

random.seed(SEED)


def get_weighted_category() -> str:
    categories = list(CATEGORIES.keys())
    weights = list(CATEGORIES.values())
    return random.choices(categories, weights=weights, k=1)[0]


def generate_response_time(category: str) -> int:
    base_times = {
        "Техническая проблема": random.uniform(30, 180),      # 0.5 - 3 h
        "Вопрос по оплате": random.uniform(15, 120),          # 15 - 2 h
        "Консультация": random.uniform(10, 90),               # 10 - 1.5 h
        "Жалоба на качество": random.uniform(20, 150),        # 0.33 - 2.5 h
        "Предложение": random.uniform(60, 240),               # 1-4 h
        "Другое": random.uniform(30, 200),                    # 0.5 - 3.3 h
    }
    
    response_time = base_times[category]
    
    response_time *= random.uniform(0.8, 1.2)
    
    return int(response_time)


def generate_resolution_time(category: str, response_time: int) -> int:
    """
    Генерация времени решения (в минутах) с учётом категории и времени реакции.
    """
    base_complexity = {
        "Техническая проблема": random.uniform(120, 1440),      # 2 - 24 h
        "Вопрос по оплате": random.uniform(30, 240),            # 0.5 - 4 h
        "Консультация": random.uniform(15, 180),                # 0.25 - 3 h
        "Жалоба на качество": random.uniform(60, 480),          # 1 - 8 h
        "Предложение": random.uniform(30, 300),                 # 0.5 - 5 h
        "Другое": random.uniform(60, 600),                      # 1 - 10 h
    }
    
    resolution_time = base_complexity[category]
    
    resolution_time = max(resolution_time, response_time * 1.1)
    
    resolution_time *= random.uniform(0.7, 1.3)
    
    return int(resolution_time)


def generate_rating(category: str, response_time: int, resolution_time: int) -> int:
    base_satisfaction = {
        "Техническая проблема": 0.7,
        "Вопрос по оплате": 0.75,
        "Консультация": 0.85,
        "Жалоба на качество": 0.5,
        "Предложение": 0.9,
        "Другое": 0.8,
    }
    
    response_impact = 1.0
    if response_time < 30:
        response_impact = 1.2
    elif response_time > 120:
        response_impact = 0.8
    elif response_time > 240:
        response_impact = 0.6
    
    resolution_impact = 1.0
    if resolution_time < 60:
        resolution_impact = 1.3
    elif resolution_time > 360:
        resolution_impact = 0.7
    elif resolution_time > 720:
        resolution_impact = 0.5

    satisfaction_prob = base_satisfaction[category] * response_impact * resolution_impact
    satisfaction_prob = max(0.1, min(0.98, satisfaction_prob))
    

    if random.random() < satisfaction_prob:
        return random.choices([4, 5], weights=[0.3, 0.7])[0]
    else:
        return random.choices([1, 2, 3], weights=[0.2, 0.3, 0.5])[0]


def generate_ticket_date() -> datetime:
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    days_range = (end_date - start_date).days
    
    random_days = random.randint(0, days_range)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    
    return start_date + timedelta(days=random_days, 
                                   hours=random_hours, 
                                   minutes=random_minutes)


def generate(num_rows: int, output_file: str, seed: int = SEED) -> None:
    random.seed(seed)   
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    fieldnames = [
        "ticket_id",
        "created_at",
        "response_time_minutes",
        "resolution_time_minutes",
        "user_rating",
        "category",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, num_rows + 1):
            category = get_weighted_category()
            created_at = generate_ticket_date()

            response_time = generate_response_time(category)
            resolution_time = generate_resolution_time(category, response_time)
            
            rating = generate_rating(category, response_time, resolution_time)
            
            if random.random() < 0.1:
                rating = None

            writer.writerow(
                {
                    "ticket_id": i,
                    "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "response_time_minutes": response_time,
                    "resolution_time_minutes": resolution_time,
                    "user_rating": rating,
                    "category": category,
                }
            )

    print(f"Сгенерировано {num_rows} тикетов → {output_file}")



# --- CLI ARGUMENTS VARIANT 19 CHERENKOV ---

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Customer support SINTETIC generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--count", "-c",
        type=int,
        default=NUM_ROWS,
        help=f"Количество генерируемых строк (по умолчанию: {NUM_ROWS})"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=OUTPUT_FILE,
        help=f"Путь для сохранения CSV файла (по умолчанию: {OUTPUT_FILE})"
    )

    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=SEED,
        help=f"Seed для воспроизводимости (по умолчанию: {SEED})"
    )

    return parser.parse_args()


if __name__ == "__main__":
    # python3 generate_data.py --count 100
    
    args = parse_arguments()
    generate(args.count, args.output, args.seed)
  ```
  
</details>

### **Шаг №2. Были реализованы 3 CLI аргумента:**

* --output (можно изменять путь для сохранения CSV файла)
* --count (можно изменять количество генерируемых данных)
* --seed (можно изменять для изменения рандома данных (ключ рандома/соль))

<details>
  <summary> Часть кода с реализацией CLI аргументов (сама функция) </summary>
  
  ```py
  # --- CLI ARGUMENTS VARIANT 19 CHERENKOV ---

  def parse_arguments():
      """Парсинг аргументов командной строки"""
      parser = argparse.ArgumentParser(
          description="Customer support SINTETIC generator",
          formatter_class=argparse.RawDescriptionHelpFormatter
      )
  
      parser.add_argument(
          "--count", "-c",
          type=int,
          default=NUM_ROWS,
          help=f"Количество генерируемых строк (по умолчанию: {NUM_ROWS})"
      )
  
      parser.add_argument(
          "--output", "-o",
          type=str,
          default=OUTPUT_FILE,
          help=f"Путь для сохранения CSV файла (по умолчанию: {OUTPUT_FILE})"
      )
  
      parser.add_argument(
          "--seed", "-s",
          type=int,
          default=SEED,
          help=f"Seed для воспроизводимости (по умолчанию: {SEED})"
      )
  
      return parser.parse_args()
  ```

</details>

### **Шаг 3. Изменения лоадера в PostgreSQL**

Был изменен DDL-скрипт

<img width="779" height="304" alt="image" src="https://github.com/user-attachments/assets/662559f2-5107-45ee-903e-cfca40cf7731" />

### **Шаг 4. Запуск билда Docker**

После всех изменений, был произведен запуск билда Docker.

<img width="1426" height="339" alt="image" src="https://github.com/user-attachments/assets/db1ab217-8a4b-4679-9207-c50a196ee04a" />

<img width="2040" height="577" alt="image" src="https://github.com/user-attachments/assets/007dd73a-744c-411d-b00d-61d4e671a73a" />

