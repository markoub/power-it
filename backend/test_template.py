#!/usr/bin/env python3

import asyncio
import os
from models import CompiledSlide, CompiledPresentation
from tools.generate_pptx import generate_pptx_from_slides
from config import PRESENTATIONS_STORAGE_DIR

async def test_template_pptx():
    """Test PPTX generation with the template."""
    # Create test directory if it doesn't exist
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, "test", "images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test image if needed
    test_image = os.path.join(test_dir, "test_image.png")
    if not os.path.exists(test_image):
        # Try to copy an existing image if available
        source_image = os.path.join(os.path.dirname(__file__), "curl_test_image.png")
        if os.path.exists(source_image):
            import shutil
            shutil.copy(source_image, test_image)
            print(f"Copied test image to {test_image}")
    
    # Create a test presentation with slides
    presentation = CompiledPresentation(
        title="Template Test Presentation",
        slides=[
            CompiledSlide(
                title="First Content Slide",
                type="content",
                content=[
                    "This is a bullet point",
                    "This is another bullet point",
                    "This is a third bullet point with more text to test wrapping"
                ],
                notes="These are speaker notes for the first slide"
            ),
            CompiledSlide(
                title="Slide With Image",
                type="content",
                content=[
                    "Here's a slide with an image",
                    "The image should appear in the image placeholder",
                    "Text should be in the content placeholder"
                ],
                notes="Speaker notes for the image slide",
                image_url="/presentations/test/images/test_image.png"
            )
        ]
    )
    
    # Generate PPTX
    try:
        result = await generate_pptx_from_slides(presentation, "test")
        print(f"\nPPTX file generated successfully at: {result.pptx_path}")
        print(f"Total slides: {result.slide_count}")
        
        # Don't delete the file - keep it for inspection
        print(f"\nTest PPTX file saved for inspection at: {result.pptx_path}")
        print(f"Open this file to verify that the template is working properly.")
    except Exception as e:
        print(f"Error generating PPTX: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_template_pptx()) 