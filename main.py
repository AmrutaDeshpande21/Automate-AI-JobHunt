"""
Main entry point for the Job Agent

Usage:
    python main.py --job-title "Software Engineer" --location "India" --platforms all
"""

import argparse
import sys
from src.agent import JobAgent

def main():
    """Main function to run the Job Agent"""
    
    parser = argparse.ArgumentParser(
        description='Automate Job Hunting - Scrape jobs from Naukri, RemoteOK, and Wellfound'
    )
    
    parser.add_argument(
        '--job-title',
        type=str,
        required=True,
        help='Job title to search for'
    )
    
    parser.add_argument(
        '--location',
        type=str,
        default=None,
        help='Location to search in (optional)'
    )
    
    parser.add_argument(
        '--platforms',
        type=str,
        default='all',
        choices=['all', 'naukri', 'remoteok', 'wellfound'],
        help='Platforms to search on (default: all)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output CSV filename (optional)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("AUTOMATE AI JOB HUNT - Job Agent")
    print("="*80)
    print(f"\nSearching for: {args.job_title}")
    if args.location:
        print(f"Location: {args.location}")
    print(f"Platforms: {args.platforms}")
    print("\n" + "="*80 + "\n")
    
    # Initialize and run the Job Agent
    agent = JobAgent()
    
    # Search for jobs
    df = agent.search_jobs(
        job_title=args.job_title,
        location=args.location,
        platforms=args.platforms
    )
    
    # Display summary
    agent.display_summary()
    
    # Save to CSV
    if not df.empty:
        agent.save_to_csv(filename=args.output)
    
    print("\n✓ Job scraping completed successfully!")

if __name__ == '__main__':
    main()
