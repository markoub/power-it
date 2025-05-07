#!/usr/bin/env python
"""
Command-line script to fetch logos from worldvectorlogo.com
"""
import os
import argparse
import logging
from logo_fetcher import LogoFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Fetch logos from worldvectorlogo.com')
    parser.add_argument('term', help='Search term for the logo')
    parser.add_argument('--output-dir', '-o', default='./logos',
                        help='Directory to save downloaded logos (default: ./logos)')
    parser.add_argument('--filename', '-f', 
                        help='Filename to save the logo (default: <term>.svg)')
    parser.add_argument('--info-only', '-i', action='store_true',
                        help='Only display logo information, do not download')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger('').setLevel(logging.DEBUG)
    
    # Create output directory if it doesn't exist
    if not args.info_only:
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize logo fetcher
    fetcher = LogoFetcher(None if args.info_only else args.output_dir)
    
    if args.info_only:
        # Just search and display information
        logo_info = fetcher.search_logo(args.term)
        if logo_info:
            print(f"Found logo: {logo_info['name']}")
            print(f"URL: {logo_info['url']}")
            print(f"Image URL: {logo_info['image_url']}")
        else:
            print(f"No logo found for '{args.term}'")
    else:
        # Download the logo
        success, result = fetcher.download_logo(args.term, args.filename)
        if success:
            print(f"Successfully downloaded logo to: {result}")
        else:
            print(f"Failed to download logo: {result}")

if __name__ == '__main__':
    main() 