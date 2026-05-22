# Automate AI Job Hunt

An intelligent job agent that automatically scrapes job listings from multiple platforms including Naukri, RemoteOK, and Wellfound.

## Features

- **Multi-Platform Support**: Scrape jobs from Naukri, RemoteOK, and Wellfound
- **Smart Data Collection**:
  - Naukri: HTML scraping with BeautifulSoup
  - RemoteOK: Public API integration
  - Wellfound: Firecrawl-based scraping
- **Structured Data Storage**: Store jobs in CSV format with all relevant details
- **Easy to Use**: Command-line interface for quick job searches

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Steps

1. Clone the repository:
```bash
git clone https://github.com/AmrutaDeshpande21/Automate-AI-JobHunt.git
cd Automate-AI-JobHunt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (for Wellfound/Firecrawl):
```bash
export FIRECRAWL_API_KEY=your_api_key_here
```

## Usage

### Basic Job Search

Search for "Python Developer" jobs:
```bash
python main.py --job-title "Python Developer"
```

### With Location

Search for "Data Scientist" jobs in "India":
```bash
python main.py --job-title "Data Scientist" --location "India"
```

### Specific Platform

Search only on RemoteOK:
```bash
python main.py --job-title "Full Stack Developer" --platforms remoteok
```

### Custom Output File

Save results to a custom file:
```bash
python main.py --job-title "Frontend Developer" --output "frontend_jobs.csv"
```

## Project Structure

```
Automate-AI-JobHunt/
├── src/
│   ├── __init__.py
│   ├── job_agent.py              # Main agent orchestrator
│   ├── naukri_scraper.py         # Naukri HTML scraper
│   ├── remoteok_scraper.py       # RemoteOK API scraper
│   └── wellfound_scraper.py      # Wellfound Firecrawl scraper
├── doc/
│   ├── context.md                # Project context
│   └── architecture.md           # Phase-wise architecture
├── data/                         # Output CSV files
├── main.py                       # Entry point
├── requirements.txt              # Python dependencies
├── .gitignore
└── README.md
```

## CSV Output Format

The scraped jobs are stored in CSV format with the following columns:

| Column | Description |
|--------|-------------|
| title | Job title |
| company | Company name |
| location | Job location |
| description | Job description |
| link | Application link |
| source | Job platform (Naukri/RemoteOK/Wellfound) |
| scraped_date | Date and time of scraping |

## Technologies Used

- **BeautifulSoup**: HTML parsing and scraping
- **Requests**: HTTP library for API calls
- **Pandas**: Data manipulation and CSV operations
- **Selenium**: Dynamic web scraping (when needed)
- **Firecrawl**: Intelligent web scraping for Wellfound

## API Keys Required

- **Firecrawl**: Required for Wellfound scraping. Get it from [Firecrawl](https://firecrawl.dev)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Add support for more job platforms
- [ ] Implement job filtering and recommendations
- [ ] Add email notifications for new jobs
- [ ] Build a web UI for easier interaction
- [ ] Implement scheduling for periodic job scraping
- [ ] Add salary range extraction
- [ ] Database integration for persistent storage

## Support

For issues, suggestions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ by Amruta Deshpande**

---

*This project is developed as part of the Masai School Cohort live project.* 
