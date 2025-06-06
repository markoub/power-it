"""
Fresh Presentations Test Data

These presentations are in their initial state with no steps completed.
Used for testing creation flows, deletion, and initial states.
"""

FRESH_PRESENTATIONS = [
    {
        "id": 1,
        "name": "Fresh Test Presentation 1",
        "topic": "Artificial Intelligence in Healthcare",
        "author": "Test Author",
        "description": "For delete tests - single deletion",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 2,
        "name": "Fresh Test Presentation 2",
        "topic": "Sustainable Energy Solutions",
        "author": "Test Author",
        "description": "For general fresh state tests",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 3,
        "name": "Fresh Test Presentation 3",
        "topic": "Modern Web Development",
        "author": "Test Author",
        "description": "For delete tests - multiple deletion",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 4,
        "name": "Fresh Test Presentation 4",
        "topic": "Data Science Fundamentals",
        "author": "Test Author",
        "description": "For delete tests - multiple deletion",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]