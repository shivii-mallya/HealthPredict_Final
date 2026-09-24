# Predictive Hospital Resource Allocation

## Overview

Predictive Hospital Resource Allocation is an AI-powered healthcare resource planning system designed to help hospitals anticipate patient demand and prepare resources in advance.

The system uses historical hospital admission data to forecast short-term patient demand and translates those predictions into estimated requirements for ICU capacity, general admissions, bed-days, medical supplies, and staff.

The dashboard also provides external health-context information from CDC respiratory disease surveillance data, helping users interpret broader COVID-19, influenza, and RSV activity alongside the hospital's own demand forecast.

The project focuses on supporting sustainable healthcare resource utilization, reducing shortages, and improving preparedness during periods of increased healthcare demand.

---

## Problem Statement

Public healthcare systems can face resource shortages during periods of increased patient admissions. This can result in:

- Overcrowded emergency and hospital facilities
- Insufficient ICU and general bed capacity
- Medical supply shortages
- Increased pressure on healthcare staff
- Longer patient waiting times
- Unequal access to available healthcare resources

Traditional resource planning can be reactive. This project aims to provide a predictive approach by using historical admission patterns to estimate upcoming demand and translate that demand into resource requirements.

---

## Key Features

### 1. Hospital Demand Forecasting

The system uses historical hospital admission data to generate a short-term 7-day admission forecast.

The forecasting pipeline uses:

- Historical admission counts
- Lag-based features
- Rolling averages
- Day-of-week information
- Random Forest Regression

The forecast provides expected daily admissions along with a planning range.

---

### 2. External Health Context — CDC

CDC respiratory disease surveillance data is presented between the hospital demand forecast and resource planning sections.

The CDC section provides:

- COVID-19 emergency-department visit percentage
- Influenza emergency-department visit percentage
- RSV emergency-department visit percentage
- Combined respiratory activity
- Recent respiratory activity trends

This information acts as external epidemiological context for resource planning.

CDC data is not used to retrain or modify the hospital demand forecasting model.

**Data source:** CDC National Syndromic Surveillance Program (NSSP)

---

### 3. Resource Planning

The predicted admission demand is converted into estimated resource requirements using historical hospital resource utilization rates.

The system estimates:

- ICU admissions required
- General admissions required
- Bed-days required
- Staff required
- Medical supply units required

The calculations are designed to remain transparent and explainable.

---

### 4. Resource Shortage Detection

The system compares predicted medical supply requirements with the latest available inventory.

It identifies whether tracked supplies are:

- Sufficient
- In shortage

The dashboard also displays the estimated surplus or shortage.

---

### 5. Inventory & Staffing Insights

The dashboard provides resource-related information to help planners understand expected requirements and available resources.

Inventory information is derived from the provided hospital inventory data.

---

### 6. Equity & Access

The dashboard includes an Equity & Access section focused on healthcare accessibility and resource availability.

The unnecessary search-bar feature was removed to keep the section simpler and more focused on the available project data.

---

## Dashboard Flow

The dashboard is organized as:

