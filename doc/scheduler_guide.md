# Job Hunt Agent - Automation & Scheduling Guide

This guide explains how to automate the Job Hunt Agent to run periodically (e.g., daily) on Windows and Unix-like operating systems.

---

## 1. Automation Script

An automation script has been created at the root of the project:
* **Windows**: [run_agent.bat](file:///d:/Masai_AI_Projects/AI_Job_Hunt/run_agent.bat)

This script automatically navigates to the project directory, activates the virtual environment, and runs `main.py` with default arguments: `--job-title "Frontend Developer" --location "Bangalore"`.

You can also pass custom arguments to the batch file (e.g., `run_agent.bat --job-title "Python Developer" --platforms naukri`).

---

## 2. Scheduling on Windows (Task Scheduler)

To configure the script to run automatically every day at a specific time:

1. **Open Task Scheduler**:
   * Press `Win + R`, type `taskschd.msc`, and press **Enter**.

2. **Create a Basic Task**:
   * In the right panel, click **Create Basic Task...**
   * Name the task: `Job Hunt Scraper Agent`.
   * Description: `Runs the Job Scraper daily to aggregate Naukri, RemoteOK, and Wellfound jobs into doc/master_jobs.csv`.
   * Click **Next**.

3. **Choose Trigger Interval**:
   * Select **Daily** and click **Next**.
   * Set the start time (e.g., `9:00 AM`) and recurrence to every `1` day. Click **Next**.

4. **Select Action**:
   * Select **Start a program** and click **Next**.

5. **Configure Start Program**:
   * **Program/script**: Click **Browse** and select [run_agent.bat](file:///d:/Masai_AI_Projects/AI_Job_Hunt/run_agent.bat).
   * **Start in (optional)**: Set this to the absolute path of the workspace: `D:\Masai_AI_Projects\AI_Job_Hunt`. (This is critical to resolve relative python paths correctly).
   * Click **Next**.

6. **Finish**:
   * Review settings and click **Finish**.

Now, your Task Scheduler will run the script daily at the configured time, appending and deduplicating jobs into `doc/master_jobs.csv` and logging output to `doc/scraping.log`.

---

## 3. Scheduling on macOS/Linux (Cron)

If running in a Unix-like environment, configure the scheduler using `cron`:

1. Open your cron table configuration:
   ```bash
   crontab -e
   ```

2. Add a cron entry (e.g., to run daily at 9:00 AM):
   ```cron
   0 9 * * * /bin/bash /absolute/path/to/AI_Job_Hunt/.venv/bin/python /absolute/path/to/AI_Job_Hunt/main.py --job-title "Frontend Developer" --location "Bangalore" >> /absolute/path/to/AI_Job_Hunt/doc/cron_run.log 2>&1
   ```

3. Save and close. The system daemon will automatically execute the agent at the specified intervals.
