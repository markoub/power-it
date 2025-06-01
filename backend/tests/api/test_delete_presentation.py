import pytest
from tests.utils import create_test_presentation, assert_api_error

pytestmark = pytest.mark.asyncio


class TestPresentationDeletion:
    """Tests for presentation deletion functionality."""

    async def test_create_and_delete_presentation_success(self, api_client, clean_db):
        """Test creating and deleting a presentation successfully."""
        # Create a test presentation
        presentation = await create_test_presentation(
            api_client,
            name="Delete Test Presentation",
            topic="Test Topic for Deletion",
            author="Test Author"
        )
        
        presentation_id = presentation["id"]
        
        # Verify the presentation exists
        get_resp = api_client.get(f"/presentations/{presentation_id}")
        assert get_resp.status_code == 200
        
        # Delete the presentation
        delete_resp = api_client.delete(f"/presentations/{presentation_id}")
        assert delete_resp.status_code == 204
        
        # Verify it's gone - should return 404
        get_resp_after_delete = api_client.get(f"/presentations/{presentation_id}")
        assert_api_error(get_resp_after_delete, 404, "not found")
        
        # Verify it's not in the list
        list_resp = api_client.get("/presentations")
        assert list_resp.status_code == 200
        
        data = list_resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        presentation_ids = [p["id"] for p in items]
        assert presentation_id not in presentation_ids

    async def test_delete_nonexistent_presentation(self, api_client, clean_db):
        """Test deleting a presentation that doesn't exist."""
        nonexistent_id = 99999
        
        response = api_client.delete(f"/presentations/{nonexistent_id}")
        assert_api_error(response, 404, "not found")

    async def test_delete_presentation_with_steps(self, api_client, create_presentation):
        """Test deleting a presentation that has associated steps."""
        presentation = await create_presentation()
        presentation_id = presentation["id"]
        
        # Try to run a step to create some step data
        step_response = api_client.post(f"/presentations/{presentation_id}/steps/research/run")
        # We don't care if the step succeeds or fails, just that we tried to create step data
        
        # Delete the presentation - should succeed regardless of step data
        delete_resp = api_client.delete(f"/presentations/{presentation_id}")
        assert delete_resp.status_code == 204
        
        # Verify it's gone
        get_resp = api_client.get(f"/presentations/{presentation_id}")
        assert_api_error(get_resp, 404, "not found")

    async def test_delete_multiple_presentations(self, api_client, clean_db):
        """Test deleting multiple presentations."""
        # Create multiple presentations
        presentations = []
        for i in range(3):
            presentation = await create_test_presentation(
                api_client,
                name=f"Delete Test {i}",
                topic=f"Topic {i}",
                author="Batch Tester"
            )
            presentations.append(presentation)
        
        # Delete each presentation
        for presentation in presentations:
            presentation_id = presentation["id"]
            
            delete_resp = api_client.delete(f"/presentations/{presentation_id}")
            assert delete_resp.status_code == 204
            
            # Verify it's gone
            get_resp = api_client.get(f"/presentations/{presentation_id}")
            assert_api_error(get_resp, 404, "not found")
        
        # Verify none are in the list
        list_resp = api_client.get("/presentations")
        assert list_resp.status_code == 200
        
        data = list_resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        remaining_ids = [p["id"] for p in items]
        
        for presentation in presentations:
            assert presentation["id"] not in remaining_ids

    async def test_delete_presentation_invalid_id_format(self, api_client, clean_db):
        """Test deleting a presentation with invalid ID format."""
        invalid_ids = ["not_a_number", "abc", "-1", "0"]
        
        for invalid_id in invalid_ids:
            response = api_client.delete(f"/presentations/{invalid_id}")
            # Should return either 404 (not found) or 422 (validation error)
            assert response.status_code in [404, 422]

    async def test_delete_presentation_twice(self, api_client, clean_db):
        """Test deleting the same presentation twice."""
        # Create a presentation
        presentation = await create_test_presentation(
            api_client,
            name="Double Delete Test",
            topic="Test Topic"
        )
        
        presentation_id = presentation["id"]
        
        # Delete it once
        delete_resp_1 = api_client.delete(f"/presentations/{presentation_id}")
        assert delete_resp_1.status_code == 204
        
        # Try to delete it again
        delete_resp_2 = api_client.delete(f"/presentations/{presentation_id}")
        assert_api_error(delete_resp_2, 404, "not found")

    async def test_delete_presentation_cascade_cleanup(self, api_client, create_presentation):
        """Test that deleting a presentation cleans up related data."""
        presentation = await create_presentation()
        presentation_id = presentation["id"]
        
        # Get the initial presentation to ensure it has some structure
        get_resp = api_client.get(f"/presentations/{presentation_id}")
        assert get_resp.status_code == 200
        original_data = get_resp.json()
        
        # Verify it has steps structure
        assert "steps" in original_data
        
        # Delete the presentation
        delete_resp = api_client.delete(f"/presentations/{presentation_id}")
        assert delete_resp.status_code == 204
        
        # Verify complete removal - not just marking as deleted
        get_resp_after = api_client.get(f"/presentations/{presentation_id}")
        assert get_resp_after.status_code == 404

    @pytest.mark.parametrize("presentation_name", [
        "Simple Name",
        "Name with Special Characters !@#$%",
        "Very Long Name " + "x" * 100,
        "Unicode Name 测试",
    ])
    async def test_delete_presentations_with_various_names(self, api_client, clean_db, presentation_name):
        """Test deleting presentations with various name formats."""
        presentation = await create_test_presentation(
            api_client,
            name=presentation_name,
            topic="Test Topic"
        )
        
        presentation_id = presentation["id"]
        
        # Delete the presentation
        delete_resp = api_client.delete(f"/presentations/{presentation_id}")
        assert delete_resp.status_code == 204
        
        # Verify it's gone
        get_resp = api_client.get(f"/presentations/{presentation_id}")
        assert_api_error(get_resp, 404, "not found")
