import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="CSV / Excel Analyzer", page_icon="📊", layout="wide")

st.title("📊 CSV / Excel Analyzer")
st.markdown("Upload a CSV or Excel file to explore summary statistics and charts.")

# ── File Upload ──────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx", "xls"])

@st.cache_data
def load_data(file):
    name = file.name
    if name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if uploaded_file:
    df = load_data(uploaded_file)

    st.success(f"✅ Loaded **{uploaded_file.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")

    # ── Preview ──────────────────────────────────────────────────────────────
    with st.expander("🔍 Data Preview", expanded=True):
        st.dataframe(df.head(50), use_container_width=True)

    # ── Summary Statistics ───────────────────────────────────────────────────
    st.subheader("📋 Summary Statistics")

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if num_cols:
        st.markdown("**Numeric columns**")
        st.dataframe(df[num_cols].describe().T.style.format("{:.2f}"), use_container_width=True)

    if cat_cols:
        st.markdown("**Categorical columns**")
        cat_summary = pd.DataFrame({
            "Unique values": [df[c].nunique() for c in cat_cols],
            "Most frequent": [df[c].mode()[0] if not df[c].mode().empty else "—" for c in cat_cols],
            "Missing (%)": [round(df[c].isna().mean() * 100, 1) for c in cat_cols],
        }, index=cat_cols)
        st.dataframe(cat_summary, use_container_width=True)

    # ── Charts ───────────────────────────────────────────────────────────────
    st.subheader("📈 Charts")

    tab1, tab2, tab3 = st.tabs(["Distribution", "Correlation Heatmap", "Bar / Count"])

    # Tab 1 – Distribution of a numeric column
    with tab1:
        if num_cols:
            col = st.selectbox("Select a numeric column", num_cols, key="dist_col")
            bins = st.slider("Number of bins", 5, 100, 20)
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.histplot(df[col].dropna(), bins=bins, kde=True, ax=ax, color="#4C72B0")
            ax.set_title(f"Distribution of {col}")
            ax.set_xlabel(col)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No numeric columns found.")

    # Tab 2 – Correlation heatmap
    with tab2:
        if len(num_cols) >= 2:
            fig, ax = plt.subplots(figsize=(8, 6))
            corr = df[num_cols].corr()
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, linewidths=0.5)
            ax.set_title("Correlation Heatmap")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Need at least 2 numeric columns for a correlation heatmap.")

    # Tab 3 – Bar chart for a categorical column
    with tab3:
        if cat_cols:
            col = st.selectbox("Select a categorical column", cat_cols, key="bar_col")
            top_n = st.slider("Show top N values", 3, 30, 10)
            counts = df[col].value_counts().head(top_n)
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.barplot(x=counts.values, y=counts.index, ax=ax, palette="viridis")
            ax.set_title(f"Top {top_n} values in '{col}'")
            ax.set_xlabel("Count")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No categorical columns found.")

    # ── Download cleaned data ────────────────────────────────────────────────
    st.subheader("⬇️ Download")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download data as CSV", csv_bytes, "data.csv", "text/csv")

else:
    st.info("👆 Upload a CSV or Excel file to get started.")