
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from django.utils import translation
from django.utils.translation import gettext
from asgiref.sync import sync_to_async
from bot.middlewares.db_user import get_user

router = Router()

# /lang command: show current language and offer inline buttons
@router.message(Command(commands=["lang"]))
async def lang_command(message: types.Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)
    current_lang = user.language
    text = gettext("Current language:") + f" {current_lang}"
    # Inline buttons for language selection
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=gettext("🇺🇸 English"), callback_data="set_lang:en")],
        [InlineKeyboardButton(text=gettext("🇷🇺 Русский"), callback_data="set_lang:ru")],
        [InlineKeyboardButton(text=gettext("🇺🇿 O'zbek"), callback_data="set_lang:uz")],
    ])
    await message.answer(text, reply_markup=keyboard)

# Callback handler to change language
@router.callback_query(lambda c: c.data.startswith("set_lang:"))
async def set_language(callback: types.CallbackQuery):
    _, lang_code = callback.data.split(":", 1)
    user = await get_user(callback.from_user.id)
    # Update language in DB
    user.language = lang_code
    # Save synchronously using sync_to_async
    await sync_to_async(user.save)()
    # Activate language for response
    translation.activate(lang_code)
    # Localized confirmation message
    msg = gettext("Language changed to") + f" {lang_code}"
    await callback.message.edit_text(msg)
    await callback.answer()
