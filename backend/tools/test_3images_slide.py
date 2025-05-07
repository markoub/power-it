import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SlidePresentation, Slide
from tools.generate_pptx import generate_pptx_from_slides

async def test_3images_slide():
    """
    Test the generation of a 3Images slide
    """
    print("Testing 3Images slide generation...")
    
    # Create a test slide presentation with a 3Images slide
    slides = SlidePresentation(
        title="3Images Test Presentation",
        slides=[
            # Welcome slide
            Slide(
                type="Welcome",
                fields={
                    "title": "3Images Test Presentation",
                    "subtitle": "Testing the 3Images slide type",
                    "author": "Test User"
                }
            ),
            # A 3Images slide
            Slide(
                type="3Images",
                fields={
                    "title": "Three Images Slide",
                    "subtitleimage1": "Image 1 Subtitle",
                    "subtitleimage2": "Image 2 Subtitle",
                    "subtitleimage3": "Image 3 Subtitle"
                }
            )
        ]
    )
    
    # Generate the PowerPoint presentation
    result = await generate_pptx_from_slides(slides, "test")
    
    print(f"Generated PPTX file: {result.pptx_path}")
    print(f"Slide count: {result.slide_count}")
    
    return result

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_3images_slide()) 