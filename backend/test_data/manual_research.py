"""
Manual Research Presentations Test Data

These presentations use manual research workflow.
Used for testing manual research input and processing.
"""

MANUAL_RESEARCH_PRESENTATIONS = [
    {
        "id": 13,
        "name": "Manual Research Test 1",
        "topic": "User Provided Content",
        "author": "Test Author",
        "description": "For manual research workflow tests",
        "steps": [
            {
                "step": "manual_research", 
                "status": "completed",
                "result": {
                    "content": """This is manually provided research content for testing purposes. It includes custom information that the user has gathered from their own sources.

Key Points:
- Custom data point 1
- Custom data point 2
- Custom data point 3

This content is used to test the manual research workflow where users provide their own content instead of using AI generation."""
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]