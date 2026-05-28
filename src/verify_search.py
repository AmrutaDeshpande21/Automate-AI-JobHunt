"""
Verification script for specific title and location search
"""

from src.agent import JobAgent
import pandas as pd

def verify_specific_search():
    agent = JobAgent()
    
    # Target search
    job_title = "Python Developer"
    location = "Bangalore"
    
    print(f"\n[START] Starting search for '{job_title}' in '{location}'...")
    
    # Search across all platforms (it will skip those without keys/drivers gracefully)
    df = agent.search_jobs(job_title=job_title, location=location, platforms='all')
    
    if df.empty:
        print("[INFO] No jobs found in initial search. This might be due to API limits, missing drivers, or search criteria.")
    else:
        print(f"[SUCCESS] Found {len(df)} raw jobs.")
        
        # Process them
        processed_df, stats = agent.process_jobs()
        
        # Save them (Phase 4 completion check)
        filepath = agent.save_to_csv(append=True)
        
        if not processed_df.empty:
            print("\n--- SAMPLE JOBS FOUND ---")
            print(processed_df[['title', 'company', 'location', 'source']].head())
            print("\n[SUCCESS] Verification successful: JobAgent can search, process, and store jobs.")
        else:
            print("[INFO] Processing resulted in 0 valid jobs.")

if __name__ == "__main__":
    verify_specific_search()
