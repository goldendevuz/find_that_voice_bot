from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.utils.translation import gettext
from voices.models import Voice, BotUser

router = Router()

class SaveVoiceStates(StatesGroup):
    waiting_for_description = State()

@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Cancelled")

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        gettext(
            "👋 Welcome to Find That Voice!\n\n"
            "Send me any voice message, and I'll ask you for a description. "
            "Later, you can search for it in any chat by typing:\n"
            "`@FindThatVoiceBot <your description>`"
        ),
        parse_mode="Markdown",
    )

@router.message(F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    # Store the voice details in state
    await state.update_data(
        file_id=message.voice.file_id,
        file_unique_id=message.voice.file_unique_id
    )
    await state.set_state(SaveVoiceStates.waiting_for_description)
    await message.reply(gettext("🎙️ Voice received! Now, send me a text description or keywords for this voice."))

@router.message(SaveVoiceStates.waiting_for_description, F.text)
async def handle_description(message: types.Message, state: FSMContext, db_user: BotUser):
    data = await state.get_data()
    file_id = data.get("file_id")
    file_unique_id = data.get("file_unique_id")
    description = message.text

    if not file_id:
        await message.reply("Something went wrong. Please send the voice message again.")
        await state.clear()
        return

    # Save to database
    try:
        await sync_to_async(Voice.objects.create)(
            owner=db_user,
            file_id=file_id,
            file_unique_id=file_unique_id,
            description=description
        )
        await message.reply(gettext("✅ Voice saved successfully! You can now search for it using inline mode."))
    except IntegrityError:
        # If the user already saved this exact voice, we could just update the description, but let's keep it simple.
        await message.reply(gettext("⚠️ You have already saved this voice message."))
    except Exception as e:
        await message.reply(gettext("❌ Failed to save voice. Please try again."))
    finally:
        await state.clear()

@router.message(SaveVoiceStates.waiting_for_description, ~F.text)
async def handle_invalid_description(message: types.Message):
    await message.reply(gettext("Please send text only for the description."))
