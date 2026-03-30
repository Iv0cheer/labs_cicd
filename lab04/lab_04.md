# ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ

## Вариант 19: Survey System (Система опросов)

## Цель

Применить полученные знания по созданию и развертыванию трехзвенного приложения (Frontend + Backend + Database) в кластере Kubernetes. Научиться организовывать взаимодействие между микросервисами.

## Структура проекта:

<details><summary>Открыть структуру проекта</summary>

```
↳ lab04_cicd
  ↳ backend
    ↳ Dockerfile
    ↳ main.py
    ↳ requirements.txt
  ↳ frontend
    ↳ app.py
    ↳ Dockerfile
    ↳ requirements.txt
  ↳ k8s
    ↳ fullstack.yaml
```

<img width="272" height="220" alt="image" src="https://github.com/user-attachments/assets/b0cd9806-837f-498e-9680-1ad6bdf3cf62" />


</details>

---

### Папка backend включает в себя 3 файла:

#### Файл main.py

Скрипт, работающий на основе API на FastAPI. Содержит в себе функции

* Модели данных (как выглядят таблицы в постгри)
* Логику обработки запросов
* URL по которым можно обращаться к сервисам (API как раз)

<details><summary>Листинг кода файла main.py</summary>

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import time

time.sleep(5)

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_NAME = os.getenv("DB_NAME", "survey_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# бдшечка
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="options")
    votes = relationship("Vote", back_populates="option", cascade="all, delete-orphan")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("options.id"))
    option = relationship("Option", back_populates="votes")

# таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Survey System API")

# схемы
class OptionCreate(BaseModel):
    text: str

class QuestionCreate(BaseModel):
    text: str
    options: list[OptionCreate]

class VoteRequest(BaseModel):
    option_id: int

# эндпоинты (URL API)
@app.post("/questions")
def create_question(question: QuestionCreate):
    db = SessionLocal()
    try:
        # вопрос
        db_question = Question(text=question.text)
        db.add(db_question)
        db.commit()
        
        # Получаем ID
        question_id = db_question.id
        
        # Создаем опции
        for opt in question.options:
            db_option = Option(text=opt.text, question_id=question_id)
            db.add(db_option)
        
        db.commit()
        
        return {"message": "Question created", "question_id": question_id}
    
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

@app.get("/questions")
def get_questions():
    db = SessionLocal()
    try:
        questions = db.query(Question).all()
        result = []
        for q in questions:
            result.append({
                "id": q.id,
                "text": q.text,
                "options": [{"id": opt.id, "text": opt.text} for opt in q.options]
            })
        return result
    finally:
        db.close()

@app.get("/questions/{question_id}/results")
def get_results(question_id: int):
    db = SessionLocal()
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        results = []
        for opt in question.options:
            vote_count = db.query(func.count(Vote.id)).filter(Vote.option_id == opt.id).scalar() or 0
            results.append({
                "option_id": opt.id,
                "option_text": opt.text,
                "votes": vote_count
            })
        return {
            "question_id": question_id, 
            "question_text": question.text, 
            "results": results
        }
    finally:
        db.close()

