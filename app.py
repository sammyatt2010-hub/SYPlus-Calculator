import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Upgrade & Settlement Feasibility Calculator",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Upgrade & Settlement Feasibility Calculator")
st.markdown(
    "Ad-hoc calculator to check customer upgrade feasibility, buyout settlements, and potential upsell margins."
)
st.markdown("---")

# --- SECTION 1: AGREEMENT INPUTS ---
st.header("1. Current Agreement Details")

col1, col2 = st.columns(2)

with col1:
  st.subheader("Lease Agreement")
  lease_time_val = st.number_input(
      "Remaining Time Value", min_value=0.0, value=12.0, step=1.0, key="lease_val"
  )
  lease_time_unit = st.selectbox(
      "Unit", ["Months", "Years"], key="lease_unit"
  )
  cost_lease_monthly = st.number_input(
      "Cost of Lease per Month (£)", min_value=0.0, value=100.0, step=10.0
  )

with col2:
  st.subheader("Services Agreement")
  copy_from_lease = st.checkbox("Copy time remaining from Lease", value=True)

  if copy_from_lease:
    service_time_val = lease_time_val
    service_time_unit = lease_time_unit
    st.info(f"Using lease duration: {service_time_val} {service_time_unit}")
  else:
    service_time_val = st.number_input(
        "Remaining Time Value",
        min_value=0.0,
        value=12.0,
        step=1.0,
        key="serv_val",
    )
    service_time_unit = st.selectbox(
        "Unit", ["Months", "Years"], key="serv_unit"
    )

  cost_services_monthly = st.number_input(
      "Cost of Services per Month (£)", min_value=0.0, value=50.0, step=10.0
  )

# --- CONVERT TO MONTHS FOR CALCULATION ---
lease_months = (
    lease_time_val
    if lease_time_unit == "Months"
    else lease_time_val * 12
)
service_months = (
    service_time_val
    if service_time_unit == "Months"
    else service_time_val * 12
)

# --- SECTION 2: SETTLEMENT CALCULATIONS ---
total_lease_buyout = lease_months * cost_lease_monthly
lease_buyout_70_reduction = total_lease_buyout * 0.30  # 70% off means paying 30%
total_services_buyout = service_months * cost_services_monthly

st.markdown("---")
st.header("2. Settlement Figures")

res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
  st.metric(
      label="Total Lease Buyout",
      value=f"£{total_lease_buyout:,.2f}",
      help=f"{int(lease_months)} months @ £{cost_lease_monthly}/mo",
  )

with res_col2:
  st.metric(
      label="Lease Buyout (70% Reduction)",
      value=f"£{lease_buyout_70_reduction:,.2f}",
      delta="-70%",
      delta_color="inverse",
  )

with res_col3:
  st.metric(
      label="Total Services Buyout",
      value=f"£{total_services_buyout:,.2f}",
      help=f"{int(service_months)} months @ £{cost_services_monthly}/mo",
  )

# --- SECTION 3: UPSELL FEASIBILITY ---
st.markdown("---")
st.header("3. Upsell Feasibility & Potential Margin")

handset_count = st.number_input(
    "Number of Handsets", min_value=0, value=2, step=1
)
handset_unit_price = 1500.0
total_potential_finance = handset_count * handset_unit_price

st.subheader(
    f"Total Potential Finance Value: £{total_potential_finance:,.2f} "
    f"({handset_count} handsets @ £{1500:,.0f} each)"
)

# Calculate remaining profit/margin based on lease buyouts (Standard vs 70% Reduction)
standard_margin = total_potential_finance - total_lease_buyout
discounted_margin = total_potential_finance - lease_buyout_70_reduction

margin_col1, margin_col2 = st.columns(2)

with margin_col1:
  st.metric(
      label="Estimated Margin (Standard Lease Buyout)",
      value=f"£{standard_margin:,.2f}",
      help="Potential Finance minus Standard Lease Buyout",
  )

with margin_col2:
  st.metric(
      label="Estimated Margin (70% Reduced Buyout)",
      value=f"£{discounted_margin:,.2f}",
      help="Potential Finance minus 70% Reduced Lease Buyout",
  )
