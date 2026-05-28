# Context: Building a Job Agent

## Problem Statement
We aim to develop a job agent that automates the process of job hunting by scraping job listings from multiple platforms, including Naukri, RemoteOK, and Wellfound. The agent will focus on retrieving jobs relevant to specific titles provided by the user. Once the jobs are scraped, the agent will store the data in a CSV file with the following details:

- Job Title
- Job Location
- Company Name
- Job Description
- Application Link
- Other relevant details

## Objectives
1. Automate job scraping from Naukri, RemoteOK, and Wellfound.
2. Filter jobs based on user-specified titles.
3. Store the scraped job data in a structured CSV format.
4. Ensure the data includes all critical details for job applications.

## Benefits
- Saves time and effort in manual job searching.
- Provides a centralized repository of job listings.
- Enables easy filtering and analysis of job opportunities.

## Reference Websites
- [Naukri](https://www.naukri.com)
- [RemoteOK](https://remoteok.io)
- [Wellfound](https://wellfound.com)

## Data Collection Methods
- **Naukri**: We will use HTML scraping to extract job listings.
- **RemoteOK**: We will utilize their Public API to fetch job data.
- **Wellfound**: We will use Firecrawl for scraping job information.

## Status Update (2026-05-28)
- **Phase 1**: Completed. Project structure established.
- **Phase 2 (Data Collection Implementation)**: **COMPLETED**.
- **Phase 3 (Data Processing and Filtering)**: **COMPLETED & TESTED**.
  - **Normalization**: Enhanced `DataCleaner` with comprehensive city mappings (including "banglore" -> "Bangalore") and title metadata removal.
  - **Filtering**: Implemented multi-criteria filtering including inclusive and exclusive keyword matching.
  - **Deduplication**: Refined the removal of duplicate listings based on composite keys (title, company, location).
  - **Testing**: Implemented browser integration testing allowing users to view the search pages directly in their browser and run automated scrapers (BeautifulSoup/Selenium) end-to-end.
- **Phase 4 (Data Storage)**: **COMPLETED & TESTED**.
  - **CSV Schema**: Enforced strict order, type-casting, and column isolation.
  - **Appending & Deduplication**: Integrated historic search appending and duplicate prevention into the core storage pipeline.
  - **Lock Resilience**: Implemented file-write retry logic and automatic backup creation in case of write permission lockouts.
- **Phase 5 (Automation & Scheduling)**: **COMPLETED**.
  - **Logging**: Configured robust system-wide logging to console and `doc/scraping.log`.
  - **Scheduling**: Created Windows scheduler batch launcher `run_agent.bat` and documented step-by-step setup guides in `doc/scheduler_guide.md`.
- **Phase 6 (Testing & Validation)**: **COMPLETED**.
  - **API Validation**: Corrected field mappings for the RemoteOK API and implemented error fallback controls for Wellfound's Firecrawl scraper.
  - **Automated Tests**: Implemented `test_data_storage.py` and `test_integration.py` validating storage constraints, log delivery, browser-spawning URLs, and all scraper classes.

## Development Log (Step-by-Step)

### Step 1: Project Alignment & Cleanup
- Analyzed `architecture.md` and `context.md` to establish Phase 2 goals.
- Converted `requirements.md` into a standard `requirements.txt`.
- Removed unnecessary `requirements.md` to keep the workspace clean.

### Step 2: Enhancing Naukri Scraper (BS4)
- Updated `src/scrapers/naukri.py` with modern browser headers and referral URLs to reduce bot detection.
- Implemented a flexible selector system to handle Naukri's varying HTML structure (targeting `jobTuple` and `cust-job-tuple` classes).

### Step 3: Implementing Wellfound Parsing
- Developed the parsing logic in `src/scrapers/wellfound.py` to process data from the Firecrawl API.
- Added heuristic regex parsing for Markdown blocks and fallback BeautifulSoup parsing for HTML content.

### Step 4: Adding Selenium for Dynamic Content
- Introduced `NaukriSeleniumScraper` as a subclass in `naukri.py`.
- Integrated Selenium with a headless Chrome option to handle JavaScript-heavy content that basic `requests` cannot capture.
- Updated `requirements.txt` with `selenium` and `webdriver-manager`.

### Step 5: Integration & Scraper Validation
- Updated `src/scrapers/__init__.py` to export the new Selenium scraper.
- Created `src/test_scrapers.py`, a dedicated testing script to verify that each platform (RemoteOK, Naukri, Wellfound) can successfully retrieve job data.
- Verified that `JobAgent` correctly orchestrates these scrapers through the `search_jobs` method.

### Step 6: Implementing Advanced Data Processing (Phase 3)
- **Enhanced Cleaning**: Upgraded `src/processors/cleaner.py` with expanded mapping for Indian/Global cities and a specialized title cleaning routine that removes noise like "Urgent Hiring" or extraneous brackets.
- **Improved Filtering**: Added "Exclusion Keywords" support to `src/processors/filter.py`, allowing users to skip jobs with certain words (e.g., excluding "Intern" or "Senior" as needed).
- **Pipeline Integration**: Exposed the new filtering capabilities through `DataProcessor` and the main `JobAgent` interface for easier end-user access.

### Step 7: Scraper Testing & Browser Integration (Phase 3 Testing)
- **Typo Normalization**: Added `'banglore': 'Bangalore'` to `common_location_mappings` in `src/processors/cleaner.py` to robustly handle common search variations.
- **HTML Scraper Test Script**: Created [test_html_scraper.py](file:///d:/Masai_AI_Projects/AI_Job_Hunt/test_html_scraper.py) to test BeautifulSoup/Selenium scrapers, opening search pages in the browser and processing the output.
- **Browser Automation Bypass**: Added standard browser user-agents to `NaukriSeleniumScraper` Chrome options to prevent Cloudflare blocks.
- **JobAgent Integration**: Switched the default scraper for Naukri in `JobAgent` to `NaukriSeleniumScraper(headless=True)` to make it work out-of-the-box.
- **Browser Opening Integration**: Added `--open-browser` argument to [main.py](file:///d:/Masai_AI_Projects/AI_Job_Hunt/main.py) which uses Python's `webbrowser` module to open the corresponding job page for search verification.
- **End-to-End Test Validation**: Verified search for "Frontend Developer" in "BAnglore" successfully opens the browser page, scrapes 25 jobs, filters them to 23 valid jobs, and saves them to a CSV.

### Step 8: Finalizing Data Storage (Phase 4)
- **Automated Storage Tests**: Wrote [test_data_storage.py](file:///d:/Masai_AI_Projects/AI_Job_Hunt/test_data_storage.py) verifying strict schema structures, unique appending, and composite duplicate filtering.
- **Strict Schema Enforcement**: Cleaned and casting values to standard string type, dropping non-schema columns in `job_agent.py`.
- **Write-Lock Fallbacks**: Added a PermissionError check to retry writing locked CSV files (e.g., opened in Excel) with fallback to timestamped backup names.
- **CLI Options**: Added `--no-master` (to skip master listing compilation) and `--append` (to append to custom output files rather than overwriting them).
- **Verification**: Ran tests and manual searches to confirm master file integration and historical run deduplication.

### Step 9: Phase 5 & 6 System Verification Run
- **Search Execution**: Successfully executed `python main.py --job-title "python developer" --location "Bangalore" --output jobs.csv` using the `.venv` Python environment.
- **Aggregation**: The script searched across multiple boards (Naukri, RemoteOK, and Wellfound) automatically.
- **Data Capture**: Scraped 20 raw jobs from Naukri. RemoteOK fetched 0 matching jobs (as Tech roles are currently scarce on its public endpoint). Wellfound outputted a warning and exited gracefully due to missing `FIRECRAWL_API_KEY`.
- **Deduplication & Storage**: Cleaned and validated the scraped jobs, removed 2 duplicate entries, and successfully saved 18 unique job listings to `doc/jobs.csv` and appended them to `doc/master_jobs.csv`.

### Step 10: Wellfound Scraper Parameters Encoding & Browser Integration Fixes
- **Query Param Encoding**: Fixed a bug in `src/scrapers/wellfound.py` where search query parameters were concatenated without URL-encoding. Imported and utilized `urllib.parse.urlencode` to correctly handle space-separated query titles (e.g. `"Sales Executive"`) and special characters in location params.
- **Multitarget Browser Launching**: Refactored the `--open-browser` feature in `main.py`. Instead of exclusively opening the Naukri search page, the runner now dynamically opens the browser search page for all active scraper platforms (Naukri, RemoteOK, and Wellfound) selected in the `--platforms` flag.
- **Verification Run**: Verified search for `"Sales Executive"` in `"Bengaluru"` with `--platforms wellfound --open-browser`. It successfully normalized the location to `"Bangalore"`, constructed the properly encoded URL `https://wellfound.com/jobs?q=Sales+Executive&l=Bangalore`, launched it in the system browser, and exited cleanly.
- **Test Validation**: Executed all integration and storage test suites using python's unittest runner. All 8 tests passed without errors.

### Step 11: Bypassing Wellfound Login Wall & Parser Implementation
- **Bypassing Login Redirects**: Identified that Wellfound redirects unauthenticated search query requests (`/jobs?q=...`) to the home landing page. Discovered and implemented Wellfound's public SEO directory URL route (`/role/l/{role-slug}/{location-slug}`) which allows guest users and crawlers to access full job lists without logging in.
- **Card-Based Markdown Parser**: Reconstructed the empty `_parse_wellfound_jobs` parser in `src/scrapers/wellfound.py` to match the markdown structure returned by Firecrawl on Wellfound's SEO route. Implemented block splitting based on company card prefixes (`[![Logo](...)`) and extracted job titles, companies, locations, descriptions, and application URLs.
- **Verification & Integration Tests**: Executed `test_integration.py` successfully. The scraper fetched and parsed **32 live jobs** from Wellfound. Committed and pushed both fixes to GitHub (Commit `4566042`).

### Step 12: Automating Browser Search Page Launching
- **Default-On Browser Launching**: Refactored `main.py` so that opening the browser search page for selected platforms runs automatically by default when executing the scraping process.
- **Opt-Out Mechanism**: Added a new `--no-browser` CLI flag to allow users and automated schedulers (such as Task Scheduler/cron jobs) to bypass spawning the web browser.
- **Verification**: Verified that executing the script opens browser pages for Naukri, RemoteOK, and Wellfound automatically, and that executing with `--no-browser` disables it. Committed and pushed to GitHub (Commit `7bc6762`).




