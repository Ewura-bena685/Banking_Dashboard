# Banking Performance Dashboard (Streamlit)

A small Streamlit dashboard for demonstrating banking KPIs, with cached data generation, responsive layout, metric tooltips, and export buttons.

## Files
- `demo.py` — main Streamlit application
- `requirements.txt` — Python dependencies

## Quick start
1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run demo.py
```

The app opens in your default browser (usually at http://localhost:8501).

## Notes
- Upload CSV: include columns `Month`, `Revenue`, `Transactions`, `Balance`, `Deposits`, `Loans`, `NPS`. The app normalizes `Month` where possible.
- Export: use the **Download CSV** or **Download Snapshot (JSON)** buttons to save the current dataset or a small dashboard snapshot.
- Caching: `@st.cache_data` is used for demo data generation and plot construction to reduce re-renders.

## Contact
Built by Esther Ewurabena Appiah — appiahewurabena685@gmail.com
