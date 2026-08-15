import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Resale Hunter Mobile",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.block-container {
    max-width: 760px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}
div[data-testid="stMetric"] {
    background: rgba(128,128,128,0.08);
    padding: 12px;
    border-radius: 14px;
}
.stButton > button, .stDownloadButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    font-size: 1rem;
}
div[data-testid="stNumberInput"] input {
    min-height: 44px;
}
.mobile-card {
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
}
.mobile-card h3 {
    margin-top: 0;
    margin-bottom: 6px;
}
.big-profit {
    font-size: 1.35rem;
    font-weight: 700;
}
.muted {
    opacity: 0.72;
    font-size: 0.92rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🔎 Resale Hunter")
st.caption("Phone-friendly test mode")

with st.expander("⚙️ Alert settings", expanded=False):
    min_profit = st.number_input("Minimum profit ($)", 0.0, value=30.0, step=5.0)
    min_roi = st.number_input("Minimum ROI (%)", 0.0, value=25.0, step=5.0)
    min_confidence = st.number_input("Minimum confidence", 0, 100, value=70, step=5)
    tax_pct = st.number_input("Purchase tax (%)", 0.0, 15.0, value=6.35, step=0.05)
    fee_pct = st.number_input("Selling fee (%)", 0.0, 40.0, value=13.25, step=0.25)
    outbound_shipping = st.number_input("Outbound shipping ($)", 0.0, value=10.0, step=1.0)

sample = pd.read_csv("sample_deals.csv")

def calc(row):
    buy = float(row["buy_price"])
    resale = float(row["estimated_resale_price"])
    tax = buy * tax_pct / 100
    acquisition = buy + tax
    fees = resale * fee_pct / 100
    profit = resale - acquisition - fees - outbound_shipping
    roi = profit / acquisition * 100 if acquisition else 0
    qualifies = (
        profit >= min_profit
        and roi >= min_roi
        and float(row["confidence_score"]) >= min_confidence
    )
    return pd.Series({
        "net_profit": profit,
        "roi_pct": roi,
        "qualifies": qualifies
    })

df = pd.concat([sample, sample.apply(calc, axis=1)], axis=1)
df = df.sort_values(["qualifies","net_profit","roi_pct"], ascending=[False,False,False])
alerts = df[df["qualifies"]].copy()

c1, c2 = st.columns(2)
c1.metric("Scanned", len(df))
c2.metric("Alerts", len(alerts))

c3, c4 = st.columns(2)
c3.metric("Best profit", f"${df['net_profit'].max():,.0f}")
c4.metric("Best ROI", f"{df['roi_pct'].max():.0f}%")

st.subheader("🔥 Best opportunities")

if len(alerts) == 0:
    st.info("No listings pass your current settings.")
else:
    for _, r in alerts.iterrows():
        st.markdown(
            f"""
            <div class="mobile-card">
                <h3>{r['product']}</h3>
                <div class="muted">{r['source']}</div>
                <p>
                    Buy: <b>${r['buy_price']:.2f}</b><br>
                    Est. resale: <b>${r['estimated_resale_price']:.2f}</b>
                </p>
                <div class="big-profit">Est. profit: ${r['net_profit']:.2f}</div>
                <p>ROI: <b>{r['roi_pct']:.1f}%</b> · Confidence: <b>{int(r['confidence_score'])}/100</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.link_button("Open listing", r["url"])

st.subheader("All scanned listings")

for _, r in df.iterrows():
    status = "✅ Alert" if r["qualifies"] else "— Pass"
    with st.expander(f"{status} · {r['product']}"):
        st.write(f"**Source:** {r['source']}")
        st.write(f"**Buy:** ${r['buy_price']:.2f}")
        st.write(f"**Estimated resale:** ${r['estimated_resale_price']:.2f}")
        st.write(f"**Estimated profit:** ${r['net_profit']:.2f}")
        st.write(f"**ROI:** {r['roi_pct']:.1f}%")
        st.write(f"**Confidence:** {int(r['confidence_score'])}/100")
        st.link_button("Open listing", r["url"])

st.divider()

st.subheader("➕ Test your own deal")
product = st.text_input("Product name")
buy = st.number_input("Buy price", min_value=0.0, value=0.0, step=1.0)
resale = st.number_input("Estimated resale price", min_value=0.0, value=0.0, step=1.0)
confidence = st.slider("Confidence", 0, 100, 70)

if st.button("Check deal"):
    if buy > 0 and resale > 0:
        tax = buy * tax_pct / 100
        acquisition = buy + tax
        fees = resale * fee_pct / 100
        profit = resale - acquisition - fees - outbound_shipping
        roi = profit / acquisition * 100 if acquisition else 0
        qualifies = profit >= min_profit and roi >= min_roi and confidence >= min_confidence

        if qualifies:
            st.success(f"🔥 ALERT — Estimated profit ${profit:.2f} · ROI {roi:.1f}%")
        else:
            st.warning(f"Doesn't meet your alert settings — Profit ${profit:.2f} · ROI {roi:.1f}%")
    else:
        st.info("Enter a buy price and estimated resale price first.")

st.caption("Sample listings are examples only, not verified current deals.")
