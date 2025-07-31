import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Lane Frequency Dashboard", layout="wide")

st.title("Lane Frequency Dashboard (YTD)")

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # =========================
    # DATA CLEANING
    # =========================
    origin_col = 'ORIG'
    dest_col = 'DEST'
    del_time_col = 'DEL TIME'

    # Filter rows with valid delivery times
    df = df[df[del_time_col].notna()]

    # Strip spaces from ORIG and DEST
    df[origin_col] = df[origin_col].astype(str).str.strip()
    df[dest_col] = df[dest_col].astype(str).str.strip()

    # =========================
    # KPI METRICS
    # =========================
    total_shipments = len(df)
    total_origins = df[origin_col].nunique()
    total_destinations = df[dest_col].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Shipments (YTD)", f"{total_shipments:,}")
    col2.metric("Unique Origins", f"{total_origins}")
    col3.metric("Unique Destinations", f"{total_destinations}")

    st.markdown("---")

    # =========================
    # ORIGIN ANALYSIS
    # =========================
    st.subheader("Top Origins")
    origin_counts = df[origin_col].value_counts().reset_index()
    origin_counts.columns = ['Origin', 'Frequency']

    fig_origin = px.bar(
        origin_counts.head(20),
        x='Origin',
        y='Frequency',
        text='Frequency',
        color='Frequency',
        color_continuous_scale='Blues'
    )
    fig_origin.update_traces(textposition='outside')
    fig_origin.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_origin, use_container_width=True)

    # =========================
    # DESTINATION ANALYSIS
    # =========================
    st.subheader("Top Destinations")
    dest_counts = df[dest_col].value_counts().reset_index()
    dest_counts.columns = ['Destination', 'Frequency']

    fig_dest = px.bar(
        dest_counts.head(20),
        x='Destination',
        y='Frequency',
        text='Frequency',
        color='Frequency',
        color_continuous_scale='Greens'
    )
    fig_dest.update_traces(textposition='outside')
    fig_dest.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_dest, use_container_width=True)

    # =========================
    # LANE ANALYSIS
    # =========================
    st.subheader("Top Lanes (Origin → Destination)")
    lane_counts = df.groupby([origin_col, dest_col]).size().reset_index(name='Frequency')
    lane_counts['Lane'] = lane_counts[origin_col] + " → " + lane_counts[dest_col]
    lane_counts = lane_counts.sort_values('Frequency', ascending=False).head(20)

    fig_lanes = px.bar(
        lane_counts,
        x='Lane',
        y='Frequency',
        text='Frequency',
        color='Frequency',
        color_continuous_scale='YlOrRd'
    )
    fig_lanes.update_traces(textposition='outside')
    fig_lanes.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_lanes, use_container_width=True)

    # =========================
    # HEATMAP OF ALL LANES
    # =========================
    st.subheader("Lane Heatmap")
    heatmap_data = df.groupby([origin_col, dest_col]).size().reset_index(name='Frequency')
    heatmap_pivot = heatmap_data.pivot(index=origin_col, columns=dest_col, values='Frequency').fillna(0)

    fig_heatmap = px.imshow(
        heatmap_pivot,
        text_auto=True,
        aspect='auto',
        color_continuous_scale='Blues'
    )
    fig_heatmap.update_layout(height=600)
    st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    st.warning("Please upload an Excel file to view the dashboard.")
