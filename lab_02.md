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

[Файл generate_data.py](/generate_data.py)


### **Шаг №2. Были реализованы 3 CLI аргумента:**

* --output (можно изменять путь для сохранения CSV файла)
* --count (можно изменять количество генерируемых данных)
* --seed (можно изменять для изменения рандома данных (ключ рандома/соль))

<details>
  <summary> ___Часть кода с реализацией CLI аргументов (сама функция)___ </summary>
  
  ```py
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
  ```

</details>

### **Шаг 3. Изменения лоадера в PostgreSQL**

Был изменен DDL-скрипт
<details><summary>Был изменен DDL-скрипт</summary>
  
  ```py
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
  ```

</details>

### **Шаг 4. Изменение дашборда**

Дашборд был также видоизменен под поставленную предметную область.

[Файл dashboard.py](/dashboard.py)

### **Шаг 5. Запуск билда Docker**

После всех изменений, был произведен запуск билда Docker.

<img width="1426" height="339" alt="image" src="https://github.com/user-attachments/assets/db1ab217-8a4b-4679-9207-c50a196ee04a" />

<img width="2040" height="577" alt="image" src="https://github.com/user-attachments/assets/007dd73a-744c-411d-b00d-61d4e671a73a" />


### **Шаг 6. Запуск localhost для проверки работоспособности дашборда.**

<img width="2314" height="866" alt="image" src="https://github.com/user-attachments/assets/81f12f33-5a9e-4bce-b8a5-76c2a14f775b" />

<img width="2311" height="1085" alt="image" src="https://github.com/user-attachments/assets/a5b4cefd-094d-4adf-b48b-6d46b108e058" />


#### **Анализ для бизнеса:**

1. Сокращать время первого ответа. Возможно первый ответ запускает диалог и уточнение проблемы, пока пользователь на месте. Возможно стоит сделать базу знаний или чат бота для автоматического решения частых проблем (или добавить автоответ с уточнением).
2. Перераспределить нагрузку в выходные. В выходные время решения выше. Проблема не в ответе - а в человеческих ресурсах. Нужно обновить или добавить кого-нибудь в команду (нужна дежурная смена)
3. Управление пиковыми часами - видны дневные пики, соответственно нужно больше операторов днем, чем ночью



## **Выводы по работе**

Освоил полный цикл создания воспроизводимых аналитических решений: от написания Python-кода для обработки данных до контейнеризации с помощью Docker и развертывания в изолированной среде.


## **Приложение**

* [Файл dashboard.py](/dashboard.py)
* [Файл loader.py](/loader.py)
* [Файл generate_data.py](/generate_data.py)
