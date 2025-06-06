"""
Illustrations Complete Presentations Test Data

These presentations have completed research, slides, and illustrations.
Used for testing PPTX generation and compiled view.
"""

ILLUSTRATIONS_COMPLETE_PRESENTATIONS = [
    {
        "id": 11,
        "name": "Illustrations Complete Test 1",
        "topic": "Cybersecurity Fundamentals",
        "author": "Test Author",
        "description": "For compiled/PPTX tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Cybersecurity Fundamentals

## Overview
Cybersecurity involves protecting systems, networks, and data from digital attacks.

## Key Concepts
- Confidentiality
- Integrity
- Availability
- Authentication
- Authorization""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Cybersecurity Fundamentals", "content": "Protecting Digital Assets", "type": "welcome"},
                        {"title": "Topics", "content": "• Security Principles\n• Common Threats\n• Protection Strategies\n• Best Practices", "type": "table_of_contents"},
                        {"title": "CIA Triad", "content": "• Confidentiality\n• Integrity\n• Availability", "type": "content"},
                        {"title": "Common Threats", "content": "• Malware\n• Phishing\n• Ransomware\n• DDoS attacks", "type": "content_image"},
                        {"title": "Protection Layers", "content": "• Network security\n• Application security\n• Endpoint protection\n• Data encryption", "type": "three_images"},
                        {"title": "Best Practices", "content": "• Strong passwords\n• Regular updates\n• Backup data\n• Security training", "type": "content"},
                        {"title": "Thank You", "content": "Stay Secure!", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {
                        "slide_4": {"url": "/api/images/cyber_threats.png", "alt": "Common cyber threats visualization"},
                        "slide_5": [
                            {"url": "/api/images/network_security.png", "alt": "Network security"},
                            {"url": "/api/images/app_security.png", "alt": "Application security"},
                            {"url": "/api/images/data_encryption.png", "alt": "Data encryption"}
                        ]
                    }
                }
            },
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]