@app.post("/vote")
def vote(vote: VoteRequest):
    db = SessionLocal()
    try:
        option = db.query(Option).filter(Option.id == vote.option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        
        new_vote = Vote(option_id=vote.option_id)
        db.add(new_vote)
        db.commit()
        return {"message": "Vote recorded"}
    
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

</details>

#### Файл requirements.txt

Содержит зависимости для любимого питона

<details><summary>Листинг файла requirements.txt</summary>

```python
fastapi
uvicorn
psycopg2-binary
sqlalchemy
pydantic
```

</details>


#### Файл backend/Dockerfile

Содержит docker-образ бэкенда

<details><summary>Листинг файла Dockerfile</summary>

```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

</details>

---

### Папка frontend включает в себя также 3 файла:

#### requirements.txt

Содержит зависимости для любимого питона

<details><summary>Листинг файла requirements.txt</summary>

```python
streamlit
requests
pandas
```

</details>


#### Файл app.py

Содержит UI для стримлита

<details><summary>Листинг кода файла app.py</summary>

```python
import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

st.set_page_config(page_title="Survey System", layout="wide")
st.title("Система опросов")

menu = st.sidebar.radio("Меню", ["Создать опрос", "Пройти опрос", "Результаты"])

# создание нового вопроса
if menu == "Создать опрос":
    st.header("Создать новый опрос")
    
    question_text = st.text_input("Вопрос")
    options_text = st.text_area("Варианты ответов (каждый с новой строки)")
    
    if st.button("Создать опрос"):
        if question_text and options_text:
            options_list = [{"text": opt.strip()} for opt in options_text.split("\n") if opt.strip()]
            if len(options_list) >= 2:
                payload = {
                    "text": question_text,
                    "options": options_list
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/questions", json=payload)
                    if res.status_code == 200:
                        st.success("Опрос успешно создан!")
                    else:
                        st.error(f"Ошибка: {res.text}")
                except Exception as e:
                    st.error(f"Ошибка подключения: {e}")
            else:
                st.warning("Нужно минимум 2 варианта ответа")
        else:
            st.warning("Заполните все поля")

# прохождение опроса
elif menu == "Пройти опрос":
    st.header("Пройти опрос")
    
    try:
        res = requests.get(f"{BACKEND_URL}/questions")
        if res.status_code == 200:
            questions = res.json()
            if questions:
                selected_q = st.selectbox("Выберите опрос", questions, format_func=lambda x: x["text"])
                
                if selected_q:
                    st.write(f"**{selected_q['text']}**")
                    selected_option = st.radio("Варианты:", selected_q["options"], format_func=lambda x: x["text"])
                    
                    if st.button("Голосовать"):
                        vote_payload = {"option_id": selected_option["id"]}
                        vote_res = requests.post(f"{BACKEND_URL}/vote", json=vote_payload)
                        if vote_res.status_code == 200:
                            st.success("Голос принят! Спасибо за участие.")
                        else:
                            st.error("Ошибка при голосовании")
            else:
                st.info("Нет доступных опросов. Создайте новый.")
        else:
            st.error("Не удалось загрузить опросы")
    except Exception as e:
        st.error(f"Ошибка подключения к бэкенду: {e}")

# результаты, аналитика и граффик
elif menu == "Результаты":
    st.header("Результаты опросов")
    
    try:
        res = requests.get(f"{BACKEND_URL}/questions")
        if res.status_code == 200:
            questions = res.json()
            if questions:
                selected_q = st.selectbox("Выберите опрос для просмотра", questions, format_func=lambda x: x["text"])
                
                if selected_q:
                    results_res = requests.get(f"{BACKEND_URL}/questions/{selected_q['id']}/results")
                    if results_res.status_code == 200:
                        data = results_res.json()
                        st.subheader(data["question_text"])
                        
                        results_df = []
                        total_votes = 0
                        for r in data["results"]:
                            results_df.append({"Вариант": r["option_text"], "Голосов": r["votes"]})
                            total_votes += r["votes"]
                        
                        if total_votes > 0:
                            st.dataframe(results_df)
                            st.write(f"**Всего голосов:** {total_votes}")
                            
                            # Простая визуализация
                            for r in data["results"]:
                                percent = (r["votes"] / total_votes) * 100
                                st.write(f"{r['option_text']}: {r['votes']} голосов ({percent:.1f}%)")
                                st.progress(percent / 100)
                        else:
                            st.info("Пока нет голосов")
    except Exception as e:
        st.error(f"Ошибка: {e}")

```

</details>

#### Файл frontend/Dockerfile

Содержит docker-образ фронтА

<details><summary>Листинг файла Dockerfile</summary>

```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

</details>

---

### Папка k8s и манифест:

Содержит docker-образ фронтА

<details><summary>Листинг файла fullstack.yaml</summary>

```yaml
# PostgreSQL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deploy
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_USER
          value: "user"
        - name: POSTGRES_PASSWORD
          value: "password"
        - name: POSTGRES_DB
          value: "survey_db"
        ports:
        - containerPort: 5432
---
# PostgreSQL Service
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
---
# pgAdmin
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgadmin-deploy
  labels:
    app: pgadmin
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pgadmin
  template:
    metadata:
      labels:
        app: pgadmin
    spec:
      containers:
      - name: pgadmin
        image: dpage/pgadmin4:latest
        env:
        - name: PGADMIN_DEFAULT_EMAIL
          value: "admin@example.com"
        - name: PGADMIN_DEFAULT_PASSWORD
          value: "admin123"
        - name: PGADMIN_CONFIG_SERVER_MODE
          value: "False"
        ports:
        - containerPort: 80
---
# pgAdmin Service
apiVersion: v1
kind: Service
metadata:
  name: pgadmin-service
spec:
  type: NodePort
  selector:
    app: pgadmin
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30090
---
# Backend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deploy
  labels:
    app: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: survey-backend:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_USER
          value: "user"
        - name: DB_PASSWORD
          value: "password"
        - name: DB_NAME
          value: "survey_db"
        ports:
        - containerPort: 8000
---
# Backend Service
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000
---
# Frontend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deploy
  labels:
    app: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: survey-frontend:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: BACKEND_URL
          value: "http://backend-service:8000"
        ports:
        - containerPort: 8501
---
# Frontend Service
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 8501
      nodePort: 30080
```

</details>

---

### Сборка образов

#### Сборка образа backend

<img width="912" height="508" alt="image" src="https://github.com/user-attachments/assets/7072c1ae-ef5b-4b20-85d5-fe92c6cc6102" />

#### Сборка образа frontend

<img width="874" height="311" alt="image" src="https://github.com/user-attachments/assets/3186bc32-45c7-415d-8b52-7a49d30193e7" />

#### Запуск миникуба и применение манифестов

> Запуск миникуба

<img width="1076" height="367" alt="image" src="https://github.com/user-attachments/assets/2fa2f577-804b-4f9e-94cf-236a94afbe55" />

> Применение манифестов

<img width="691" height="374" alt="image" src="https://github.com/user-attachments/assets/7a44d0b3-aca2-444b-8fd7-b14181426cb0" />

---

### Проверка таблиц PostgreSQL

Я специально добавил в манифест PGAdmin4 чтобы удобно посмотреть что как создалось

<img width="306" height="101" alt="image" src="https://github.com/user-attachments/assets/871c7dbe-db71-4789-b505-582b8a1c7d88" />

<details><summary>Таблица options</summary>

<img width="287" height="118" alt="image" src="https://github.com/user-attachments/assets/3f0cc345-aa1b-4bc2-a9b1-7aa326b676e6" />

</details>

<details><summary>Таблица questions</summary>

<img width="263" height="79" alt="image" src="https://github.com/user-attachments/assets/bf626347-ed26-4fa2-a11c-8a954b089697" />

</details>

<details><summary>Таблица votes</summary>

<img width="220" height="81" alt="image" src="https://github.com/user-attachments/assets/b4a9d4ea-2479-4417-8287-9be5abfe8994" />

</details>

---

### Проверка стримлита

<details><summary>Начальная страница (создание опроса)</summary>

<img width="1319" height="554" alt="image" src="https://github.com/user-attachments/assets/fb1c869a-56aa-4c94-b632-c948d5e52145" />

</details>

<details><summary>Страница прохождения опросов</summary>

<img width="772" height="560" alt="image" src="https://github.com/user-attachments/assets/a1a7d586-6a04-440a-bb97-b43fc4bce3f8" />

</details>

<details><summary>Страница результатов</summary>

<img width="2312" height="844" alt="image" src="https://github.com/user-attachments/assets/eb1360dc-f695-47a3-8cfc-dc8c63f04719" />

</details>

---

### Проверка заполненности таблиц в PGAdmin4

<details><summary>Таблица options</summary>

<img width="315" height="356" alt="image" src="https://github.com/user-attachments/assets/f565b88b-fbeb-4b15-86a2-c8432f4a03b8" />

</details>

<details><summary>Таблица questions</summary>

<img width="330" height="258" alt="image" src="https://github.com/user-attachments/assets/d0e6cf0d-90c9-4122-a77d-5bff9f9c4ba4" />

</details>

<details><summary>Таблица votes</summary>

<img width="289" height="613" alt="image" src="https://github.com/user-attachments/assets/ff316944-c556-4380-8516-cb5decf6fc5f" />

</details>

---

## Проблемы при работе с лабораторной работой

| Проблема | Решение |
|-------------|-------------|
| В кластере Kubernetes остались следы от предыдущей лабораторной работы с Odoo | Очистил все кластера деплоев и сервисов в kubectl |
| При создании опроса возникала ошибка `sqlalchemy.orm.exc.DetachedInstanceError` | Немного поменял логику файла `main.py`, сделал сохранение id объекта пораньше |
| Проблема с открытием pgAdmin в браузере | Пробросил другой порт, все заработало |
| Компьютер не выдерживает такой нагрузки с виртуализацией, часто зависало, два раза ПК даже перезагружался сам по себе, просто потому что | Через силу, через боль... |

## Выводы

>> В ходе выполнения работы была успешно достигнута цель по созданию и развертыванию трехзвенного приложения (Frontend, Backend, Database) в кластере Kubernetes, а также отработаны навыки организации сетевого взаимодействия
