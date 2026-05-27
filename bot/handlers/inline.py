import uuid
from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultCachedVoice, ChosenInlineResult
from asgiref.sync import sync_to_async
from django.db.models import F as DjangoF

from voices.models import Voice, BotUser

router = Router()

@router.inline_query()
async def inline_query_handler(query: InlineQuery, db_user: BotUser):
    text = query.query.strip()
    
    # We will search globally across all voices to support the "shared" aspect,
    # but could be filtered by db_user if we wanted it strictly personal.
    
    @sync_to_async
    def search_voices():
        qs = Voice.objects.all()
        if text:
            # Simple ILIKE search
            qs = qs.filter(description__icontains=text)
        
        # Order by usage count for better relevance, limit to 50 (Telegram max)
        return list(qs.order_by('-usage_count', '-created_at')[:50])
        
    voices = await search_voices()
    
    results = []
    for voice in voices:
        # Telegram requires a unique string ID for each inline result
        result_id = str(voice.id)
        
        results.append(
            InlineQueryResultCachedVoice(
                id=result_id,
                voice_file_id=voice.file_id,
                title=voice.description[:100],  # Title shown in inline menu
            )
        )
        
    await query.answer(results, cache_time=5, is_personal=False)


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
