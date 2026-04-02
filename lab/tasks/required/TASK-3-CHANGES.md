# Изменения для Task 3 fix

## Изменённые файлы

Эти файлы нужно скопировать на VM в `~/se-toolkit-lab-7/bot/`:

### 1. `bot/services/llm_client.py`
**Изменения:**
- Улучшен system prompt — явно требует вызова инструментов
- Добавлен `debug` параметр в `chat_with_tools()`
- Добавлены debug логи для отслеживания tool calls

### 2. `bot/handlers/intent_router.py`
**Изменения:**
- Добавлены debug логи для диагностики
- Вывод LLM URL и модели в debug режиме

---

## Как загрузить на VM

### Вариант 1: Через git (рекомендуется)

```bash
# На хосте (Windows)
git add bot/services/llm_client.py bot/handlers/intent_router.py
git commit -m "Fix Task 3: Add debug logging and improve tool calling"
git push

# На VM
cd ~/se-toolkit-lab-7
git pull
```

### Вариант 2: Через SCP

```powershell
# На хосте (Windows PowerShell)
scp bot/services/llm_client.py root@10.93.24.134:~/se-toolkit-lab-7/bot/services/
scp bot/handlers/intent_router.py root@10.93.24.134:~/se-toolkit-lab-7/bot/handlers/
```

### Вариант 3: Через общую папку

Если используете Samba/общую папку — скопируйте файлы напрямую.

---

## Проверка на VM

```bash
# 1. Restart Qwen proxy (если 401 ошибка)
cd ~/qwen-code-oai-proxy && docker compose restart

# 2. Проверить .env.bot.secret
cat .env.bot.secret
# Должно быть:
# LLM_API_KEY=am70fMzdYbObjpscFKEGr3nw4PcDkdFqy7TP5VeZ1oyb4cihcVkVyZ4i95LGt7cK6UnVC-4mFlyR3ZBtBOYtpA
# LLM_API_BASE_URL=http://localhost:42005/v1
# LLM_API_MODEL=coder-model

# 3. Тестировать
cd ~/se-toolkit-lab-7/bot
uv run bot.py --test "what labs are available" 2>&1 | head -30
```

**Ожидаемый вывод:**
```
[router] Processing query: what labs are available
[router] LLM URL: http://localhost:42005/v1
[router] LLM model: coder-model
[tool] LLM called: get_items({})
[tool] Result: [...]
[summary] Feeding 1 tool result(s) back to LLM
```

**Если видите `[router] LLM not configured`** — проверьте `.env.bot.secret`.

**Если видите `[tool] LLM called`** — инструмент вызывается, всё работает!

---

## Тесты для autochecker

```bash
# Тест 1
uv run bot.py --test "what labs are available"

# Тест 2
uv run bot.py --test "show me scores for lab 4"

# Тест 3
uv run bot.py --test "which lab has the lowest pass rate"

# Тест 4
uv run bot.py --test "asdfgh"
```

Каждый тест должен выводить реальные данные из backend, а не заглушки.
