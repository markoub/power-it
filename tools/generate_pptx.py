import asyncio
import os
import re
from typing import List, Optional

async def convert_pptx_to_png(pptx_path: str, output_dir: Optional[str] = None) -> List[str]:
    """Convert a PPTX file to PNG images using the LibreOffice CLI."""
    print("DEBUG: Using root tools/generate_pptx.py implementation")
    if output_dir is None:
        output_dir = os.path.dirname(pptx_path)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get basename without extension
    basename = os.path.splitext(os.path.basename(pptx_path))[0]
    
    print(f"Converting PPTX file: {pptx_path}")
    print(f"Output directory: {output_dir}")
    
    # Use LibreOffice to export each slide to PNG images
    cmd = ["soffice", "--headless", "--convert-to", "png", "--outdir", output_dir, pptx_path]
    
    try:
        print(f"Running command: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        print(f"LibreOffice stdout: {stdout.decode() if stdout else 'None'}")
        print(f"LibreOffice stderr: {stderr.decode() if stderr else 'None'}")
        print(f"LibreOffice exit code: {process.returncode}")

        if process.returncode != 0:
            print(f"Error converting PPTX to PNG: {stderr.decode()}")
            return []

        # LibreOffice converts PPTX files to a single PNG file or a series of PNG files
        # with naming pattern: basename-001.png, basename-002.png, etc.
        # We need to match the specific pattern that LibreOffice creates
        expected_pattern = f"{basename}-"
        png_files = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.startswith(expected_pattern) and f.endswith('.png')
        ]

        # If no pattern-matched files found, try looking for a single output file
        if not png_files:
            # Sometimes LibreOffice just outputs a single file with the basename
            single_file = f"{basename}.png"
            single_path = os.path.join(output_dir, single_file)
            if os.path.exists(single_path):
                png_files = [single_path]
                print(f"Found single PNG output: {single_path}")

        # Sort them naturally (so -1, -2, -10 appear in the right order)
        png_files.sort(key=lambda path: [
            int(part) if part.isdigit() else part
            for part in re.split(r'(\d+)', path)
        ])

        print(f"Generated {len(png_files)} PNG files")
        for i, png_file in enumerate(png_files[:10]):  # Show just first 10 for brevity
            print(f"  - {os.path.basename(png_file)}")
        
        if len(png_files) > 10:
            print(f"  ... and {len(png_files) - 10} more files")

        # If we still couldn't find any valid PNG files, log a warning
        if not png_files:
            print(f"WARNING: No PNG files matching pattern '{expected_pattern}' found after conversion")
            # List all files in the directory for debugging
            print(f"Files in {output_dir}:")
            for f in os.listdir(output_dir):
                print(f"  - {f}")

        return png_files
        
    except Exception as e:
        print(f"Error in convert_pptx_to_png: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return [] 