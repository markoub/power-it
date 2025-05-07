import os
import sys
import json
from pptx_analyzer import analyze_pptx_template

def main():
    """
    Run template analysis and provide recommendations for fixing the table of contents issues.
    """
    # Get template path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(os.path.dirname(script_dir), "template.pptx")
    
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found at {template_path}")
        print("Please specify the correct path to your template.pptx file")
        sys.exit(1)
    
    print("Running PPTX template analysis...")
    
    # Capture the output
    import io
    import contextlib
    
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        analyze_pptx_template(template_path)
    
    output = f.getvalue()
    print(output)
    
    # Save the analysis to a file
    analysis_path = os.path.join(os.path.dirname(script_dir), "template_analysis.txt")
    with open(analysis_path, "w") as file:
        file.write(output)
    
    print(f"\nAnalysis saved to: {analysis_path}")
    print("\nRecommendations for updating generate_pptx.py based on template analysis:")
    print("1. Check the Table of Contents layout name in your template")
    print("2. Update the get_layout_by_name function calls in generate_pptx.py to match your template's layout names")
    print("3. Verify shape names for TOC sections (Section1, 01, 01Divider, etc.)")
    print("4. Update get_toc_shapes function to match your template's naming conventions")

if __name__ == "__main__":
    main() 