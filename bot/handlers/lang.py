from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from django.utils import translation
from django.utils.translation import gettext
from asgiref.sync import sync_to_async

from voices.models import BotUser

router = Router()


# /lang command
@router.message(Command("lang"))
async def lang_command(message: types.Message, state: FSMContext, db_user: BotUser):
    await state.clear()

    current_lang = db_user.language

    text = gettext("Current language:") + f" {current_lang}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇸 English", callback_data="set_lang:en")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
            [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="set_lang:uz")],
        ]
    )

    await message.answer(text, reply_markup=keyboard)


# language switch callback
@router.callback_query(F.data.startswith("set_lang:"))
async def set_language(callback: types.CallbackQuery, db_user: BotUser):
    lang_code = callback.data.split(":", 1)[1]

    # update DB
    db_user.language = lang_code
    await sync_to_async(db_user.save)()

    # activate locale for current request
    translation.activate(lang_code)

    msg = gettext("Language changed to") + f" {lang_code}"

    await callback.message.edit_text(msg)
    await callback.answer()
