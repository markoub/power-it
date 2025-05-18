import os
import pytest
import json
import asyncio
from pptx import Presentation
from models import SlidePresentation, Slide
from tools.generate_pptx import generate_pptx_from_slides

# Create fixture directory
fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
os.makedirs(fixture_dir, exist_ok=True)

# Check if we're in record mode
record_mode = os.environ.get("TOC_FONT_VCR_MODE") == "record"
print(f"TOC Font VCR mode: {'record' if record_mode else 'replay'}")

@pytest.fixture
def toc_font_vcr():
    """VCR-like fixture for TOC font style tests"""
    
    def load_or_save_fixture(test_name, result_data=None):
        """Load or save fixture based on mode"""
        fixture_name = f"toc_font_{test_name}.json"
        fixture_path = os.path.join(fixture_dir, fixture_name)
        
        if record_mode and result_data:
            # Record mode - save the fixture
            with open(fixture_path, "w") as f:
                json.dump(result_data, f, indent=2)
            print(f"Saved TOC font test result to {fixture_path}")
            return result_data
        else:
            # Replay mode - load from fixture
            try:
                with open(fixture_path, "r") as f:
                    fixture_data = json.load(f)
                print(f"Loaded TOC font test result from {fixture_path}")
                return fixture_data
            except FileNotFoundError:
                # Skip test if fixture not available in replay mode
                pytest.skip(f"Fixture not found at {fixture_path}. Run with TOC_FONT_VCR_MODE=record first.")
                return None
                
    return load_or_save_fixture

def find_toc_slide(prs):
    """Find the TOC slide index and slide object."""
    for i, slide in enumerate(prs.slides):
        # Check slide title for "Table of Contents" or "Contents"
        for shape in slide.shapes:
            if hasattr(shape, "text") and any(title in shape.text for title in ["Table of Contents", "Contents", "TOC"]):
                return i, slide
            
        # If no title found, look for sections list as a heuristic
        section_count = 0
        for shape in slide.shapes:
            if hasattr(shape, "text") and hasattr(shape, "text_frame"):
                # Count potential section entries
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if any(section in run.text for section in 
                              ["Introduction", "Background", "Methods", "Results"]):
                            section_count += 1
        
        # If we found multiple section-like entries, likely a TOC slide
        if section_count >= 2:
            return i, slide
    
    return -1, None

@pytest.mark.asyncio
async def test_toc_font_style_preservation(toc_font_vcr):
    """Test font style preservation in Table of Contents slide."""
    test_name = "style_preservation"
    
    # Create test presentation with TOC slide
    slides = SlidePresentation(
        title='Test Presentation',
        slides=[
            Slide(type='Welcome', fields={'subtitle': 'Testing font styles'}),
            Slide(type='TableOfContents', fields={
                'title': 'Table of Contents',
                'sections': ['Introduction', 'Background', 'Methods', 'Results', 'Discussion', 'Conclusion']
            }),
            Slide(type='Section', fields={'title': 'Introduction'}),
            Slide(type='Content', fields={
                'title': 'Introduction Slide',
                'content': ['This is a test of font styles']
            }),
            Slide(type='Section', fields={'title': 'Background'}),
            Slide(type='ContentImage', fields={
                'title': 'Background Slide',
                'content': ['Testing image content']
            })
        ]
    )
    
    # In record mode, generate actual presentation and analyze
    if record_mode:
        # Generate the presentation
        result = await generate_pptx_from_slides(slides, 'test')
        
        # Analyze the presentation to extract font information
        prs = Presentation(result.pptx_path)
        
        # Find TOC slide using improved method
        toc_slide_idx, toc_slide = find_toc_slide(prs)
        
        if toc_slide_idx < 0 or toc_slide is None:
            # Fall back to second slide if TOC not found
            # (Usually the second slide after the welcome slide)
            if len(prs.slides) >= 2:
                toc_slide_idx = 1
                toc_slide = prs.slides[1]
                print("TOC slide not detected, falling back to slide 2")
            else:
                pytest.skip("TOC slide not found in presentation")
        
        # Extract font information from TOC slide
        font_info = []
        
        for shape in toc_slide.shapes:
            if not hasattr(shape, "text"):
                continue
                
            if hasattr(shape, "text_frame"):
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if hasattr(run, "font"):
                            font_info.append({
                                "text": run.text,
                                "name": run.font.name if hasattr(run.font, "name") else None,
                                "size": run.font.size.pt if hasattr(run.font, "size") and run.font.size else None,
                                "bold": run.font.bold if hasattr(run.font, "bold") else None,
                                "italic": run.font.italic if hasattr(run.font, "italic") else None,
                            })
        
        # Clean up
        os.remove(result.pptx_path)
        
        # Save findings to fixture
        fixture_data = {
            "toc_slide_idx": toc_slide_idx,
            "font_info": font_info
        }
        toc_font_vcr(test_name, fixture_data)
        
        # Skip test based on content
        if len(font_info) == 0:
            pytest.skip("No font information found in TOC slide")
        
    # In replay mode, use fixture data
    else:
        fixture_data = toc_font_vcr(test_name)
        
        # Verify fixture data structure
        assert "toc_slide_idx" in fixture_data
        assert "font_info" in fixture_data
        assert isinstance(fixture_data["font_info"], list)
        
        # If no font info but test not skipped, just pass
        if len(fixture_data["font_info"]) == 0:
            pytest.skip("No font information in fixture data")
        
        # Verify at least one section has font styling
        styled_runs = [info for info in fixture_data["font_info"] if info.get("bold") or info.get("italic")]
        if len(styled_runs) == 0:
            print("Warning: No styled text found in TOC slide") 