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