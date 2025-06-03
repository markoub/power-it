from models import ResearchData
from tools.slide_config import PRESENTATION_STRUCTURE
from tools.logo_fetcher import download_logo

# This function is extracted from tools.slides for offline slide generation

def generate_offline_slides(
    research: ResearchData, 
    target_slides: int = 10, 
    author: str = None,
    target_audience: str = "general",
    content_density: str = "medium",
    presentation_duration: int = 15,
    custom_prompt: str = None
) -> dict:
    """Generate a realistic offline slides response based on research content with customization options."""
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
        presentation_title = title_candidates[0].rstrip('.').rstrip(':').lstrip('#').strip()
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
                current_section.append(line.rstrip(':').lstrip('#').strip())
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
    
    # 1. Welcome slide (always first)
    slides.append({
        "type": "Welcome",
        "fields": {
            "title": presentation_title, 
            "subtitle": "Professional Business Presentation", 
            "author": author,
            "notes": "Welcome everyone to this presentation. Today we'll explore key concepts and insights."
        },
    })

    # 2. TableOfContents slide 
    section_titles = ["Introduction", "Core Concepts", "Technical Details", "Business Applications", 
                     "Market Analysis", "Implementation Strategy", "Future Outlook", "Conclusion"]
    slides.append({
        "type": "TableOfContents",
        "fields": {
            "sections": section_titles[:8],  # Ensure we have exactly up to 8 sections
            "notes": "Here's our agenda for today. We'll cover these key areas in detail."
        },
    })

    # 3. First Section slide
    slides.append({
        "type": "Section", 
        "fields": {
            "title": "Introduction",
            "notes": "Let's begin with an introduction to set the context."
        }
    })

    # 4. Content slide (basic bullet points with markdown)
    slides.append({
        "type": "Content",
        "fields": {
            "title": "Key Concepts Overview",
            "content": [
                "Understanding the **fundamental principles** of modern systems",
                "Core components and their *relationships*",
                "Essential **terminology** and *definitions*",
                "Industry **best practices** and _standards_"
            ],
            "notes": "These are the fundamental concepts we need to understand before diving deeper."
        },
    })

    # 5. ContentImage slide with markdown
    slides.append({
        "type": "ContentImage",
        "fields": {
            "title": "System Architecture",
            "subtitle": "Modern Technology Stack",
            "content": [
                "**Cloud-native** infrastructure design with *auto-scaling*",
                "Microservices and **containerization** using _Docker_ and _Kubernetes_", 
                "**API-first** development approach with *RESTful* services",
                "Scalable and **resilient** systems with _99.99% uptime_"
            ],
            "image": "Professional illustration of modern cloud architecture with interconnected services, APIs, and data flows in a corporate technology environment",
            "notes": "This slide shows our comprehensive system architecture and how components interact."
        },
    })

    # 6. Section slide
    slides.append({
        "type": "Section",
        "fields": {
            "title": "Technical Implementation", 
            "notes": "Now let's dive into the technical details of our solution."
        }
    })

    # 7. ImageFull slide
    slides.append({
        "type": "ImageFull",
        "fields": {
            "title": "Data Flow Visualization",
            "image": "Detailed technical diagram showing data flow from ingestion through processing to analytics, with modern database systems and real-time streaming",
            "explanation": "This comprehensive diagram illustrates how data moves through our system, from initial collection through various processing stages to final analytics and reporting. Each component is optimized for performance and reliability.",
            "notes": "Take a moment to observe the complete data flow. Notice how we ensure data integrity at each stage."
        },
    })

    # 8. 3Images slide
    slides.append({
        "type": "3Images",
        "fields": {
            "title": "Three Pillars of Success",
            "image1": "Modern office environment with professionals collaborating on digital transformation initiatives",
            "image2": "Advanced technology dashboard showing real-time analytics and performance metrics", 
            "image3": "Future-oriented visualization of AI and automation in business processes",
            "subtitleimage1": "People & Culture",
            "subtitleimage2": "Technology & Innovation",
            "subtitleimage3": "Future Vision",
            "notes": "These three pillars form the foundation of our strategic approach."
        },
    })

    # 9. ContentWithLogos slide with markdown
    slides.append({
        "type": "ContentWithLogos",
        "fields": {
            "title": "Industry Leaders & Partners",
            "content": [
                "Strategic partnerships with **technology giants** for _innovation_",
                "**Collaborative** innovation initiatives with *global reach*",
                "Shared commitment to **excellence** and _quality_",
                "Integrated solutions and **platforms** across *multiple domains*"
            ],
            "logo1": "Google",
            "logo2": "Microsoft", 
            "logo3": "Amazon",
            "notes": "We work with the best in the industry to deliver exceptional results."
        },
    })

    # 10. Additional Content slide with markdown to reach target
    if len(slides) < target_slides:
        slides.append({
            "type": "Content",
            "fields": {
                "title": "Next Steps & Conclusion",
                "content": [
                    "**Implementation roadmap** with *key milestones* and timeline",
                    "Key **success metrics** and _KPIs_ for measurement",
                    "Resources and **support** available through _multiple channels_",
                    "**Thank you** for your *attention* and engagement"
                ],
                "notes": "Let's wrap up with clear next steps and how to move forward."
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

    # Generate speaker notes based on duration and density
    avg_words_per_minute = 150
    total_words_budget = presentation_duration * avg_words_per_minute
    words_per_slide = total_words_budget // len(slides) if len(slides) > 0 else 100
    
    # Adjust content based on density
    density_multipliers = {"low": 0.6, "medium": 1.0, "high": 1.4}
    actual_words = int(words_per_slide * density_multipliers.get(content_density, 1.0))
    
    # Create audience-specific speaker notes
    audience_styles = {
        "executives": "business impact and strategic value",
        "technical": "implementation details and technical specifications", 
        "general": "key concepts and practical applications",
        "students": "educational context and learning objectives",
        "sales": "customer benefits and competitive advantages"
    }
    
    for slide in slides:
        title = slide.get("fields", {}).get("title", "this slide")
        style = audience_styles.get(target_audience, audience_styles["general"])
        
        if actual_words <= 50:
            notes = f"Brief notes for {title} focusing on {style}."
        elif actual_words <= 100:
            notes = f"Speaker notes for {title}. This slide covers {style}. Key points to emphasize during presentation."
        else:
            notes = f"Comprehensive speaker notes for {title}. This slide focuses on {style}. Include detailed explanations of each point, provide context and background information, and connect to broader presentation themes. Estimated speaking time: {actual_words // 150:.1f} minutes."
            
        slide.setdefault("fields", {})["notes"] = notes

    return {"title": presentation_title, "author": author, "slides": slides}
