"""
Wizard Testing Presentations Test Data

These presentations are specifically designed for testing wizard functionality.
Different states to test wizard context awareness and improvements.
"""

WIZARD_TESTING_PRESENTATIONS = [
    {
        "id": 14,
        "name": "Wizard Fresh Test",
        "topic": "Space Exploration",
        "author": "Test Author",
        "description": "For wizard general context tests",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 15,
        "name": "Wizard Research Ready",
        "topic": "Renewable Energy",
        "author": "Test Author",
        "description": "For wizard research context tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Renewable Energy

## Overview
Renewable energy comes from natural sources that are constantly replenished.

## Types of Renewable Energy

### Solar Power
- Photovoltaic cells convert sunlight to electricity
- Solar thermal systems for heating
- Concentrated solar power plants
- Residential and commercial applications

### Wind Energy
- Onshore wind farms
- Offshore wind installations
- Small-scale wind turbines
- Wind energy storage solutions

### Hydroelectric Power
- Large-scale dams
- Run-of-river systems
- Tidal power generation
- Wave energy converters

### Other Sources
- Geothermal energy
- Biomass and biofuels
- Hydrogen fuel cells
- Nuclear fusion (future)

## Benefits
- Reduced carbon emissions
- Energy independence
- Job creation
- Long-term cost savings""",
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
        "id": 16,
        "name": "Wizard Slides Ready",
        "topic": "Mobile App Development",
        "author": "Test Author",
        "description": "For wizard slides context tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Mobile App Development

## Overview
Mobile app development involves creating software applications for mobile devices.

## Platforms
- iOS (iPhone, iPad)
- Android
- Cross-platform solutions

## Development Approaches
- Native development
- Hybrid applications
- Progressive Web Apps
- Cross-platform frameworks""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Mobile App Development", "content": "Building the Future", "type": "welcome"},
                        {"title": "Overview", "content": "• Platforms\n• Development Process\n• Tools\n• Best Practices", "type": "table_of_contents"},
                        {"title": "Platform Choice", "content": "• iOS - Swift/Objective-C\n• Android - Kotlin/Java\n• Cross-platform - React Native/Flutter", "type": "content"},
                        {"title": "Development Process", "content": "• Planning\n• Design\n• Development\n• Testing\n• Deployment", "type": "content"},
                        {"title": "Essential Tools", "content": "• IDEs\n• Version control\n• Testing frameworks\n• Analytics", "type": "content_with_logos", "logos": ["Xcode", "Android Studio", "Git", "Firebase"]},
                        {"title": "Best Practices", "content": "• User-centric design\n• Performance optimization\n• Security first\n• Regular updates", "type": "content"},
                        {"title": "Thank You", "content": "Happy coding!", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 17,
        "name": "Wizard Complete Test",
        "topic": "Digital Transformation",
        "author": "Test Author",
        "description": "For wizard improvements tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Digital Transformation

## Overview
Digital transformation is the integration of digital technology into all areas of business.

## Key Areas
- Customer experience
- Operational processes
- Business models
- Company culture""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Digital Transformation", "content": "Reshaping Business", "type": "welcome"},
                        {"title": "Agenda", "content": "• What is DX?\n• Key Drivers\n• Implementation\n• Success Factors", "type": "table_of_contents"},
                        {"title": "Understanding DX", "content": "• Technology integration\n• Process optimization\n• Cultural change\n• Customer focus", "type": "content"},
                        {"title": "Key Technologies", "content": "• Cloud computing\n• AI and ML\n• IoT\n• Big Data", "type": "content_image"},
                        {"title": "Implementation Steps", "content": "• Assess current state\n• Define vision\n• Create roadmap\n• Execute and iterate", "type": "content"},
                        {"title": "Success Factors", "content": "• Leadership commitment\n• Employee engagement\n• Customer centricity\n• Agile approach", "type": "content"},
                        {"title": "Thank You", "content": "Transform today!", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {
                        "slide_4": {"url": "/api/images/dx_technologies.png", "alt": "Digital transformation technologies"}
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
                "result": {"file_path": "/storage/presentations/17/output.pptx"}
            }
        ]
    },
    {
        "id": 18,
        "name": "Wizard Context Test",
        "topic": "5G Technology",
        "author": "Test Author",
        "description": "For basic wizard tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# 5G Technology

## Overview
5G is the fifth generation of cellular network technology.

## Key Features
- Ultra-fast speeds (up to 10 Gbps)
- Low latency (1ms)
- Massive device connectivity
- Network slicing capabilities

## Benefits
- Enhanced mobile broadband
- IoT at scale
- Mission-critical services
- Fixed wireless access

## Applications
- Smart cities
- Autonomous vehicles
- Remote surgery
- Virtual reality
- Industrial automation""",
                    "links": []
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]