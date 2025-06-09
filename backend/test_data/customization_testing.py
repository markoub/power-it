"""
Customization Testing Presentations Test Data

These presentations test slides customization and PPTX generation features.
Different slide types and customization scenarios.
"""

CUSTOMIZATION_TESTING_PRESENTATIONS = [
    {
        "id": 26,
        "name": "Slide Customization Test",
        "topic": "Business Strategy",
        "author": "Test Author",
        "description": "For testing slide customization features - research ready",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Business Strategy

## Executive Summary
Modern business strategy requires agility, innovation, and customer focus.

## Strategic Planning
- Vision and mission alignment
- Market analysis
- Competitive positioning
- Resource allocation

## Key Success Factors
- Customer centricity
- Digital transformation
- Operational excellence
- Talent management

## Implementation
- Strategic initiatives
- KPIs and metrics
- Change management
- Continuous improvement""",
                    "links": []
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 27,
        "name": "PPTX Generation Test",
        "topic": "Education Technology",
        "author": "Test Author",
        "description": "For testing PPTX export features",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Education Technology

## Overview
EdTech is transforming how we learn and teach in the digital age.

## Key Trends
- Online learning platforms
- AI-powered personalization
- Virtual classrooms
- Gamification

## Benefits
- Accessibility
- Flexibility
- Cost-effectiveness
- Data-driven insights""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Education Technology", "content": "Learning Reimagined", "type": "welcome"},
                        {"title": "Contents", "content": "• EdTech Overview\n• Current Trends\n• Case Studies\n• Future Vision", "type": "table_of_contents"},
                        {"title": "Digital Learning", "content": "• E-learning platforms\n• Mobile education\n• Cloud-based systems\n• Analytics dashboards", "type": "content"},
                        {"title": "AI in Education", "content": "• Personalized learning paths\n• Intelligent tutoring\n• Automated grading\n• Predictive analytics", "type": "content"},
                        {"title": "Thank You", "content": "The future of learning is here", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {}
                }
            },
            {
                "step": "compiled", 
                "status": "completed",
                "result": {"message": "Presentation compiled successfully"}
            },
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 28,
        "name": "Template Styles Test",
        "topic": "Design Systems",
        "author": "Test Author",
        "description": "For testing different template styles",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Design Systems

## What is a Design System?
A collection of reusable components and guidelines.

## Components
- UI elements
- Typography
- Color palette
- Spacing system

## Benefits
- Consistency
- Efficiency
- Scalability
- Collaboration""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Design Systems", "content": "Building Consistency at Scale", "type": "welcome"},
                        {"title": "Overview", "content": "• Introduction\n• Core Components\n• Implementation\n• Best Practices", "type": "table_of_contents"},
                        {"title": "Component Library", "content": "• Buttons\n• Forms\n• Cards\n• Navigation", "type": "content"},
                        {"title": "Visual Language", "content": "Typography, colors, and spacing", "type": "section"},
                        {"title": "Design Tokens", "content": "• Primary colors\n• Secondary colors\n• Typography scale\n• Spacing units", "type": "content"},
                        {"title": "Thank You", "content": "Design with purpose", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]