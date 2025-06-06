"""
Fully Complete Presentations Test Data

These presentations have all steps completed.
Used for testing complete presentations, editing, and final outputs.
"""

FULLY_COMPLETE_PRESENTATIONS = [
    {
        "id": 12,
        "name": "Complete Test Presentation 1",
        "topic": "Project Management Best Practices",
        "author": "Test Author",
        "description": "For wizard/editing tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Project Management Best Practices

## Overview
Effective project management is crucial for delivering successful outcomes on time and within budget.

## Key Principles
- Clear objectives
- Stakeholder engagement
- Risk management
- Continuous improvement""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Project Management Best Practices", "content": "Delivering Success", "type": "welcome"},
                        {"title": "Agenda", "content": "• PM Fundamentals\n• Planning Phase\n• Execution\n• Monitoring\n• Closing", "type": "table_of_contents"},
                        {"title": "Project Lifecycle", "content": "• Initiation\n• Planning\n• Execution\n• Monitoring\n• Closing", "type": "content"},
                        {"title": "Planning Excellence", "content": "• Define scope clearly\n• Create realistic timeline\n• Allocate resources\n• Identify risks", "type": "content"},
                        {"title": "Effective Execution", "content": "• Communicate regularly\n• Track progress\n• Manage changes\n• Resolve issues quickly", "type": "content_image"},
                        {"title": "Key Success Factors", "content": "• Strong leadership\n• Team collaboration\n• Stakeholder buy-in\n• Continuous learning", "type": "content"},
                        {"title": "Thank You", "content": "Questions?", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {
                        "slide_5": {"url": "/api/images/project_dashboard.png", "alt": "Project execution dashboard"}
                    }
                }
            },
            {
                "step": "compiled", 
                "status": "completed",
                "result": {"message": "Presentation compiled successfully"}
            },
            {
                "step": "pptx", 
                "status": "completed",
                "result": {"file_path": "/storage/presentations/11/output.pptx"}
            }
        ]
    }
]