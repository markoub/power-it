import asyncio
from tools.generate_pptx import generate_pptx_from_slides
from models import SlidePresentation, Slide

async def test():
    """Test font style preservation in Table of Contents slide."""
    print("Creating test presentation with TOC...")
    
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
    
    # Generate the presentation
    result = await generate_pptx_from_slides(slides, 'test')
    print(f"Generated presentation at: {result.pptx_path}")
    print("Please check the presentation to verify font styles are preserved in the TOC slide")

if __name__ == "__main__":
    asyncio.run(test()) 