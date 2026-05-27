# Find That Voice Bot

A minimal but production-usable Telegram inline voice search bot.

## Features
- Save voice messages with a custom text description.
- Instantly search and send saved voice messages in any chat using inline mode (`@botname query`).
- Simple Django admin panel to view users and voices.
- Built with Python, Aiogram 3, Django ORM, and PostgreSQL.

## How to Run Locally

### 1. Configure Environment
Copy the example environment file and edit it:
```bash
cp .env.example .env
```
Make sure to add your Telegram `BOT_TOKEN` in the `.env` file. (You can get one from [@BotFather](https://t.me/BotFather)).

### 2. Run with Docker Compose
```bash
docker-compose up -d --build
```

This will start three containers:
- `db`: PostgreSQL database
- `bot`: The Aiogram bot process
- `admin`: The Django admin web interface (running on port `8000`)

### 3. Access Admin Panel
First, create a superuser for the Django admin:
```bash
docker-compose exec admin python manage.py createsuperuser
```

Then navigate to `http://localhost:8000/admin` in your browser.

## Inline Mode Setup
To enable inline mode, you must talk to [@BotFather](https://t.me/BotFather):
1. Send `/mybots`
2. Select your bot
3. Go to **Bot Settings** -> **Inline Mode**
4. Click **Turn on**

## Architecture Notes
- We use Django purely for its excellent ORM and out-of-the-box Admin panel.
- The bot logic runs asynchronously using Aiogram 3.
- Database access from Aiogram handlers is wrapped in `sync_to_async` because Django's ORM is primarily synchronous.
- There is no Redis; Aiogram's MemoryStorage is used for simple FSM states.