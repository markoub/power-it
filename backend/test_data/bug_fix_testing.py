"""
Bug Fix Testing Presentations Test Data

These presentations test specific bug fixes and edge cases.
Designed to ensure regression tests for previously identified issues.
"""

BUG_FIX_TESTING_PRESENTATIONS = [
    {
        "id": 29,
        "name": "Empty Images Bug Test",
        "topic": "Healthcare Innovation",
        "author": "Test Author",
        "description": "For testing empty images handling",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Healthcare Innovation

## Digital Health Revolution
Technology is transforming healthcare delivery and patient outcomes.

## Key Innovations
- Telemedicine
- AI diagnostics
- Wearable devices
- Electronic health records

## Impact
- Improved accessibility
- Better patient outcomes
- Cost reduction
- Personalized medicine""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Healthcare Innovation", "content": "Transforming Patient Care", "type": "welcome"},
                        {"title": "Topics", "content": "• Digital Health\n• AI in Medicine\n• Patient Experience\n• Future Trends", "type": "table_of_contents"},
                        {"title": "Telemedicine", "content": "• Remote consultations\n• Virtual care\n• Remote monitoring\n• Digital prescriptions", "type": "content_image"},
                        {"title": "AI Diagnostics", "content": "• Image analysis\n• Predictive analytics\n• Treatment recommendations\n• Drug discovery", "type": "content"},
                        {"title": "Thank You", "content": "Health is wealth", "type": "content"}
                    ]
                }
            },
            {
                "step": "illustration", 
                "status": "completed",
                "result": {
                    "images": {}  # Empty images object to test handling
                }
            },
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 30,
        "name": "Special Characters Test",
        "topic": "Fintech & Banking",
        "author": "Test Author",
        "description": "For testing special characters in content",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Fintech & Banking

## Overview
Financial technology is disrupting traditional banking with innovative solutions.

## Key Areas
- Mobile payments ($100B+ market)
- Blockchain & cryptocurrencies
- P2P lending
- Robo-advisors

