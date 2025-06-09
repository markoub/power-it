"""
Clarification Testing Presentations Test Data

These presentations are for testing research clarification workflows.
"""

CLARIFICATION_TESTING_PRESENTATIONS = [
    {
        "id": 19,
        "name": "Clarification Test ADK",
        "topic": "Google ADK",
        "author": "Test Author",
        "description": "For testing clarification when topic has ambiguous acronym (ADK)",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 20,
        "name": "Clarification Test Clear Topic", 
        "topic": "Machine Learning in Healthcare",
        "author": "Test Author",
        "description": "For testing when topic is clear and no clarification needed",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 21,
        "name": "Clarification Test SDK",
        "topic": "Google SDK",
        "author": "Test Author", 
        "description": "For testing clarification when topic has ambiguous acronym (SDK)",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]