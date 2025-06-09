"""
Step Status Testing Presentations Test Data

These presentations test different step statuses (pending, processing, error, etc.)
"""

STEP_STATUS_TESTING_PRESENTATIONS = [
    {
        "id": 22,
        "name": "Step Pending Test",
        "topic": "Robotics",
        "author": "Test Author",
        "description": "For step pending tests - all steps pending",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 23,
        "name": "Step Running Test",
        "topic": "Nanotechnology",
        "author": "Test Author",
        "description": "For step running tests - research in progress",
        "steps": [
            {"step": "research", "status": "processing"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 33,
        "name": "Dedicated Step Pending Test",
        "topic": "Renewable Energy Fresh",
        "author": "Test Author", 
        "description": "Dedicated presentation for step pending test - all steps pending",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 24,
        "name": "Step Error Test",
        "topic": "Virtual Reality",
        "author": "Test Author",
        "description": "For step error tests - research failed",
        "steps": [
            {
                "step": "research", 
                "status": "error",
                "error": "Failed to generate research: API timeout"
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 25,
        "name": "Step Mixed Status Test",
        "topic": "Augmented Reality",
        "author": "Test Author",
        "description": "For mixed step status tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Augmented Reality

## Overview
AR overlays digital content on the real world, enhancing our perception of reality.

## Key Technologies
- Computer vision
- SLAM (Simultaneous Localization and Mapping)
- Depth sensing
- Display technologies

## Applications
- Gaming and entertainment
- Education and training
- Healthcare
- Manufacturing
- Retail""",
                    "links": []
                }
            },
            {"step": "slides", "status": "processing"},
            {"step": "illustration", "status": "pending"},
            {
                "step": "compiled", 
                "status": "error",
                "error": "Previous step not completed"
            },
            {"step": "pptx", "status": "pending"},
        ]
    }
]