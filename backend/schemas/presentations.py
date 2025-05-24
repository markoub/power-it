from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PresentationResponse(BaseModel):
    """Base presentation response model"""
    id: int = Field(description="Unique identifier for the presentation")
    name: str = Field(description="Name of the presentation")
    topic: Optional[str] = Field(None, description="Main topic of the presentation")
    author: Optional[str] = Field(None, description="Author of the presentation")
    thumbnail_url: Optional[str] = Field(None, description="URL to the first slide thumbnail image")
    created_at: str = Field(description="ISO-formatted creation timestamp")
    updated_at: str = Field(description="ISO-formatted last update timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Introduction to AI",
                "topic": "Artificial Intelligence",
                "author": "John Doe",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-01T12:30:00"
            }
        }
    )

class PresentationStepResponse(BaseModel):
    """Presentation step response model"""
    id: int = Field(description="Unique identifier for the step")
    step: str = Field(description="Step type identifier: research, manual_research, slides, images, compiled, pptx")
    status: str = Field(description="Current status of the step: pending, running, completed, error")
    result: Optional[Dict[str, Any]] = Field(None, description="Result data for the completed step. Structure depends on step type")
    error_message: Optional[str] = Field(None, description="Error message if step failed")
    created_at: str = Field(description="ISO-formatted creation timestamp")
    updated_at: str = Field(description="ISO-formatted last update timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "step": "research",
                "status": "completed",
                "result": {
                    "content": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.\n\nThe ideal characteristic of artificial intelligence is its ability to rationalize and take actions that have the best chance of achieving a specific goal. A subset of artificial intelligence is machine learning, which refers to the concept that computer programs can automatically learn from and adapt to new data without being assisted by humans.",
                    "links": [
                        {"href": "https://example.com/ai-basics", "title": "AI Basics"},
                        {"href": "https://example.com/ml-intro", "title": "Intro to Machine Learning"}
                    ]
                },
                "error_message": None,
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-01T12:30:00"
            }
        }
    )

class PresentationDetailResponse(BaseModel):
    """Detailed presentation response with steps"""
    id: int = Field(description="Unique identifier for the presentation")
    name: str = Field(description="Name of the presentation")
    topic: Optional[str] = Field(None, description="Main topic of the presentation")
    author: Optional[str] = Field(None, description="Author of the presentation")
    thumbnail_url: Optional[str] = Field(None, description="URL to the first slide thumbnail image")
    created_at: str = Field(description="ISO-formatted creation timestamp")
    updated_at: str = Field(description="ISO-formatted last update timestamp")
    steps: List[PresentationStepResponse] = Field(description="List of all steps for this presentation with their statuses and results")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Introduction to AI",
                "topic": "Artificial Intelligence",
                "author": "John Doe",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-01T12:30:00",
                "steps": [
                    {
                        "id": 1,
                        "step": "research",
                        "status": "completed",
                        "result": {
                            "content": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines...",
                            "links": [
                                {"href": "https://example.com/ai-basics", "title": "AI Basics"}
                            ]
                        },
                        "error_message": None,
                        "created_at": "2023-01-01T12:00:00",
                        "updated_at": "2023-01-01T12:30:00"
                    },
                    {
                        "id": 2,
                        "step": "slides",
                        "status": "completed",
                        "result": {
                            "title": "Introduction to AI",
                            "slides": [
                                {
                                    "type": "welcome",
                                    "fields": {
                                        "title": "Introduction to AI",
                                        "subtitle": "Understanding the Basics of Artificial Intelligence"
                                    }
                                },
                                {
                                    "type": "content",
                                    "fields": {
                                        "title": "What is AI?",
                                        "content": "• The simulation of human intelligence in machines\n• Designed to think and learn like humans\n• Abilities include problem-solving, learning, and decision making"
                                    }
                                }
                            ]
                        },
                        "error_message": None,
                        "created_at": "2023-01-01T12:05:00",
                        "updated_at": "2023-01-01T12:35:00"
                    }
                ]
            }
        }
    )

class StepUpdateRequest(BaseModel):
    """Model for updating a step's result"""
    result: Dict[str, Any] = Field(description="Updated result data for the step. Structure depends on step type")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": {
                    "content": "Updated research content on Artificial Intelligence (AI). AI refers to the simulation of human intelligence in machines that are programmed to think and learn like humans...",
                    "links": [
                        {"href": "https://example.com/ai-guide", "title": "Comprehensive AI Guide"},
                        {"href": "https://example.com/ai-applications", "title": "Real-world AI Applications"}
                    ]
                }
            }
        }
    )

class PresentationCreate(BaseModel):
    """Model for creating a new presentation"""
    name: str = Field(description="Name of the presentation")
    topic: Optional[str] = Field(None, description="Main topic for the presentation. Required if research_type is 'research'")
    research_content: Optional[str] = Field(None, description="Manual research content. Required if research_type is 'manual_research'")
    research_type: str = Field("pending", description="Type of research to perform: 'research' for AI-generated, 'manual_research' for user-provided content, or 'pending' for initial creation")
    author: Optional[str] = Field(None, description="Author name for the presentation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Introduction to AI",
                "author": "John Doe",
                "research_type": "pending"
            }
        }
    )

class SlideModificationRequest(BaseModel):
    """Model for slide modification request"""
    prompt: str = Field(description="User prompt describing how to modify the slide or presentation")
    slide_index: Optional[int] = Field(None, description="Index of the specific slide to modify. If not provided, the entire presentation may be modified")
    current_step: Optional[str] = Field(None, description="Current step in the presentation process (e.g., 'slides', 'compiled')")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Make this slide more engaging and add a section about machine learning",
                "slide_index": 2,
                "current_step": "slides"
            }
        }
    )

class TopicUpdateRequest(BaseModel):
    """Request schema for updating presentation topic"""
    topic: str = Field(
        description="The new topic for the presentation"
    ) 