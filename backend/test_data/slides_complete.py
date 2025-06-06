"""
Slides Complete Presentations Test Data

These presentations have completed research and slides steps.
Used for testing illustration generation and slide viewing.
"""

SLIDES_COMPLETE_PRESENTATIONS = [
    {
        "id": 9,
        "name": "Slides Complete Test 1",
        "topic": "Digital Marketing Strategies",
        "author": "Test Author",
        "description": "For illustration tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Digital Marketing Strategies

## Overview
Digital marketing encompasses all marketing efforts that use electronic devices or the internet.

## Key Strategies

### Content Marketing
- Blog posts and articles
- Video content
- Infographics
- Podcasts

### Social Media Marketing
- Platform selection
- Content calendars
- Engagement strategies
- Influencer partnerships

### SEO & SEM
- Keyword research
- On-page optimization
- Link building
- PPC campaigns

### Email Marketing
- List building
- Segmentation
- Automation
- A/B testing""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Digital Marketing Strategies", "content": "Transforming Business in the Digital Age", "type": "welcome"},
                        {"title": "Agenda", "content": "• Introduction to Digital Marketing\n• Content Marketing\n• Social Media Strategies\n• SEO & SEM\n• Email Marketing\n• Analytics & Measurement", "type": "table_of_contents"},
                        {"title": "What is Digital Marketing?", "content": "• Marketing through electronic devices and internet\n• Reaches customers where they spend time\n• Measurable and targeted approach\n• Cost-effective compared to traditional marketing", "type": "content"},
                        {"title": "Content Marketing", "content": "Creating valuable content to attract and retain customers", "type": "section"},
                        {"title": "Content Types", "content": "• Blog posts and articles\n• Video content\n• Infographics\n• Podcasts\n• E-books and whitepapers", "type": "content"},
                        {"title": "Social Media Marketing", "content": "• Choose the right platforms\n• Create engaging content\n• Build community\n• Monitor and respond", "type": "content_with_logos", "logos": ["Facebook", "Twitter", "LinkedIn", "Instagram"]},
                        {"title": "SEO & SEM Strategies", "content": "• Keyword research and optimization\n• Quality content creation\n• Technical SEO\n• Paid search campaigns", "type": "content_image"},
                        {"title": "Email Marketing Excellence", "content": "• Build quality lists\n• Segment your audience\n• Personalize messages\n• Test and optimize", "type": "content"},
                        {"title": "Measuring Success", "content": "• Set clear KPIs\n• Use analytics tools\n• Track conversions\n• Iterate and improve", "type": "content"},
                        {"title": "Thank You", "content": "Questions?", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 10,
        "name": "Slides Complete Test 2",
        "topic": "Remote Work Best Practices",
        "author": "Test Author",
        "description": "For markdown slide tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Remote Work Best Practices

## Overview
Remote work has become increasingly common, requiring new strategies for productivity and collaboration.

## Key Areas

### Communication
- Regular check-ins
- Clear expectations
- Asynchronous communication
- Video conferencing etiquette

### Productivity
- Time management
- Goal setting
- Distraction elimination
- Work-life balance

### Technology
- Collaboration tools
- Security measures
- Hardware setup
- Software requirements""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Remote Work Best Practices", "content": "Succeeding in the Digital Workplace", "type": "welcome"},
                        {"title": "Overview", "content": "• Communication Strategies\n• Productivity Tips\n• Technology Setup\n• Work-Life Balance\n• Team Collaboration", "type": "table_of_contents"},
                        {"title": "Effective Communication", "content": "• Schedule regular check-ins\n• Use video for important discussions\n• Document decisions clearly\n• Respect time zones", "type": "content"},
                        {"title": "Productivity at Home", "content": "• Create dedicated workspace\n• Establish routine\n• Take regular breaks\n• Set clear boundaries", "type": "content_image"},
                        {"title": "Essential Tools", "content": "• Video conferencing\n• Project management\n• File sharing\n• Communication platforms", "type": "content_with_logos", "logos": ["Zoom", "Slack", "Microsoft Teams", "Google Workspace"]},
                        {"title": "Security Considerations", "content": "• Use VPN connections\n• Enable two-factor authentication\n• Keep software updated\n• Follow company policies", "type": "content"},
                        {"title": "Maintaining Balance", "content": "• Set work hours\n• Take lunch breaks\n• Exercise regularly\n• Disconnect after hours", "type": "content"},
                        {"title": "Team Building Remotely", "content": "• Virtual coffee breaks\n• Online team activities\n• Celebrate achievements\n• Foster inclusive culture", "type": "content"},
                        {"title": "Key Takeaways", "content": "• Communication is crucial\n• Structure enables success\n• Technology empowers productivity\n• Balance prevents burnout", "type": "content"},
                        {"title": "Questions?", "content": "Thank you for your attention", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]