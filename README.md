# YandexGPT: извлечение сущностей из юридических документов

Docker-окружение для домашнего задания по NER. Интерфейс — JupyterLab.
Базовый образ: официальный Jupyter Docker Stacks с датированным тегом.
Дополнительные библиотеки перечислены в `requirements.txt`; диапазоны версий
не являются lock-файлом и могут разрешаться иначе при будущей пересборке.

## Настройка

Требуются запущенный Docker Desktop и Docker Compose.

При первом клонировании:

```bash
cp .env.example .env
chmod 600 .env
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Вставьте сгенерированное значение в `JUPYTER_TOKEN` внутри `.env`.
Если локальный `.env` уже подготовлен, повторно копировать шаблон не нужно.
Заполните `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`. `YANDEX_MODEL_URI` можно
заполнить позже при настройке запросов. Секреты вводятся только локально.

## Запуск

```bash
docker compose up -d --build
docker compose ps
```

Откройте http://localhost:8888/lab и введите `JUPYTER_TOKEN` из `.env`.
Порт доступен только на локальном компьютере. Авторизация Jupyter включена.
Для другого порта измените `JUPYTER_PORT` в `.env`.

Папки `notebooks/`, `data/` и `outputs/` сохраняются на компьютере и доступны
в Jupyter. Удаление контейнера не удаляет эти файлы.

Проверка доступности настроек в ячейке без вывода ключа:

```python
import os

assert os.environ.get("YANDEX_API_KEY"), "Заполните YANDEX_API_KEY в .env"
assert os.environ.get("YANDEX_FOLDER_ID"), "Заполните YANDEX_FOLDER_ID в .env"
print("Настройки YandexGPT доступны")
```

Compose передаёт переменные при создании контейнера; `load_dotenv()` внутри
ноутбука не нужен. После изменения ключа пересоздайте контейнер:

```bash
docker compose up -d --force-recreate
```

Остановка:

```bash
docker compose down
```

## Секреты и публикация

`.env` исключён из Git; в репозитории хранится только `.env.example`.
Docker получает при сборке только Dockerfile и requirements.txt: секреты
не попадают в образ. В контейнер передаются переменные окружения, а сам
файл `.env` не монтируется. Не выводите ключи и всё окружение в ноутбуках;
перед публикацией проверьте сохранённые выводы ячеек.

На этом этапе API-клиент и NER-пайплайн ещё не реализованы.
