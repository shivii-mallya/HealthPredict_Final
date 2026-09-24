import json
from pathlib import Path
import pandas as pd
from cdc_service import get_available_geographies, get_cdc_summary

BASE_DIR = Path(__file__).resolve().parent

REQUIRED_ADMISSION_COLUMNS = [
    "Date", "Total_Admissions", "ICU_Admissions", "General_Admissions",
    "Total_Bed_Days", "Staff_Required", "Medical_Supply_Usage"
]

def load_data(admission_file=None, inventory_file=None):
    """Load the cleaned project Excel files."""
    admission_file = admission_file or BASE_DIR / "Daily_Admissions_Data (1).xlsx"
    inventory_file = inventory_file or BASE_DIR / "Inventory_Data.xlsx"

    admissions = pd.read_excel(admission_file, sheet_name="Daily_Admissions")
    inventory = pd.read_excel(inventory_file, sheet_name="Inventory_Data")

    admissions["Date"] = pd.to_datetime(admissions["Date"], errors="coerce")
    admissions = admissions[admissions["Date"].notna()].copy()
    admissions = admissions[
        pd.to_numeric(admissions["Total_Admissions"], errors="coerce").notna()
    ].copy()

    for col in REQUIRED_ADMISSION_COLUMNS[1:]:
        admissions[col] = pd.to_numeric(admissions[col], errors="coerce")

    inventory["Date"] = pd.to_datetime(inventory["Date"], errors="coerce")
    inventory = inventory[inventory["Date"].notna()].copy()
    inventory["Inventory_Available"] = pd.to_numeric(
        inventory["Inventory_Available"], errors="coerce"
    )
    inventory = inventory.dropna(
        subset=["Resource_Type", "Inventory_Available"]
    )

    return admissions, inventory


def calculate_historical_rates(admissions):
    """Calculate transparent resource ratios from the historical data."""
    total = admissions["Total_Admissions"].sum()
    if total <= 0:
        raise ValueError("Total historical admissions must be greater than zero.")

    return {
        "icu_rate": admissions["ICU_Admissions"].sum() / total,
        "general_rate": admissions["General_Admissions"].sum() / total,
        "bed_days_per_admission": admissions["Total_Bed_Days"].sum() / total,
        "staff_per_admission": admissions["Staff_Required"].sum() / total,
        "supply_units_per_admission": admissions["Medical_Supply_Usage"].sum() / total,
    }


def calculate_requirements(predicted_total_admissions, rates):
    """
    Convert Member 1's predicted total admissions into resource requirements.
    This is intentionally simple and explainable for the hackathon.
    """
    if predicted_total_admissions <= 0:
        raise ValueError("Predicted admissions must be greater than zero.")

    return {
        "predicted_total_admissions": int(round(predicted_total_admissions)),
        "required_icu_admissions": int(round(
            predicted_total_admissions * rates["icu_rate"]
        )),
        "required_general_admissions": int(round(
            predicted_total_admissions * rates["general_rate"]
        )),
        "required_bed_days": int(round(
            predicted_total_admissions * rates["bed_days_per_admission"]
        )),
        "required_staff": int(round(
            predicted_total_admissions * rates["staff_per_admission"]
        )),
        "required_medical_supply_units": int(round(
            predicted_total_admissions * rates["supply_units_per_admission"]
        )),
    }


def get_latest_inventory(inventory):
    """Return the latest known stock for each inventory resource."""
    latest = (
        inventory.sort_values("Date")
        .groupby("Resource_Type", as_index=False)
        .tail(1)
    )
    return latest[["Date", "Resource_Type", "Inventory_Available"]].copy()


def calculate_inventory_status(required_supply_units, inventory):
    """
    Compare predicted medical-supply demand against the latest total inventory.
    This is a prototype-level check because the current admissions dataset does
    not map each usage unit to a specific inventory item.
    """
    supply_items = ["Gloves", "IV Drip", "Surgical Mask"]
    latest = get_latest_inventory(inventory)
    supply_stock = latest[
        latest["Resource_Type"].isin(supply_items)
    ]["Inventory_Available"].sum()

    difference = supply_stock - required_supply_units

    if difference < 0:
        status = "SHORTAGE"
    else:
        status = "SUFFICIENT"

    return {
        "tracked_supply_stock": int(round(supply_stock)),
        "required_supply_units": int(round(required_supply_units)),
        "surplus_or_shortage": int(round(difference)),
        "status": status,
        "tracked_items": supply_items,
    }


def build_resource_report(predicted_total_admissions, admissions, inventory):
    """Main function used by Member 4 / the dashboard."""
    rates = calculate_historical_rates(admissions)
    requirements = calculate_requirements(predicted_total_admissions, rates)
    supply_status = calculate_inventory_status(
        requirements["required_medical_supply_units"], inventory
    )

    report = {
        **requirements,
        "resource_status": {
            "medical_supplies": supply_status["status"],
        },
        "medical_supply_status": supply_status,
        "historical_rates": rates,
    }
    return report


if __name__ == "__main__":
    admissions, inventory = load_data()
    forecast = pd.read_csv(BASE_DIR / "forecast.csv")
    predicted = forecast["Predicted_Admissions"].sum()

    report = build_resource_report(predicted, admissions, inventory)
    dashboard_data = {
        "forecast": [
        {
            "date": row["Date"],
            "expected": float(row["Predicted_Admissions"]),
            "lower": round(max(0, float(row["Predicted_Admissions"]) - 2), 2),
            "upper": round(float(row["Predicted_Admissions"]) + 2, 2)
        }
        for _, row in forecast.iterrows()
],
    }

    with open(BASE_DIR / "dashboard_data.json", "w") as f:
        json.dump(dashboard_data, f, indent=4)

        # Generate CDC data for the frontend
    cdc_geographies = get_available_geographies()
    cdc_summaries = {}

    for geography in cdc_geographies:
        try:
            cdc_summaries[geography] = get_cdc_summary(geography)
        except Exception as e:
            print(f"CDC data unavailable for {geography}: {e}")

    cdc_dashboard_data = {
        "geographies": cdc_geographies,
        "summaries": cdc_summaries
    }

    with open(BASE_DIR / "cdc_data.json", "w") as f:
        json.dump(cdc_dashboard_data, f, indent=4)

    print("\n=== HOSPITAL RESOURCE ALLOCATION BACKEND ===")
    print(f"ML 7-day forecast: {predicted:.2f} admissions")
    print(f"Required ICU admissions: {report['required_icu_admissions']}")
    print(f"Required general admissions: {report['required_general_admissions']}")
    print(f"Required bed-days: {report['required_bed_days']}")
    print(f"Required staff: {report['required_staff']}")
    print(f"Required medical-supply units: {report['required_medical_supply_units']}")
    print(f"Tracked supply stock: {report['medical_supply_status']['tracked_supply_stock']}")
    print(f"Supply status: {report['medical_supply_status']['status']}")

