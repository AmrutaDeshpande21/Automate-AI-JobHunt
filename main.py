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
    
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip data cleaning step'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip data validation step'
    )
    
    parser.add_argument(
        '--no-deduplicate',
        action='store_true',
        help='Skip duplicate removal step'
    )
    
    parser.add_argument(
        '--filter-locations',
        type=str,
        nargs='+',
        default=None,
        help='Filter jobs by locations (space-separated)'
    )
    
    parser.add_argument(
        '--filter-sources',
        type=str,
        nargs='+',
        default=None,
        help='Filter jobs by sources (space-separated, e.g., naukri remoteok)'
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
    
    # Process jobs (cleaning, validation, deduplication)
    print("\n" + "="*80)
    print("PROCESSING JOBS")
    print("="*80)
    
    df, stats = agent.process_jobs(
        clean=not args.no_clean,
        validate=not args.no_validate,
        remove_duplicates=not args.no_deduplicate
    )
    
    # Filter jobs if criteria provided
    if args.filter_locations or args.filter_sources:
        print("\n" + "="*80)
        print("FILTERING JOBS")
        print("="*80)
        
        df = agent.filter_jobs(
            title_keywords=[args.job_title],
            locations=args.filter_locations,
            sources=args.filter_sources
        )
    
    # Display summary
    agent.display_summary()
    
    # Save to CSV
    if not df.empty:
        agent.save_to_csv(filename=args.output)
    
    print("\n✓ Job scraping completed successfully!")

if __name__ == '__main__':
    main()
