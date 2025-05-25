from models import ResearchData
from tools.slide_config import PRESENTATION_STRUCTURE
from tools.logo_fetcher import download_logo

# This function is extracted from tools.slides for offline slide generation

def generate_offline_slides(research: ResearchData, target_slides: int = 10, author: str = None) -> dict:
    """Generate a realistic offline slides response based on research content."""
    if author is None:
        author = PRESENTATION_STRUCTURE.get("default_author", "AI Presenter")

    research_content = research.content if research and research.content else "Artificial Intelligence in Modern Business"

    lines = research_content.split('\n')
    title_candidates = []
    for line in lines[:10]:
        line = line.strip()
        if len(line) > 10 and len(line) < 100 and not line.startswith('-') and not line.startswith('•'):
            title_candidates.append(line)
    if title_candidates:
        presentation_title = title_candidates[0].rstrip('.').rstrip(':')
    else:
        presentation_title = "Business Presentation"

    content_sections = []
    current_section = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 5:
            if (
                line.isupper()
                or line.endswith(':')
                or line.startswith('#')
                or (len(line) < 50 and not line.startswith('-') and not line.startswith('•'))
            ):
                if current_section:
                    content_sections.append(current_section)
                    current_section = []
                current_section.append(line.rstrip(':').rstrip('#').strip())
            else:
                current_section.append(line)
    if current_section:
        content_sections.append(current_section)
    if not content_sections:
        content_sections = [
            ["Introduction", "Overview of the topic", "Key concepts and definitions"],
            ["Main Content", "Core information and insights", "Important details and analysis"],
            ["Applications", "Practical applications", "Real-world examples and use cases"],
            ["Conclusion", "Summary of key points", "Next steps and recommendations"],
        ]

    slides = []
    slides.append({
        "type": "Welcome",
        "fields": {"title": presentation_title, "subtitle": "Professional Business Presentation", "author": author},
    })

    section_count = 0
    slide_count = 1
    for section_data in content_sections[:4]:
        section_title = section_data[0] if section_data else f"Section {section_count + 1}"
        section_content = section_data[1:] if len(section_data) > 1 else ["Content for this section"]
        slides.append({"type": "Section", "fields": {"title": section_title}})
        slide_count += 1
        section_count += 1
        slides_in_section = 0
        max_slides_per_section = min(3, max(1, (target_slides - len(content_sections) - 1) // len(content_sections)))
        for i, content_item in enumerate(section_content[:max_slides_per_section]):
            if slide_count >= target_slides:
                break
            if slides_in_section == 0 and len(content_item) > 20:
                slides.append({
                    "type": "ContentImage",
                    "fields": {
                        "title": f"{section_title} Overview",
                        "subtitle": "Key Points and Insights",
                        "content": [content_item, f"Important aspects of {section_title.lower()}", "Supporting details and context"],
                        "image": f"Professional illustration representing {section_title.lower()} concepts and applications in business environment",
                    },
                })
            elif slides_in_section == 1 and section_count <= 2:
                slides.append({
                    "type": "ImageFull",
                    "fields": {
                        "title": f"{section_title} in Detail",
                        "image": f"Detailed visual representation of {content_item[:50]}... showing modern business applications and innovative solutions",
                        "explanation": f"This image illustrates the key concepts and practical applications related to {section_title.lower()}, demonstrating real-world implementation and benefits",
                    },
                })
            elif slides_in_section == 2 and section_count == 2:
                slides.append({
                    "type": "3Images",
                    "fields": {
                        "title": f"Three Aspects of {section_title}",
                        "image1": f"Modern technology solutions for {section_title.lower()} showing digital transformation",
                        "image2": f"Business processes and workflows related to {section_title.lower()} in corporate environment",
                        "image3": f"Future trends and innovations in {section_title.lower()} with growth projections",
                        "image1subtitle": "Technology Solutions",
                        "image2subtitle": "Business Processes",
                        "image3subtitle": "Future Innovations",
                    },
                })
            elif "company" in content_item.lower() or "business" in content_item.lower() or any(word in content_item.lower() for word in ["google", "microsoft", "amazon", "apple", "meta"]):
                slides.append({
                    "type": "ContentWithLogos",
                    "fields": {
                        "title": f"Leading Companies in {section_title}",
                        "content": [
                            content_item,
                            "Industry leaders and innovators",
                            "Key players driving innovation",
                            "Market leaders setting industry standards",
                        ],
                        "logo1": "Google",
                        "logo2": "Microsoft",
                        "logo3": "Amazon",
                    },
                })
            else:
                slides.append({
                    "type": "Content",
                    "fields": {
                        "title": content_item if len(content_item) < 60 else f"{section_title} Details",
                        "content": [
                            content_item,
                            f"Key insights about {section_title.lower()}",
                            "Supporting information and context",
                            "Practical implications and applications",
                        ],
                    },
                })
            slides_in_section += 1
            slide_count += 1

    if slide_count < target_slides:
        slides.append({
            "type": "Content",
            "fields": {
                "title": "Thank You & Questions",
                "content": ["Thank you for your attention", "Questions and discussion", "Contact information available", "Additional resources provided"],
            },
        })

    for i, slide in enumerate(slides):
        if slide.get("type") == "ContentWithLogos":
            for logo_field in ["logo1", "logo2", "logo3"]:
                if logo_field in slide["fields"] and slide["fields"][logo_field]:
                    logo_term = slide["fields"][logo_field]
                    try:
                        success, result = download_logo(logo_term)
                        if success:
                            slide["fields"][logo_field] = result
                    except Exception:
                        pass

    for slide in slides:
        title = slide.get("fields", {}).get("title", "this slide")
        slide.setdefault("fields", {})["notes"] = f"Speaker notes for {title}."

    return {"title": presentation_title, "author": author, "slides": slides}
