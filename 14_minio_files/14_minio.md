# ДЗ 14. Запустить сервис S3
## Домашнее задание
Запустить сервис S3

Цель:
научиться работать с S3 подобными сервисами

Описание/Пошаговая инструкция выполнения домашнего задания:
1. Запустить сервис S3 в облаке или локально (Docker + minio)
2. Создать бакет используя API
3. Сохранить файл в бакет используя API
4. Сохраните файл программно - выберите знакомый язык программирования (C#, Java, Go, Python или любой другой, для которого есть библиотека для работы с S3), отправьте файл в бакет и потом получите массив файлов из бакет и отобразите в браузере или консоли.

Для пунктов 2 и 3 сделайте скриншоты результата выполнения.  
Для пункта 4 приложите ссылку на репозитарий на гитхабе с исходным кодом.

---
## Запуск MinIO в Docker

Запускаем MinIO в Docker:
```bash
docker run -d --name otus_minio -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

Коннектимся к контейнеру и запускаем `bash` и далее будем работать через встроенную утилиту `mc`:
```bash
docker exec -it otus_minio bash
```

Сначала зададим `alias` с именем `otus`:
```bash
mc alias set otus http://localhost:9000 
```

Проверяем:
```bash
mc alias ls otus
otus
  URL       : http://localhost:9000
  AccessKey : 
  SecretKey : 
  API       : 
  Path      : auto
  Src       : /tmp/.mc/config.json
```
Алиас успешно создан.

Далее создаём новый `bucket` с именем `mybucket` по пути `myminio`:
```bash
mc mb myminio/mybucket
Bucket created successfully `myminio/mybucket`.
```

Проверяем наличие бакета по пути `myminio`:
```bash
mc ls myminio
[2025-07-10 15:08:47 UTC] 4.0KiB mybucket/
```

Создадим файл, которые потом положим в `mybucket`:
```bash
echo "Hello MinIO from Otus" > hello.txt
```

Загрузим файл `hello.txt`
```bash
mc cp hello.txt myminio/mybucket
```

Проверяем наличие файла:
```bash
mc ls myminio/mybucket
[2025-07-10 15:22:52 UTC]    22B hello.txt
```

![png](14_minio_files/first_test.png)

## Работа с MinIO через Python

Устанавливаем библиотеку `minio`:
```bash
pip install minio
```

Создаём `otusminio.py`:
```python
from minio import Minio
from minio.error import S3Error
import os

# Инициализация клиента MinIO
minio_client = Minio(
    endpoint="localhost:9000",
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
)

bucket_name = "my-test-bucket"

def create_bucket():
    """Создает бакет"""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Бакет {bucket_name} успешно создан")
        else:
            print(f"Бакет {bucket_name} уже существует")
    except S3Error as exc:
        print(f"Ошибка при создании бакета: {exc}")

def upload_file(file_path, object_name=None):
    """Загружает файл в бакет"""
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )
        print(f"Файл {file_path} успешно загружен как {object_name}")
    except S3Error as exc:
        print(f"Ошибка при загрузке файла: {exc}")

def list_files():
    """Выводит список файлов в бакете"""
    try:
        objects = minio_client.list_objects(bucket_name)
        print("\nФайлы в бакете:")
        for obj in objects:
            print(f"- {obj.object_name} (размер: {obj.size} байт, дата: {obj.last_modified})")
    except S3Error as exc:
        print(f"Ошибка при получении списка файлов: {exc}")

def download_and_display(object_name):
    """Скачивает и отображает содержимое файла"""
    try:
        response = minio_client.get_object(bucket_name, object_name)
        content = response.read().decode('utf-8')
        print(f"\nСодержимое файла {object_name}:\n{content}")
    except S3Error as exc:
        print(f"Ошибка при получении файла: {exc}")
    finally:
        response.close()
        response.release_conn()

def main():
    create_bucket()
    
    # Создаем тестовый файл
    test_file = "example.txt"
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("Hello from MinIO Python client!\nThis is a test file.")
    
    upload_file(test_file)
    list_files()
    download_and_display(test_file)

if __name__ == "__main__":
    main()
```

Запускаем:
```bash
python3 otusminio.py
Бакет my-test-bucket успешно создан
Файл example.txt успешно загружен как example.txt

Файлы в бакете:
- example.txt (размер: 52 байт, дата: 2025-07-10 16:00:00.501000+00:00)

Содержимое файла example.txt:
Hello from MinIO Python client!
This is a test file.
```

![png](14_minio_files/python_result.png)
