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

## Phase 2 (Implementation progress in this repo)
- Added an initial `src/job_agent` code scaffold with a scrapers framework.
- Implemented **RemoteOK** scraping via its `/api` endpoint and title filtering.
- Added placeholders for **Naukri** and **Wellfound** to be completed in later Phase 2 steps (dynamic scraping / Firecrawl integration).
- Next Phase 2 steps: implement Naukri HTML/dynamic parsing and wire up Firecrawl for Wellfound; then add a CSV persistence layer (Phase 4).
