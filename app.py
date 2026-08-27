import io
import json
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page configuration
st.set_page_config(
    page_title="Upgrade & Settlement Feasibility Calculator",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Upgrade & Settlement Feasibility Calculator")
st.markdown(
    "Ad-hoc calculator to check customer upgrade feasibility, buyout settlements,"
    " and true lease margins."
)
st.markdown("---")

# --- SESSION STATE INITIALIZATION FOR LOADED DATA ---
if "loaded_session" not in st.session_state:
  st.session_state.loaded_session = {}

session_defaults = st.session_state.loaded_session

# --- SECTION 0: CUSTOMER DETAILS & STATE LOAD/SAVE ---
st.header("0. Customer & Session")
col_cust1, col_cust2 = st.columns([2, 1])

with col_cust1:
  customer_name = st.text_input(
      "Customer / Company Name",
      value=session_defaults.get("customer_name", ""),
      placeholder="e.g. Acme Corp Ltd",
  )

with col_cust2:
  uploaded_file = st.file_uploader("Load Saved Session (.json)", type=["json"])
  if uploaded_file is not None:
    try:
      loaded_data = json.load(uploaded_file)
      st.session_state.loaded_session = loaded_data
      st.success("Session loaded! Refreshing...")
      st.rerun()
    except Exception as e:
      st.error(f"Error loading file: {e}")

# --- SECTION 1: AGREEMENT INPUTS ---
st.markdown("---")
st.header("1. Current Agreement Details")

col1, col2 = st.columns(2)

with col1:
  st.subheader("Lease Agreement")
  default_lease_time = session_defaults.get("lease_time_val", 0.0)
  default_lease_unit_idx = (
      0 if session_defaults.get("lease_time_unit", "Months") == "Months" else 1
  )
  default_cost_lease = session_defaults.get("cost_lease_monthly", 0.0)

  lease_time_val = st.number_input(
      "Remaining Time Value",
      min_value=0.0,
      value=float(default_lease_time),
      step=1.0,
      key="lease_val",
  )
  lease_time_unit = st.selectbox(
      "Unit", ["Months", "Years"], index=default_lease_unit_idx, key="lease_unit"
  )
  cost_lease_monthly = st.number_input(
      "Cost of Lease per Month (£)",
      min_value=0.0,
      value=float(default_cost_lease),
      step=10.0,
      key="lease_cost_input",
  )

with col2:
  st.subheader("Services Agreement")
  copy_from_lease = st.checkbox(
      "Copy time remaining from Lease",
      value=session_defaults.get("copy_from_lease", True),
  )

  if copy_from_lease:
    service_time_val = lease_time_val
    service_time_unit = lease_time_unit
    st.info(f"Using lease duration: {service_time_val} {service_time_unit}")
  else:
    default_serv_time = session_defaults.get("service_time_val", 0.0)
    default_serv_unit_idx = (
        0 if session_defaults.get("service_time_unit", "Months") == "Months" else 1
    )
    service_time_val = st.number_input(
        "Remaining Time Value",
        min_value=0.0,
        value=float(default_serv_time),
        step=1.0,
        key="serv_val",
    )
    service_time_unit = st.selectbox(
        "Unit", ["Months", "Years"], index=default_serv_unit_idx, key="serv_unit"
    )

  default_cost_serv = session_defaults.get("cost_services_monthly", 0.0)
  cost_services_monthly = st.number_input(
      "Cost of Services per Month (£)",
      min_value=0.0,
      value=float(default_cost_serv),
      step=10.0,
      key="serv_cost_input",
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
      help="30% of total remaining lease",
  )

with res_col3:
  st.metric(
      label="Total Services Buyout",
      value=f"£{total_services_buyout:,.2f}",
      help=f"{int(service_months)} months @ £{cost_services_monthly}/mo",
  )


# --- HELPER FUNCTION FOR COLORED CARDS ---
def render_colored_card(title, amount, help_text=""):
  if amount < 0:
    bg_color = "#FEE2E2"  # Light Red
    border_color = "#EF4444"  # Red
    text_color = "#991B1B"
    status_label = "DEFICIT"
  elif amount <= 3000:
    bg_color = "#FEF3C7"  # Light Amber
    border_color = "#F59E0B"  # Amber
    text_color = "#92400E"
    status_label = "TIGHT MARGIN"
  else:
    bg_color = "#D1FAE5"  # Light Green
    border_color = "#10B981"  # Green
    text_color = "#065F46"
    status_label = "HEALTHY MARGIN"

  card_html = f"""
    <div style="background-color: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 13px; font-weight: bold; color: {text_color}; text-transform: uppercase;">{title}</span>
        <h2 style="color: {text_color}; margin: 5px 0 5px 0;">£{amount:,.2f}</h2>
        <span style="background-color: {border_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;">{status_label}</span>
        {f'<p style="font-size: 11px; color: {text_color}; margin-top: 8px; margin-bottom: 0;">{help_text}</p>' if help_text else ''}
    </div>
    """
  st.markdown(card_html, unsafe_allow_html=True)


# --- SECTION 3: UPSELL & LEASE FUND ---
st.markdown("---")
st.header("3. Upsell Feasibility & Lease Fund")

default_handsets = session_defaults.get("handset_count", 0)
handset_count = st.number_input(
    "Number of Handsets",
    min_value=0,
    value=int(default_handsets),
    step=1,
    key="handset_input",
)
handset_unit_price = 1500.0
total_potential_finance = handset_count * handset_unit_price

include_services_in_fund = st.checkbox(
    "Include Services Buyout in Fund Deductions",
    value=session_defaults.get("include_services_in_fund", False),
    key="inc_serv_fund",
)

services_cost_to_add = (
    total_services_buyout if include_services_in_fund else 0.0
)

standard_total_buyout = total_lease_buyout + services_cost_to_add
discounted_total_buyout = lease_buyout_70_reduction + services_cost_to_add

standard_lease_fund = total_potential_finance - standard_total_buyout
discounted_lease_fund = total_potential_finance - discounted_total_buyout

st.subheader(
    f"Total Potential Finance Value: £{total_potential_finance:,.2f} "
    f"({handset_count} handsets @ £{1500:,.0f} each)"
)

fund_col1, fund_col2 = st.columns(2)

with fund_col1:
  render_colored_card(
      "Available Lease Fund (Standard Buyout)",
      standard_lease_fund,
      "Potential Finance minus Standard Lease Buyout",
  )

with fund_col2:
  render_colored_card(
      "Available Lease Fund (70% Reduced Buyout)",
      discounted_lease_fund,
      "Potential Finance minus 70% Reduced Buyout",
  )

# --- SECTION 4: NEW SOLUTION DEAL TERMS & NET LEASE MARGIN ---
st.markdown("---")
st.header("4. New Solution Deal Terms & Net Lease Margin")

col_new1, col_new2 = st.columns(2)

with col_new1:
  default_new_monthly = session_defaults.get("new_monthly_price", 0.0)
  new_monthly_price = st.number_input(
      "New Deal Monthly Price (£)",
      min_value=0.0,
      value=float(default_new_monthly),
      step=10.0,
      key="new_monthly_input",
      help="Enter the monthly cost charged to the customer for the new solution",
  )

with col_new2:
  default_new_term = session_defaults.get("new_contract_term_years", 3.0)
  new_contract_term_years = st.number_input(
      "New Contract Term (Years)",
      min_value=0.0,
      value=float(default_new_term),
      step=1.0,
      key="new_term_input",
      help="Enter the contract length in years (e.g., 3 or 5 years)",
  )

# Calculate total solution cost automatically from monthly price * term (in months)
total_new_solution_cost = new_monthly_price * (new_contract_term_years * 12)

st.info(
    f"Calculated Total New Solution Value: **£{total_new_solution_cost:,.2f}**"
    f" ({int(new_contract_term_years * 12)} months @"
    f" £{new_monthly_price:,.2f}/mo)"
)

standard_net_margin = standard_lease_fund - total_new_solution_cost
discounted_net_margin = discounted_lease_fund - total_new_solution_cost

margin_col1, margin_col2 = st.columns(2)

with margin_col1:
  render_colored_card(
      "Net Lease Margin (Standard Buyout)",
      standard_net_margin,
      "Available Lease Fund minus Total New Solution Value",
  )

with margin_col2:
  render_colored_card(
      "Net Lease Margin (70% Reduced Buyout)",
      discounted_net_margin,
      "Available Lease Fund (70% Reduced) minus Total New Solution Value",
  )

# --- SECTION 5: EXPORT & SAVE SESSION ---
st.markdown("---")
st.header("5. Save & Export Report")

current_state_dict = {
    "customer_name": customer_name,
    "lease_time_val": lease_time_val,
    "lease_time_unit": lease_time_unit,
    "cost_lease_monthly": cost_lease_monthly,
    "copy_from_lease": copy_from_lease,
    "service_time_val": service_time_val,
    "service_time_unit": service_time_unit,
    "cost_services_monthly": cost_services_monthly,
    "handset_count": handset_count,
    "include_services_in_fund": include_services_in_fund,
    "new_monthly_price": new_monthly_price,
    "new_contract_term_years": new_contract_term_years,
}

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
  json_str = json.dumps(current_state_dict, indent=4)
  safe_cust_filename = (
      customer_name.strip().replace(" ", "_").lower()
      if customer_name
      else "upgrade_calc_session"
  )
  st.download_button(
      label="💾 Save Session (Download JSON)",
      data=json_str,
      file_name=f"{safe_cust_filename}_session.json",
      mime="application/json",
  )

with col_dl2:

  def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=15,
    )

    elements.append(
        Paragraph("Upgrade & Settlement Feasibility Report", title_style)
    )
    cust_display = customer_name if customer_name else "Not Specified"
    elements.append(
        Paragraph(
            f"<b>Customer:</b> {cust_display} | <b>Date:</b> 2026-08-27",
            subtitle_style,
        )
    )

    data = [
        ["Agreement / Metric", "Details / Value"],
        [
            "Lease Remaining",
            (
                f"{lease_time_val} {lease_time_unit} @"
                f" £{cost_lease_monthly:,.2f}/mo"
            ),
        ],
        ["Total Lease Buyout", f"£{total_lease_buyout:,.2f}"],
        (
            "Lease Buyout (70% Reduction)",
            f"£{lease_buyout_70_reduction:,.2f} (-70%)",
        ),
        [
            "Services Remaining",
            (
                f"{service_time_val} {service_time_unit} @"
                f" £{cost_services_monthly:,.2f}/mo"
            ),
        ],
        ["Total Services Buyout", f"£{total_services_buyout:,.2f}"],
        [
            "Potential Finance ({0} Handsets @ £1,500)".format(handset_count),
            f"£{total_potential_finance:,.2f}",
        ],
        ["Available Lease Fund (Standard)", f"£{standard_lease_fund:,.2f}"],
        (
            "Available Lease Fund (70% Reduced)",
            f"£{discounted_lease_fund:,.2f}",
        ),
        [
            "New Solution Deal Terms",
            (
                f"£{new_monthly_price:,.2f}/mo for"
                f" {new_contract_term_years} years"
            ),
        ],
        [
            "Total New Solution Cost",
            f"£{total_new_solution_cost:,.2f}",
        ],
        ["Net Lease Margin (Standard Buyout)", f"£{standard_net_margin:,.2f}"],
        (
            "Net Lease Margin (70% Reduced Buyout)",
            f"£{discounted_net_margin:,.2f}",
        ),
    ]

    t = Table(data, colWidths=[240, 260])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#F3F4F6")],
            ),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
        ])
    )

    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


  pdf_data = generate_pdf()
  st.download_button(
      label="📄 Download PDF Report",
      data=pdf_data,
      file_name=f"{safe_cust_filename}_report.pdf",
      mime="application/pdf",
  )
