import json
from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultCachedVoice, ChosenInlineResult
from asgiref.sync import sync_to_async
from django.db.models import Q, F
from django.core.cache import cache

from voices.models import Voice

router = Router()


def cache_key(user_id: int, query: str):
    return f"voice_search:{user_id}:{query.strip().lower()}"


@router.inline_query()
async def inline_query_handler(query: InlineQuery, db_user):
    text = query.query.strip().lower()
    key = cache_key(db_user.telegram_id, text)

    cached = cache.get(key)
    if cached:
        return await query.answer(cached, cache_time=30, is_personal=True)

    @sync_to_async
    def search():
        qs = Voice.objects.filter(
            is_active=True,
            is_archived=False
        ).filter(
            Q(is_public=True) | Q(owner=db_user)
        )

        if text:
            qs = qs.filter(description__icontains=text)

        return list(qs.order_by("-usage_count", "-created")[:50])

    voices = await search()

    results = [
        InlineQueryResultCachedVoice(
            id=str(v.id),
            voice_file_id=v.file_id,
            title=v.description[:80],
        )
        for v in voices
    ]

    cache.set(key, results, timeout=600)

    await query.answer(results, cache_time=30, is_personal=True)


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen: ChosenInlineResult):
    try:
        voice_id = chosen.result_id

        @sync_to_async
        def inc():
            Voice.objects.filter(id=voice_id).update(
                usage_count=F("usage_count") + 1
            )

        await inc()
    except Exception:
        pass
