"""Factory classes for creating mock objects used in tests."""

from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class MockFactory:
    """Factory for creating various mock objects used in tests."""
    
    @staticmethod
    def create_mock_shape(
        name: Optional[str] = None,
        text: str = "",
        shape_type: int = 1,
        has_text_frame: bool = True,
        position: Dict[str, int] = None
    ) -> MagicMock:
        """
        Create a mock PowerPoint shape object.
        
        Args:
            name: Shape name
            text: Text content
            shape_type: Placeholder type
            has_text_frame: Whether shape has text frame
            position: Dict with left, top, width, height
            
        Returns:
            Mock shape object
        """
        shape = MagicMock()
        shape.name = name
        shape.text = text
        
        if has_text_frame:
            shape.has_text_frame = True
            shape.text_frame = MagicMock()
            shape.text_frame.text = text
            shape.text_frame.paragraphs = [MagicMock()]
            shape.text_frame.paragraphs[0].text = text
        else:
            shape.has_text_frame = False
            shape.text_frame = None
        
        # Placeholder format
        shape.placeholder_format = MagicMock()
        shape.placeholder_format.type = shape_type
        
        # Position and size
        position = position or {"left": 0, "top": 0, "width": 100, "height": 100}
        shape.left = position["left"]
        shape.top = position["top"]
        shape.width = position["width"]
        shape.height = position["height"]
        
        # Other common attributes
        shape.element = MagicMock()
        shape.shape_type = 1  # MSO_SHAPE_TYPE.PLACEHOLDER
        
        return shape
    
    @staticmethod
    def create_mock_slide(
        shapes: Optional[List[MagicMock]] = None,
        layout_name: str = "Title Slide",
        slide_index: int = 0
    ) -> MagicMock:
        """
        Create a mock PowerPoint slide object.
        
        Args:
            shapes: List of mock shapes to add to slide
            layout_name: Name of the slide layout
            slide_index: Index of the slide
            
        Returns:
            Mock slide object
        """
        slide = MagicMock()
        
        # Shapes collection
        shapes = shapes or []
        slide.shapes = MagicMock()
        slide.shapes.__iter__ = lambda self: iter(shapes)
        slide.shapes.__len__ = lambda self: len(shapes)
        slide.shapes.__getitem__ = lambda self, idx: shapes[idx]
        
        # Title placeholder
        title_shape = None
        for shape in shapes:
            if hasattr(shape, 'placeholder_format') and shape.placeholder_format.type == 0:
                title_shape = shape
                break
        
        slide.shapes.title = title_shape
        
        # Add shape methods
        def add_picture(image_path, left, top, width=None, height=None):
            pic = MagicMock()
            pic.left = left
            pic.top = top
            pic.width = width or 100
            pic.height = height or 100
            pic.image_path = image_path
            shapes.append(pic)
            return pic
        
        slide.shapes.add_picture = add_picture
        
        # Slide layout
        slide.slide_layout = MagicMock()
        slide.slide_layout.name = layout_name
        
        # Slide properties
        slide.slide_id = slide_index
        slide.name = f"Slide{slide_index + 1}"
        
        return slide
    
    @staticmethod
    def create_mock_presentation(
        slides: Optional[List[MagicMock]] = None,
        layouts: Optional[List[str]] = None
    ) -> MagicMock:
        """
        Create a mock PowerPoint presentation object.
        
        Args:
            slides: List of mock slides
            layouts: List of layout names
            
        Returns:
            Mock presentation object
        """
        presentation = MagicMock()
        
        # Slides collection
        slides = slides or []
        presentation.slides = MagicMock()
        presentation.slides.__iter__ = lambda self: iter(slides)
        presentation.slides.__len__ = lambda self: len(slides)
        presentation.slides.__getitem__ = lambda self, idx: slides[idx]
        
        # Add slide method
        def add_slide(layout):
            new_slide = MockFactory.create_mock_slide(layout_name=layout.name)
            slides.append(new_slide)
            return new_slide
        
        presentation.slides.add_slide = add_slide
        
        # Slide layouts
        layouts = layouts or [
            "Title Slide", "Title and Content", "Section Header",
            "Two Content", "Comparison", "Title Only", "Blank",
            "Content with Caption", "Picture with Caption",
            "Welcome", "Content", "ContentImage", "Section"
        ]
        
        presentation.slide_layouts = []
        for i, layout_name in enumerate(layouts):
            layout = MagicMock()
            layout.name = layout_name
            layout.index = i
            presentation.slide_layouts.append(layout)
        
        # Save method
        presentation.save = MagicMock()
        
        return presentation
    
    @staticmethod
    def create_gemini_mock_model(
        responses: Optional[List[Dict[str, Any]]] = None,
        default_response: Optional[Dict[str, Any]] = None
    ) -> MagicMock:
        """
        Create a mock Gemini GenerativeModel.
        
        Args:
            responses: List of responses to return in sequence
            default_response: Default response if responses list is exhausted
            
        Returns:
            Mock GenerativeModel
        """
        model = MagicMock()
        
        # Default response structure
        if default_response is None:
            default_response = {
                "title": "Test Presentation",
                "slides": [
                    {
                        "type": "Welcome",
                        "fields": {
                            "title": "Test Presentation",
                            "subtitle": "Test Subtitle",
                            "author": "Test Author"
                        }
                    }
                ]
            }
        
        # Track response index for both sync and async
        response_index = [0]  # Use list to make it mutable in nested functions
        
        def get_next_response():
            # Get next response or use default
            if responses and response_index[0] < len(responses):
                response_data = responses[response_index[0]]
                response_index[0] += 1
            else:
                response_data = default_response
            return response_data
        
        async def generate_content_async(*args, **kwargs):
            response_data = get_next_response()
            
            # Create mock response
            mock_response = MagicMock()
            mock_response.text = json.dumps(response_data)
            
            return mock_response
        
        def generate_content_sync(*args, **kwargs):
            response_data = get_next_response()
            
            # Create mock response
            mock_response = MagicMock()
            mock_response.text = json.dumps(response_data)
            
            return mock_response
        
        model.generate_content_async = generate_content_async
        model.generate_content = generate_content_sync
        
        return model
    
    @staticmethod
    def create_openai_mock_client(
        image_responses: Optional[List[Dict[str, Any]]] = None
    ) -> MagicMock:
        """
        Create a mock OpenAI client.
        
        Args:
            image_responses: List of image generation responses
            
        Returns:
            Mock OpenAI client
        """
        client = MagicMock()
        
        # Default image response
        default_image_response = {
            "created": int(datetime.now().timestamp()),
            "data": [{
                "url": "https://example.com/generated_image.png",
                "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
            }]
        }
        
        # Image generation
        images_mock = MagicMock()
        response_iter = iter(image_responses) if image_responses else None
        
        def generate(**kwargs):
            if response_iter:
                try:
                    response_data = next(response_iter)
                except StopIteration:
                    response_data = default_image_response
            else:
                response_data = default_image_response
            
            mock_response = MagicMock()
            mock_response.created = response_data.get("created", int(datetime.now().timestamp()))
            mock_response.data = []
            
            for data in response_data.get("data", []):
                img = MagicMock()
                img.url = data.get("url")
                img.b64_json = data.get("b64_json")
                mock_response.data.append(img)
            
            return mock_response
        
        images_mock.generate = generate
        client.images = images_mock
        
        return client
    
    @staticmethod
    def create_mock_api_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "",
        headers: Optional[Dict[str, str]] = None
    ) -> MagicMock:
        """
        Create a mock HTTP response.
        
        Args:
            status_code: HTTP status code
            json_data: JSON response data
            text: Text response
            headers: Response headers
            
        Returns:
            Mock response object
        """
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        response.headers = headers or {}
        
        if json_data is not None:
            response.json = MagicMock(return_value=json_data)
        else:
            response.json = MagicMock(side_effect=ValueError("No JSON data"))
        
        response.raise_for_status = MagicMock()
        if status_code >= 400:
            response.raise_for_status.side_effect = Exception(f"HTTP {status_code} error")
        
        return response
    
    @staticmethod
    def create_mock_database_session() -> MagicMock:
        """
        Create a mock database session.
        
        Returns:
            Mock SQLAlchemy session
        """
        session = AsyncMock()
        
        # Common session methods
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        session.add = MagicMock()
        session.delete = MagicMock()
        session.query = MagicMock()
        session.flush = AsyncMock()
        
        # Context manager support
        async def __aenter__():
            return session
        
        async def __aexit__(exc_type, exc_val, exc_tb):
            await session.close()
        
        session.__aenter__ = __aenter__
        session.__aexit__ = __aexit__
        
        return session