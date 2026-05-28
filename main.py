"""
Main entry point for the Job Agent

Usage:
    python main.py --job-title "Software Engineer" --location "India" --platforms all
"""

import argparse
import sys
from src.agent import JobAgent
from src.utils.logger import logger

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
    
    parser.add_argument(
        '--open-browser',
        action='store_true',
        help='Open the job search page in the system web browser'
    )
    
    parser.add_argument(
        '--no-master',
        action='store_true',
        help='Skip appending jobs to the central master list (master_jobs.csv)'
    )
    
    parser.add_argument(
        '--append',
        action='store_true',
        help='Append and deduplicate results if saving to a custom output file instead of overwriting'
    )
    
    args = parser.parse_args()
    
    logger.info("================================================================================")
    logger.info("AUTOMATE AI JOB HUNT - Job Agent")
    logger.info("================================================================================")
    logger.info(f"Searching for: {args.job_title}")
    if args.location:
        logger.info(f"Location: {args.location}")
    logger.info(f"Platforms: {args.platforms}")
    logger.info("================================================================================")
    
    # Open browser if requested
    if args.open_browser:
        import webbrowser
        from urllib.parse import urlencode
        from src.processors.cleaner import DataCleaner
        cleaner = DataCleaner()
        normalized_loc = cleaner._normalize_location(args.location) if args.location else ""
        
        # Determine which platforms were selected
        platforms_to_open = []
        if args.platforms.lower() == 'all':
            platforms_to_open = ['naukri', 'remoteok', 'wellfound']
        else:
            platforms_to_open = [args.platforms.lower()]
            
        for platform in platforms_to_open:
            if platform == 'naukri':
                search_title_url = args.job_title.lower().replace(' ', '-')
                search_loc_url = normalized_loc.lower().replace(' ', '-') if normalized_loc else ""
                if search_loc_url:
                    url = f"https://www.naukri.com/{search_title_url}-jobs-in-{search_loc_url}-1"
                else:
                    url = f"https://www.naukri.com/{search_title_url}-jobs-1"
            elif platform == 'wellfound':
                role_slug = args.job_title.lower().strip().replace(' ', '-')
                role_slug = ''.join(c for c in role_slug if c.isalnum() or c == '-')
                if normalized_loc:
                    loc_slug = normalized_loc.lower().strip().replace(' ', '-')
                    loc_slug = ''.join(c for c in loc_slug if c.isalnum() or c == '-')
                    url = f"https://wellfound.com/role/l/{role_slug}/{loc_slug}"
                else:
                    url = f"https://wellfound.com/role/{role_slug}"
            elif platform == 'remoteok':
                params = {'q': args.job_title}
                url = f"https://remoteok.com/remote-jobs?{urlencode(params)}"
            else:
                continue
                
            logger.info(f"Opening {platform.capitalize()} search page in default web browser: {url}")
            try:
                webbrowser.open(url)
                logger.info(f"{platform.capitalize()} browser tab opened successfully!")
            except Exception as e:
                logger.warning(f"Failed to open {platform.capitalize()} browser tab: {e}")
    
    # Initialize and run the Job Agent
    agent = JobAgent()
    
    # Search for jobs
    df = agent.search_jobs(
        job_title=args.job_title,
        location=args.location,
        platforms=args.platforms
    )
    
    # Process jobs (cleaning, validation, deduplication)
    logger.info("================================================================================")
    logger.info("PROCESSING JOBS")
    logger.info("================================================================================")
    
    df, stats = agent.process_jobs(
        clean=not args.no_clean,
        validate=not args.no_validate,
        remove_duplicates=not args.no_deduplicate
    )
    
    # Filter jobs if criteria provided
    if args.filter_locations or args.filter_sources:
        logger.info("================================================================================")
        logger.info("FILTERING JOBS")
        logger.info("================================================================================")
        
        df = agent.filter_jobs(
            title_keywords=[args.job_title],
            locations=args.filter_locations,
            sources=args.filter_sources
        )
    
    # Display summary
    agent.display_summary()
    
    # Save to CSV
    if not df.empty:
        # Save to central master list (if not disabled)
        if not args.no_master:
            agent.save_to_csv(filename='master_jobs.csv', append=True)
            
        # Save to custom output file if provided, or fallback to timestamped file if master is skipped
        if args.output:
            agent.save_to_csv(filename=args.output, append=args.append)
        elif args.no_master:
            agent.save_to_csv(filename=None, append=False)
    
    logger.info("Job scraping completed successfully!")

if __name__ == '__main__':
    main()
