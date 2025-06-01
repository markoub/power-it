"""
Tests for the refactored API structure
"""
import pytest

pytestmark = pytest.mark.asyncio


class TestAPIStructure:
    """Tests for the API structure and endpoint registration."""

    async def test_root_endpoint(self, api_client):
        """Test the root endpoint returns the correct message."""
        response = api_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "PowerIt Presentation Assistant API is running"}

    async def test_openapi_schema_accessible(self, api_client):
        """Test the OpenAPI schema is accessible."""
        response = api_client.get("/api/openapi.json")
        assert response.status_code == 200
        
        # Check that important sections are present
        schema = response.json()
        assert "paths" in schema
        assert "components" in schema
        assert "info" in schema

    async def test_swagger_ui_accessible(self, api_client):
        """Test that Swagger UI docs are accessible."""
        response = api_client.get("/docs")
        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()

    async def test_redoc_accessible(self, api_client):
        """Test that ReDoc documentation is accessible."""
        response = api_client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()


class TestEndpointRegistration:
    """Tests for endpoint registration in the OpenAPI schema."""

    @pytest.fixture
    async def api_schema(self, api_client):
        """Get the OpenAPI schema for testing."""
        response = api_client.get("/api/openapi.json")
        assert response.status_code == 200
        return response.json()

    async def test_presentations_endpoints_registered(self, api_schema):
        """Test that the presentations endpoints are registered."""
        paths = api_schema["paths"]
        
        # Check for key presentation endpoints
        assert "/presentations" in paths
        assert "/presentations/{presentation_id}" in paths
        
        # Check HTTP methods
        presentations_path = paths["/presentations"]
        assert "get" in presentations_path  # List presentations
        assert "post" in presentations_path  # Create presentation
        
        presentation_detail_path = paths["/presentations/{presentation_id}"]
        assert "get" in presentation_detail_path  # Get presentation
        assert "delete" in presentation_detail_path  # Delete presentation

    async def test_presentation_steps_endpoints_registered(self, api_schema):
        """Test that presentation step endpoints are registered."""
        paths = api_schema["paths"]
        
        # Check for step execution endpoints
        step_patterns = [
            "/presentations/{presentation_id}/steps/{step_name}/run",
            "/presentations/{presentation_id}/steps/{step_name}",
        ]
        
        for pattern in step_patterns:
            assert pattern in paths, f"Step endpoint {pattern} should be registered"

    async def test_images_endpoints_registered(self, api_schema):
        """Test that the images endpoints are registered."""
        paths = api_schema["paths"]
        
        # Check for image endpoint
        assert "/images" in paths
        
        # Check HTTP method
        images_path = paths["/images"]
        assert "post" in images_path  # Generate images

    async def test_logos_endpoints_registered(self, api_schema):
        """Test that the logos endpoints are registered."""
        paths = api_schema["paths"]
        
        # Check for logos endpoints
        assert "/logos/search" in paths
        assert "/logos/{term}" in paths
        
        # Check HTTP methods - search uses POST, term uses GET
        logos_search_path = paths["/logos/search"]
        assert "post" in logos_search_path
        
        logos_term_path = paths["/logos/{term}"]
        assert "get" in logos_term_path

    async def test_pptx_endpoints_registered(self, api_schema):
        """Test that PPTX-related endpoints are registered."""
        paths = api_schema["paths"]
        
        # Check for actual PPTX endpoints in the router
        pptx_patterns = [
            "/presentations/{presentation_id}/download-pptx",
            "/presentations/{presentation_id}/download-pdf",
            "/presentations/{presentation_id}/pptx-slides",
            "/presentations/{presentation_id}/pptx-slides/{filename}",
        ]
        
        # At least one PPTX endpoint should exist
        pptx_endpoints_found = [pattern for pattern in pptx_patterns if pattern in paths]
        assert len(pptx_endpoints_found) > 0, "Should have at least one PPTX endpoint"

    @pytest.mark.parametrize("endpoint,methods", [
        ("/presentations", ["get", "post"]),
        ("/presentations/{presentation_id}", ["get", "delete"]),
        ("/images", ["post"]),
        ("/logos/search", ["post"]),
        ("/logos/{term}", ["get"]),
    ])
    async def test_endpoint_methods(self, api_schema, endpoint, methods):
        """Test that endpoints support expected HTTP methods."""
        paths = api_schema["paths"]
        
        if endpoint in paths:
            endpoint_config = paths[endpoint]
            for method in methods:
                assert method in endpoint_config, f"Endpoint {endpoint} should support {method.upper()}"

    async def test_api_tags_organization(self, api_schema):
        """Test that API endpoints are properly tagged for organization."""
        paths = api_schema["paths"]
        
        # Check that endpoints have tags
        for path, path_config in paths.items():
            for method, method_config in path_config.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    assert "tags" in method_config, f"Endpoint {method.upper()} {path} should have tags"
                    assert len(method_config["tags"]) > 0, f"Endpoint {method.upper()} {path} should have non-empty tags"

    async def test_api_operation_ids(self, api_schema):
        """Test that API operations have unique operation IDs."""
        paths = api_schema["paths"]
        operation_ids = set()
        
        for path, path_config in paths.items():
            for method, method_config in path_config.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    if "operationId" in method_config:
                        operation_id = method_config["operationId"]
                        assert operation_id not in operation_ids, f"Duplicate operation ID: {operation_id}"
                        operation_ids.add(operation_id)

    async def test_api_response_schemas(self, api_schema):
        """Test that API endpoints define proper response schemas."""
        paths = api_schema["paths"]
        
        for path, path_config in paths.items():
            for method, method_config in path_config.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    assert "responses" in method_config, f"Endpoint {method.upper()} {path} should define responses"
                    
                    responses = method_config["responses"]
                    # Should at least define some successful response
                    success_codes = ["200", "201", "202", "204"]
                    has_success_response = any(code in responses for code in success_codes)
                    assert has_success_response, f"Endpoint {method.upper()} {path} should define a success response"


class TestAPIHealthCheck:
    """Tests for API health and readiness."""

    async def test_api_responds_to_requests(self, api_client):
        """Test that the API responds to basic requests."""
        response = api_client.get("/")
        assert response.status_code == 200

    async def test_api_handles_404_gracefully(self, api_client):
        """Test that the API handles 404 errors gracefully."""
        response = api_client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    async def test_api_handles_method_not_allowed(self, api_client):
        """Test that the API handles method not allowed errors."""
        # Try to POST to an endpoint that only supports GET
        response = api_client.post("/docs")
        assert response.status_code in [404, 405, 422]  # Various frameworks handle this differently 