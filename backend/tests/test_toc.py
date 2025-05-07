"""
Unit tests for Table of Contents slide generation
"""
import os
import pytest
import asyncio
from pptx import Presentation

from models import SlidePresentation, Slide

from tools.generate_pptx import generate_pptx_from_slides
from tools.pptx_toc import create_table_of_contents_slide

@pytest.mark.asyncio
async def test_toc_generation():
    """Test the generation of a Table of Contents slide with sections"""
    
    # Create test data with sections
    test_slides = [
        Slide(
            type="Welcome",
            fields={
                "title": "Eyelid Rejuvenation: Surgical & Non-Surgical Approaches",
                "subtitle": "An Overview for Surgeons & Anti-Aging Professionals",
                "author": "Ana Malivukovic"
            }
        ),
        Slide(
            type="TableOfContents",
            fields={
                "title": "Table of Contents",
                "sections": [
                    "Understanding Eyelid Aging",
                    "Surgical Approaches", 
                    "Non-Surgical Options",
                    "Treatment Algorithms"
                ]
            }
        ),
        Slide(
            type="Section",
            fields={
                "title": "Understanding Eyelid Aging"
            }
        ),
        Slide(
            type="Content",
            fields={
                "title": "The Aging Eyelid: More Than Just Cosmetics",
                "content": [
                    "Eyes as Focal Point: The eyelids often show aging first.",
                    "Aesthetic vs. Functional Issues: Beyond cosmetics.",
                    "Prevalence: Eyelid lifts are among the top 5 cosmetic surgeries.",
                    "Goal: Achieve a youthful, rested eye appearance."
                ]
            }
        )
    ]
    
    # Create presentation and generate PPTX
    presentation = SlidePresentation(
        title="Test TOC",
        slides=test_slides
    )
    
    result = await generate_pptx_from_slides(presentation, presentation_id="test")
    
    # Check that file was created
    assert os.path.exists(result.pptx_path)
    
    # Open the PPTX and analyze the TOC slide
    prs = Presentation(result.pptx_path)
    
    # TOC should be the second slide
    assert len(prs.slides) >= 2, "Presentation should have at least 2 slides"
    toc_slide = prs.slides[1]
    
    # Check for table of contents title
    title_found = False
    for shape in toc_slide.shapes:
        if hasattr(shape, "text_frame") and "Table of Contents" in shape.text_frame.text:
            title_found = True
            break
    
    assert title_found, "Table of Contents title not found in TOC slide"
    
    # Check for all section titles in TOC slide
    section_titles = test_slides[1].fields["sections"] 
    for section_title in section_titles:
        section_found = False
        for shape in toc_slide.shapes:
            if hasattr(shape, "text_frame") and section_title in shape.text_frame.text:
                section_found = True
                break
        
        assert section_found, f"Section title '{section_title}' not found in TOC slide"
    
    # Check that numbered format is used (example: "01  Understanding Eyelid Aging")
    numbered_format_found = False
    for shape in toc_slide.shapes:
        if hasattr(shape, "text_frame"):
            for section_index, section_title in enumerate(section_titles, 1):
                if f"{section_index:02d}  {section_title}" in shape.text_frame.text:
                    numbered_format_found = True
                    break
    
    assert numbered_format_found, "Numbered format (01 Section) not found in TOC slide"
    
    return result.pptx_path


@pytest.mark.asyncio
async def test_toc_with_empty_sections():
    """Test TOC generation with empty sections list"""
    
    # Create test data with empty sections list in TOC
    test_slides = [
        Slide(
            type="Welcome",
            fields={
                "title": "Test Presentation",
                "subtitle": "Testing TOC with empty sections"
            }
        ),
        Slide(
            type="TableOfContents",
            fields={
                "title": "Table of Contents",
                "sections": []
            }
        ),
        Slide(
            type="Content",
            fields={
                "title": "Test Content",
                "content": ["Test content item"]
            }
        )
    ]
    
    # Create presentation and generate PPTX
    presentation = SlidePresentation(
        title="Test Empty TOC",
        slides=test_slides
    )
    
    result = await generate_pptx_from_slides(presentation, presentation_id="test")
    
    # Check that file was created
    assert os.path.exists(result.pptx_path)
    
    # Open the PPTX and analyze
    prs = Presentation(result.pptx_path)
    
    # TOC should be the second slide
    assert len(prs.slides) >= 2, "Presentation should have at least 2 slides"
    toc_slide = prs.slides[1]
    
    # Check for table of contents title
    title_found = False
    for shape in toc_slide.shapes:
        if hasattr(shape, "text_frame") and "Table of Contents" in shape.text_frame.text:
            title_found = True
            break
    
    assert title_found, "Table of Contents title not found in TOC slide"
    
    return result.pptx_path


if __name__ == "__main__":
    asyncio.run(test_toc_generation()) 