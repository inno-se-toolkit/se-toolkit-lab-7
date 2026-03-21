# Lab 7 Bot — Инструкция по развёртыванию на VM

## Подключение к VM

```bash
# Через VPN университета
ssh root@<vm-ip-address>
# или
ssh <your-username>@<vm-ip-address>
```

## Быстрое развёртывание

```bash
cd ~/se-toolkit-lab-7
chmod +x scripts/deploy-bot.sh
./scripts/deploy-bot.sh
```

## Ручное развёртывание

### Шаг 1: Pull изменений

```bash
cd ~/se-toolkit-lab-7
git pull origin main
```

### Шаг 2: Настройка переменных окружения

Создайте `.env.docker.secret` в корне проекта:

```bash
cp .env.docker.example .env.docker.secret
nano .env.docker.secret
```

**Обязательные переменные:**

| Переменная | Описание | Где взять |
|------------|----------|-----------|
| `BOT_TOKEN` | Telegram bot token | [@BotFather](https://t.me/BotFather) |
| `LMS_API_KEY` | Ключ LMS API | Из предыдущих lab |
| `LMS_API_HOST_ADDRESS` | Адрес хоста для API | `0.0.0.0` |
| `LMS_API_HOST_PORT` | Порт API | `42002` |
| `BACKEND_HOST_ADDRESS` | Адрес хоста backend | `127.0.0.1` |
| `BACKEND_HOST_PORT` | Порт backend | `42002` |

**Опциональные (для LLM):**

| Переменная | Описание |
|------------|----------|
| `LLM_API_KEY` | Ключ LLM API |
| `LLM_API_BASE_URL` | URL LLM API (например, `http://host.docker.internal:42005`) |
| `LLM_API_MODEL` | Модель (например, `coder-model`) |

### Шаг 3: Запуск бота

```bash
# Остановить старый процесс бота (если есть)
pkill -f "bot.py" 2>/dev/null || true

# Запустить через Docker Compose
docker compose --env-file .env.docker.secret up --build -d bot

# Проверить статус
docker compose --env-file .env.docker.secret ps bot

# Посмотреть логи
docker compose --env-file .env.docker.secret logs bot --tail 30
```

## Проверка работы

### 1. В Telegram

Откройте вашего бота и отправьте:

```
/start
```

Должно появиться приветственное сообщение.

### 2. Тестовые команды

```
/help
/health
/labs
/scores lab-04
```

### 3. Natural language (если настроен LLM)

```
какие есть лабораторные работы?
покажи оценки для lab-04
```

## Troubleshooting

### Бот не отвечает в Telegram

1. Проверьте `BOT_TOKEN`:
```bash
docker compose --env-file .env.docker.secret logs bot | grep -i "token\|auth"
```

2. Убедитесь что бот запущен:
```bash
docker compose --env-file .env.docker.secret ps bot
```

### Ошибка "connection refused" к backend

В Docker используется сетевое имя сервиса, не `localhost`:

```bash
# В .env.docker.secret должно быть:
LMS_API_BASE_URL=http://backend:8000
```

### LLM возвращает ошибку подключения

1. Проверьте доступность LLM:
```bash
curl http://localhost:42005/v1/models -H "Authorization: Bearer YOUR_LLM_API_KEY"
```

2. В Docker используйте `host.docker.internal`:
```bash
LLM_API_BASE_URL=http://host.docker.internal:42005
```

### Бот падает при старте

Посмотрите полные логи:
```bash
docker compose --env-file .env.docker.secret logs bot
```

Частые причины:
- Отсутствует `BOT_TOKEN`
- Неправильный `LMS_API_KEY`
- Backend не запущен

## Обновление бота

```bash
cd ~/se-toolkit-lab-7
git pull origin main
docker compose --env-file .env.docker.secret up --build -d bot
```

## Остановка бота

```bash
docker compose --env-file .env.docker.secret stop bot
# или удалить контейнер
docker compose --env-file .env.docker.secret rm -f bot
```

## Проверка acceptance criteria

### На GitHub (main branch)

- [ ] `bot/PLAN.md` существует (≥100 слов)
- [ ] `bot/pyproject.toml` существует
- [ ] `bot/handlers/` с модулями существует
- [ ] `bot/Dockerfile` существует
- [ ] `docker-compose.yml` содержит сервис `bot`
- [ ] README содержит секцию "Deploy"

### На VM

- [ ] Репозиторий клонирован в `~/se-toolkit-lab-7`
- [ ] `.env.bot.secret` с `BOT_TOKEN`, `LMS_API_KEY` существует
- [ ] `cd bot && uv sync` работает (или Docker build)
- [ ] `cd bot && python bot.py --test "/start"` exit 0 с выводом
- [ ] Бот контейнер запущен (`docker ps`)
- [ ] Бот отвечает в Telegram на `/start`
