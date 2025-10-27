import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
# ------------------ Page setup ------------------
st.set_page_config(page_title="Shopping EDA", page_icon="🛍️", layout="wide")
# put this near the top (after set_page_config)


# subtle top bar
st.markdown(
    """
    <style>
      .topbar {padding: 0.6rem 0; border-bottom: 1px solid rgba(128,128,128,0.15);}
      .metric > div {background: rgba(127,127,127,0.06); border-radius: 12px; padding: 0.6rem 0.8rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ Data loader ------------------


df = pd.read_csv("shopping_behavior_updated.csv")

# ------------------ Sidebar ------------------
with st.sidebar:
    st.header("🧭 Navigation")
    st.caption("Switch between pages below")
    # nav at bottom after dict definition — keep UX coherent
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.write("Quick EDA and sales insights. Use the filters on Page 1, then explore breakdowns on Page 2.")
    st.caption("Tip: Use the download at the bottom to export filtered data.")

# ------------------ PAGE 1 ------------------
def page1():
    st.title("🛍️ Shopping Behaviour Dashboard")
    st.markdown('<div class="topbar"></div>', unsafe_allow_html=True)

    # Filters
    left, right = st.columns(2)
    with left:
        season = st.selectbox(
            "Select Season",
            ["All"] + sorted(df["Season"].dropna().unique().tolist())
            if "Season" in df.columns else ["All"]
        )
    with right:
        payment = st.selectbox(
            "Select Payment Method",
            ["All"] + sorted(df["Payment Method"].dropna().unique().tolist())
            if "Payment Method" in df.columns else ["All"]
        )

    # Filtered copy
    filtered = df.copy()
    if "Season" in filtered.columns and season != "All":
        filtered = filtered[filtered["Season"] == season]
    if "Payment Method" in filtered.columns and payment != "All":
        filtered = filtered[filtered["Payment Method"] == payment]

    st.caption(f"Filtered: **{len(filtered):,} rows × {filtered.shape[1]} cols**")

    # KPIs
    k1, k2, k3 = st.columns(3)
    total_purchase = filtered["Purchase Amount (USD)"].sum() if "Purchase Amount (USD)" in filtered.columns else 0
    avg_rating = filtered["Review Rating"].mean() if "Review Rating" in filtered.columns else 0
    total_records = len(filtered)

    with k1:
        st.container().markdown('<div class="metric">', unsafe_allow_html=True)
        st.metric("Total Purchase (USD)", f"{total_purchase:,.0f}")
        st.container().markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.container().markdown('<div class="metric">', unsafe_allow_html=True)
        st.metric("Average Rating", f"{avg_rating:,.2f}")
        st.container().markdown('</div>', unsafe_allow_html=True)
    with k3:
        st.container().markdown('<div class="metric">', unsafe_allow_html=True)
        st.metric("Total Records", f"{total_records:,}")
        st.container().markdown('</div>', unsafe_allow_html=True)

    # Tabs — same charts, nicer defaults
    tab1, tab2, tab3 = st.tabs(["📦 Category Purchases", "⭐ Rating by Gender", "📈 Season Trend"])

    with tab1:
        if {"Category", "Purchase Amount (USD)"} <= set(filtered.columns) and not filtered.empty:
            cat_sum = (
                filtered.groupby("Category", as_index=False)["Purchase Amount (USD)"]
                .sum()
                .sort_values("Purchase Amount (USD)", ascending=False)
            )
            fig1 = px.bar(
                cat_sum,
                x="Category",
                y="Purchase Amount (USD)",
                title="Total Purchase by Category",
            )
            fig1.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Need columns: 'Category' & 'Purchase Amount (USD)' and non-empty data.")

    with tab2:
        if {"Gender", "Review Rating"} <= set(filtered.columns) and not filtered.empty:
            fig2 = px.box(
                filtered,
                x="Gender",
                y="Review Rating",
                title="Review Rating by Gender",
                points="all",
            )
            fig2.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Need columns: 'Gender' & 'Review Rating' and non-empty data.")

    with tab3:
        if {"Season", "Purchase Amount (USD)"} <= set(filtered.columns) and not filtered.empty:
            season_sum = (
                filtered.groupby("Season", as_index=False)["Purchase Amount (USD)"]
                .sum()
            )
            fig3 = px.line(
                season_sum,
                x="Season",
                y="Purchase Amount (USD)",
                markers=True,
                title="Seasonality of Purchases",
            )
            fig3.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Need columns: 'Season' & 'Purchase Amount (USD)' and non-empty data.")

    # Preview & download

# ------------------ PAGE 2 ------------------
def page2():
    st.title("📈 Sales Analysis & Insights")
    st.markdown('<div class="topbar"></div>', unsafe_allow_html=True)

    # 1) Category × Gender
    st.subheader("Overview by Category and Gender")
    if {"Category", "Gender", "Purchase Amount (USD)"} <= set(df.columns) and not df.empty:
        pivot = (
            df.groupby(["Category", "Gender"], as_index=False)["Purchase Amount (USD)"]
              .sum()
              .sort_values("Purchase Amount (USD)", ascending=False)
        )
        fig = px.bar(
            pivot,
            x="Category",
            y="Purchase Amount (USD)",
            color="Gender",
            barmode="group",
            title="Total Purchase by Category and Gender",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need columns: 'Category', 'Gender', 'Purchase Amount (USD)'.")

    # 2) Payment share
    st.subheader("Payment Method Preferences")
    if {"Payment Method", "Purchase Amount (USD)"} <= set(df.columns) and not df.empty:
        pay_sum = (
            df.groupby("Payment Method", as_index=False)["Purchase Amount (USD)"]
              .sum()
              .sort_values("Purchase Amount (USD)", ascending=False)
        )
        fig2 = px.pie(
            pay_sum,
            names="Payment Method",
            values="Purchase Amount (USD)",
            title="Share of Payment Methods",
            hole=0.35,
        )
        fig2.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Need columns: 'Payment Method', 'Purchase Amount (USD)'.")

    # 3) Correlations (nice, compact)
    
#------------------------PAGE3-----------------------------------------#
def page3():
    st.title("🌀 Animated Loyalty / Season Dynamics")
    st.markdown('<div class="topbar"></div>', unsafe_allow_html=True)

    # --- Check required columns ---
    needed_cols = {"Season", "Category", "Purchase Amount (USD)"}
    if not (needed_cols <= set(df.columns)):
        st.warning(f"Missing columns: {needed_cols - set(df.columns)}")
        return

    # --- Aggregate data ---
    g = (
        df.groupby(["Season", "Category"], as_index=False)["Purchase Amount (USD)"]
          .sum()
    )

    # --- Optional: make seasons ordered for nicer animation ---
    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    if set(season_order).issuperset(g["Season"].unique()):
        g["Season"] = pd.Categorical(g["Season"], season_order, ordered=True)
        g = g.sort_values(["Season", "Purchase Amount (USD)"], ascending=[True, False])

    # --- Keep y-axis fixed for smoother animation ---
    y_max = g["Purchase Amount (USD)"].max() * 1.1

    # --- Animated bar chart ---
    fig = px.bar(
        g,
        x="Category",
        y="Purchase Amount (USD)",
        color="Category",
        title="Animated Purchases by Category Across Seasons"
    )
    fig2=px.treemap(df,path=['Category','Item Purchased'],
    values='Purchase Amount (USD)',
    title='Revenue Treemap: Category → Item')
     # customize annotation style

    # --- Adjust animation speed (optional) ---

    fig2.update_traces(textinfo="label+value")

    # --- Display ---
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig2,useuse_container_width=True)
    

# ------------------ Router ------------------
pgs = {
    "🏠 Home": page1,
    "💹 Sales": page2,
    "🥶Product":page3
}
pg = st.sidebar.radio("Navigate Pages:", options=list(pgs.keys()))
pgs[pg]()
