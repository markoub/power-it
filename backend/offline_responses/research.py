from models import ResearchData

OFFLINE_RESEARCH_RESPONSE = {
    "title": "Artificial Intelligence in Modern Business",
    "summary": "This presentation explores how AI is transforming business operations, improving efficiency, and creating new opportunities for innovation across multiple industries.",
    "sections": [
        {
            "title": "Introduction to AI in Business",
            "content": [
                "AI is revolutionizing how businesses operate",
                "Companies are using AI to automate tasks, gain insights, and create new products",
                "85% of executives believe AI will significantly change their business model",
            ],
        },
        {
            "title": "Key AI Technologies",
            "content": [
                "Machine Learning algorithms for prediction and pattern recognition",
                "Natural Language Processing for communication and text analysis",
                "Computer Vision for image and video understanding",
                "Robotics and automation for physical tasks",
            ],
        },
        {
            "title": "Business Applications",
            "content": [
                "Customer service: Chatbots and virtual assistants",
                "Marketing: Personalization and targeting",
                "Operations: Predictive maintenance and supply chain optimization",
                "HR: Candidate screening and employee engagement",
                "Finance: Fraud detection and algorithmic trading",
            ],
        },
        {
            "title": "Implementation Challenges",
            "content": [
                "Data quality and availability issues",
                "Integration with legacy systems",
                "Skills gap and training requirements",
                "Ethical considerations and bias",
                "Regulatory compliance",
            ],
        },
        {
            "title": "Success Stories",
            "content": [
                "Amazon: Recommendation engines and logistics optimization",
                "JPMorgan Chase: Contract analysis with AI",
                "Unilever: AI-driven hiring reducing time-to-hire by 90%",
                "Walmart: Inventory management and demand forecasting",
            ],
        },
        {
            "title": "Future Trends",
            "content": [
                "AI democratization through no-code tools",
                "Increased focus on explainable AI",
                "Edge AI for real-time processing",
                "Human-AI collaboration models",
                "Specialized AI for industry-specific applications",
            ],
        },
        {
            "title": "Getting Started",
            "content": [
                "Identify high-value use cases",
                "Start with small, measurable pilot projects",
                "Build cross-functional teams with business and technical expertise",
                "Focus on data strategy and governance",
                "Measure ROI and scale successful initiatives",
            ],
        },
    ],
    "keywords": [
        "Artificial Intelligence",
        "Machine Learning",
        "Business Transformation",
        "Automation",
        "Digital Innovation",
    ],
    "companies": ["Google", "Microsoft", "Amazon", "IBM", "Tesla"],
}

async def get_offline_research(query: str) -> ResearchData:
    """Return a ResearchData object based on the fixed offline response."""
    sections_md = ""
    for section in OFFLINE_RESEARCH_RESPONSE["sections"]:
        sections_md += f"## {section['title']}\n\n"
        for item in section["content"]:
            sections_md += f"- {item}\n"
        sections_md += "\n"
    title = OFFLINE_RESEARCH_RESPONSE["title"]
    content = f"# {title}\n\n{OFFLINE_RESEARCH_RESPONSE['summary']}\n\n{sections_md}"
    return ResearchData(content=content, links=[])
