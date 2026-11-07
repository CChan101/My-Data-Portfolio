# NYC 311 Service Requests: Predicting Agency Resolution Velocity

An end-to-end machine learning and civic analytics project predicting whether NYC 311 municipal service requests will be resolved within 7 days, identifying operational bottlenecks across agencies and boroughs.

**Collaborators:** Christopher Chan, Lincon Chopra, Nino Alishvili, Rojina Dhikari  
**Course Project:** CIS 9660 | Zicklin School of Business, Baruch College  
**Dataset:** [NYC Open Data - 311 Service Requests (2020 to Present)](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9/about_data)  
**Deliverables:** [📄 Download Presentation Deck (PPTX)]([./311 Service Requests & Agency Responses/CIS 9660 Presentation.pptx](https://github.com/CChan101/My-Data-Portfolio/blob/main/311%20Service%20Requests%20%26%20Agency%20Responses/CIS%209660%20Presentation.pptx))

---

## 📌 Executive Summary

New York City receives thousands of 311 complaints daily across dozens of agencies. While quick-response issues like illegal parking or noise complaints are resolved within hours, complex complaints—such as housing unsanitary conditions or infrastructure repair—often face protracted delays that hurt resident quality of life.

This project implements machine learning classification models to predict early in a ticket's lifecycle whether it will meet a **7-day resolution benchmark**. By isolating the organizational, geographic, and seasonal drivers of resolution speed, this framework provides municipal leadership with actionable early-delay detection and targeted resource allocation capabilities.

### 🔑 High-Level Takeaways
* **Top Performing Model:** **Logistic Regression** achieved the highest 3-Fold Cross-Validation **F1-Score of 0.942** and **Accuracy of 90.1%**, outperforming tree-based and distance-based alternatives.
* **Geographic Disparity:** Staten Island (85.25%) and Queens (84.17%) boast the highest 7-day closure rates, whereas Manhattan (76.57%) and the Bronx (77.69%) face the longest systemic backlogs.
* **Category Bottlenecks:** Quality-of-life and enforcement tickets (illegal parking, noise) close within 7 days >99% of the time, while tenant living condition complaints (unsanitary conditions: ~25%, plumbing: ~40%) take substantially longer to resolve.

---

## 📊 Dataset & Feature Engineering

Data was sourced directly via the **NYC Open Data Socrata API**, spanning closed requests submitted between **January 1, 2026, and April 30, 2026**.

* **Target Variable:** `Closed Within 7 Days` (Binary: `1` if `Resolution Days <= 7`, `0` otherwise).
* **Predictor Features:**
  * **Categorical / Organizational:** `Agency` (e.g., NYPD, DSNY, HPD, DEP, DOT), `Complaint Type`.
  * **Spatial:** `Borough` (Bronx, Brooklyn, Manhattan, Queens, Staten Island).
  * **Temporal:** Created `Day of Week` and `Month` extracted from raw timestamp strings.
* **Data Preprocessing:** Filtered for fully resolved records, imputed/handled null values, standardized borough naming, and vectorized categorical variables.

---

## 🔍 Exploratory Data Analysis & Operational Insights

### 1. Agency Workload vs. Resolution Efficiency
Agency workload does not strictly dictate closure velocity. High-volume agencies like the NYPD process hundreds of thousands of tickets with near-100% 7-day turnaround due to rapid on-site inspection workflows. In contrast, agencies dealing with complex physical inspections (e.g., HPD, DOB, DCWP) exhibit marked resolution bottlenecks despite moderate ticket volume.

![Agency Workload vs Efficiency](assets/agency_workload_efficiency.png)

### 2. Resolution Performance by Borough
Analysis of closure velocity across the five boroughs revealed distinct geographic tiers:

| Borough | 7-Day Closure Rate | Operational Observation |
| :--- | :---: | :--- |
| **Staten Island** | **85.25%** | Highest resolution rate citywide |
| **Queens** | **84.17%** | High compliance across residential and transit tickets |
| **Brooklyn** | **81.19%** | Moderate turnaround across dense mixed-use districts |
| **Bronx** | **77.69%** | Disproportionate volume of complex housing inspections |
| **Manhattan** | **76.57%** | Dense commercial and infrastructure load slowing response |

![Closure Rate by Borough](assets/borough_closure_rates.png)


### 3. Complaint Type Resolution Velocity
Resolution rates are heavily polarized based on the nature of municipal intervention:
* **Rapid Turnaround (~95–100%):** Illegal Parking, Blocked Driveway, Noise (Street/Sidewalk, Residential), Heat/Hot Water, Traffic Signal Condition.
* **Severe Turnaround Lag (<50%):** Street Condition (72%), Plumbing (40.5%), and Unsanitary Living Conditions (25.3%).

![Top Complaints vs Closure Rate](assets/complaint_type_rates.png)

---

## 🤖 Machine Learning Modeling & Evaluation

Because timely resolution is critical and municipal data can exhibit severe class skew, **F1-Score** was selected as the primary optimization metric to balance Precision and Recall. Models were evaluated using **3-Fold Cross-Validation**.

### Model Performance Comparison

| Model | CV Accuracy | CV Precision | CV Recall | CV F1-Score | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression** | **0.901** | **0.940** | **0.944** | **0.942** | 🏆 **Best Overall Model** |
| **Decision Tree** | 0.890 | 0.925 | 0.949 | 0.937 | Highly interpretable decision boundaries |
| **K-Nearest Neighbors (KNN)** | 0.889 | 0.928 | 0.942 | 0.935 | Strong baseline on sampled partitions |
| **Random Forest** | 0.866 | 0.871 | **0.990** | 0.927 | Highest sensitivity/recall rate |

> **Selection Rationale:** While Random Forest maximized recall (0.990), **Logistic Regression** delivered superior overall precision (0.940) and the highest CV F1-score (0.942) while providing clear coefficient interpretability for city planners.

### Predicted Outcomes & Probability Distribution
Evaluating probability distributions across test samples revealed sharp differentiation between routine complaints (concentrated between 0.80–1.0 probability) and chronic agency backlogs (peaking between 0.30–0.45 probability).

| Predicted Probability Distribution | Class Prediction Volume |
| :---: | :---: |
| ![Probability Distribution](assets/predicted_probabilities.png) | ![Prediction Counts](assets/predicted_outcomes.png) |

---

## 💡 Practical Implications & Recommendations

1. **Dynamic Resident SLA Expectations:** Integrate model scoring into the 311 intake portal to provide realistic, dynamic resolution windows rather than generic static timeframes.
2. **Early Intervention Routing:** Automatically flag incoming complaints predicted to exceed 7 days for priority triaging and secondary agency dispatch.
3. **Specialized Inspection Surge Teams:** Reallocate cross-agency inspectors to housing maintenance categories (plumbing, unsanitary conditions) to address the primary drivers of municipal backlog.
4. **Geographic Equity Audits:** Address systemic dispatch lags in Manhattan and the Bronx by standardizing inter-borough staffing and equipment depots.

---

## 🛠️ Tech Stack & Methods
* **Language & Core Libraries:** Python (`pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`)
* **API Integration:** Socrata Open Data API (NYC Open Data)
* **Modeling Techniques:** Binary Classification, Logistic Regression, Decision Trees, Random Forests, KNN, 3-Fold Cross-Validation
* **Metrics:** Accuracy, Precision, Recall, F1-Score

---

## 📁 Repository Structure

```text
311 Service Requests & Agency Responses/
├── README.md                              <- Executive case study and model findings
├── CIS 9660 Presentation (4).pptx         <- Full slide deck
├── assets/                                <- Exported visual artifacts
│   ├── agency_workload_efficiency.png     <- Slide 5 scatter plot
│   ├── borough_closure_rates.png          <- Slide 6 borough chart
│   ├── complaint_type_rates.png           <- Slide 6 complaint bar chart
│   ├── predicted_probabilities.png        <- Slide 10 probability histogram
│   └── predicted_outcomes.png             <- Slide 11 outcome breakdown
└── scripts/                               <- Model training and data extraction code