## Market Stats
- 80% of banks investing in fintech
- <50ms transaction speeds
- 24/7 availability
- "Zero-fee" banking models""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Fintech & Banking", "content": "The Future of Finance", "type": "welcome"},
                        {"title": "Overview", "content": "• Market Trends\n• Technologies\n• Use Cases\n• ROI & Benefits", "type": "table_of_contents"},
                        {"title": "Payment Revolution", "content": "• $1T+ digital payments\n• <1s processing\n• 99.9% uptime\n• \"Contactless\" everywhere", "type": "content"},
                        {"title": "Blockchain Impact", "content": "• Smart contracts\n• DeFi protocols\n• NFTs & tokenization\n• Cross-border payments", "type": "content"},
                        {"title": "Thank You!", "content": "Questions & Answers", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    },
    {
        "id": 31,
        "name": "Long Content Test",
        "topic": "Environmental Sustainability",
        "author": "Test Author",
        "description": "For testing long content handling",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Environmental Sustainability

## Introduction
Environmental sustainability is one of the most critical challenges facing humanity today. It encompasses the responsible interaction with the environment to avoid depletion or degradation of natural resources and allow for long-term environmental quality. The practice of environmental sustainability helps to ensure that the needs of today's population are met without jeopardizing the ability of future generations to meet their own needs.

## Climate Change and Global Warming
Climate change represents one of the most pressing environmental challenges of our time. The Earth's climate is warming at an unprecedented rate due to human activities, particularly the emission of greenhouse gases such as carbon dioxide, methane, and nitrous oxide. These emissions come from various sources including burning fossil fuels for electricity, heat, and transportation, deforestation, industrial processes, and agricultural practices.

The consequences of climate change are far-reaching and include rising global temperatures, melting ice caps and glaciers, rising sea levels, more frequent and severe weather events, changes in precipitation patterns, and disruptions to ecosystems and biodiversity. These changes pose significant risks to human health, food security, water resources, and economic stability.

## Renewable Energy Solutions
The transition to renewable energy sources is crucial for achieving environmental sustainability. Renewable energy comes from natural sources that are constantly replenished, such as sunlight, wind, rain, tides, waves, and geothermal heat. Unlike fossil fuels, renewable energy sources produce little to no greenhouse gas emissions during operation.

Solar power harnesses energy from the sun using photovoltaic cells or concentrated solar power systems. Wind energy captures the kinetic energy of moving air using wind turbines. Hydroelectric power generates electricity from flowing water. Geothermal energy taps into the Earth's internal heat. Biomass energy comes from organic materials. Each of these technologies has unique advantages and challenges, but collectively they offer a path toward a sustainable energy future.

## Sustainable Agriculture and Food Systems
Agriculture has a significant impact on the environment, accounting for approximately 24% of global greenhouse gas emissions. Sustainable agriculture practices aim to meet society's food and textile needs while minimizing environmental impact and maintaining economic viability for farmers.

Key sustainable agriculture practices include crop rotation, cover cropping, reduced tillage, integrated pest management, precision agriculture, agroforestry, and organic farming. These practices help to maintain soil health, reduce water usage, minimize chemical inputs, preserve biodiversity, and sequester carbon in the soil.

## Circular Economy and Waste Management
The circular economy represents a shift from the traditional linear "take-make-dispose" model to one that keeps resources in use for as long as possible, extracts maximum value from them while in use, and recovers and regenerates products and materials at the end of their service life.

This approach involves designing products for durability, repairability, and recyclability; promoting sharing and collaborative consumption models; implementing effective recycling and composting programs; and developing new business models that incentivize resource efficiency. The circular economy not only reduces environmental impact but also creates economic opportunities and jobs.

## Water Conservation and Management
Water is a precious and finite resource that is essential for life. With growing populations, urbanization, and climate change, water scarcity is becoming an increasingly serious global challenge. Sustainable water management involves using water efficiently, protecting water quality, and ensuring equitable access to water resources.

Water conservation strategies include implementing water-efficient technologies and practices in homes, businesses, and agriculture; protecting and restoring watersheds and wetlands; treating and reusing wastewater; harvesting rainwater; and developing drought-resistant crops. Integrated water resource management approaches consider the entire water cycle and balance the needs of different users and ecosystems.

## Biodiversity Conservation
Biodiversity—the variety of life on Earth—is essential for ecosystem functioning and human well-being. However, biodiversity is declining at an alarming rate due to habitat loss, pollution, climate change, overexploitation, and invasive species. Conservation efforts are crucial to protect and restore biodiversity.

Conservation strategies include establishing and managing protected areas, restoring degraded ecosystems, implementing sustainable land-use practices, combating wildlife trafficking, managing invasive species, and integrating biodiversity considerations into development planning. Community-based conservation approaches that involve and benefit local people are often the most effective.

## Corporate Sustainability and ESG
Businesses play a crucial role in achieving environmental sustainability. Corporate sustainability involves integrating environmental, social, and governance (ESG) considerations into business operations and decision-making. This includes reducing carbon emissions, minimizing waste, using resources efficiently, ensuring responsible supply chains, and transparently reporting on sustainability performance.

Many companies are setting science-based targets for emissions reduction, investing in renewable energy, implementing circular economy principles, and developing sustainable products and services. Investors are increasingly considering ESG factors in their investment decisions, recognizing that sustainable businesses are often more resilient and profitable in the long term.

## Individual Actions and Lifestyle Changes
While systemic changes are necessary for achieving environmental sustainability, individual actions also matter. Personal choices regarding consumption, transportation, energy use, and lifestyle can collectively make a significant impact.

Individuals can contribute to sustainability by reducing energy consumption, choosing renewable energy, using public transportation or electric vehicles, eating less meat, reducing food waste, buying local and sustainable products, recycling and composting, conserving water, and supporting businesses and policies that prioritize sustainability. Education and awareness are key to empowering individuals to make informed choices.

## Policy and Governance
Effective policies and governance structures are essential for driving the transition to environmental sustainability. This includes international agreements like the Paris Climate Agreement, national legislation and regulations, carbon pricing mechanisms, subsidies for renewable energy, standards for energy efficiency and emissions, and investments in green infrastructure.

Multi-stakeholder collaboration involving governments, businesses, civil society, and individuals is necessary to develop and implement effective sustainability policies. Transparency, accountability, and evidence-based decision-making are crucial for ensuring that policies achieve their intended outcomes.

## Conclusion
Environmental sustainability is not just an option but a necessity for the survival and prosperity of current and future generations. It requires fundamental changes in how we produce and consume energy, grow food, manage resources, and organize our societies. While the challenges are significant, the solutions exist, and the benefits of action far outweigh the costs of inaction. By working together and taking decisive action now, we can create a sustainable, equitable, and prosperous future for all.""",
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
        "name": "Unicode Content Test",
        "topic": "Global Languages",
        "author": "Test Author",
        "description": "For testing Unicode and multilingual content",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Global Languages 🌍

## Language Diversity
The world speaks over 7,000 languages, each with unique characteristics.

## Major Language Families
- Indo-European (English, español, हिन्दी, русский)
- Sino-Tibetan (中文, བོད་ཡིག)
- Afro-Asiatic (العربية, עברית)
- Niger-Congo (Swahili, Yorùbá)
- Austronesian (Bahasa, Tagalog)

## Writing Systems
- Latin: A, B, C
- Cyrillic: А, Б, В
- Arabic: ا, ب, ت
- Chinese: 你好
- Japanese: こんにちは
- Korean: 안녕하세요
- Emoji: 😀 🎉 ❤️

## Mathematical Symbols
- Greek letters: α, β, γ, δ, π, Σ
- Math operators: ∑, ∏, ∫, ∂, ∞
- Special symbols: ©, ®, ™, €, £, ¥""",
                    "links": []
                }
            },
            {
                "step": "slides", 
                "status": "completed",
                "result": {
                    "slides": [
                        {"title": "Global Languages 🌍", "content": "Unity in Diversity", "type": "welcome"},
                        {"title": "Agenda", "content": "• Language Families\n• Writing Systems\n• Digital Communication\n• Future of Languages", "type": "table_of_contents"},
                        {"title": "Hello World! 👋", "content": "• English: Hello\n• Español: Hola\n• 中文: 你好\n• العربية: مرحبا\n• हिन्दी: नमस्ते", "type": "content"},
                        {"title": "Symbols & Math", "content": "• π ≈ 3.14159\n• E = mc²\n• ∑(1 to ∞) = ∞\n• © 2024 Global Inc.", "type": "content"},
                        {"title": "Thank You! 🙏", "content": "Merci • Gracias • 谢谢 • شكراً • धन्यवाद", "type": "content"}
                    ]
                }
            },
            {"step": "illustration", "status": "pending"},
            {"step": "compiled", "status": "pending"},
            {"step": "pptx", "status": "pending"},
        ]
    }
]