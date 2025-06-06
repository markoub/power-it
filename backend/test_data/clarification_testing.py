"""
Clarification Testing Presentations Test Data

These presentations are for testing research clarification workflows.
"""

CLARIFICATION_TESTING_PRESENTATIONS = [
    {
        "id": 19,
        "name": "Clarification Ready Test",
        "topic": "Artificial Intelligence Ethics",
        "author": "Test Author",
        "description": "For research clarification tests - no method selected",
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
        "name": "Clarification AI Selected",
        "topic": "Smart Cities",
        "author": "Test Author",
        "description": "For AI research clarification tests",
        "ai_research_selected": True,
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
        "name": "Clarification Manual Selected",
        "topic": "Custom Research Topic",
        "author": "Test Author",
        "description": "For manual research clarification tests",
        "manual_research_selected": True,
        "steps": [
            {"step": "manual_research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]