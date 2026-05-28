from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.utils.translation import gettext

from voices.models import Voice, BotUser
from django.core.cache import cache
from bot.handlers.inline import cache_key

router = Router()


class SaveVoiceStates(StatesGroup):
    waiting_for_description = State()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        gettext("📢 Send a voice message, then add a description to save it as a PRIVATE voice.\n\n🛠️ Later you can make it public via the inline editor.")
    )


@router.message(F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    await state.update_data(
        file_id=message.voice.file_id,
        file_unique_id=message.voice.file_unique_id
    )

    await state.set_state(SaveVoiceStates.waiting_for_description)

    await message.answer(
        gettext("🎙️ Voice received! 🎧 Please send a description.")
    )


@router.message(SaveVoiceStates.waiting_for_description, F.text)
async def save_voice(message: types.Message, state: FSMContext, db_user: BotUser):
    data = await state.get_data()

    try:
        await sync_to_async(Voice.objects.create)(
            owner=db_user,
            file_id=data["file_id"],
            file_unique_id=data["file_unique_id"],
            description=message.text,
            is_public=False,   # DEFAULT PRIVATE
        )

        await message.answer(gettext("✅ Voice saved as PRIVATE. 📁"))
        cache.delete(cache_key(db_user.telegram_id, ""))

    except IntegrityError:
        await message.answer(gettext("⚠️ This voice already exists."))

    finally:
        await state.clear()


@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(gettext("❌ Cancelled."))
