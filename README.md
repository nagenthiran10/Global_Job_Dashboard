# Global Job Market & Skill Demand Analysis

## Project Overview
This project provides a comprehensive, end-to-end analysis of the global tech job market. It ingests, cleans, and analyzes over 32,000 real-world job postings to identify key trends in compensation, remote work demand, and required skills. The goal is to provide actionable insights for job seekers and competitive intelligence for employers.

## Tools Used
*   **Python (Pandas/NumPy):** Automated data cleaning, feature engineering (categorizing experience levels and salary ranges), and data pipeline execution.
*   **SQL (SQLite):** Relational database management and complex analytical querying (aggregations, statistical distributions, ranking).
*   **Power BI:** Interactive data visualization, DAX measure creation, and executive dashboard design.

## Project Structure
```text
📦 Global Job Market
 ┣ 📂 data/        # Raw & cleaned datasets (.xlsx), SQLite database (.db)
 ┣ 📂 python/      # ETL scripts, data processing, and feature engineering
 ┣ 📂 sql/         # Analytical queries for insights and reporting
 ┣ 📂 powerbi/     # Power BI dashboard files and DAX documentation
 ┗ 📜 README.md    # Project documentation
```

## Key Insights
1.  **The Remote Premium:** Remote roles command higher compensation, averaging **~$131,000** compared to $121,000 for on-site/hybrid positions.
2.  **Experience Scaling:** Compensation scales aggressively with seniority. Entry-level roles average ~$81k, jumping to **$110k+** for mid-level and **$145k+** for senior roles.
3.  **Demand vs. Value:** While *Data Analyst* is the highest-volume role on the market, *Data Scientists* and *Data Engineers* command significantly higher average salaries.
4.  **Benefits & Pay:** Top-tier companies don't substitute base pay for benefits; roles offering health insurance also average **$13,000 higher** in base salary.

## Dashboard Summary
The Power BI dashboard provides an interactive executive overview utilizing a clean, Z-pattern layout. It features:
*   **High-Level KPIs:** Instant visibility into Average Salary, Maximum Earning Potential, and Total Job Volume.
*   **Geographic Analysis:** A dynamic map visualizing the salary distribution across different countries.
*   **Role & Experience Benchmarks:** Categorical bar and line charts breaking down compensation by specific job titles and experience levels (Entry/Mid/Senior).
*   **Dynamic Filtering:** Slicers allowing users to instantly drill down by specific locations, titles, or experience levels.