```text
Hospital Overview
        ↓
7-Day Hospital Demand Forecast
        ↓
External Health Context (CDC)
        ↓
Required Resource Planning
        ↓
Resource Shortages & Alerts
        ↓
Inventory & Staffing
        ↓
Equity & Access

This flow allows users to move from:

Current situation → Expected demand → External health context → Required resources → Resource gaps → Access considerations

## System Architecture
                 Hospital Data
                      ↓
              Historical Admissions
                      ↓
              Data Preparation
                      ↓
             Feature Engineering
                      ↓
             Random Forest Model
                      ↓
              7-Day Forecast
                      ↓
          ┌───────────┴───────────┐
          ↓                       ↓
  CDC Health Context       Resource Planning
          ↓                       ↓
 COVID / Flu / RSV       ICU / Beds / Staff /
   Trends & Activity       Medical Supplies
                                  ↓
                         Inventory Comparison
                                  ↓
                         Shortage / Surplus
                                  ↓
                              Dashboard


## Machine Learning
Model

Random Forest Regressor

Features

The forecasting model uses:

Lag 1 admission count
Lag 7 admission count
3-day rolling average
7-day rolling average
Day of week
Evaluation Metrics

The model is evaluated using:

Mean Absolute Error (MAE)
Root Mean Squared Error (RMSE)

The current prototype achieved:

MAE  : 2.76
RMSE : 3.84

These results should be interpreted as a prototype evaluation because the provided hospital dataset contains only a limited period of daily observations.

Data Sources
Organization-Provided Data

The project uses organization-provided sample datasets including:

Patient admission data
Inventory data
Vendor data
Staff data
Financial data
Hospital directory data
External Data

CDC respiratory emergency-department surveillance data is used as an external health-context layer.

CDC data includes:

COVID-19
Influenza
RSV
Combined respiratory activity
Technology Stack
Machine Learning & Data Processing
Python
Pandas
NumPy
Scikit-learn
Dashboard
HTML
CSS
JavaScript
Data Storage / Exchange
CSV
JSON
Excel
Project Structure
Project/
│
├── Backend/
│   ├── backend.py
│   ├── cdc_service.py
│   ├── forecast.csv
│   ├── dashboard_data.json
│   ├── cdc_data.json
│   ├── Daily_Admissions_Data (1).xlsx
│   ├── Inventory_Data.xlsx
│   ├── requirements.txt
│   └── README.md
│
└── Frontend/
    ├── index.html
    └── dashboard_data.json

## How It Works
Step 1 — Historical Data

Historical hospital admission and resource data is loaded and cleaned.

Step 2 — Demand Forecasting

Admission data is converted into daily observations and used to create lag and rolling-average features.

A Random Forest model predicts admission demand for the next seven days.

Step 3 — External Health Context

CDC respiratory surveillance data is processed to obtain recent COVID-19, influenza, and RSV activity.

Step 4 — Resource Estimation

The predicted admission demand is converted into estimated requirements for ICU admissions, general admissions, bed-days, staff, and medical supplies.

Step 5 — Inventory Analysis

Required medical supplies are compared with the latest available inventory to identify potential shortages or surplus.

Step 6 — Dashboard

All outputs are presented through a single dashboard for easier interpretation and planning.

Sustainability & Impact

The project supports sustainable healthcare planning by helping hospitals anticipate demand instead of relying only on reactive resource allocation.

Potential benefits include:

Better resource preparedness
Reduced medical supply wastage
Earlier identification of shortages
Improved staff planning
Better utilization of hospital capacity
Support for more equitable access to healthcare resources
Limitations

This is a hackathon prototype and has several limitations:

The hospital admission dataset covers a limited time period.
The current forecasting model is intended for short-term demand prediction.
The available data is not sufficient for reliable long-term seasonal forecasting.
CDC surveillance data represents U.S. emergency-department surveillance and is therefore used as external context rather than as a direct input to the hospital forecasting model.
Resource requirements are estimated using historical resource-to-admission ratios.
Current inventory analysis operates at a prototype level and does not map every predicted usage unit to an individual inventory item.
Future Scope

Potential future improvements include:

Larger historical datasets for stronger seasonal forecasting
More advanced time-series models
Real-time hospital data integration
Region-specific demand forecasting
More detailed resource-to-inventory mapping
Automated alerts for upcoming shortages
Improved healthcare accessibility and equity analysis
Integration with live hospital management systems
Team

Developed as part of a hackathon project under the theme:

Sustainable Healthcare

Aligned with:

SDG 3 — Good Health and Well-being

SDG 10 — Reduced Inequalities

## Disclaimer

This project is a predictive analytics prototype developed for demonstration and hackathon purposes. Its predictions should not be treated as medical advice or as a replacement for professional hospital resource-management decisions.