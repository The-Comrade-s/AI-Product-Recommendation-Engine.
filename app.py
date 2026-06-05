"""
SmartRecommend - AI Product Recommendation Engine
Main application entry point
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import pickle
import warnings
warnings.filterwarnings("ignore")

# ── Path setup ─────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from utils.helpers import init_session, format_naira, CATEGORY_ICONS, CATEGORY_COLORS
from utils.helpers import get_star_display, truncate_text, log_activity

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartRecommend",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ─── Root variables ─── */
:root {
  --primary: #6c3fe0;
  --primary-dark: #4f2ca8;
  --primary-light: #a78bfa;
  --accent: #f59e0b;
  --accent-pink: #f43f5e;
  --success: #10b981;
  --bg-dark: #0f0a1e;
  --bg-card: #1a1035;
  --bg-card2: #211544;
  --text-primary: #f0eaff;
  --text-secondary: #9f87c4;
  --border: #2e1f5e;
  --shadow: 0 4px 24px rgba(108,63,224,0.18);
}

/* ─── Global resets ─── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
}

.stApp {
  background: linear-gradient(135deg, #0f0a1e 0%, #140d2b 50%, #0a0616 100%);
  min-height: 100vh;
}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #130e28 0%, #0e0922 100%) !important;
  border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label {
  color: var(--text-primary) !important;
}

/* ─── Hide default streamlit elements ─── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ─── Typography ─── */
h1, h2, h3, h4 {
  font-family: 'Sora', sans-serif;
  color: var(--text-primary);
}

/* ─── Metric cards ─── */
[data-testid="metric-container"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 1.2rem !important;
}
[data-testid="metric-container"] label {
  color: var(--text-secondary) !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
  color: var(--text-primary) !important;
  font-family: 'Sora', sans-serif !important;
  font-size: 1.8rem !important;
  font-weight: 700 !important;
}

/* ─── Buttons ─── */
.stButton > button {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  padding: 0.5rem 1.2rem !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 15px rgba(108,63,224,0.3) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(108,63,224,0.45) !important;
}

/* ─── Input fields ─── */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
  background: var(--bg-card2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border-radius: 12px !important;
  gap: 4px !important;
  padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px !important;
  color: var(--text-secondary) !important;
  font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--primary) !important;
  color: white !important;
}

/* ─── Expander ─── */
.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border-radius: 12px !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 4px; }

/* ─── Custom card component ─── */
.sr-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.4rem;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
}
.sr-card:hover {
  border-color: var(--primary-light);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}
.sr-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  opacity: 0;
  transition: opacity 0.25s;
}
.sr-card:hover::before { opacity: 1; }

/* ─── Product card ─── */
.product-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
}
.product-card:hover {
  border-color: var(--primary-light);
  box-shadow: 0 8px 30px rgba(108,63,224,0.25);
  transform: translateY(-4px);
}
.product-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background: linear-gradient(135deg, #1e1040, #2a1860);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}
.product-body { padding: 1rem; }
.product-name {
  font-family: 'Sora', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
  line-height: 1.3;
}
.product-category {
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.5rem;
}
.product-price {
  font-family: 'Sora', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--primary-light);
}
.product-rating {
  font-size: 0.78rem;
  color: var(--accent);
}
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin: 2px;
}
.badge-primary { background: rgba(108,63,224,0.2); color: var(--primary-light); border: 1px solid rgba(108,63,224,0.3); }
.badge-success { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.badge-warning { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.25); }
.badge-pink { background: rgba(244,63,94,0.15); color: #fb7185; border: 1px solid rgba(244,63,94,0.25); }

/* ─── Hero banner ─── */
.hero-banner {
  background: linear-gradient(135deg, #1a0a3e 0%, #2d1065 40%, #1a0a3e 100%);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 2.5rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.hero-banner::after {
  content: '';
  position: absolute;
  top: -50%; right: -10%;
  width: 60%;
  height: 200%;
  background: radial-gradient(circle, rgba(108,63,224,0.15) 0%, transparent 70%);
}

/* ─── Section header ─── */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 1.5rem 0 1rem 0;
}
.section-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
}
.view-all-link {
  font-size: 0.82rem;
  color: var(--primary-light);
  text-decoration: none;
  font-weight: 500;
}

/* ─── Sidebar branding ─── */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.5rem 0 1.5rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.brand-name {
  font-family: 'Sora', sans-serif;
  font-size: 1.3rem;
  font-weight: 800;
  color: white;
}
.brand-name span { color: var(--primary-light); }
.brand-tag {
  font-size: 0.65rem;
  color: var(--text-secondary);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ─── Nav item ─── */
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0.65rem 1rem;
  border-radius: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
  text-decoration: none;
}
.nav-item:hover, .nav-item.active {
  background: rgba(108,63,224,0.15);
  color: var(--text-primary);
}
.nav-item.active { border-left: 3px solid var(--primary-light); }

/* ─── Star rating ─── */
.stars { color: #f59e0b; font-size: 0.85rem; }

/* ─── Recommendation reason chip ─── */
.reason-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(108,63,224,0.1);
  border: 1px solid rgba(108,63,224,0.25);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.75rem;
  color: var(--primary-light);
  margin: 3px;
}

/* ─── Progress bar ─── */
.pref-bar-wrap { margin: 6px 0; }
.pref-label { display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 4px; }
.pref-bar { height: 6px; background: var(--bg-card2); border-radius: 4px; overflow: hidden; }
.pref-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--primary), var(--primary-light)); }

/* ─── Category pill ─── */
.cat-pill {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 72px;
  text-align: center;
}
.cat-pill:hover, .cat-pill.active {
  background: rgba(108,63,224,0.2);
  border-color: var(--primary-light);
}
.cat-icon { font-size: 1.6rem; }
.cat-label { font-size: 0.68rem; color: var(--text-secondary); font-weight: 500; }

/* ─── Alert / info box ─── */
.info-box {
  background: rgba(108,63,224,0.08);
  border: 1px solid rgba(108,63,224,0.2);
  border-radius: 14px;
  padding: 1rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* ─── Analytics gauge ─── */
.gauge-wrap {
  text-align: center;
  padding: 1rem;
}
.gauge-value {
  font-family: 'Sora', sans-serif;
  font-size: 2.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary-light), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ─── In-stock badge ─── */
.in-stock { color: #34d399; font-size: 0.75rem; font-weight: 600; }
.out-stock { color: #fb7185; font-size: 0.75rem; font-weight: 600; }

/* ─── Divider ─── */
.sr-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 1.2rem 0;
}

/* ─── Trend rank badge ─── */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px; height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  font-family: 'Sora', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
}

/* ─── Confidence meter ─── */
.conf-bar { height: 8px; border-radius: 4px; background: var(--bg-card2); margin: 6px 0; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #10b981, #34d399); }

/* ─── Slider ─── */
.stSlider > div > div > div > div { background: var(--primary) !important; }

/* ─── Responsive mobile ─── */
@media (max-width: 768px) {
  .hero-banner { padding: 1.5rem; }
  .product-name { font-size: 0.82rem; }
  .product-price { font-size: 0.95rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Initialize session ────────────────────────────────────────────────────────
init_session()

# ── Load data & model ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_engine():
    """Load or build the recommendation engine"""
    model_path = os.path.join(ROOT, "models", "recommendation_model.pkl")
    data_dir = os.path.join(ROOT, "data")
    db_dir = os.path.join(ROOT, "database")
    
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(db_dir, exist_ok=True)
    
    # Generate data if not present
    products_csv = os.path.join(data_dir, "products.csv")
    if not os.path.exists(products_csv):
        from utils.data_generator import generate_all_data
        generate_all_data(data_dir, os.path.join(db_dir, "database.db"))
    
    # Build model if not present
    if not os.path.exists(model_path):
        from utils.recommendation_engine import build_and_save_model
        build_and_save_model(
            os.path.join(data_dir, "products.csv"),
            os.path.join(data_dir, "ratings.csv"),
            model_path
        )
    
    from utils.recommendation_engine import HybridRecommender
    engine = HybridRecommender.load(model_path)
    return engine


@st.cache_data(show_spinner=False)
def load_products():
    path = os.path.join(ROOT, "data", "products.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_users():
    path = os.path.join(ROOT, "data", "users.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_activities():
    path = os.path.join(ROOT, "data", "activities.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div style="font-size:1.8rem">🛍️</div>
      <div>
        <div class="brand-name">Smart<span>Recommend</span></div>
        <div class="brand-tag">AI Product Recommender</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # User info
    st.markdown(f"""
    <div style="background:rgba(108,63,224,0.1);border:1px solid rgba(108,63,224,0.2);border-radius:14px;padding:1rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#6c3fe0,#a78bfa);display:flex;align-items:center;justify-content:center;font-size:1.2rem;">👤</div>
        <div>
          <div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;font-size:0.9rem;">{st.session_state.user_name}</div>
          <div style="font-size:0.72rem;color:#9f87c4;">Good Evening, {st.session_state.user_name.split()[0]} 👋</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    pages = {
        "🏠 Home": "Home",
        "🔍 Search Products": "Search",
        "🤖 Recommendations": "Recommendations",
        "💝 Wishlist": "Wishlist",
        "👤 Profile": "Profile",
        "📊 Analytics Dashboard": "Analytics",
        "⚙️ Admin Panel": "Admin",
    }
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    
    for label, page in pages.items():
        is_active = st.session_state.current_page == page
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()

    # Top categories mini chart
    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.8rem;color:#9f87c4;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.7rem;">Top Categories</div>
    """, unsafe_allow_html=True)
    
    cat_stats = [
        ("Electronics", 40, "#6c3fe0"),
        ("Fashion", 20, "#f43f5e"),
        ("Home & Kitchen", 15, "#10b981"),
        ("Books", 10, "#f59e0b"),
        ("Others", 15, "#0ea5e9"),
    ]
    for cat, pct, color in cat_stats:
        st.markdown(f"""
        <div class="pref-bar-wrap">
          <div class="pref-label"><span>{cat}</span><span>{pct}%</span></div>
          <div class="pref-bar"><div class="pref-fill" style="width:{pct}%;background:{color};"></div></div>
        </div>
        """, unsafe_allow_html=True)

    # Upgrade promo
    st.markdown("""
    <div style="background:linear-gradient(135deg,#4c1d95,#6c3fe0);border-radius:16px;padding:1rem;margin-top:1rem;text-align:center;">
      <div style="font-size:1.2rem;margin-bottom:0.4rem;">👑</div>
      <div style="font-family:'Sora',sans-serif;font-weight:700;color:white;font-size:0.85rem;margin-bottom:0.3rem;">Upgrade Your Experience</div>
      <div style="font-size:0.72rem;color:rgba(255,255,255,0.7);margin-bottom:0.8rem;">Get personalized recommendations and exclusive offers</div>
    </div>
    """, unsafe_allow_html=True)


# ── Loading spinner ───────────────────────────────────────────────────────────
with st.spinner("🚀 Initializing SmartRecommend AI Engine..."):
    try:
        engine = load_engine()
        products_df = load_products()
        users_df = load_users()
        activities_df = load_activities()
        data_loaded = True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        data_loaded = False

# Store in session for pages
st.session_state["engine"] = engine if data_loaded else None
st.session_state["products_df"] = products_df if data_loaded else pd.DataFrame()
st.session_state["users_df"] = users_df if data_loaded else pd.DataFrame()
st.session_state["activities_df"] = activities_df if data_loaded else pd.DataFrame()


# ── Route to pages ────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "Home":
    import pages.home as home_page
    home_page.render()
elif page == "Search":
    import pages.search as search_page
    search_page.render()
elif page == "Recommendations":
    import pages.recommendations as recs_page
    recs_page.render()
elif page == "Wishlist":
    import pages.wishlist as wishlist_page
    wishlist_page.render()
elif page == "Profile":
    import pages.profile as profile_page
    profile_page.render()
elif page == "Analytics":
    import pages.analytics as analytics_page
    analytics_page.render()
elif page == "Admin":
    import pages.admin as admin_page
    admin_page.render()
