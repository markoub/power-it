import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import init_db, SessionLocal
from sqlalchemy.future import select
from prompts import get_prompt, PromptModel

@pytest.mark.asyncio
async def test_get_prompt_creates_default(tmp_path):
    await init_db()
    text = await get_prompt("research_prompt_test", "DEFAULT TEXT")
    assert text == "DEFAULT TEXT"
    async with SessionLocal() as db:
        result = await db.execute(select(PromptModel).filter(PromptModel.name == "research_prompt_test"))
        obj = result.scalars().first()
        assert obj is not None
        assert obj.text == "DEFAULT TEXT"

    # Update text directly
    async with SessionLocal() as db:
        obj.text = "UPDATED"
        db.add(obj)
        await db.commit()

    text2 = await get_prompt("research_prompt_test", "SHOULD NOT USE")
    assert text2 == "UPDATED"
