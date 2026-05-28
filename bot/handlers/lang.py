import json
from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils import translation
from django.db import transaction
from bot.middlewares.db_user import get_user

router = Router()

# /lang command: show current language and offer inline buttons
@router.message(commands=["lang"])
async def lang_command(message: types.Message):
    user: get_user = await get_user(message.from_user.id)
    current_lang = user.language
    text = f"Current language: {current_lang}"
    # Inline buttons for language selection
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="English", callback_data="set_lang:en"),
            InlineKeyboardButton(text="Русский", callback_data="set_lang:ru"),
            InlineKeyboardButton(text="O'zbek", callback_data="set_lang:uz"),
        ]
    ])
    await message.answer(text, reply_markup=keyboard)

# Callback handler to change language
@router.callback_query(lambda c: c.data.startswith("set_lang:"))
async def set_language(callback: types.CallbackQuery):
    _, lang_code = callback.data.split(":", 1)
    user = await get_user(callback.from_user.id)
    # Update language in DB atomically
    await transaction.on_commit(lambda: None)  # placeholder to ensure async context
    user.language = lang_code
    await user.save()
    # Activate language for response
    translation.activate(lang_code)
    # Localized confirmation message
    msg = translation.gettext("Language changed to") + f" {lang_code}"
    await callback.message.edit_text(msg)
    await callback.answer()
