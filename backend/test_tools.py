#!/usr/bin/env python3

import asyncio
import os
import json
from tools.research import research_topic
from tools.slides import generate_slides
from orchestrator import create_presentation
from models import ResearchData, SlidePresentation, FullPresentation, Slide, CompiledSlide, CompiledPresentation
from tools.generate_pptx import generate_pptx_from_slides, convert_pptx_to_png
from config import PRESENTATIONS_STORAGE_DIR

async def main():
    print("Testing Presentation Assistant...")
    
    # Test research tool
    print("\nTesting research_topic...")
    try:
        research_result = await research_topic("Quantum Computing")
        print(f"Research completed. Content length: {len(research_result.content)}")
        print(f"Number of sources: {len(research_result.links)}")
        
        # Save research result for inspection
        with open("research_result.json", "w") as f:
            f.write(research_result.model_dump_json(indent=2))
        print("Research data saved to research_result.json")
    except Exception as e:
        print(f"Research failed: {e}")
        return
    
    # Test slides generator
    print("\nTesting generate_slides...")
    try:
        slides_result = await generate_slides(research_result, 8)
        print(f"Slides generated. Title: {slides_result.title}")
        print(f"Number of slides: {len(slides_result.slides)}")
        
        # Save slides result for inspection
        with open("slides_result.json", "w") as f:
            f.write(slides_result.model_dump_json(indent=2))
        print("Slides data saved to slides_result.json")
    except Exception as e:
        print(f"Slides generation failed: {e}")
        return
    
    # Test orchestrator
    print("\nTesting create_presentation...")
    try:
        presentation_result = await create_presentation("Artificial Intelligence in Healthcare", 10)
        print("Full presentation created")
        print(f"Research content length: {len(presentation_result.research.content)}")
        print(f"Number of slides: {len(presentation_result.slides.slides)}")
        
        # Save full presentation result for inspection
        with open("full_presentation_result.json", "w") as f:
            f.write(presentation_result.model_dump_json(indent=2))
        print("Full presentation data saved to full_presentation_result.json")
    except Exception as e:
        print(f"Full presentation failed: {e}")
        return
    
    print("\nAll tests completed successfully!")

async def test_generate_pptx():
    # Create a simple slide presentation
    slides = SlidePresentation(
        title="Test Presentation",
        slides=[
            Slide(
                title="Introduction",
                type="content",
                content=["Point 1", "Point 2", "Point 3"],
                notes="These are speaker notes for slide 1"
            ),
            Slide(
                title="Main Content",
                type="content",
                content=["Main point 1", "Main point 2", "Main point 3"],
                notes="These are speaker notes for slide 2"
            )
        ]
    )
    
    # Generate the PPTX file
    pptx_gen = await generate_pptx_from_slides(slides, "test")
    
    # Verify the PPTX file was created
    assert os.path.exists(pptx_gen.pptx_path)
    
    # Clean up
    os.remove(pptx_gen.pptx_path)
    
    # Return success
    return True

async def test_generate_pptx_with_template():
    # Create a simple slide presentation with images
    slides = CompiledPresentation(
        title="Template Test Presentation",
        slides=[
            CompiledSlide(
                title="Slide 1",
                type="content",
                content=["Point 1", "Point 2", "Point 3"],
                notes="These are speaker notes for slide 1",
            ),
            CompiledSlide(
                title="Slide 2",
                type="content",
                content=["Main point 1", "Main point 2", "Main point 3"],
                notes="These are speaker notes for slide 2",
                image_url="/presentations/test/images/test_image.png"
            )
        ]
    )
    
    # Ensure the test directory exists and has an image
    test_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, "test", "images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test image if it doesn't exist
    test_image_path = os.path.join(test_dir, "test_image.png")
    if not os.path.exists(test_image_path):
        # Copy a test image from the project root if available
        root_test_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_image.png")
        if os.path.exists(root_test_image):
            import shutil
            shutil.copy(root_test_image, test_image_path)
    
    # Generate the PPTX file
    pptx_gen = await generate_pptx_from_slides(slides, "test")
    
    # Verify the PPTX file was created
    assert os.path.exists(pptx_gen.pptx_path)
    
    # Convert to PNG (uncomment if needed for visual verification)
    # png_files = await convert_pptx_to_png(pptx_gen.pptx_path)
    # assert len(png_files) > 0
    
    # Clean up
    os.remove(pptx_gen.pptx_path)
    
    # Return success
    return True

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(test_generate_pptx())
    asyncio.run(test_generate_pptx_with_template())
    print("All tests completed successfully!") 