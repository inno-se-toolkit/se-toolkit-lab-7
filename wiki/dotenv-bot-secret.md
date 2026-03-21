# `.env.bot.secret`

<h2>Table of contents</h2>

- [About `.env.bot.secret`](#about-envbotsecret)
- [`BOT_TOKEN`](#bot_token)
- [LMS backend connection](#lms-backend-connection)
  - [`LMS_API_BASE_URL`](#lms_api_base_url)
  - [`LMS_API_KEY`](#lms_api_key)

## About `.env.bot.secret`

`.env.bot.secret` is a [`.env` file](./environments.md#env-file) that stores [environment variables](./environments.md#environment-variable) for the Telegram bot.

The values configure the bot token and the [LMS API](./lms-api.md#about-the-lms-api) connection.

Default values: [`.env.bot.example`](../.env.bot.example)

> [!NOTE]
> `.env.bot.secret` was added to [`.gitignore`](./git.md#gitignore) because you may specify there
> [secrets](./environments.md#secrets) such as the [`BOT_TOKEN`](#bot_token).

## `BOT_TOKEN`

The Telegram bot token obtained from [`@BotFather`](https://core.telegram.org/bots#botfather).

Default: `<bot-token>`

## LMS backend connection

The bot calls these endpoints to communicate with the [LMS API](./lms-api.md#about-the-lms-api).

### `LMS_API_BASE_URL`

The [LMS API base URL](./lms-api.md#lms-api-base-url).

Default: `<lms-api-base-url>`

### `LMS_API_KEY`

The [LMS API key](./lms-api.md#lms-api-key).

Its value must match the value of [`LMS_API_KEY`](./dotenv-docker-secret.md#lms_api_key) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret) used for deployment.

Default: `my-secret-api-key`
