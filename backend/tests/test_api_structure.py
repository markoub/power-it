"""
Tests for the refactored API structure
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import api_new
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_new import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns the correct message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "PowerIt Presentation Assistant API is running"}

def test_openapi_schema():
    """Test the OpenAPI schema is accessible"""
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    # Check that important sections are present
    schema = response.json()
    assert "paths" in schema
    assert "components" in schema
    # Remove tags assertion as they are embedded within paths, not at the root level
    # assert "tags" in schema

def test_swagger_ui():
    """Test that Swagger UI docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()

def test_presentations_endpoints_exist():
    """Test that the presentations endpoints are registered"""
    response = client.get("/api/openapi.json")
    schema = response.json()
    
    # Check for key presentation endpoints
    assert "/presentations" in schema["paths"]
    assert "/presentations/{presentation_id}" in schema["paths"]
    
def test_images_endpoints_exist():
    """Test that the images endpoints are registered"""
    response = client.get("/api/openapi.json")
    schema = response.json()
    
    # Check for image endpoint
    assert "/images" in schema["paths"]

def test_logos_endpoints_exist():
    """Test that the logos endpoints are registered"""
    response = client.get("/api/openapi.json")
    schema = response.json()
    
    # Check for logos endpoints
    assert "/logos/search" in schema["paths"]
    assert "/logos/{term}" in schema["paths"] 