"""
Research Complete Presentations Test Data

These presentations have completed research step.
Used for testing slides generation and research content display.
"""

RESEARCH_COMPLETE_PRESENTATIONS = [
    {
        "id": 5,
        "name": "Research Complete Test 1",
        "topic": "Machine Learning Applications",
        "author": "Test Author",
        "description": "For slides generation tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Machine Learning Applications

Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.

## Key Applications

### 1. Healthcare
- Diagnostic imaging analysis
- Drug discovery and development
- Personalized treatment plans
- Patient risk prediction

### 2. Finance
- Fraud detection systems
- Algorithmic trading
- Risk assessment models
- Credit scoring

### 3. Transportation
- Autonomous vehicles
- Route optimization
- Traffic prediction
- Maintenance forecasting

### 4. Technology
- Search engines
- Recommendation systems
- Natural language processing
- Computer vision

## Types of Machine Learning

ML algorithms can be categorized into:
- **Supervised Learning**: Using labeled data for training
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error""",
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
        "description": "For slides generation tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Climate Change Impact

## Overview
Climate change represents one of the most pressing challenges of our time, affecting ecosystems, economies, and societies worldwide.

## Key Impacts

### Environmental Effects
- Rising global temperatures
- Melting ice caps and glaciers
- Sea level rise
- Extreme weather events
- Ecosystem disruption

### Economic Consequences
- Agricultural productivity changes
- Infrastructure damage
- Energy sector adaptation costs
- Health care expenses
- Migration and displacement costs

### Social Implications
- Food security concerns
- Water scarcity
- Public health challenges
- Climate refugees
- Inequality exacerbation

## Mitigation Strategies
- Renewable energy transition
- Carbon capture technologies
- Sustainable transportation
- Forest conservation
- International cooperation""",
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
        "description": "For slides display tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Blockchain Technology

## Introduction
Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography.

## Key Features
- **Decentralization**: No single point of control
- **Transparency**: All transactions are visible
- **Immutability**: Records cannot be altered retroactively
- **Security**: Cryptographic protection

## Applications

### Cryptocurrency
- Bitcoin
- Ethereum
- Smart contracts

### Business Applications
- Supply chain management
- Digital identity
- Healthcare records
- Voting systems

### Financial Services
- Cross-border payments
- Securities trading
- Trade finance
- Insurance claims

## Challenges
- Scalability issues
- Energy consumption
- Regulatory uncertainty
- Interoperability""",
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
        "description": "For wizard tests",
        "steps": [
            {
                "step": "research", 
                "status": "completed",
                "result": {
                    "content": """# Quantum Computing

## Overview
Quantum computing harnesses quantum mechanical phenomena to process information in fundamentally new ways.

## Key Concepts
- **Qubits**: Quantum bits that can exist in superposition
- **Entanglement**: Quantum correlation between particles
- **Quantum Gates**: Operations on qubits
- **Quantum Supremacy**: Outperforming classical computers

## Applications

### Cryptography
- Breaking current encryption
- Quantum key distribution
- Post-quantum cryptography

### Drug Discovery
- Molecular simulation
- Protein folding
- Drug interaction modeling

### Optimization
- Traffic flow optimization
- Financial portfolio optimization
- Supply chain management

### Machine Learning
- Quantum neural networks
- Feature mapping
- Optimization algorithms

## Current Limitations
- Quantum decoherence
- Error rates
- Limited qubit count
- Extreme cooling requirements""",
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