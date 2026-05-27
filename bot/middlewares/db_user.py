from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from asgiref.sync import sync_to_async
from voices.models import BotUser

class DbUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
        
        # Get or create DB user
        db_user, _ = await sync_to_async(BotUser.objects.get_or_create)(
            telegram_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
            }
        )
        
        # If the user changed their username/first_name, update it
        updated = False
        if db_user.username != user.username:
            db_user.username = user.username
            updated = True
        if db_user.first_name != user.first_name:
            db_user.first_name = user.first_name
            updated = True
            
        if updated:
            await sync_to_async(db_user.save)()
            
        data["db_user"] = db_user
        
        return await handler(event, data)
