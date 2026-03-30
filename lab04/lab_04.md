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

### Папка backend включает в себя 3 файла:

#### Файл main.py

Скрипт, работающий на основе API на FastAPI. Содержит в себе функции

* Модели данных (как выглядят таблицы в постгри)
* Логику обработки запросов
* URL по которым можно обращаться к сервисам (API как раз)

<details><summary>Листинг кода файла main.py</summary>

```python

```


</details>

#### Файл requirements.txt

Содержит зависимости для любимого питона

<details><summary>Листинг файла requirements.txt</summary>

```python

```

</details>


#### Файл backend/Dockerfile

Содержит docker-образ бэкенда

<details><summary>Листинг файла Dockerfile</summary>

```python

```

</details>


### Папка frontend включает в себя также 3 файла:

#### requirements.txt

Содержит зависимости для любимого питона

<details><summary>Листинг файла requirements.txt</summary>

```python

```

</details>


#### Файл app.py

Содержит UI для стримлита

<details><summary>Листинг кода файла app.py</summary>

```python

```

#### Файл frontend/Dockerfile

Содержит docker-образ фронтА

<details><summary>Листинг файла Dockerfile</summary>

```python

```

</details>


### Папка k8s и манифест:

Содержит docker-образ фронтА

<details><summary>Листинг файла fullstack.yaml</summary>

```yaml

```

</details>


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


## Проблемы при работе с лабораторной работой

| Проблема | Решение |
|-------------|-------------|
| В кластере Kubernetes остались следы от предыдущей лабораторной работы с Odoo | Очистил все кластера деплоев и сервисов в kubectl |
| При создании опроса возникала ошибка `sqlalchemy.orm.exc.DetachedInstanceError` | Немного поменял логику файла `main.py`, сделал сохранение id объекта пораньше |
| Проблема с открытием pgAdmin в браузере | Пробросил другой порт, все заработало |
| Компьютер не выдерживает такой нагрузки с виртуализацией, часто зависало, два раза ПК даже перезагружался сам по себе, просто потому что | Через силу, через боль... |
