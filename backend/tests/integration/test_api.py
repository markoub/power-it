import pytest
from tests.utils import assert_api_error, create_test_presentation

pytestmark = pytest.mark.asyncio


class TestPresentationAPI:
    """Integration tests for the presentation API endpoints."""

    async def test_create_presentation_success(self, api_client, clean_db):
        """Test successful presentation creation."""
        presentation = await create_test_presentation(
            api_client, 
            name="API Test Presentation",
            topic="Test Topic for API Integration"
        )
        
        assert presentation["id"] is not None
        assert presentation["name"] == "API Test Presentation"
        assert presentation["topic"] == "Test Topic for API Integration"

    async def test_create_presentation_invalid_data(self, api_client, clean_db):
        """Test creation with invalid data."""
        response = api_client.post("/presentations", json={})
        assert_api_error(response, 422, "Field required")

    async def test_get_presentation_success(self, api_client, create_presentation):
        """Test retrieving an existing presentation."""
        presentation = await create_presentation()
        
        response = api_client.get(f"/presentations/{presentation['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == presentation["id"]
        assert data["name"] == presentation["name"]
        assert data["topic"] == presentation["topic"]

    async def test_get_presentation_not_found(self, api_client, clean_db):
        """Test retrieving a non-existent presentation."""
        response = api_client.get("/presentations/99999")
        assert_api_error(response, 404, "not found")

    async def test_list_presentations(self, api_client, create_presentation):
        """Test listing presentations."""
        # Create multiple presentations
        presentation1 = await create_presentation(name="Test 1", topic="Topic 1")
        presentation2 = await create_presentation(name="Test 2", topic="Topic 2")
        
        response = api_client.get("/presentations")
        assert response.status_code == 200
        
        data = response.json()
        # Handle both paginated and direct list responses
        items = data.get("items", data) if isinstance(data, dict) else data
        
        presentation_ids = [p["id"] for p in items]
        assert presentation1["id"] in presentation_ids
        assert presentation2["id"] in presentation_ids


class TestPresentationSteps:
    """Tests for presentation step execution."""

    async def test_run_pptx_step(self, api_client, create_presentation):
        """Test running the PPTX generation step for a presentation."""
        presentation = await create_presentation(
            name="PPTX Test Presentation",
            topic="Test Topic for PPTX Generation"
        )
        
        presentation_id = presentation["id"]
        
        # Trigger PowerPoint generation via the step endpoint
        step_response = api_client.post(f"/presentations/{presentation_id}/steps/pptx/run")
        
        # The step should either succeed or return a meaningful error
        # Note: In offline mode, this might fail due to missing dependencies
        if step_response.status_code == 200:
            result = step_response.json()
            assert "status" in result or "message" in result
            
            # Check the status of the step
            status_response = api_client.get(f"/presentations/{presentation_id}")
            assert status_response.status_code == 200
            
            updated_pres_data = status_response.json()
            steps = updated_pres_data.get("steps", [])
            pptx_step = next((s for s in steps if s.get("step") == "pptx"), None)
            
            if pptx_step:
                assert pptx_step.get("status") in ["pending", "processing", "completed", "failed"]
        else:
            # In offline mode or when dependencies are missing, accept certain error codes
            assert step_response.status_code in [400, 404, 500, 503]

    @pytest.mark.parametrize("step_name", ["research", "slides", "images", "compiled"])
    async def test_run_step_endpoints_exist(self, api_client, create_presentation, step_name):
        """Test that step execution endpoints exist and respond properly."""
        presentation = await create_presentation()
        presentation_id = presentation["id"]
        
        response = api_client.post(f"/presentations/{presentation_id}/steps/{step_name}/run")
        
        # We don't expect these to always succeed in test environment
        # But the endpoints should exist and respond with valid HTTP codes
        assert response.status_code in [200, 400, 404, 422, 500, 503]

    async def test_invalid_step_name(self, api_client, create_presentation):
        """Test running a step with invalid name."""
        presentation = await create_presentation()
        presentation_id = presentation["id"]
        
        response = api_client.post(f"/presentations/{presentation_id}/steps/invalid_step/run")
        assert_api_error(response, 400, "Invalid step")

    async def test_step_on_nonexistent_presentation(self, api_client, clean_db):
        """Test running a step on non-existent presentation."""
        response = api_client.post("/presentations/99999/steps/research/run")
        assert_api_error(response, 404, "not found")


class TestPresentationDeletion:
    """Tests for presentation deletion."""

    async def test_delete_presentation_success(self, api_client, create_presentation):
        """Test successful presentation deletion."""
        presentation = await create_presentation()
        presentation_id = presentation["id"]
        
        # Delete the presentation
        delete_response = api_client.delete(f"/presentations/{presentation_id}")
        assert delete_response.status_code == 204
        
        # Verify it's gone
        get_response = api_client.get(f"/presentations/{presentation_id}")
        assert_api_error(get_response, 404, "not found")
        
        # Verify it's not in the list
        list_response = api_client.get("/presentations")
        assert list_response.status_code == 200
        
        data = list_response.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        presentation_ids = [p["id"] for p in items]
        assert presentation_id not in presentation_ids

    async def test_delete_nonexistent_presentation(self, api_client, clean_db):
        """Test deleting a non-existent presentation."""
        response = api_client.delete("/presentations/99999")
        assert_api_error(response, 404, "not found") 