# NYC DDC: BidScope Procurement Data Pipeline & Report Automation

> **Note on Data Files:** Raw BidScope CSV exports and PDF bid tabs are omitted from this repository due to proprietary municipal workflow sourcing. The repository showcases the underlying ETL architecture, data parsing logic, and programmatic Excel transformation script.

An end-to-end Python ETL automation tool developed for the New York City Department of Design and Construction (NYC DDC) to streamline capital project procurement analytics, eliminate manual data entry, and automate weekly bid tabulation reporting.

**Agency:** New York City Department of Design and Construction (NYC DDC)  
**Author:** Christopher Chan  
**Domain:** Municipal Procurement & Public Infrastructure Analytics  
**Tech Stack:** Python (`pandas`, `openpyxl`, `pdfplumber`), Windows Batch Scripting, Microsoft Excel  

---

## 📌 Business Problem & Operational Impact

At the NYC Department of Design and Construction (DDC), tracking municipal contractor bids across capital infrastructure projects requires compiling data from multiple fragmented sources: structured BidScope system exports and unstructured vendor Bid Tabulation PDFs.

### The Operational Challenge
* **Manual Data Entry Bottleneck:** Previous data entry involved manually copying, pasting, and reconciling contractor bid sheets across separate workbooks every reporting cycle.
* **Integrity & Formatting Risks:** Repetitive manual input frequently introduced formatting breaks, shifted rows, inconsistent tab naming, and broken Excel formula references.
* **Repetitive Maintenance:** Manually reapplying auto-filters, updating contractor rank orders, and reconstructing template layouts added unnecessary administrative overhead.

### The Automated Solution
This lightweight ETL pipeline replaces the manual workflow with a single-click script. It extracts multi-format inputs (CSVs and PDFs), performs programmatic validation and schema alignment in Pandas, and leverages `ExcelWriter` to populate pre-formatted agency templates (`Beautiful Spreadsheet`) while preserving all visual formatting, formulas, and filter criteria.

* **Turnaround Reduction:** Reduced weekly reporting cycle time from **~2 hours of manual collation to a few steps of running the script and verifying**.
* **Zero Transcription Error:** 100% elimination of manual entry discrepancies across line-item pricing and vendor rankings.
* **Zero-Friction Adoption:** Packaged with an autonomous batch runner that configures the environment and dependencies on first launch without requiring command-line experience.

---

## ⚙️ Architecture & Pipeline Workflow

```text
 ┌─────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
 │   Input Files   │ ────> │  Extract & Clean CSVs  │ ────> │ Filter for Compliance  │
 │ (CSVs + BidTab) │       │                        │       │  & Excel Compatibility │
 └─────────────────┘       └────────────────────────┘       └────────────────────────┘
                                                                         │
 ┌─────────────────┐       ┌────────────────────────┐                    │
 │  Output Folder  │ <──── │ Transfer to Template   │ <──────────────────┘
 │ (Filled Sheets) │       │ & Auto-Refill Filters  │       ┌────────────────────────┐
 └─────────────────┘       └────────────────────────┘ <──── │  Scrape Bid Tab (PDF)  │
                                                            │   into Tabular Schema  │
                                                            └────────────────────────┘
```

### Pipeline Execution Details

1. **Multi-Source Extraction:**
   * **BidScope CSV Ingestion:** Ingests bidder data from BidScope Excel files
   * **PDF Tabular Extraction:** Programmatically scrapes vendor line-item estimates and bid summaries directly from unstructured `Bid Tab.pdf` documents into Pandas DataFrames.
2. **Transformation & Normalization:**
   * Cleans raw headers, trims trailing whitespace, standardizes vendor entity names, and validates numeric data types.
   * Filters and structures records into normalized relational DataFrames ready for side-by-side procurement evaluation.
3. **Template Population & Filter Persistence:**
   * Ingests the protected agency master styling workbook.
   * Writes transformed datasets into designated sheets using Pandas `ExcelWriter` and `openpyxl`.
   * Programmatically reapplies auto-filters and dynamic column adjustments without overriding existing master styling.
4. **Isolated Production Export:**
   * Generates a timestamped, distribution-ready workbook (`Beautiful Spreadsheet Filled.xlsx`), ensuring the master template remains untouched.

---

## 🛠️ Zero-Friction Execution Design

To ensure team members across municipal departments can run the automation without command-line knowledge, the process is wrapped in a self-bootstrapping Windows batch file (`run this.bat`):

```bat
@echo off
:: Self-bootstrapping environment verification and runner
if not exist .venv (
    echo Provisioning local Python virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate
echo Checking and installing required libraries...
pip install -r requirements.txt --quiet
python process_reports.py
echo.
echo Process complete. Press any key to exit.
pause
```

* **Automated Dependency Setup:** Automatically detects if dependencies (`pandas`, `openpyxl`, `pdfplumber`) are installed; if missing, it provisions a virtual environment (`.venv`) and configures them silently.
* **Write-Lock Protection:** Includes pre-run validation checks to alert users if target files are open in Microsoft Excel, preventing file write-lock errors.

---

## 💡 Engineering Highlights

* **Resilient File Handling:** Uses isolated read/write buffers so that source files and base templates are never mutated or corrupted during runtime.
* **Portable Architecture:** Built to operate on standard agency-issued Windows workstations without requiring administrative software privileges or custom system configurations.
* **Modular Pipeline:** The transformation functions in `process_reports.py` are modularized, allowing easy adaptation for future BidScope schema updates or additional municipal report types.
