#!/usr/bin/env python3
"""
Вариант 19 - Customer Support Dashboard
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    df['total_time'] = df['response_time_minutes'] + df['resolution_time_minutes']
    df['weekend'] = df['created_at'].dt.dayofweek.isin([5, 6])
    
    return df

# --- Интерфейс ---
st.set_page_config(page_title="Аналитика поддержки", layout="wide")
st.title("Анализ работы службы поддержки")

try:
    df = load_data()
except Exception as e:
    st.error(f"Не удалось подключиться к БД: {e}")
    st.info("Убедитесь, что контейнер loader завершил загрузку данных.")
    st.stop()

# --- Фильтры ---
st.sidebar.header("Фильтры")

# Фильтр по категориям
categories = st.sidebar.multiselect(
    "Категория проблемы", 
    options=sorted(df["category"].unique()), 
    default=sorted(df["category"].unique())
)

# Фильтр по времени ответа
response_range = st.sidebar.slider(
    "Диапазон времени ответа (мин)",
    min_value=int(df["response_time_minutes"].min()),
    max_value=int(df["response_time_minutes"].max()),
    value=(0, 120)
)

# Применяем фильтры
df_filtered = df[
    (df["category"].isin(categories)) &
    (df["response_time_minutes"].between(response_range[0], response_range[1]))
]

# --- Метрики ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Всего тикетов", f"{len(df_filtered):,}")
with col2:
    avg_response = df_filtered['response_time_minutes'].mean()
    st.metric("Ср. время реакции", f"{avg_response:.0f} мин")
with col3:
    avg_resolution = df_filtered['resolution_time_minutes'].mean()
    st.metric("Ср. время решения", f"{avg_resolution:.0f} мин")
with col4:
    avg_rating = df_filtered['user_rating'].mean()
    st.metric("Ср. рейтинг", f"{avg_rating:.1f}" if not pd.isna(avg_rating) else "Н/Д")

st.divider()

# --- ГРАФИК 1: Зависимость времени решения от времени ответа ---
st.subheader("Как время ответа влияет на время решения")

response_bins = pd.cut(df_filtered['response_time_minutes'], bins=12)
agg_data = df_filtered.groupby(response_bins, observed=True).agg({
    'resolution_time_minutes': ['mean', 'std', 'count'],
    'response_time_minutes': 'mean'
}).round(1)

agg_data.columns = ['resolution_mean', 'resolution_std', 'count', 'response_mean']
agg_data = agg_data.reset_index()
agg_data['response_bin'] = agg_data['response_mean'].round(0)

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

fig1.add_trace(
    go.Scatter(
        x=agg_data['response_bin'],
        y=agg_data['resolution_mean'],
        mode='lines+markers',
        name='Среднее время решения',
        line=dict(color='red', width=3),
        marker=dict(size=10)
    ),
    secondary_y=False
)

fig1.add_trace(
    go.Scatter(
        x=agg_data['response_bin'],
        y=agg_data['resolution_mean'] + agg_data['resolution_std'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ),
    secondary_y=False
)

fig1.add_trace(
    go.Scatter(
        x=agg_data['response_bin'],
        y=agg_data['resolution_mean'] - agg_data['resolution_std'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 0, 0, 0.1)',
        name='Разброс (±1σ)',
        hoverinfo='skip'
    ),
    secondary_y=False
)

fig1.add_trace(
    go.Bar(
        x=agg_data['response_bin'],
        y=agg_data['count'],
        name='Количество тикетов',
        marker_color='lightblue',
        opacity=0.5
    ),
    secondary_y=True
)

fig1.update_layout(
    title="Прямая зависимость: чем быстрее ответ, тем быстрее решение",
    xaxis_title="Время ответа (минуты)",
    height=500,
    hovermode='x unified'
)

fig1.update_yaxes(title_text="Среднее время решения (мин)", secondary_y=False)
fig1.update_yaxes(title_text="Количество тикетов", secondary_y=True)

st.plotly_chart(fig1, use_container_width=True)
st.caption("Видна четкая линейная зависимость между временем ответа и временем решения.")

# --- ГРАФИК 2: Сравнение будних и выходных дней ---
st.subheader("Сравнение эффективности в будни и выходные")

weekday_data = df_filtered[~df_filtered['weekend']].copy()
weekend_data = df_filtered[df_filtered['weekend']].copy()

weekday_hourly = weekday_data.groupby('hour').agg({
    'resolution_time_minutes': 'mean',
    'response_time_minutes': 'mean',
    'user_rating': 'mean',
    'created_at': 'count'
}).round(1).reset_index()

weekend_hourly = weekend_data.groupby('hour').agg({
    'resolution_time_minutes': 'mean',
    'response_time_minutes': 'mean',
    'user_rating': 'mean',
    'created_at': 'count'
}).round(1).reset_index()

fig2 = make_subplots(specs=[[{"secondary_y": True}]])

fig2.add_trace(
    go.Scatter(
        x=weekday_hourly['hour'],
        y=weekday_hourly['resolution_time_minutes'],
        mode='lines+markers',
        name='Время решения (будни)',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ),
    secondary_y=False
)

fig2.add_trace(
    go.Scatter(
        x=weekend_hourly['hour'],
        y=weekend_hourly['resolution_time_minutes'],
        mode='lines+markers',
        name='Время решения (выходные)',
        line=dict(color='orange', width=3),
        marker=dict(size=8)
    ),
    secondary_y=False
)

fig2.add_trace(
    go.Bar(
        x=weekday_hourly['hour'],
        y=weekday_hourly['created_at'],
        name='Количество (будни)',
        marker_color='blue',
        opacity=0.3,
        showlegend=True
    ),
    secondary_y=True
)

fig2.add_trace(
    go.Bar(
        x=weekend_hourly['hour'],
        y=weekend_hourly['created_at'],
        name='Количество (выходные)',
        marker_color='orange',
        opacity=0.3,
        showlegend=True
    ),
    secondary_y=True
)

fig2.update_layout(
    title="Сравнение времени решения в будни и выходные по часам",
    xaxis_title="Час дня",
    height=500,
    hovermode='x unified',
    barmode='group'
)

fig2.update_yaxes(title_text="Среднее время решения (мин)", secondary_y=False)
fig2.update_yaxes(title_text="Количество тикетов", secondary_y=True)

st.plotly_chart(fig2, use_container_width=True)
st.caption("В выходные время решения выше, особенно в нерабочие часы.")

# --- ГРАФИК 3: Горизонтальная столбчатая диаграмма по категориям ---
st.subheader("Распределение заявок по категориям с метриками")

category_stats = df_filtered.groupby('category').agg({
    'created_at': 'count',
    'response_time_minutes': 'mean',
    'resolution_time_minutes': 'mean',
    'user_rating': 'mean'
}).round(1).reset_index()

category_stats.columns = ['Категория', 'Количество', 'Ср. время ответа', 'Ср. время решения', 'Ср. рейтинг']
category_stats = category_stats.sort_values('Количество', ascending=True)

fig3 = go.Figure()

fig3.add_trace(go.Bar(
    y=category_stats['Категория'],
    x=category_stats['Количество'],
    orientation='h',
    marker=dict(
        color=category_stats['Ср. рейтинг'],
        colorscale='RdYlGn',
        cmin=3.5,
        cmax=5.0,
        colorbar=dict(title="Ср. рейтинг")
    ),
    text=category_stats['Количество'].astype(str) + ' заявок',
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>' +
                  'Количество: %{x}<br>' +
                  'Ср. время ответа: %{customdata[0]} мин<br>' +
                  'Ср. время решения: %{customdata[1]} мин<br>' +
                  'Ср. рейтинг: %{customdata[2]}<extra></extra>',
    customdata=category_stats[['Ср. время ответа', 'Ср. время решения', 'Ср. рейтинг']]
))

fig3.update_layout(
    title="Объем обращений по категориям (цвет = средний рейтинг)",
    xaxis_title="Количество заявок",
    yaxis_title="Категория",
    height=400,
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig3, use_container_width=True)
st.caption("Зеленый цвет = высокий рейтинг. Чем правее столбец, тем больше обращений.")

st.divider()
