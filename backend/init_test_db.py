#!/usr/bin/env python3
"""
Test Database Initialization Script

This script creates a test database with pre-seeded presentations in different states
to support E2E testing without having to recreate data for each test.

Test Data Categories:
1. Fresh presentations (for create/delete tests)
2. Presentations with completed research (for slides tests)
3. Presentations with completed slides (for illustration tests)
4. Presentations with completed illustrations (for compiled/pptx tests)
5. Full presentations with all steps completed (for wizard/editing tests)
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

# Test data for different presentation states
TEST_PRESENTATIONS = [
    # Category 1: Fresh presentations (just created, no steps completed)
    {
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
    
    # Category 2: Presentations with completed research (for slides tests)
    {
        "name": "Research Complete Test 1",
        "topic": "Machine Learning Applications",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. Key applications include:\n\n1. Healthcare: Diagnostic imaging, drug discovery, personalized treatment\n2. Finance: Fraud detection, algorithmic trading, risk assessment\n3. Transportation: Autonomous vehicles, route optimization\n4. Technology: Search engines, recommendation systems, natural language processing\n\nML algorithms can be categorized into supervised learning (using labeled data), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error).",
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
        "name": "Research Complete Test 2",
        "topic": "Climate Change Impact",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations occur naturally, scientific evidence shows that human activities have been the main driver since the 1800s.\n\nKey impacts include:\n1. Rising global temperatures\n2. Melting ice caps and glaciers\n3. Sea level rise\n4. Extreme weather events\n5. Ecosystem disruption\n\nMitigation strategies involve reducing greenhouse gas emissions through renewable energy, energy efficiency, and sustainable practices.",
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
        "name": "Research Complete Test 3",
        "topic": "Blockchain Technology",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Blockchain is a distributed ledger technology that maintains a secure and decentralized record of transactions. Originally developed for Bitcoin, blockchain has evolved to support various applications beyond cryptocurrency.\n\nKey features:\n1. Decentralization: No single point of control\n2. Transparency: All transactions are visible to network participants\n3. Immutability: Records cannot be altered once confirmed\n4. Security: Cryptographic protection of data\n\nApplications include smart contracts, supply chain management, digital identity, and decentralized finance (DeFi).",
                    "links": [
                        {"href": "https://example.com/blockchain-intro", "title": "Introduction to Blockchain"},
                        {"href": "https://example.com/blockchain-apps", "title": "Blockchain Applications"}
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
        "name": "Research Complete Test 4",
        "topic": "Quantum Computing",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Quantum computing leverages quantum mechanical phenomena to process information in fundamentally new ways. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits that can exist in superposition.\n\nKey concepts:\n1. Superposition: Qubits can be in multiple states simultaneously\n2. Entanglement: Qubits can be correlated in ways that classical bits cannot\n3. Quantum interference: Amplifying correct answers while canceling wrong ones\n\nPotential applications include cryptography, drug discovery, financial modeling, and optimization problems.",
                    "links": [
                        {"href": "https://example.com/quantum-basics", "title": "Quantum Computing Basics"},
                        {"href": "https://example.com/quantum-future", "title": "Future of Quantum Computing"}
                    ]
                }
            },
            {"step": "slides", "status": "pending"},
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # Category 3: Presentations with completed slides (for illustration tests)
    {
        "name": "Slides Complete Test 1",
        "topic": "Digital Marketing Strategies",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Digital marketing encompasses all marketing efforts that use electronic devices or the internet. Key strategies include SEO, content marketing, social media marketing, email marketing, and PPC advertising.",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "title": "Digital Marketing Strategies",
                    "author": "Test Author",
                    "slides": [
                        {
                            "type": "welcome",
                            "fields": {
                                "title": "Digital Marketing Strategies",
                                "subtitle": "Effective Approaches for Modern Business",
                                "author": "Test Author"
                            }
                        },
                        {
                            "type": "table_of_contents",
                            "fields": {
                                "title": "Table of Contents",
                                "sections": [
                                    "Introduction to Digital Marketing",
                                    "SEO and Content Marketing",
                                    "Social Media Strategies",
                                    "Email Marketing",
                                    "PPC Advertising"
                                ]
                            }
                        },
                        {
                            "type": "section",
                            "fields": {
                                "title": "Introduction to Digital Marketing"
                            }
                        },
                        {
                            "type": "content",
                            "fields": {
                                "title": "What is Digital Marketing?",
                                "content": "Digital marketing encompasses all marketing efforts that use electronic devices or the internet. It allows businesses to connect with customers where they spend their time online."
                            }
                        },
                        {
                            "type": "content_image",
                            "fields": {
                                "title": "Key Digital Channels",
                                "content": "• Search engines\n• Social media platforms\n• Email\n• Websites and blogs\n• Mobile apps",
                                "image": "digital_channels"
                            }
                        }
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # Category 4: Presentations with completed illustrations (for compiled/pptx tests)
    {
        "name": "Illustrations Complete Test 1",
        "topic": "Cybersecurity Fundamentals",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Cybersecurity involves protecting digital information, systems, and networks from digital attacks, unauthorized access, and data breaches.",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "title": "Cybersecurity Fundamentals",
                    "author": "Test Author",
                    "slides": [
                        {
                            "type": "welcome",
                            "fields": {
                                "title": "Cybersecurity Fundamentals",
                                "subtitle": "Protecting Digital Assets",
                                "author": "Test Author"
                            }
                        },
                        {
                            "type": "content_image",
                            "fields": {
                                "title": "Common Threats",
                                "content": "• Malware\n• Phishing\n• Ransomware\n• Data breaches",
                                "image": "cyber_threats"
                            }
                        }
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": [
                        {
                            "slide_index": 1,
                            "slide_title": "Common Threats",
                            "prompt": "Cybersecurity threats visualization with malware, phishing, and ransomware icons",
                            "image_field_name": "image",
                            "image_path": "test_cyber_threats.png"
                        }
                    ]
                }
            },
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    
    # Category 5: Full presentations (all steps completed) for wizard/editing tests
    {
        "name": "Complete Test Presentation 1",
        "topic": "Project Management Best Practices",
        "author": "Test Author",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": "Project management involves planning, executing, and closing projects efficiently. Key methodologies include Agile, Waterfall, and Scrum. Best practices include clear communication, risk management, and stakeholder engagement.",
                    "links": [
                        {"href": "https://example.com/pm-guide", "title": "Project Management Guide"}
                    ]
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "title": "Project Management Best Practices",
                    "author": "Test Author",
                    "slides": [
                        {
                            "type": "welcome",
                            "fields": {
                                "title": "Project Management Best Practices",
                                "subtitle": "Delivering Successful Projects",
                                "author": "Test Author"
                            }
                        },
                        {
                            "type": "content",
                            "fields": {
                                "title": "Key Methodologies",
                                "content": "• Agile: Iterative approach with flexibility\n• Waterfall: Sequential phases\n• Scrum: Framework for complex product development"
                            }
                        },
                        {
                            "type": "content_image",
                            "fields": {
                                "title": "Success Factors",
                                "content": "• Clear objectives\n• Effective communication\n• Risk management\n• Stakeholder engagement",
                                "image": "pm_success"
                            }
                        }
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": [
                        {
                            "slide_index": 2,
                            "slide_title": "Success Factors",
                            "prompt": "Project management success factors with teams collaborating and charts",
                            "image_field_name": "image",
                            "image_path": "test_pm_success.png"
                        }
                    ]
                }
            },
            {
                "step": "compiled", 
                "status": "completed",
                "result": {
                    "title": "Project Management Best Practices",
                    "author": "Test Author",
                    "slides": [
                        {
                            "type": "welcome",
                            "fields": {
                                "title": "Project Management Best Practices",
                                "subtitle": "Delivering Successful Projects",
                                "author": "Test Author"
                            },
                            "image_url": None
                        },
                        {
                            "type": "content",
                            "fields": {
                                "title": "Key Methodologies",
                                "content": "• Agile: Iterative approach with flexibility\n• Waterfall: Sequential phases\n• Scrum: Framework for complex product development"
                            },
                            "image_url": None
                        },
                        {
                            "type": "content_image",
                            "fields": {
                                "title": "Success Factors",
                                "content": "• Clear objectives\n• Effective communication\n• Risk management\n• Stakeholder engagement",
                                "image": "pm_success"
                            },
                            "image_url": "/presentations/5/images/test_pm_success.png"
                        }
                    ]
                }
            },
            {
                "step": "pptx", 
                "status": "completed",
                "result": {
                    "presentation_id": 5,
                    "pptx_filename": "project_management_best_practices.pptx",
                    "pptx_path": "/tmp/test_pptx/project_management_best_practices.pptx",
                    "slide_count": 3,
                    "png_paths": [
                        "/tmp/test_pptx/slide_0.png",
                        "/tmp/test_pptx/slide_1.png",
                        "/tmp/test_pptx/slide_2.png"
                    ]
                }
            },
        ]
    },
    
    # Category 6: Manual research presentations
    {
        "name": "Manual Research Test 1",
        "topic": "User Provided Content",
        "author": "Test Author",
        "steps": [
            {
                "step": "manual_research", 
                "status": "completed",
                "result": {
                    "content": "This is manually provided research content for testing the manual research workflow. It contains custom insights and information provided directly by the user rather than generated by AI.",
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

async def clear_test_database():
    """Clear the test database of all presentations and steps."""
    print("🗑️  Clearing test database...")
    
    async with SessionLocal() as db:
        # Delete all presentations and their steps (cascade will handle steps)
        await db.execute(text("DELETE FROM presentation_steps"))
        await db.execute(text("DELETE FROM presentations"))
        await db.commit()
    
    print("✅ Test database cleared")

async def create_test_presentation(db, presentation_data):
    """Create a single test presentation with its steps."""
    # Create presentation
    presentation = Presentation(
        name=presentation_data["name"],
        topic=presentation_data["topic"],
        author=presentation_data["author"],
        thumbnail_url=None,
        is_deleted=False
    )
    
    db.add(presentation)
    await db.flush()  # Get the ID
    
    # Create steps
    for step_data in presentation_data["steps"]:
        step = PresentationStepModel(
            presentation_id=presentation.id,
            step=step_data["step"],
            status=step_data["status"]
        )
        
        # Set result if provided
        if "result" in step_data:
            step.set_result(step_data["result"])
        
        db.add(step)
    
    await db.commit()
    await db.refresh(presentation)
    
    return presentation

async def seed_test_database():
    """Seed the test database with test presentations."""
    print("🌱 Seeding test database...")
    
    async with SessionLocal() as db:
        created_presentations = []
        
        for i, presentation_data in enumerate(TEST_PRESENTATIONS, 1):
            try:
                presentation = await create_test_presentation(db, presentation_data)
                created_presentations.append(presentation)
                print(f"✅ Created presentation {i}: {presentation.name} (ID: {presentation.id})")
            except Exception as e:
                print(f"❌ Error creating presentation {i}: {e}")
                raise
    
    print(f"🎉 Successfully seeded {len(created_presentations)} test presentations")
    return created_presentations

async def display_test_data_summary():
    """Display a summary of the test data for documentation."""
    print("\n📊 Test Database Summary:")
    print("=" * 50)
    
    async with SessionLocal() as db:
        result = await db.execute(text("""
            SELECT p.id, p.name, p.topic, p.author,
                   GROUP_CONCAT(ps.step || ':' || ps.status) as steps
            FROM presentations p
            LEFT JOIN presentation_steps ps ON p.id = ps.presentation_id
            GROUP BY p.id, p.name, p.topic, p.author
            ORDER BY p.id
        """))
        
        presentations = result.fetchall()
        
        for pres in presentations:
            print(f"\nID {pres[0]}: {pres[1]}")
            print(f"  Topic: {pres[2]}")
            print(f"  Author: {pres[3]}")
            if pres[4]:
                steps = pres[4].split(',')
                print(f"  Steps: {', '.join(steps)}")
    
    print("\n📝 Usage Guide:")
    print("=" * 50)
    print("Fresh presentations (IDs 1-2): For create/delete tests")
    print("Research complete (IDs 3-4): For slides generation tests")
    print("Slides complete (ID 5): For illustration tests")
    print("Illustrations complete (ID 6): For compiled/PPTX tests")
    print("Complete presentation (ID 7): For wizard/editing tests")
    print("Manual research (ID 8): For manual research workflow tests")

async def main():
    """Main function to initialize the test database."""
    print("🚀 Initializing PowerIt Test Database")
    print("=" * 40)
    
    try:
        # Initialize database schema
        await init_db()
        print("✅ Database schema initialized")
        
        # Clear existing test data
        await clear_test_database()
        
        # Seed with test data
        await seed_test_database()
        
        # Display summary
        await display_test_data_summary()
        
        print("\n🎯 Test database is ready!")
        print("Use POWERIT_ENV=test to connect to this database in your tests.")
        
    except Exception as e:
        print(f"❌ Error initializing test database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())