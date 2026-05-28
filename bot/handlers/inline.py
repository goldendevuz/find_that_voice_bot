import uuid
from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultCachedVoice, ChosenInlineResult, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.db.models import F as DjangoF, Q
from django.core.cache import cache

from voices.models import Voice, BotUser
from bot.utils.cache import cache_key, invalidate_inline_cache

router = Router()

@router.inline_query()
async def inline_query_handler(query: InlineQuery, db_user: BotUser):
    text = query.query.strip()
    
    # We will search globally across all voices to support the "shared" aspect,
    # but could be filtered by db_user if we wanted it strictly personal.
    
    @sync_to_async
    def search_voices():
        qs = Voice.objects.filter(is_active=True).filter(
            Q(is_public=True) | Q(owner=db_user)
        )
        if text:
            qs = qs.filter(description__icontains=text)
        # Order by usage count, limit to 50
        return list(qs.order_by('-usage_count', '-created_at')[:50])
        
    # Check cache first
    cache_key_str = cache_key(db_user.telegram_id, text)
    cached = cache.get(cache_key_str)
    if cached:
        await query.answer(cached, cache_time=600, is_personal=False)
        return

    voices = await search_voices()

    results = []
    for voice in voices:
        result_id = str(voice.id)
        # Inline keyboard for edit actions
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_desc:{voice.id}"),
            InlineKeyboardButton(text="🔁 Replace", callback_data=f"replace_audio:{voice.id}"),
            InlineKeyboardButton(text="📦 Archive", callback_data=f"archive:{voice.id}"),
            InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete:{voice.id}")
        ]])
        results.append(
            InlineQueryResultCachedVoice(
                id=result_id,
                voice_file_id=voice.file_id,
                title=voice.description[:100],
                reply_markup=keyboard,
            )
        )
    # Store in cache for 10 minutes
    cache.set(cache_key_str, results, timeout=600)
    await query.answer(results, cache_time=600, is_personal=False)


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult):
    # The chosen_result.result_id is our voice.id
    try:
        voice_id = int(chosen_result.result_id)
        
        @sync_to_async
        def increment_usage():
            Voice.objects.filter(id=voice_id).update(usage_count=DjangoF('usage_count') + 1)
            
        await increment_usage()
    except (ValueError, TypeError):
        pass
