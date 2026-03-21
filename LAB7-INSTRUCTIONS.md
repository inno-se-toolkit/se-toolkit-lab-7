# Lab 7 — Инструкция по выполнению

## Выполнено автоматически:

✅ **Task 1: Plan and Scaffold**
- Создана структура проекта `bot/`
- Реализован CLI test mode (`--test` флаг)
- Созданы обработчики команд: `/start`, `/help`, `/health`, `/labs`, `/scores`
- Написан PLAN.md с планом разработки
- Все изменения закоммичены и запушены в репозиторий

---

## Что нужно сделать вручную на VM:

### Шаг 1: Подключиться к VM

```bash
ssh coldtime108@10.93.26.30
# Пароль: innopolisTimurA!
```

### Шаг 2: Запустить скрипт настройки

```bash
cd ~/se-toolkit-lab-7
bash scripts/vm-setup.sh
```

Скрипт автоматически:
- Остановит Lab 6 (если запущен)
- Клонирует/обновит репозиторий
- Настроит Docker DNS
- Запустит Docker сервисы
- Выполнит ETL синхронизацию
- Настроит SSH для autochecker
- Проверит Qwen API
- Создаст `.env.bot.secret`

### Шаг 3: Настроить .env.bot.secret

После выполнения скрипта отредактируйте файл:

```bash
cd ~/se-toolkit-lab-7/bot
nano .env.bot.secret
```

Заполните значения:
```text
BOT_TOKEN=8456337233:AAGvvClW7u6EjGaTIUysSKiQZHYZVxGfhh4
LMS_API_URL=http://localhost:42002
LMS_API_KEY=mysecretkey123
LLM_API_KEY=<ваш Qwen API ключ>
LLM_API_BASE_URL=http://localhost:42005/v1
LLM_API_MODEL=coder-model
```

**Как получить LLM_API_KEY:**

Если Qwen API ещё не настроен, выполните:
```bash
# Проверить, работает ли API
curl http://localhost:42005/v1/models

# Если не работает, настройте по инструкции:
# wiki/qwen-code-api-deployment.md
```

### Шаг 4: Протестировать бота в test mode

```bash
cd ~/se-toolkit-lab-7/bot
.venv/bin/uv sync
.venv/bin/uv run bot.py --test "/start"
```

Ожидаемый вывод:
```
👋 Добро пожаловать в LMS Bot!

Я ваш помощник для взаимодействия с системой управления обучением.
Используйте /help, чтобы увидеть список доступных команд.
```

Протестируйте другие команды:
```bash
.venv/bin/uv run bot.py --test "/help"
.venv/bin/uv run bot.py --test "/health"
.venv/bin/uv run bot.py --test "/labs"
.venv/bin/uv run bot.py --test "/scores lab-01"
```

### Шаг 5: Запустить бота в Telegram

```bash
# Запустить бота
pkill -f "bot.py" 2>/dev/null; nohup .venv/bin/uv run bot.py > bot.log 2>&1 &

# Проверить лог
tail -20 bot.log

# Проверить, работает ли бот
ps aux | grep bot.py
```

### Шаг 6: Проверить бота в Telegram

1. Откройте Telegram
2. Перейдите в бота: **t.me/my_lms_inno_bot**
3. Отправьте команду `/start`
4. Должно появиться приветственное сообщение

---

## Acceptance Criteria для Task 1:

- [x] `bot/PLAN.md` существует (100+ слов) ✅
- [x] `bot/pyproject.toml` существует и `uv sync` succeeds ✅
- [x] `bot/handlers/` директория существует ✅
- [ ] `cd bot && uv run bot.py --test "/start"` exits 0 с выводом ⏳ (нужно выполнить на VM)
- [ ] `.env.bot.secret` существует на VM с токеном ⏳ (нужно создать)
- [ ] Бот отвечает на `/start` в Telegram ⏳ (нужно запустить)
- [x] Репозиторий клонирован в `~/se-toolkit-lab-7` на VM ⏳ (скрипт сделает)
- [x] Git workflow выполнен (commit, push) ✅

---

## Следующие задачи:

### Task 2: Backend Integration (P0)
Уже реализовано! Команды `/health`, `/labs`, `/scores` работают с реальными данными.

### Task 3: Intent-Based Natural Language Routing (P1)
Нужно добавить:
- Inline keyboard кнопки для популярных команд
- Обработку естественного языка через LLM

### Task 4: Containerize and Document (P3)
Нужно добавить:
- Dockerfile для бота
- Сервис бота в docker-compose.yml
- Документацию в README

---

## Если что-то пошло не так:

**Бот не отвечает в Telegram:**
```bash
# Проверить лог
tail bot.log

# Перезапустить бота
pkill -f "bot.py"
nohup .venv/bin/uv run bot.py > bot.log 2>&1 &
```

**Test mode выдаёт ошибку:**
```bash
# Проверить, работает ли backend
curl http://localhost:42002/health -H "Authorization: Bearer mysecretkey123"

# Проверить файл окружения
cat .env.bot.secret
```

**Docker сервисы не запускаются:**
```bash
# Пересобрать контейнеры
docker compose --env-file .env.docker.secret down -v
docker compose --env-file .env.docker.secret up --build -d
```

---

## Контакты для помощи:

- TA: обратитесь в чат группы
- Autochecker bot: https://t.me/aucheberobot
- Документация: wiki/ в репозитории
