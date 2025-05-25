from sqlalchemy.future import select
from database import SessionLocal, PromptModel

async def get_prompt(name: str, default: str) -> str:
    """Retrieve a prompt from the database or create it with the default."""
    async with SessionLocal() as db:
        result = await db.execute(select(PromptModel).filter(PromptModel.name == name))
        prompt = result.scalars().first()
        if not prompt:
            prompt = PromptModel(name=name, text=default)
            db.add(prompt)
            await db.commit()
            await db.refresh(prompt)
        return prompt.text
