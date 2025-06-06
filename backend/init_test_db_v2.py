#!/usr/bin/env python3
"""
Enhanced Test Database Initialization Script V2

This script creates a comprehensive test database with pre-seeded presentations 
in various states to support ALL E2E tests without requiring new presentation creation.

Test Data Categories:
1. Fresh presentations (for create/delete tests)
2. Presentations with completed research (for slides tests)
3. Presentations with completed slides (for illustration tests)
4. Presentations with completed illustrations (for compiled/pptx tests)
5. Full presentations with all steps completed (for wizard/editing tests)
6. Wizard testing presentations (for wizard context and improvements)
7. Clarification testing presentations (for research clarification)
8. Step status testing presentations (for step navigation and status)
9. Customization testing presentations (for slides customization)
10. Bug fix verification presentations (for testing specific fixes)
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Presentation, PresentationStepModel, init_db, SessionLocal, StepStatus
from sqlalchemy import text

# Comprehensive test data for all E2E test scenarios
TEST_PRESENTATIONS = [
    # ===========================================
    # Category 1: Fresh presentations (ID 1-4)
    # ===========================================
    {
        "id": 1,
        "name": "Fresh Test Presentation 1",
        "topic": "Artificial Intelligence in Healthcare",
        "author": "Test Author",
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
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 2: Research completed (ID 5-8)
    # ===========================================
    {
        "id": 5,
        "name": "Research Complete Test 1",
        "topic": "Machine Learning Applications",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Machine Learning Applications\n\nMachine Learning (ML) is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.\n\n## Key Applications\n\n### 1. Healthcare\n- Diagnostic imaging analysis\n- Drug discovery and development\n- Personalized treatment plans\n- Patient risk prediction\n\n### 2. Finance\n- Fraud detection systems\n- Algorithmic trading\n- Risk assessment models\n- Credit scoring\n\n### 3. Transportation\n- Autonomous vehicles\n- Route optimization\n- Traffic prediction\n- Maintenance forecasting\n\n### 4. Technology\n- Search engines\n- Recommendation systems\n- Natural language processing\n- Computer vision\n\n## Types of Machine Learning\n\nML algorithms can be categorized into:\n- **Supervised Learning**: Using labeled data for training\n- **Unsupervised Learning**: Finding patterns in unlabeled data\n- **Reinforcement Learning**: Learning through trial and error",
                    "links": [
                        {"href": "https://example.com/ml-basics", "title": "Machine Learning Fundamentals"},
                        {"href": "https://example.com/ml-applications", "title": "Real-world ML Applications"}
                    ]
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 6,
        "name": "Research Complete Test 2",
        "topic": "Climate Change Impact",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Climate Change Impact\n\n## Overview\nClimate change represents one of the most pressing challenges of our time, affecting ecosystems, economies, and societies worldwide.\n\n## Key Impacts\n\n### Environmental Effects\n- Rising global temperatures\n- Melting ice caps and glaciers\n- Sea level rise\n- Extreme weather events\n- Ecosystem disruption\n\n### Economic Consequences\n- Agricultural productivity changes\n- Infrastructure damage\n- Energy sector adaptation costs\n- Health care expenses\n- Migration and displacement costs\n\n### Social Implications\n- Food security concerns\n- Water scarcity\n- Public health challenges\n- Climate refugees\n- Inequality exacerbation\n\n## Mitigation Strategies\n- Renewable energy transition\n- Carbon capture technologies\n- Sustainable transportation\n- Forest conservation\n- International cooperation",
                    "links": [
                        {"href": "https://example.com/climate-science", "title": "Climate Science Basics"},
                        {"href": "https://example.com/climate-solutions", "title": "Climate Solutions"}
                    ]
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 7,
        "name": "Research Complete Test 3",
        "topic": "Blockchain Technology",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Blockchain Technology\n\n## Introduction\nBlockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography.\n\n## Key Features\n- **Decentralization**: No single point of control\n- **Transparency**: All transactions are visible\n- **Immutability**: Records cannot be altered retroactively\n- **Security**: Cryptographic protection\n\n## Applications\n\n### Cryptocurrency\n- Bitcoin\n- Ethereum\n- Smart contracts\n\n### Business Applications\n- Supply chain management\n- Digital identity\n- Healthcare records\n- Voting systems\n\n### Financial Services\n- Cross-border payments\n- Securities trading\n- Trade finance\n- Insurance claims\n\n## Challenges\n- Scalability issues\n- Energy consumption\n- Regulatory uncertainty\n- Interoperability",
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
        "id": 8,
        "name": "Research Complete Test 4",
        "topic": "Quantum Computing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Quantum Computing\n\n## Overview\nQuantum computing harnesses quantum mechanical phenomena to process information in fundamentally new ways.\n\n## Key Concepts\n- **Qubits**: Quantum bits that can exist in superposition\n- **Entanglement**: Quantum correlation between particles\n- **Quantum Gates**: Operations on qubits\n- **Quantum Supremacy**: Outperforming classical computers\n\n## Applications\n\n### Cryptography\n- Breaking current encryption\n- Quantum key distribution\n- Post-quantum cryptography\n\n### Drug Discovery\n- Molecular simulation\n- Protein folding\n- Drug interaction modeling\n\n### Optimization\n- Traffic flow optimization\n- Financial portfolio optimization\n- Supply chain management\n\n### Machine Learning\n- Quantum neural networks\n- Feature mapping\n- Optimization algorithms\n\n## Current Limitations\n- Quantum decoherence\n- Error rates\n- Limited qubit count\n- Extreme cooling requirements",
                    "links": []
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 3: Slides completed (ID 9-10)
    # ===========================================
    {
        "id": 9,
        "name": "Slides Complete Test 1",
        "topic": "Digital Marketing Strategies",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Digital Marketing Strategies\n\n## Overview\nDigital marketing encompasses all marketing efforts that use electronic devices or the internet.\n\n## Key Strategies\n\n### Content Marketing\n- Blog posts and articles\n- Video content\n- Infographics\n- Podcasts\n\n### Social Media Marketing\n- Platform selection\n- Content calendars\n- Engagement strategies\n- Influencer partnerships\n\n### SEO & SEM\n- Keyword research\n- On-page optimization\n- Link building\n- PPC campaigns\n\n### Email Marketing\n- List building\n- Segmentation\n- Automation\n- A/B testing",
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
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Remote Work Best Practices\n\n## Overview\nRemote work has become increasingly common, requiring new strategies for productivity and collaboration.\n\n## Key Areas\n\n### Communication\n- Regular check-ins\n- Clear expectations\n- Asynchronous communication\n- Video conferencing etiquette\n\n### Productivity\n- Time management\n- Goal setting\n- Distraction elimination\n- Work-life balance\n\n### Technology\n- Collaboration tools\n- Security measures\n- Hardware setup\n- Software requirements",
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
    },
    
    # ===========================================
    # Category 4: Illustrations completed (ID 11-12)
    # ===========================================
    {
        "id": 11,
        "name": "Illustrations Complete Test 1",
        "topic": "Cybersecurity Fundamentals",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Cybersecurity Fundamentals\n\n## Overview\nCybersecurity involves protecting systems, networks, and data from digital attacks.\n\n## Key Concepts\n- Confidentiality\n- Integrity\n- Availability\n- Authentication\n- Authorization",
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
    },
    {
        "id": 12,
        "name": "Illustrations Complete Test 2",
        "topic": "Healthy Living Tips",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Healthy Living Tips\n\n## Overview\nHealthy living encompasses physical, mental, and social well-being.\n\n## Key Areas\n- Nutrition\n- Exercise\n- Sleep\n- Stress Management\n- Social Connections",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Healthy Living Tips", "content": "Your Guide to Wellness", "type": "welcome"},
                        {"title": "Topics", "content": "• Nutrition\n• Exercise\n• Sleep\n• Mental Health\n• Social Wellness", "type": "table_of_contents"},
                        {"title": "Balanced Nutrition", "content": "• Eat variety of foods\n• Control portions\n• Stay hydrated\n• Limit processed foods", "type": "content_image"},
                        {"title": "Regular Exercise", "content": "• 150 minutes weekly\n• Mix cardio and strength\n• Find activities you enjoy\n• Start gradually", "type": "content"},
                        {"title": "Quality Sleep", "content": "• 7-9 hours nightly\n• Consistent schedule\n• Dark, cool room\n• Limit screens before bed", "type": "content_image"},
                        {"title": "Mental Wellness", "content": "• Practice mindfulness\n• Manage stress\n• Seek support\n• Express gratitude", "type": "content"},
                        {"title": "Stay Healthy!", "content": "Small changes, big impact", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {
                        "slide_3": {"url": "/api/images/nutrition_pyramid.png", "alt": "Balanced nutrition guide"},
                        "slide_5": {"url": "/api/images/sleep_cycle.png", "alt": "Healthy sleep patterns"}
                    }
                }
            },
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 5: Fully completed (ID 13-14)
    # ===========================================
    {
        "id": 13,
        "name": "Complete Test Presentation 1",
        "topic": "Project Management Best Practices",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Project Management Best Practices\n\n## Overview\nEffective project management is crucial for delivering successful outcomes on time and within budget.\n\n## Key Principles\n- Clear objectives\n- Stakeholder engagement\n- Risk management\n- Continuous improvement",
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
                "result": {"file_path": "/storage/presentations/13/output.pptx"}
            }
        ]
    },
    {
        "id": 14,
        "name": "Complete Test Presentation 2",
        "topic": "Future of Education",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Future of Education\n\n## Overview\nEducation is evolving rapidly with technology and changing societal needs.\n\n## Key Trends\n- Online learning\n- Personalized education\n- Skills-based learning\n- Lifelong learning",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "The Future of Education", "content": "Transforming How We Learn", "type": "welcome"},
                        {"title": "Topics", "content": "• Current Challenges\n• Emerging Technologies\n• New Models\n• Future Vision", "type": "table_of_contents"},
                        {"title": "Education Today", "content": "• One-size-fits-all approach\n• Limited accessibility\n• Skills gap\n• High costs", "type": "content"},
                        {"title": "Technology Integration", "content": "• AI-powered tutoring\n• Virtual reality\n• Blockchain credentials\n• Adaptive learning", "type": "content_image"},
                        {"title": "New Learning Models", "content": "• Microlearning\n• Competency-based\n• Project-based\n• Peer-to-peer", "type": "content"},
                        {"title": "Vision 2030", "content": "• Accessible to all\n• Personalized paths\n• Continuous learning\n• Global collaboration", "type": "image_full"},
                        {"title": "Join the Revolution", "content": "The future of learning is here", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {
                        "slide_4": {"url": "/api/images/edtech_tools.png", "alt": "Educational technology tools"},
                        "slide_6": {"url": "/api/images/future_classroom.png", "alt": "Vision of future education"}
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
                "result": {"file_path": "/storage/presentations/14/output.pptx"}
            }
        ]
    },
    
    # ===========================================
    # Category 6: Manual research (ID 15)
    # ===========================================
    {
        "id": 15,
        "name": "Manual Research Test 1",
        "topic": "User Provided Content",
        "author": "Test Author",
        "steps": [
            {
                "step": "manual_research", 
                "status": "completed",
                "result": {
                    "content": "This is manually provided research content for testing purposes. It includes custom information that the user has gathered from their own sources.\n\nKey Points:\n- Custom data point 1\n- Custom data point 2\n- Custom data point 3\n\nThis content is used to test the manual research workflow where users provide their own content instead of using AI generation."
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 7: Wizard testing (ID 16-20)
    # ===========================================
    {
        "id": 16,
        "name": "Wizard Fresh Test",
        "topic": "Space Exploration",
        "author": "Test Author",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 17,
        "name": "Wizard Research Ready",
        "topic": "Renewable Energy",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Renewable Energy\n\n## Overview\nRenewable energy comes from natural sources that are constantly replenished.\n\n## Types\n- Solar power\n- Wind energy\n- Hydroelectric\n- Geothermal\n- Biomass",
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
        "id": 18,
        "name": "Wizard Slides Ready",
        "topic": "Mobile App Development",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Mobile App Development\n\n## Overview\nMobile app development involves creating software applications for mobile devices.\n\n## Platforms\n- iOS\n- Android\n- Cross-platform",
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
        "id": 19,
        "name": "Wizard Complete Test",
        "topic": "Digital Transformation",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Digital Transformation\n\n## Overview\nDigital transformation is the integration of digital technology into all areas of business.\n\n## Key Areas\n- Customer experience\n- Operational processes\n- Business models\n- Company culture",
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
                "result": {"file_path": "/storage/presentations/19/output.pptx"}
            }
        ]
    },
    {
        "id": 20,
        "name": "Wizard Context Test",
        "topic": "5G Technology",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# 5G Technology\n\n## Overview\n5G is the fifth generation of cellular network technology.\n\n## Benefits\n- Ultra-fast speeds\n- Low latency\n- Massive connectivity\n- Energy efficiency",
                    "links": []
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 8: Clarification testing (ID 21-23)
    # ===========================================
    {
        "id": 21,
        "name": "Clarification Ready Test",
        "topic": "Artificial Intelligence Ethics",
        "author": "Test Author",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 22,
        "name": "Clarification AI Selected",
        "topic": "Smart Cities",
        "author": "Test Author",
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
        "id": 23,
        "name": "Clarification Manual Selected",
        "topic": "Custom Research Topic",
        "author": "Test Author",
        "manual_research_selected": True,
        "steps": [
            {"step": "manual_research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 9: Step status testing (ID 24-27)
    # ===========================================
    {
        "id": 24,
        "name": "Step Pending Test",
        "topic": "Robotics",
        "author": "Test Author",
        "steps": [
            {"step": "research", "status": "pending"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 25,
        "name": "Step Running Test",
        "topic": "Nanotechnology",
        "author": "Test Author",
        "steps": [
            {"step": "research", "status": "processing"},
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 26,
        "name": "Step Error Test",
        "topic": "Virtual Reality",
        "author": "Test Author",
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
        "id": 27,
        "name": "Step Mixed Status Test",
        "topic": "Augmented Reality",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {"content": "# Augmented Reality\n\nAR overlays digital content on the real world."}
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
    },
    
    # ===========================================
    # Category 10: Customization testing (ID 28-30)
    # ===========================================
    {
        "id": 28,
        "name": "Slides Customization Test",
        "topic": "Social Media Strategy",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Social Media Strategy\n\n## Overview\nSocial media strategy involves planning and executing content across social platforms.\n\n## Key Elements\n- Content planning\n- Audience targeting\n- Engagement tactics\n- Performance metrics",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Social Media Strategy", "content": "Engaging Your Audience", "type": "welcome"},
                        {"title": "Topics", "content": "• Platform Selection\n• Content Strategy\n• Engagement\n• Analytics", "type": "table_of_contents"},
                        {"title": "Choose Your Platforms", "content": "• Know your audience\n• Focus on 2-3 platforms\n• Quality over quantity\n• Platform-specific content", "type": "content"},
                        {"title": "Content That Connects", "content": "• Tell stories\n• Use visuals\n• Be authentic\n• Add value", "type": "content_image"},
                        {"title": "Engagement Strategies", "content": "• Respond quickly\n• Ask questions\n• Run contests\n• User-generated content", "type": "content"},
                        {"title": "Measure Success", "content": "• Track engagement rate\n• Monitor reach\n• Analyze conversions\n• Adjust strategy", "type": "content"},
                        {"title": "Let's Connect!", "content": "Questions?", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 29,
        "name": "PPTX Debug Test",
        "topic": "Cloud Computing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Cloud Computing\n\n## Overview\nCloud computing delivers computing services over the internet.",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Cloud Computing", "content": "The Future of IT", "type": "welcome"},
                        {"title": "Overview", "content": "• What is Cloud?\n• Service Models\n• Benefits\n• Challenges", "type": "table_of_contents"},
                        {"title": "Service Models", "content": "• IaaS - Infrastructure\n• PaaS - Platform\n• SaaS - Software", "type": "content"},
                        {"title": "Key Benefits", "content": "• Scalability\n• Cost efficiency\n• Flexibility\n• Innovation", "type": "content"},
                        {"title": "Thank You", "content": "Embrace the cloud!", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {"images": {}}
            },
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 30,
        "name": "Quick Test Presentation",
        "topic": "Quick Testing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Quick Testing\n\nThis is a minimal presentation for quick testing purposes.",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Quick Test", "content": "Testing 123", "type": "welcome"},
                        {"title": "Content", "content": "• Point 1\n• Point 2\n• Point 3", "type": "content"},
                        {"title": "End", "content": "Done", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # ===========================================
    # Category 11: Bug fix verification (ID 31-35)
    # ===========================================
    {
        "id": 31,
        "name": "Fix Verification Test 1",
        "topic": "Edge Case Testing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Edge Case Testing\n\n## Special Characters\nTesting with special characters: & < > \" ' \n\n## Unicode\nTesting with unicode: 🚀 🎯 ✨\n\n## Long Content\n" + ("This is a very long line of content that should test text wrapping and overflow handling. " * 10),
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
        "id": 32,
        "name": "Fix Verification Test 2",
        "topic": "Empty Content Testing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "",
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
        "id": 33,
        "name": "Fix Verification Test 3",
        "topic": "Markdown Edge Cases",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Heading 1\n## Heading 2\n### Heading 3\n#### Heading 4\n##### Heading 5\n###### Heading 6\n\n**Bold** *Italic* ***Bold Italic***\n\n- List item 1\n  - Nested item 1.1\n  - Nested item 1.2\n- List item 2\n\n1. Numbered item 1\n2. Numbered item 2\n   1. Nested numbered 2.1\n   2. Nested numbered 2.2\n\n> Blockquote\n> Multiple lines\n\n`inline code`\n\n```python\ndef hello():\n    print('Hello, World!')\n```\n\n[Link](https://example.com)\n\n---\n\nHorizontal rule above",
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
        "id": 34,
        "name": "Research Apply Fix Test",
        "topic": "Testing Research Updates",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Original Research Content\n\nThis content should be updatable through the wizard.",
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
        "id": 35,
        "name": "Navigation Fix Test",
        "topic": "Step Navigation Testing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "# Navigation Test\n\nTesting step navigation and status updates.",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Navigation Test", "content": "Testing", "type": "welcome"},
                        {"title": "Content", "content": "Test content", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]

async def init_test_database():
    """Initialize the test database with comprehensive test data"""
    print("🚀 Initializing Enhanced PowerIt Test Database V2")
    print("=" * 50)
    
    # Initialize database schema
    init_db()
    print("✅ Database schema initialized")
    
    # Clear existing data
    with SessionLocal() as db:
        db.execute(text("DELETE FROM presentation_steps"))
        db.execute(text("DELETE FROM presentations"))
        db.commit()
        print("🗑️  Cleared existing test data")
    
    # Seed test presentations
    print("🌱 Seeding comprehensive test database...")
    
    with SessionLocal() as db:
        for pres_data in TEST_PRESENTATIONS:
            # Create presentation with specific ID
            presentation = Presentation(
                id=pres_data["id"],
                name=pres_data["name"],
                topic=pres_data["topic"],
                author=pres_data["author"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(presentation)
            db.flush()  # Get the ID
            
            # Add steps
            for step_data in pres_data["steps"]:
                step = PresentationStepModel(
                    presentation_id=presentation.id,
                    step=step_data["step"],
                    status=StepStatus(step_data["status"]),
                    result=json.dumps(step_data.get("result", {})) if step_data.get("result") else None,
                    error=step_data.get("error"),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(step)
            
            db.commit()
            print(f"✅ Created presentation {presentation.id}: {presentation.name}")
    
    print(f"\n🎉 Successfully seeded {len(TEST_PRESENTATIONS)} test presentations")
    
    # Print summary
    print("\n📊 Test Database Summary:")
    print("=" * 50)
    categories = {
        "Fresh": list(range(1, 5)),
        "Research Complete": list(range(5, 9)),
        "Slides Complete": list(range(9, 11)),
        "Illustrations Complete": list(range(11, 13)),
        "Fully Complete": list(range(13, 15)),
        "Manual Research": [15],
        "Wizard Testing": list(range(16, 21)),
        "Clarification Testing": list(range(21, 24)),
        "Step Status Testing": list(range(24, 28)),
        "Customization Testing": list(range(28, 31)),
        "Bug Fix Verification": list(range(31, 36))
    }
    
    for category, ids in categories.items():
        print(f"\n{category} (IDs {ids[0]}-{ids[-1]}):")
        for id in ids:
            pres = next((p for p in TEST_PRESENTATIONS if p["id"] == id), None)
            if pres:
                print(f"  ID {id}: {pres['name']}")
    
    print("\n🎯 Test database is ready for comprehensive E2E testing!")
    print("All tests can now use preseeded data without creating new presentations.")

if __name__ == "__main__":
    asyncio.run(init_test_database())