# Flutter Web Control Panel

The Telegram bot is useful, but some users prefer opening a browser instead of chatting in Telegram. In this optional task, you build a small Flutter web control panel that shows the same core information and actions in a browser UI.

This is a browser-based companion to the Telegram bot: same backend, same data, same commands, but presented as a web app.

## Requirements targeted

- **P4.1** Flutter web app with a useful UI
- **P4.2** Served through Caddy on `/flutter`
- **P4.3** Queries the LMS backend through the same endpoints
- **P4.4** Quick actions for common bot commands

## What you will build

A Flutter web app with a simple dashboard and action panel. Caddy serves the compiled Flutter build at `/flutter`, so users can open `http://<your-vm-ip-address>:42002/flutter` in a browser.

The app should show:

- a header with the project name
- quick action buttons for common commands
- a results panel that updates when the user clicks a button
- a list of recent responses or current data

## Commands and menu

The app must support the same slash commands as the Telegram bot. When the user types a message starting with `/`, the app handles it directly:

| Command         | What it does                         |
| --------------- | ------------------------------------ |
| `/start`        | Welcome message with app description |
| `/help`         | Lists all commands with descriptions  |
| `/health`       | Calls backend, reports up/down       |
| `/labs`         | Lists available labs                 |
| `/scores <lab>` | Per-task pass rates for a lab        |

The app must show a **command menu** — a set of clickable buttons or chips visible in the UI so users can discover available actions without typing.

## How it works

The Flutter app runs entirely in the browser. It calls the backend API endpoints through Caddy:

| What           | Browser app                                       |
| -------------- | ------------------------------------------------- |
| Transport      | Browser (Flutter web)                             |
| Backend access | `/items`, `/analytics/*` (via Caddy reverse proxy) |
| Hosting        | Static files served by Caddy                      |

## Backend endpoints

Same endpoints as the Telegram bot, all available through Caddy without the `Authorization` header:

| Endpoint                                         | Returns                        |
| ------------------------------------------------ | ------------------------------ |
| `GET /items/`                                    | Labs and tasks                 |
| `GET /learners/`                                 | Enrolled students              |
| `GET /analytics/scores?lab=lab-01`               | Score distribution (4 buckets) |
| `GET /analytics/pass-rates?lab=lab-01`           | Per-task averages              |
| `GET /analytics/timeline?lab=lab-01`             | Submissions per day            |
| `GET /analytics/groups?lab=lab-01`               | Per-group performance          |
| `GET /analytics/top-learners?lab=lab-01&limit=5` | Top N learners                 |
| `GET /analytics/completion-rate?lab=lab-01`      | Completion percentage          |
| `POST /pipeline/sync`                            | Trigger ETL sync               |

## Deliverables

### 1. Flutter web app (`flutter_chatbot/`)

A Flutter project inside the repo with a simple web UI. The app must:

- display a browser-friendly control panel
- show a command menu with buttons or chips
- handle `/start`, `/help`, `/health`, `/labs`, `/scores <lab>` directly
- call backend endpoints and render their results
- handle errors gracefully

The project structure:

```text
se-toolkit-lab-7/
├── flutter_chatbot/         ← NEW
│   ├── lib/
│   │   ├── main.dart        ← entry point
│   │   ├── dashboard.dart   ← UI
│   │   └── lms_service.dart ← backend API client
│   ├── web/                 ← Flutter web assets
│   ├── pubspec.yaml         ← dependencies
│   └── ...
├── bot/                     ← existing Telegram bot
├── backend/                 ← existing
└── docker-compose.yml       ← existing
```

### 2. Compiled web build

Build the Flutter app for web and place the output where Caddy can serve it:

```terminal
cd flutter_chatbot
flutter build web --base-href /flutter/
```

### 3. Caddy configuration (`caddy/Caddyfile`)

Add a route to serve the Flutter build at `/flutter`:

```text
handle_path /flutter* {
    root * /srv/flutter
    try_files {path} /index.html
    file_server
}
```

### 4. Docker integration

Update the Caddy service in `docker-compose.yml` to mount the Flutter build directory:

```yaml
caddy:
  volumes:
    - ./caddy/Caddyfile:/etc/caddy/Caddyfile
    - ./flutter_chatbot/build/web:/srv/flutter
```

## Verify

### Build the Flutter app

On your VM (or locally), install Flutter and build:

```terminal
cd ~/se-toolkit-lab-7/flutter_chatbot
flutter build web --base-href /flutter/
```

### Update Caddy and restart

```terminal
cd ~/se-toolkit-lab-7
docker compose --env-file .env.docker.secret up --build -d
```

### Verify in the browser

Open `http://<your-vm-ip-address>:42002/flutter` in your browser. You should see the browser control panel.

**What to check:**

1. The page loads without errors
2. A command menu is visible
3. Click a menu button — the corresponding command runs and a response appears
4. Type `/health` — the app reports backend status
5. Type `/labs` — the app lists available labs
6. Type `/scores lab-04` — the app shows per-task pass rates
7. Type `hello` — the app responds with a friendly message, not an error

### Common problems

| Symptom                        | Likely cause                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------- |
| 404 at `/flutter`             | Caddy route missing or Flutter build not mounted. Check `Caddyfile` and `docker-compose.yml`.   |
| Blank page, console errors    | `--base-href` not set to `/flutter/` during build. Rebuild with the correct base href.           |
| CORS errors in browser console | Backend rejecting cross-origin requests. Use relative URLs and go through Caddy.                |
| Request fails in browser      | Check that the backend is healthy and the app is calling the proxied endpoint paths.             |

## Acceptance criteria

### On `GitHub`

- [ ] [`Git workflow`](../../../wiki/git-workflow.md) followed (issue, branch, PR, review, merge).

### On `GitHub` on the `main` branch

- [ ] `flutter_chatbot/` directory with a Flutter project exists.
- [ ] `flutter_chatbot/pubspec.yaml` exists.
- [ ] `caddy/Caddyfile` includes a `/flutter` route.
- [ ] Source code contains a command menu (buttons, chips, or equivalent UI element).

### On the VM (REMOTE)

- [ ] `curl -sf http://localhost:42002/flutter/ | head -c 100` returns HTML.
- [ ] Backend still healthy (`curl -sf http://localhost:42002/docs` returns 200).
- [ ] Browser control panel loads at `http://<your-vm-ip-address>:42002/flutter`.
- [ ] Command menu is visible with clickable actions.
- [ ] `/health` returns backend status.
- [ ] `/labs` lists available labs.
- [ ] `/scores lab-04` shows per-task pass rates.
