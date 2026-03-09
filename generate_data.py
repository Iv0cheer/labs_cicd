#!/usr/bin/env python3
"""
Генератор синтетических данных: поездки такси-парка.
Вариант 19 — Customer Support	
Columns: ticket_id, created_at, response_time_minutes, resolution_time_minutes, user_rating, category.
"""

import csv
import os
import random
import sys
import argparse
from datetime import datetime, timedelta
import numpy as np

SEED = 42
NUM_ROWS = 5_000
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "support_tickets.csv")

# Категории с весами
CATEGORIES = {
    "Техническая проблема": 20,
    "Вопрос по оплате": 25,
    "Консультация": 30,
    "Жалоба на качество": 10,
    "Предложение": 10,
    "Другое": 5,
}

# Целевое время решения (в минутах)
TARGET_RESOLUTION_TIME = 35

random.seed(SEED)
np.random.seed(SEED)


def get_weighted_category() -> str:
    categories = list(CATEGORIES.keys())
    weights = list(CATEGORIES.values())
    return random.choices(categories, weights=weights, k=1)[0]


def is_weekend(date: datetime) -> bool:
    """Проверка, является ли день выходным (суббота или воскресенье)"""
    return date.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def generate_response_time(category: str, created_at: datetime) -> int:
    """
    Генерация времени ответа с зависимостью от категории и скорости ответа
    ЗАКОНОМЕРНОСТЬ 1: Чем быстрее ответ - тем быстрее решение
    """
    # Базовая логика: консультации и вопросы по оплате - быстрые ответы
    # Технические проблемы и жалобы - медленные ответы
    base_response = {
        "Техническая проблема": 18,      # Требуют диагностики
        "Вопрос по оплате": 7,            # Быстрые ответы
        "Консультация": 5,                 # Самые быстрые
        "Жалоба на качество": 16,          # Требуют проверки
        "Предложение": 12,                  # Средние
        "Другое": 10,
    }
    
    # В выходные ответы немного медленнее (меньше персонала)
    weekend_multiplier = 1.3 if is_weekend(created_at) else 1.0
    
    response_time = base_response[category] * weekend_multiplier
    
    # Добавляем случайную вариацию
    variation = random.uniform(0.8, 1.2)
    response_time = int(response_time * variation)
    
    # Ограничиваем время ответа
    return min(response_time, 120)


def generate_resolution_time(category: str, response_time: int, created_at: datetime) -> int:
    """
    Генерация времени решения с четкой корреляцией от времени ответа,
    категории проблемы и дня недели
    
    ЗАКОНОМЕРНОСТИ:
    1. Чем быстрее ответ - тем быстрее решение (коэффициент корреляции ~0.7)
    2. В будни решение быстрее, чем в выходные
    """
    # Базовая сложность решения по категориям
    complexity = {
        "Техническая проблема": 2.2,      # Самые сложные
        "Вопрос по оплате": 0.9,           # Средние
        "Консультация": 0.5,               # Очень простые
        "Жалоба на качество": 1.8,         # Сложные
        "Предложение": 1.1,                 # Средние
        "Другое": 1.2,
    }
    
    # ЗАКОНОМЕРНОСТЬ 1: Прямая зависимость от времени ответа
    # Чем быстрее ответ, тем быстрее решение (коэффициент 0.8)
    response_impact = response_time * 0.8
    
    # ЗАКОНОМЕРНОСТЬ 2: В будни решение быстрее, чем в выходные
    # В выходные время решения увеличивается на 30-50%
    if is_weekend(created_at):
        day_multiplier = random.uniform(1.3, 1.5)  # Выходные - медленнее
    else:
        day_multiplier = random.uniform(0.7, 0.9)  # Будни - быстрее
    
    # Базовое время решения (15 минут) + зависимость от времени ответа
    base_time = 15
    resolution_time = (base_time + response_impact) * complexity[category] * day_multiplier
    
    # Добавляем случайный шум, но сохраняем закономерности
    variation = random.uniform(0.85, 1.15)
    resolution_time = resolution_time * variation
    
    # Статистическая проверка: коэффициент корреляции между response_time и resolution_time
    # должен быть высоким (подтверждение закономерности 1)
    
    return int(max(5, min(240, resolution_time)))


