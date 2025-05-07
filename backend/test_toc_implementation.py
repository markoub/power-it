"""
Test script to verify the Table of Contents implementation works with a real presentation.
"""
from pptx import Presentation
from tools.pptx_toc import process_toc_slide, create_table_of_contents_slide

# Create a new presentation
prs = Presentation("template.pptx")

# Test 1: Create a new TOC slide
print("\nTest 1: Creating a new TOC slide")
toc_data = {
    'title': 'Table of Contents',
    'sections': [
        'Executive Summary',
        'Market Analysis',
        'Competitive Landscape',
        'Product Strategy',
        'Financial Projections',
        'Implementation Plan',
        'Risk Assessment',
        'Conclusion'
    ]
}

new_toc_slide = create_table_of_contents_slide(prs, toc_data)
print("New TOC slide created successfully")

# Test 2: Update an existing TOC slide
print("\nTest 2: Updating an existing TOC slide")
updated_sections = [
    'Updated Executive Summary',
    'Updated Market Analysis',
    'Updated Competitive Landscape',
    'Updated Product Strategy',
    'Updated Financial Projections',
]

process_toc_slide(new_toc_slide, updated_sections)
print("Existing TOC slide updated successfully")

# Save the test presentation
output_file = "test_toc_output.pptx"
prs.save(output_file)
print(f"\nTest presentation saved to {output_file}")
print("Please open the file to verify the Table of Contents slides are correctly populated") 