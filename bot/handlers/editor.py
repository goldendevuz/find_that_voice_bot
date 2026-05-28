import uuid
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.db.models import F as DjangoF
from django.core.cache import cache

from voices.models import Voice, BotUser
from bot.utils.cache import cache_key, invalidate_inline_cache

router = Router()

class EditVoiceStates(StatesGroup):
    waiting_for_new_description = State()
    waiting_for_new_audio = State()

# ---------- Edit description ----------
@router.callback_query(F.data.startswith('edit_desc:'))
async def edit_description_cb(callback: types.CallbackQuery, state: FSMContext, db_user: BotUser):
    voice_id = int(callback.data.split(':', 1)[1])
    await state.update_data(voice_id=voice_id)
    await state.set_state(EditVoiceStates.waiting_for_new_description)
    await callback.message.edit_text('✏️ Send new description for the selected voice.')
    await callback.answer()

@router.message(EditVoiceStates.waiting_for_new_description, F.text)
async def set_new_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    voice_id = data.get('voice_id')
    new_desc = message.text
    @sync_to_async
    def update_desc():
        Voice.objects.filter(id=voice_id).update(description=new_desc)
        invalidate_inline_cache()
    await update_desc()
    await message.answer('✅ Description updated.')
    await state.clear()

# ---------- Replace audio ----------
@router.callback_query(F.data.startswith('replace_audio:'))
async def replace_audio_cb(callback: types.CallbackQuery, state: FSMContext, db_user: BotUser):
    voice_id = int(callback.data.split(':', 1)[1])
    await state.update_data(voice_id=voice_id)
    await state.set_state(EditVoiceStates.waiting_for_new_audio)
    await callback.message.edit_text('🔁 Please send the new voice file.')
    await callback.answer()

@router.message(EditVoiceStates.waiting_for_new_audio, F.voice)
async def set_new_audio(message: types.Message, state: FSMContext):
    data = await state.get_data()
    voice_id = data.get('voice_id')
    file_id = message.voice.file_id
    file_unique_id = message.voice.file_unique_id
    @sync_to_async
    def update_audio():
        Voice.objects.filter(id=voice_id).update(file_id=file_id, file_unique_id=file_unique_id)
        invalidate_inline_cache()
    await update_audio()
    await message.answer('✅ Audio file updated.')
    await state.clear()

# ---------- Archive (soft delete) ----------
@router.callback_query(F.data.startswith('archive:'))
async def archive_cb(callback: types.CallbackQuery, db_user: BotUser):
    voice_id = int(callback.data.split(':', 1)[1])
    @sync_to_async
    def archive():
        Voice.objects.filter(id=voice_id).update(is_active=False)
        invalidate_inline_cache()
    await archive()
    await callback.message.edit_text('📦 Voice archived (soft deleted).')
    await callback.answer()

# ---------- Delete (soft) ----------
@router.callback_query(F.data.startswith('delete:'))
async def delete_cb(callback: types.CallbackQuery, db_user: BotUser):
    voice_id = int(callback.data.split(':', 1)[1])
    @sync_to_async
    def delete():
        Voice.objects.filter(id=voice_id).update(is_active=False)
        invalidate_inline_cache()
    await delete()
    undo_button = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='↩️ Undo', callback_data=f'undo:{voice_id}')]])
    await callback.message.edit_text('🗑️ Voice removed (soft).', reply_markup=undo_button)
    await callback.answer()

# ---------- Undo ----------
@router.callback_query(F.data.startswith('undo:'))
async def undo_cb(callback: types.CallbackQuery, db_user: BotUser):
    voice_id = int(callback.data.split(':', 1)[1])
    @sync_to_async
    def undo():
        Voice.objects.filter(id=voice_id).update(is_active=True)
        invalidate_inline_cache()
    await undo()
    await callback.message.edit_text('↩️ Voice restored.')
    await callback.answer()
