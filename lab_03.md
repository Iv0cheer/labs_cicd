# **Лабораторная работа 3.1. Развертывание приложения в Kubernetes**

### Вариант № 19

| Основной сервис (App) | Вспомогательный сервис (DB/Tool) | Задача |
|------------------------|-----------------------------------|--------|
| Odoo                  | PostgreSQL                       | Развернуть ERP-систему Odoo. Проверить доступность веб-интерфейса и связь с БД. |


### Создание манифестов

<img width="261" height="125" alt="image" src="https://github.com/user-attachments/assets/74578bae-c253-425b-98bb-9eec5be0cad4" />

<details><summary>**Файл postgres-deployment.yaml**</summary>
  
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
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
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "odoo"
        - name: POSTGRES_USER
          value: "odoo"
        - name: POSTGRES_PASSWORD
          value: "odoo"
        volumeMounts:
        - mountPath: /var/lib/postgresql/data
          name: postgres-storage
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```
</details>

<details><summary>**Файл postgres-service.yaml**</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
```

</details>


<details><summary>**Файл odoo-deployment.yaml**</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odoo-deployment
  labels:
    app: odoo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: odoo
  template:
    metadata:
      labels:
        app: odoo
    spec:
      initContainers:
      - name: init-odoo-db
        image: odoo:17
        command:
          - odoo
          - -d
          - odoo
          - --db_host=postgres-service
          - --db_user=odoo
          - --db_password=odoo
          - --db_port=5432
          - -i
          - base
          - --stop-after-init
        env:
        - name: HOST
          value: "postgres-service"
        - name: PORT
          value: "5432"
        - name: USER
          value: "odoo"
        - name: PASSWORD
          value: "odoo"
      containers:
      - name: odoo
        image: odoo:17
        ports:
        - containerPort: 8069
        env:
        - name: HOST
          value: "postgres-service"
        - name: PORT
          value: "5432"
        - name: USER
          value: "odoo"
        - name: PASSWORD
          value: "odoo"
        - name: DB_NAME
          value: "odoo"
```

</details>

<details><summary>**Файл odoo-service.yaml**</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: odoo-service
spec:
  type: NodePort
  selector:
    app: odoo
  ports:
    - protocol: TCP
      port: 8069
      targetPort: 8069
      nodePort: 30019
```

</details>


### Запуск сервиса и БД

Запуск minikube

<img width="997" height="281" alt="image" src="https://github.com/user-attachments/assets/c44c404b-6594-466e-8361-ec8cbf4c2f86" />


Применение манифестов

<img width="976" height="237" alt="image" src="https://github.com/user-attachments/assets/2c591f6e-7170-4e35-9fd4-160fd415e824" />



Скриншот команды `kubectl get pods` и `kubectl get services`:

<img width="1008" height="245" alt="image" src="https://github.com/user-attachments/assets/1af4132c-3f03-44eb-80ce-efe7e34dbdcd" />

Просмотр IP запущенного сервиса и проверка работоспособности `Odoo`:

<img width="628" height="85" alt="image" src="https://github.com/user-attachments/assets/ce132d12-4caf-4b15-a0ed-de0f57248871" />

<img width="2310" height="820" alt="image" src="https://github.com/user-attachments/assets/95bdeb2d-51cb-492c-bbbf-dc6b24d68170" />

Создание БД

<img width="436" height="709" alt="image" src="https://github.com/user-attachments/assets/1c1c2876-ce07-4229-be8b-0c6d2ef33d35" />

Вход и просмотр начальной страницы

<img width="2323" height="1016" alt="image" src="https://github.com/user-attachments/assets/842a6f59-e310-4950-afda-b5933065fd94" />

Проверка работоспособности демо таблиц

<img width="2313" height="1208" alt="image" src="https://github.com/user-attachments/assets/dd7813e2-e445-47e7-92d5-3a4789d3f41c" />


## Выводы

В ходе выполнения лабораторной работы была успешно развернута ERP-система Odoo 17 в связке с СУБД PostgreSQL в кластере Kubernetes.

Трудности:
* Проблема инициализации базы данных: При первом запуске Odoo не мог найти таблицы в PostgreSQL, хотя подключение к БД устанавливалось. Ошибка `relation "ir_module_module" does not exist`
* В версии Odoo 17 отсутствует параметр --db_name, пришлось его вписывать вручную. Нельзя было посмотреть логи без него
