import asyncio
import logging
import os
import django

# Setup Django environment before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import save_voice, inline, lang
from bot.middlewares.db_user import DbUserMiddleware

async def main():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "your_bot_token_here":
        logging.error("BOT_TOKEN is not set!")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares
    dp.update.middleware(DbUserMiddleware())

    # Routers
    dp.include_router(save_voice.router)
    dp.include_router(inline.router)
    dp.include_router(lang.router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
