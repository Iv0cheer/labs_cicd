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
