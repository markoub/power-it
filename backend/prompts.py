import os
from pathlib import Path
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, PromptModel

def load_default_prompt(name: str) -> str:
    """Load default prompt from file."""
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_file = prompts_dir / f"{name}.txt"
    
    if prompt_file.exists():
        return prompt_file.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f"Default prompt file not found: {prompt_file}")

async def get_prompt(name: str, default: str = None) -> str:
    """Retrieve a prompt from the database, falling back to file defaults."""
    # First, try to get from database
    async with SessionLocal() as db:
        result = await db.execute(select(PromptModel).filter(PromptModel.name == name))
        prompt = result.scalars().first()
        
        if prompt:
            return prompt.text
        
        # If not in database, try to load default from file
        try:
            if default is None:
                default = load_default_prompt(name)
        except FileNotFoundError:
            if default is None:
                raise ValueError(f"No prompt found in database or default file for: {name}")
        
        # Store the default in database for future use
        try:
            prompt = PromptModel(name=name, text=default)
            db.add(prompt)
            await db.commit()
            await db.refresh(prompt)
            return prompt.text
        except IntegrityError:
            # Prompt was created by another concurrent call, fetch it
            await db.rollback()
            result = await db.execute(select(PromptModel).filter(PromptModel.name == name))
            prompt = result.scalars().first()
            if prompt:
                return prompt.text
            else:
                # Very unlikely, but if it still doesn't exist, return the default
                return default
