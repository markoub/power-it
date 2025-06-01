"""Tests for prompts system functionality."""

import pytest
import time
from sqlalchemy.future import select

from tests.utils import EnvironmentManager
from database import init_db, SessionLocal
from prompts import get_prompt, PromptModel


class TestPrompts:
    """Test suite for prompts system."""
    
    @pytest.mark.asyncio
    async def test_get_prompt_creates_default(self):
        """Test that get_prompt creates default prompt when not exists."""
        await init_db()
        
        # Use a unique test name to avoid conflicts
        test_name = f"research_prompt_test_{int(time.time() * 1000)}"
        text = await get_prompt(test_name, "DEFAULT TEXT")
        
        assert text == "DEFAULT TEXT"
        
        # Verify in database
        async with SessionLocal() as db:
            result = await db.execute(
                select(PromptModel).filter(PromptModel.name == test_name)
            )
            obj = result.scalars().first()
            assert obj is not None
            assert obj.text == "DEFAULT TEXT"
    
    @pytest.mark.asyncio
    async def test_get_prompt_returns_existing(self):
        """Test that get_prompt returns existing prompt instead of default."""
        await init_db()
        
        # Create unique test name
        test_name = f"research_prompt_test_{int(time.time() * 1000)}"
        
        # First call creates with default
        text1 = await get_prompt(test_name, "DEFAULT TEXT")
        assert text1 == "DEFAULT TEXT"
        
        # Update text directly in database
        async with SessionLocal() as db:
            result = await db.execute(
                select(PromptModel).filter(PromptModel.name == test_name)
            )
            obj = result.scalars().first()
            obj.text = "UPDATED TEXT"
            db.add(obj)
            await db.commit()
        
        # Second call should return updated text
        text2 = await get_prompt(test_name, "SHOULD NOT USE THIS")
        assert text2 == "UPDATED TEXT"
    
    @pytest.mark.asyncio
    async def test_get_prompt_handles_empty_default(self):
        """Test that get_prompt handles empty default text."""
        await init_db()
        
        test_name = f"empty_prompt_test_{int(time.time() * 1000)}"
        text = await get_prompt(test_name, "")
        
        assert text == ""
        
        # Verify in database
        async with SessionLocal() as db:
            result = await db.execute(
                select(PromptModel).filter(PromptModel.name == test_name)
            )
            obj = result.scalars().first()
            assert obj is not None
            assert obj.text == ""
    
    @pytest.mark.asyncio
    async def test_get_prompt_handles_long_text(self):
        """Test that get_prompt handles very long default text."""
        await init_db()
        
        test_name = f"long_prompt_test_{int(time.time() * 1000)}"
        long_text = "A" * 10000  # 10k characters
        
        text = await get_prompt(test_name, long_text)
        assert text == long_text
        assert len(text) == 10000
    
    @pytest.mark.asyncio
    async def test_prompt_model_attributes(self):
        """Test PromptModel has correct attributes."""
        await init_db()
        
        test_name = f"model_test_{int(time.time() * 1000)}"
        await get_prompt(test_name, "Test text")
        
        async with SessionLocal() as db:
            result = await db.execute(
                select(PromptModel).filter(PromptModel.name == test_name)
            )
            obj = result.scalars().first()
            
            # Check attributes
            assert hasattr(obj, 'id')
            assert hasattr(obj, 'name')
            assert hasattr(obj, 'text')
            assert hasattr(obj, 'created_at')
            assert hasattr(obj, 'updated_at')
            
            # Check values
            assert obj.name == test_name
            assert obj.text == "Test text"
            assert obj.created_at is not None
            assert obj.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_prompt_creation(self):
        """Test that concurrent calls to get_prompt work correctly."""
        await init_db()
        
        test_name = f"concurrent_test_{int(time.time() * 1000)}"
        
        # Create multiple concurrent tasks
        import asyncio
        tasks = [
            get_prompt(test_name, "DEFAULT TEXT")
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should return the same text
        assert all(r == "DEFAULT TEXT" for r in results)
        
        # Should only have one record in database
        async with SessionLocal() as db:
            result = await db.execute(
                select(PromptModel).filter(PromptModel.name == test_name)
            )
            records = result.scalars().all()
            assert len(records) == 1
    
    @pytest.mark.asyncio
    async def test_get_prompt_error_handling(self):
        """Test error handling in get_prompt."""
        # Test with uninitialized database
        # This should still work as init_db is called if needed
        test_name = f"error_test_{int(time.time() * 1000)}"
        text = await get_prompt(test_name, "DEFAULT")
        assert text == "DEFAULT"
    
    @pytest.mark.asyncio
    async def test_prompt_categories(self):
        """Test different prompt categories."""
        await init_db()
        
        # Test various prompt types
        prompts = {
            "research_prompt": "Research about {topic}",
            "slides_prompt": "Create slides for {topic}",
            "modify_prompt": "Modify the following: {content}",
            "image_prompt": "Generate image: {description}"
        }
        
        for name, default_text in prompts.items():
            test_name = f"{name}_{int(time.time() * 1000)}"
            text = await get_prompt(test_name, default_text)
            assert text == default_text
            
            # Verify all are stored
            async with SessionLocal() as db:
                result = await db.execute(
                    select(PromptModel).filter(PromptModel.name == test_name)
                )
                obj = result.scalars().first()
                assert obj is not None
                assert obj.text == default_text