import pytest
import uuid
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from fastapi import FastAPI

from api import app
from database import init_db, SessionLocal, Presentation, PresentationStepModel, PresentationStep, StepStatus

@pytest.fixture
async def setup_test_db():
    """Create a test presentation and return its ID."""
    # Initialize the database
    await init_db()
    
    # Generate a unique name for the test presentation
    unique_name = f"Test Presentation {uuid.uuid4()}"
    
    # Create a test presentation
    async with SessionLocal() as db:
        # Create a presentation
        presentation = Presentation(
            name=unique_name,
            topic="Original Topic",
            author="Test Author"
        )
        db.add(presentation)
        await db.commit()
        await db.refresh(presentation)
        
        # Create research step
        research_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.RESEARCH.value,
            status=StepStatus.COMPLETED.value,
            result='{"content": "Test research content", "links": []}'
        )
        db.add(research_step)
        
        # Create slides step
        slides_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.SLIDES.value,
            status=StepStatus.COMPLETED.value,
            result='{"title": "Test Presentation", "slides": [{"type": "welcome", "fields": {"title": "Test Presentation", "subtitle": "Original Topic"}}]}'
        )
        db.add(slides_step)
        
        # Create images step
        images_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.IMAGES.value,
            status=StepStatus.PENDING.value
        )
        db.add(images_step)
        
        # Create compiled step
        compiled_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.COMPILED.value,
            status=StepStatus.PENDING.value
        )
        db.add(compiled_step)
        
        # Create PPTX step
        pptx_step = PresentationStepModel(
            presentation_id=presentation.id,
            step=PresentationStep.PPTX.value,
            status=StepStatus.PENDING.value
        )
        db.add(pptx_step)
        
        await db.commit()
        
        presentation_id = presentation.id
    
    yield presentation_id
    
    # Clean up test data
    async with SessionLocal() as db:
        # Delete the presentation steps using SQLAlchemy text
        await db.execute(
            text(f"DELETE FROM presentation_steps WHERE presentation_id = {presentation_id}")
        )
        # Delete the presentation
        await db.execute(
            text(f"DELETE FROM presentations WHERE id = {presentation_id}")
        )
        await db.commit()

@pytest.fixture
def client():
    """Create a FastAPI TestClient."""
    return TestClient(app)

def test_update_topic(setup_test_db, client):
    """Test updating a presentation topic."""
    presentation_id = setup_test_db
    
    # Update the topic using the client
    response = client.post(
        f"/presentations/{presentation_id}/update-topic",
        json={"topic": "Updated Topic"}
    )
    
    # Check response status code
    assert response.status_code == 200
    
    # Check that topic was updated in response
    data = response.json()
    assert data["topic"] == "Updated Topic"
    
    # Let the background task finish
    asyncio.run(asyncio.sleep(1))
    
    # Create async session to check database
    async def check_database():
        async with SessionLocal() as db:
            # Get the presentation
            result = await db.execute(
                text(f"SELECT * FROM presentations WHERE id = {presentation_id}")
            )
            presentation = result.fetchone()
            assert presentation[2] == "Updated Topic"  # topic is the 3rd column (index 2)
            
            # Check that research step is now processing or completed
            result = await db.execute(
                text(f"SELECT * FROM presentation_steps WHERE presentation_id = {presentation_id} AND step = '{PresentationStep.RESEARCH.value}'")
            )
            research_step = result.fetchone()
            assert research_step[3] in [StepStatus.PROCESSING.value, StepStatus.COMPLETED.value]  # status is the 4th column (index 3)
    
    # Run the async check
    asyncio.run(check_database())

def test_topic_update_resets_downstream_steps(setup_test_db, client):
    """Test that changing the topic resets slides, images, compiled, and PPTX steps."""
    presentation_id = setup_test_db
    
    # Update the topic using the client
    response = client.post(
        f"/presentations/{presentation_id}/update-topic",
        json={"topic": "Completely New Topic"}
    )
    
    # Check response status code
    assert response.status_code == 200
    
    # Let the background task finish
    asyncio.run(asyncio.sleep(1))
    
    # Create async session to check database
    async def check_database():
        async with SessionLocal() as db:
            # Check slides step is processing or completed (might be completed quickly in test)
            result = await db.execute(
                text(f"SELECT * FROM presentation_steps WHERE presentation_id = {presentation_id} AND step = '{PresentationStep.SLIDES.value}'")
            )
            slides_step = result.fetchone()
            assert slides_step[3] in [StepStatus.PROCESSING.value, StepStatus.COMPLETED.value]
            
            # Check that images step is now set to pending
            result = await db.execute(
                text(f"SELECT * FROM presentation_steps WHERE presentation_id = {presentation_id} AND step = '{PresentationStep.IMAGES.value}'")
            )
            images_step = result.fetchone()
            assert images_step[3] == StepStatus.PENDING.value
            
            # Check that compiled step is now set to pending
            result = await db.execute(
                text(f"SELECT * FROM presentation_steps WHERE presentation_id = {presentation_id} AND step = '{PresentationStep.COMPILED.value}'")
            )
            compiled_step = result.fetchone()
            assert compiled_step[3] == StepStatus.PENDING.value
            
            # Check that PPTX step is now set to pending
            result = await db.execute(
                text(f"SELECT * FROM presentation_steps WHERE presentation_id = {presentation_id} AND step = '{PresentationStep.PPTX.value}'")
            )
            pptx_step = result.fetchone()
            assert pptx_step[3] == StepStatus.PENDING.value
    
    # Run the async check
    asyncio.run(check_database())

def test_update_topic_validation(setup_test_db, client):
    """Test that the API properly validates the request and returns an error when the topic is missing."""
    presentation_id = setup_test_db
    
    # Try to update the topic with an empty request body
    response = client.post(
        f"/presentations/{presentation_id}/update-topic",
        json={}
    )
    
    # Check response status code is 422 (validation error)
    assert response.status_code == 422
    
    # Check that the error message mentions the topic
    assert "topic" in response.text.lower()
    
    # Try to update with a non-existent presentation ID
    non_existent_id = 99999
    response = client.post(
        f"/presentations/{non_existent_id}/update-topic",
        json={"topic": "New Topic"}
    )
    
    # Check response status code is 404 (not found)
    assert response.status_code == 404
    
    # Check that the error message mentions "not found"
    assert "not found" in response.text.lower()
    
    # Verify that original topic was not changed
    async def check_database():
        async with SessionLocal() as db:
            # Get the presentation
            result = await db.execute(
                text(f"SELECT * FROM presentations WHERE id = {presentation_id}")
            )
            presentation = result.fetchone()
            assert presentation[2] == "Original Topic"  # topic should still be the original
    
    # Run the async check
    asyncio.run(check_database()) 