def generate_rating(category: str, response_time: int, resolution_time: int, created_at: datetime) -> int:
    """
    Генерация рейтинга с четкой зависимостью от времени обслуживания
    """
    # Идеальное время обслуживания (ответ + решение)
    total_service_time = response_time + resolution_time
    
    # Идеальный сервис: до 30 минут
    if total_service_time <= 30:
        rating = 5
    elif total_service_time <= 45:
        rating = 5 if random.random() < 0.8 else 4
    elif total_service_time <= 60:
        rating = 4 if random.random() < 0.7 else 3
    elif total_service_time <= 90:
        rating = 3 if random.random() < 0.6 else 2
    else:
        rating = random.choice([1, 2])
    
    # Корректировка по категории
    if category == "Жалоба на качество" and rating > 3:
        rating = max(3, rating - 1)  # Снижаем рейтинг для жалоб
    elif category == "Консультация" and rating < 4:
        rating = min(4, rating + 1)  # Повышаем для консультаций
    
    # В выходные пользователи чуть более требовательны (есть время подумать о недостатках)
    if is_weekend(created_at) and rating > 3 and random.random() < 0.3:
        rating -= 1
    
    return rating


def generate_ticket_date() -> datetime:
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    # Создаем дневной паттерн: больше обращений днем
    hour_weights = [1] * 24
    for i in range(8, 20):  # Часы пик 8-20
        hour_weights[i] = 4
    
    # В выходные паттерн другой - больше обращений во второй половине дня
    random_days = random.randint(0, (end_date - start_date).days)
    date = start_date + timedelta(days=random_days)
    
    # Корректируем веса часов в зависимости от дня недели
    if is_weekend(date):
        # В выходные больше обращений после обеда
        hour_weights = [1] * 24
        for i in range(11, 22):  # С 11 до 22 часов
            hour_weights[i] = 5
    
    random_hours = random.choices(range(24), weights=hour_weights)[0]
    random_minutes = random.randint(0, 59)
    
    return date.replace(hour=random_hours, minute=random_minutes)


def generate(num_rows: int, output_file: str, seed: int = SEED) -> None:
    random.seed(seed)   
    np.random.seed(seed)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    fieldnames = [
        "ticket_id",
        "created_at",
        "response_time_minutes",
        "resolution_time_minutes",
        "user_rating",
        "category",
    ]

    # Храним данные для точного расчета KPI и проверки закономерностей
    resolutions = []
    responses = []
    ratings = []
    weekend_resolutions = []
    weekday_resolutions = []
    correlation_pairs = []  # Для проверки корреляции

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, num_rows + 1):
            category = get_weighted_category()
            created_at = generate_ticket_date()

            response_time = generate_response_time(category, created_at)
            resolution_time = generate_resolution_time(category, response_time, created_at)
            
            rating = generate_rating(category, response_time, resolution_time, created_at)
            
            # Сохраняем для проверки закономерностей
            correlation_pairs.append((response_time, resolution_time))
            
            if is_weekend(created_at):
                weekend_resolutions.append(resolution_time)
            else:
                weekday_resolutions.append(resolution_time)
            
            # Случайно пропускаем рейтинг (10% заявок)
            if random.random() < 0.1:
                rating = None
            else:
                ratings.append(rating)

            responses.append(response_time)
            resolutions.append(resolution_time)

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

    # Выводим точные KPI
    fast_response = sum(1 for r in responses if r < 15)
    fast_resolution = sum(1 for r in resolutions if r < 40)
    avg_resolution = sum(resolutions) / len(resolutions)
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    # Проверяем закономерности
    avg_weekend_resolution = sum(weekend_resolutions) / len(weekend_resolutions) if weekend_resolutions else 0
    avg_weekday_resolution = sum(weekday_resolutions) / len(weekday_resolutions) if weekday_resolutions else 0
    
    # Вычисляем корреляцию между response_time и resolution_time
    if correlation_pairs:
        responses_list, resolutions_list = zip(*correlation_pairs)
        correlation = np.corrcoef(responses_list, resolutions_list)[0, 1]
    else:
        correlation = 0

    print(f"\n{'='*60}")
    print(f"Сгенерировано {num_rows} тикетов → {output_file}")
    print(f"{'='*60}")

# === CHERENKOV CLI ARGUMENTS ===

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Customer support synthetic generator"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=NUM_ROWS,
        help=f"Количество строк (по умолчанию: {NUM_ROWS})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=OUTPUT_FILE,
        help=f"Путь для CSV (по умолчанию: {OUTPUT_FILE})"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=SEED,
        help=f"Seed (по умолчанию: {SEED})"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    generate(args.count, args.output, args.seed)
