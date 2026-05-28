from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from asgiref.sync import sync_to_async

from voices.models import BotUser


class DbUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        db_user, _ = await sync_to_async(BotUser.objects.get_or_create)(
            telegram_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
            }
        )

        # sync updates
        changed = False

        if db_user.username != user.username:
            db_user.username = user.username
            changed = True

        if db_user.first_name != user.first_name:
            db_user.first_name = user.first_name
            changed = True

        if changed:
            await sync_to_async(db_user.save)()

        data["db_user"] = db_user

        return await handler(event, data)
