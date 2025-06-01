import pytest
import asyncio
from sqlalchemy.future import select
from database import SessionLocal, Presentation, PresentationStepModel, PresentationStep, StepStatus
from tests.utils import assert_api_error, wait_for_condition

pytestmark = pytest.mark.asyncio


class TestTopicUpdate:
    """Integration tests for topic update functionality."""

    @pytest.fixture
    async def presentation_with_steps(self, clean_db):
        """Create a test presentation with completed steps."""
        async with SessionLocal() as db:
            # Create a presentation
            presentation = Presentation(
                name="Test Presentation for Topic Update",
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
            
            yield presentation.id

    async def test_update_topic_success(self, api_client, presentation_with_steps):
        """Test updating a presentation topic."""
        presentation_id = presentation_with_steps
        
        # Update the topic using the client
        response = api_client.post(
            f"/presentations/{presentation_id}/update-topic",
            json={"topic": "Updated Topic"}
        )
        
        # Check response status code
        assert response.status_code == 200
        
        # Check that topic was updated in response
        data = response.json()
        assert data["topic"] == "Updated Topic"
        
        # Check database directly (topic update should be immediate)
        async with SessionLocal() as db:
            # Get the presentation
            presentation = await db.get(Presentation, presentation_id)
            assert presentation.topic == "Updated Topic"
            
            # Check that research step is now processing or completed
            research_step = await db.execute(
                select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.RESEARCH.value)
                )
            )
            step_result = research_step.scalars().first()
            assert step_result.status in [StepStatus.PROCESSING.value, StepStatus.COMPLETED.value]

    async def test_topic_update_resets_downstream_steps(self, api_client, presentation_with_steps):
        """Test that changing the topic resets slides, images, compiled, and PPTX steps."""
        presentation_id = presentation_with_steps
        
        # Update the topic using the client
        response = api_client.post(
            f"/presentations/{presentation_id}/update-topic",
            json={"topic": "Completely New Topic"}
        )
        
        # Check response status code
        assert response.status_code == 200
        
        # Check database directly (topic update should be immediate)
        async with SessionLocal() as db:
            # Check slides step is processing or completed
            slides_result = await db.execute(
                select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.SLIDES.value)
                )
            )
            slides_step = slides_result.scalars().first()
            assert slides_step.status in [StepStatus.PROCESSING.value, StepStatus.COMPLETED.value]
            
            # Check that images step is now set to pending
            images_result = await db.execute(
                select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.IMAGES.value)
                )
            )
            images_step = images_result.scalars().first()
            assert images_step.status == StepStatus.PENDING.value
            
            # Check that compiled step is now set to pending
            compiled_result = await db.execute(
                select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.COMPILED.value)
                )
            )
            compiled_step = compiled_result.scalars().first()
            assert compiled_step.status == StepStatus.PENDING.value
            
            # Check that PPTX step is now set to pending
            pptx_result = await db.execute(
                select(PresentationStepModel).where(
                    (PresentationStepModel.presentation_id == presentation_id) &
                    (PresentationStepModel.step == PresentationStep.PPTX.value)
                )
            )
            pptx_step = pptx_result.scalars().first()
            assert pptx_step.status == StepStatus.PENDING.value

    async def test_update_topic_validation_errors(self, api_client, presentation_with_steps):
        """Test validation errors when updating topic."""
        presentation_id = presentation_with_steps
        
        # Try to update the topic with an empty request body
        response = api_client.post(
            f"/presentations/{presentation_id}/update-topic",
            json={}
        )
        
        # Check response status code is 422 (validation error)
        assert_api_error(response, 422, "Field required")

    async def test_update_topic_nonexistent_presentation(self, api_client, clean_db):
        """Test updating topic for non-existent presentation."""
        non_existent_id = 99999
        response = api_client.post(
            f"/presentations/{non_existent_id}/update-topic",
            json={"topic": "New Topic"}
        )
        
        # Check response status code is 404 (not found)
        assert_api_error(response, 404, "not found")

    async def test_topic_update_preserves_other_fields(self, api_client, presentation_with_steps):
        """Test that topic update preserves other presentation fields."""
        presentation_id = presentation_with_steps
        
        # Get original presentation data
        get_response = api_client.get(f"/presentations/{presentation_id}")
        original_data = get_response.json()
        
        # Update the topic
        response = api_client.post(
            f"/presentations/{presentation_id}/update-topic",
            json={"topic": "New Topic"}
        )
        
        assert response.status_code == 200
        updated_data = response.json()
        
        # Check that topic was updated but other fields preserved
        assert updated_data["topic"] == "New Topic"
        assert updated_data["name"] == original_data["name"]
        assert updated_data["author"] == original_data["author"]
        assert updated_data["id"] == original_data["id"]

    @pytest.mark.parametrize("new_topic", [
        "Short",
        "A very long topic that describes something in great detail with many words",
        "Topic with Special Characters !@#$%^&*()",
        "Topic with Numbers 123 and Dates 2024",
    ])
    async def test_topic_update_various_formats(self, api_client, presentation_with_steps, new_topic):
        """Test topic update with various topic formats."""
        presentation_id = presentation_with_steps
        
        response = api_client.post(
            f"/presentations/{presentation_id}/update-topic",
            json={"topic": new_topic}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == new_topic 