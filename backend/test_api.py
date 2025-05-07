import unittest
import asyncio
from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import json

# Import app and models
from api import app
from database import Base, Presentation, PresentationStepModel, PresentationStep, StepStatus

# Create test database engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_presentations.db"
engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create test client
client = TestClient(app)

# Set up and tear down for tests
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def insert_test_presentation():
    async with TestingSessionLocal() as session:
        presentation = Presentation(name="Test Presentation", topic="Test Topic")
        session.add(presentation)
        await session.commit()
        await session.refresh(presentation)
        
        # Add steps
        research_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.RESEARCH.value,
            status=StepStatus.COMPLETED.value
        )
        research_step.set_result({
            "content": "Test research content",
            "links": [{"href": "https://example.com", "title": "Example"}]
        })
        
        slides_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.SLIDES.value,
            status=StepStatus.PENDING.value
        )
        
        session.add(research_step)
        session.add(slides_step)
        await session.commit()
        
        return presentation.id

class TestAPI(IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        # Set up database for tests
        await setup_database()
    
    def test_root(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Presentation Assistant API is running"})
    
    async def test_create_presentation(self):
        # We need to set up the database first in the async context
        await setup_database()
        
        response = client.post(
            "/presentations",
            json={"name": "New Presentation", "topic": "AI in Healthcare"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "New Presentation")
        self.assertEqual(data["topic"], "AI in Healthcare")
        self.assertIn("id", data)
    
    async def test_get_presentations(self):
        # First, create a test presentation
        presentation_id = await insert_test_presentation()
        
        # Test listing
        response = client.get("/presentations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
    
    async def test_get_presentation_detail(self):
        # Create a test presentation
        presentation_id = await insert_test_presentation()
        
        # Test retrieval
        response = client.get(f"/presentations/{presentation_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Test Presentation")
        self.assertEqual(data["topic"], "Test Topic")
        self.assertEqual(len(data["steps"]), 2)
        
        # Check steps
        research_step = next(step for step in data["steps"] if step["step"] == "research")
        self.assertEqual(research_step["status"], "completed")
        self.assertEqual(research_step["result"]["content"], "Test research content")
        
        slides_step = next(step for step in data["steps"] if step["step"] == "slides")
        self.assertEqual(slides_step["status"], "pending")
    
    async def test_run_step(self):
        # Create a test presentation
        presentation_id = await insert_test_presentation()
        
        # Test running slides step
        response = client.post(f"/presentations/{presentation_id}/steps/slides/run")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
    
    async def test_update_step(self):
        # Create a test presentation
        presentation_id = await insert_test_presentation()
        
        # Test updating slides step
        response = client.put(
            f"/presentations/{presentation_id}/steps/slides",
            json={
                "result": {
                    "title": "Updated Slides",
                    "slides": [
                        {"title": "Slide 1", "type": "title", "content": ["Content 1"]}
                    ]
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        
        # Verify update
        response = client.get(f"/presentations/{presentation_id}")
        data = response.json()
        slides_step = next(step for step in data["steps"] if step["step"] == "slides")
        self.assertEqual(slides_step["status"], "completed")
        self.assertEqual(slides_step["result"]["title"], "Updated Slides")

if __name__ == "__main__":
    unittest.main() 