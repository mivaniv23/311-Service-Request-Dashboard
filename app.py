import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Page setup
st.set_page_config(page_title="311 Service Request Dashboard", layout="wide")
st.title("311 Service Request Dashboard")
st.write("Explore Philadelphia 311 service requests from 2025.")

# Load the prepared CSV file (keep it in the same folder as app.py)
@st.cache_data
def load_data():
    data = pd.read_csv("311_2025_dashboard.csv")
    data["request_date"] = pd.to_datetime(data["request_date"], errors="coerce")
    data["resolution_days"] = pd.to_numeric(data["resolution_days"], errors="coerce")
    data = data.dropna(subset=["request_date"])
    return data

df = load_data()

# Date controls replace START_DATE and END_DATE in the notebook
min_date = df["request_date"].min().date()
max_date = df["request_date"].max().date()

left, right = st.columns(2)
with left:
    start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
with right:
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.error("The start date must be on or before the end date.")
    st.stop()

# Filter the rows to include both selected dates
filtered_df = df[
    (df["request_date"].dt.date >= start_date) &
    (df["request_date"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning("No requests were found for the selected dates.")
    st.stop()

# Simple summary metrics
total_requests = len(filtered_df)
closed_requests = filtered_df["status"].astype(str).str.lower().eq("closed").sum()
open_requests = filtered_df["status"].astype(str).str.lower().eq("open").sum()
average_resolution = filtered_df["resolution_days"].dropna().mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total requests", f"{total_requests:,}")
m2.metric("Closed requests", f"{closed_requests:,}")
m3.metric("Open requests", f"{open_requests:,}")
m4.metric(
    "Average resolution (days)",
    f"{average_resolution:.2f}" if pd.notna(average_resolution) else "N/A"
)

st.caption(f"Showing {start_date:%b %d, %Y} through {end_date:%b %d, %Y}")

# Chart 1: top 10 request types
st.subheader("Top 10 Types of 311 Requests")
top_requests = filtered_df["service_name"].value_counts().head(10).sort_values()
fig1, ax1 = plt.subplots(figsize=(8, 5))
top_requests.plot(kind="barh", ax=ax1)
ax1.set_xlabel("Number of Requests")
ax1.set_ylabel("Service Type")
fig1.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# Chart 2: requests over time
st.subheader("311 Requests Over Time")
requests_by_day = filtered_df.groupby(filtered_df["request_date"].dt.date).size()
fig2, ax2 = plt.subplots(figsize=(9, 4))
requests_by_day.plot(kind="line", ax=ax2)
ax2.set_xlabel("Request Date")
ax2.set_ylabel("Number of Requests")
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)
