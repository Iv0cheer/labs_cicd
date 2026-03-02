## **Цель работы**

Научиться разрабатывать воспроизводимые аналитические инструменты. Студенту необходимо пройти полный цикл: от написания Python-скрипта для обработки бизнес-данных до его упаковки в Docker-образ и запуска в изолированной среде.

## **Тематики данных — Вариант 9.**

#### **Предметная область — примерные поля**

Customer Support — ID тикета, время реакции, время решения, оценка пользователя, категория проблемы.

#### **Индивидуальное задание — Python CLI Arguments**

Скрипт принимает аргументы при запуске (через sys.argv или argparse), например --count 100, генерирует указанное число строк и сохраняет в CSV.

## **Реализация индивидуального задания**

### **Шаг №1. Настройка файла generate_data.py**

Изменения затронули почти весь файл, т.к. была другая тема и нужно было "подбить" генератор данных под поставленную предметную область, а также добавить обработку CLI аргументов.

<details>
  <summary> <u> ___Код Python-файла___ </u> </summary>
  
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
  <summary> ___Часть кода с реализацией CLI аргументов (сама функция)___ </summary>
  
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

### **Шаг 4. Изменение дашборда**

Дашборд был также видоизменен под поставленную предметную область.

<details>
  <summary>___Код python-файла dashboard.py___</summary>

  ```py
  #!/usr/bin/env python3
  """
  Вариант 19.
  """
  
  import os
  import pandas as pd
  import plotly.express as px
  import streamlit as st
  import psycopg2
  
  # --- Подключение к БД ---
  DB_HOST = os.getenv("DB_HOST", "db")
  DB_PORT = os.getenv("DB_PORT", "5432")
  DB_NAME = os.getenv("POSTGRES_DB", "support")
  DB_USER = os.getenv("POSTGRES_USER", "support_user")
  DB_PASS = os.getenv("POSTGRES_PASSWORD", "changeme")
  
  @st.cache_data(ttl=300)
  def load_data() -> pd.DataFrame:
      """Загрузка данных из PostgreSQL."""
      conn = psycopg2.connect(
          host=DB_HOST, port=DB_PORT,
          dbname=DB_NAME, user=DB_USER, password=DB_PASS,
      )
      df = pd.read_sql("SELECT * FROM support_tickets;", conn)
      conn.close()
      
      df['created_at'] = pd.to_datetime(df['created_at'])
      df['hour'] = df['created_at'].dt.hour
      df['day_of_week'] = df['created_at'].dt.day_name()
      
      return df
  
  # --- Интерфейс ---
  st.set_page_config(page_title="Аналитика поддержки", layout="wide")
  st.title("Служба поддержки — Анализ нагрузки")
  
  try:
      df = load_data()
  except Exception as e:
      st.error(f"Не удалось подключиться к БД: {e}")
      st.info("Убедитесь, что контейнер loader завершил загрузку данных.")
      st.stop()
  
  st.sidebar.header("Фильтры")
  categories = st.sidebar.multiselect(
      "Категория проблемы", 
      options=sorted(df["category"].unique()), 
      default=sorted(df["category"].unique())
  )
  df_filtered = df[df["category"].isin(categories)]
  
  # --- Метрики ---
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Всего тикетов", f"{len(df_filtered):,}")
  col2.metric("Ср. время реакции", f"{df_filtered['response_time_minutes'].mean():.0f} мин")
  col3.metric("Ср. время решения", f"{df_filtered['resolution_time_minutes'].mean():.0f} мин")
  col4.metric("Ср. рейтинг", f"{df_filtered['user_rating'].mean():.1f}" if df_filtered['user_rating'].notna().any() else "Н/Д")
  
  # --- Heatmap: День недели × Час ---
  st.subheader("Тепловая карта нагрузки: День недели × Час")
  
  day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  day_labels = {
      "Monday": "Пн", "Tuesday": "Вт", "Wednesday": "Ср",
      "Thursday": "Чт", "Friday": "Пт", "Saturday": "Сб", "Sunday": "Вс",
  }
  
  pivot = (
      df_filtered.groupby(["day_of_week", "hour"])
      .size()
      .reset_index(name="tickets")
  )
  pivot["day_of_week"] = pd.Categorical(pivot["day_of_week"], categories=day_order, ordered=True)
  pivot = pivot.sort_values("day_of_week")
  pivot["day_label"] = pivot["day_of_week"].map(day_labels)
  
  heatmap = pivot.pivot(index="day_label", columns="hour", values="tickets").fillna(0)
  day_label_order = [day_labels[d] for d in day_order]
  heatmap = heatmap.reindex(day_label_order)
  
  fig_heat = px.imshow(
      heatmap,
      labels=dict(x="Час", y="День недели", color="Тикетов"),
      color_continuous_scale="YlOrRd",
      aspect="auto",
  )
  fig_heat.update_layout(height=350)
  st.plotly_chart(fig_heat, use_container_width=True)
  
  # --- Гистограмма по часам ---
  st.subheader("Распределение тикетов по часам")
  hourly = df_filtered.groupby("hour").size().reset_index(name="tickets")
  fig_bar = px.bar(hourly, x="hour", y="tickets", labels={"hour": "Час", "tickets": "Тикетов"})
  fig_bar.update_layout(height=300)
  st.plotly_chart(fig_bar, use_container_width=True)
  
  # --- Топ категорий ---
  st.subheader("Топ категорий проблем")
  category_stats = (
      df_filtered.groupby("category")
      .size()
      .reset_index(name="count")
      .sort_values("count", ascending=False)
      .head(10)
  )
  fig_cat = px.bar(category_stats, x="count", y="category", orientation="h",
                   labels={"count": "Тикетов", "category": "Категория"})
  fig_cat.update_layout(height=350, yaxis=dict(autorange="reversed"))
  st.plotly_chart(fig_cat, use_container_width=True)
  
  st.caption("Данные: синтетический датасет support_tickets.csv • Streamlit + Plotly + PostgreSQL")
  ```

  
</details>

### **Шаг 5. Запуск билда Docker**

После всех изменений, был произведен запуск билда Docker.

<img width="1426" height="339" alt="image" src="https://github.com/user-attachments/assets/db1ab217-8a4b-4679-9207-c50a196ee04a" />

<img width="2040" height="577" alt="image" src="https://github.com/user-attachments/assets/007dd73a-744c-411d-b00d-61d4e671a73a" />


### **Шаг 6. Запуск localhost для проверки работоспособности дашборда.**

<img width="2335" height="1346" alt="image" src="https://github.com/user-attachments/assets/b7dd8a98-2c0b-4c4a-94fb-6cb8b9fdf403" />


## **Выводы по работе**

Освоил полный цикл создания воспроизводимых аналитических решений: от написания Python-кода для обработки данных до контейнеризации с помощью Docker и развертывания в изолированной среде.
