from pathlib import Path
import pandas as pd


# Find the CDC CSV in the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent


def find_cdc_file():
    files = list(PROJECT_DIR.glob("NSSP_*.csv"))

    if not files:
        raise FileNotFoundError(
            "CDC CSV file not found in the project folder."
        )

    return files[0]


def load_cdc_data(geography="United States"):
    csv_path = find_cdc_file()

    required_columns = [
        "week_end",
        "geography",
        "county",
        "percent_visits_combined",
        "percent_visits_covid",
        "percent_visits_influenza",
        "percent_visits_rsv"
    ]

    # Load CDC CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise RuntimeError(
            f"Unable to read CDC CSV: {e}"
        )

    # Check required columns
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CDC CSV is missing columns: {missing_columns}"
        )

    # Convert week_end to datetime
    df["week_end"] = pd.to_datetime(
        df["week_end"],
        errors="coerce"
    )

    # Remove rows with invalid dates
    df = df.dropna(subset=["week_end"])

    # Keep aggregate county data only
    df = df[
        df["county"].astype(str).str.strip().str.lower() == "all"
    ]

    # Filter by selected geography
    if geography:
        df = df[
            df["geography"].astype(str).str.strip().str.lower()
            == geography.strip().lower()
        ]

    # Check if data remains
    if df.empty:
        raise ValueError(
            f"No CDC data available for geography: {geography}"
        )

    # Convert percentage columns to numeric
    numeric_columns = [
        "percent_visits_combined",
        "percent_visits_covid",
        "percent_visits_influenza",
        "percent_visits_rsv"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Calculate respiratory activity
    #
    # Respiratory Activity =
    # COVID % + Influenza % + RSV %
    #
    df["respiratory_activity"] = df[
        [
            "percent_visits_covid",
            "percent_visits_influenza",
            "percent_visits_rsv"
        ]
    ].sum(
        axis=1,
        min_count=1
    )

    # Sort chronologically
    df = df.sort_values("week_end")

    return df


def get_available_geographies():
    """
    Return all geographic regions available
    in the CDC dataset.
    """

    csv_path = find_cdc_file()

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise RuntimeError(
            f"Unable to read CDC CSV: {e}"
        )

    # Keep aggregate county data
    df = df[
        df["county"].astype(str).str.strip().str.lower() == "all"
    ]

    # Get unique geography names
    geographies = sorted(
        df["geography"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return geographies


def get_cdc_summary(
    geography="United States",
    recent_weeks=12
):
    """
    Return the latest CDC observation and
    recent historical respiratory trend
    for the selected geography.
    """

    df = load_cdc_data(geography)

    # Latest observation
    latest = df.iloc[-1]

    # Recent historical observations
    trend_df = df.tail(recent_weeks)

    # Latest data
    latest_data = {
        "week": latest["week_end"].strftime("%Y-%m-%d"),
        "geography": latest["geography"],
        "covid": round(
            float(latest["percent_visits_covid"]), 2
        ),
        "influenza": round(
            float(latest["percent_visits_influenza"]), 2
        ),
        "rsv": round(
            float(latest["percent_visits_rsv"]), 2
        ),
        "respiratory_activity": round(
            float(latest["respiratory_activity"]), 2
        )
    }

    # Historical trend
    trend = []

    for _, row in trend_df.iterrows():

        trend.append({
            "week": row["week_end"].strftime("%Y-%m-%d"),
            "geography": row["geography"],
            "covid": round(
                float(row["percent_visits_covid"]), 2
            ),
            "influenza": round(
                float(row["percent_visits_influenza"]), 2
            ),
            "rsv": round(
                float(row["percent_visits_rsv"]), 2
            ),
            "respiratory_activity": round(
                float(row["respiratory_activity"]), 2
            )
        })

    return {
        "latest": latest_data,
        "trend": trend
    }


# Test the CDC module directly
if __name__ == "__main__":

    print("=== CDC RESPIRATORY SURVEILLANCE ===")

    try:
        # Test default United States data
        result = get_cdc_summary()

        print("\nLatest observation:")
        print(result["latest"])

        print("\nRecent trend:")

        for row in result["trend"]:
            print(row)

        # Test available regions
        print("\nAvailable regions:")

        regions = get_available_geographies()

        print(f"Total regions: {len(regions)}")

        for region in regions:
            print(region)

    except Exception as e:
        print(
            f"\nCDC processing error: {e}"
        )