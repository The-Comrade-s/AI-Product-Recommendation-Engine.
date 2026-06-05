"""
SmartRecommend - Database & Session Utilities
"""
import sqlite3
import pandas as pd
import streamlit as st
import os
import json
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "database.db")


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def log_activity(user_id: int, product_id: int, action: str):
    """Log user activity to database"""
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO user_activity (user_id, product_id, action, timestamp) VALUES (?,?,?,?)",
            (user_id, product_id, action, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_user_activity(user_id: int) -> pd.DataFrame:
    try:
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM user_activity WHERE user_id=? ORDER BY timestamp DESC LIMIT 200",
            conn, params=(user_id,)
        )
        conn.close()
        return df
    except:
        return pd.DataFrame()


def get_user_viewed_products(user_id: int) -> list:
    df = get_user_activity(user_id)
    if df.empty:
        return []
    views = df[df["action"] == "view"]["product_id"].tolist()
    return list(dict.fromkeys(views))  # unique, ordered


def add_to_wishlist(user_id: int, product_id: int):
    log_activity(user_id, product_id, "wishlist")
    if "wishlist" not in st.session_state:
        st.session_state.wishlist = []
    if product_id not in st.session_state.wishlist:
        st.session_state.wishlist.append(product_id)


def remove_from_wishlist(user_id: int, product_id: int):
    if "wishlist" in st.session_state and product_id in st.session_state.wishlist:
        st.session_state.wishlist.remove(product_id)


def init_session():
    """Initialize all session state variables"""
    defaults = {
        "user_id": 1,
        "user_name": "Oluwa Victor",
        "user_email": "oluwa.victor@gmail.com",
        "user_city": "Lagos",
        "logged_in": True,
        "viewed_products": [],
        "wishlist": [],
        "liked_products": [],
        "rated_products": {},
        "preferred_categories": ["Electronics", "Smartphones"],
        "current_product": None,
        "search_query": "",
        "selected_category": "All",
        "cart": [],
        "orders_count": 18,
        "wishlist_count": 23,
        "products_viewed": 128,
        "ratings_given": 45,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def format_naira(amount: float) -> str:
    """Format price in Nigerian Naira"""
    return f"₦{amount:,.0f}"


def get_star_display(rating: float) -> str:
    """Return star emoji string for a rating"""
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "⭐" * full + ("✨" if half else "") + "☆" * empty


def get_rating_color(rating: float) -> str:
    if rating >= 4.5:
        return "#22c55e"
    elif rating >= 4.0:
        return "#84cc16"
    elif rating >= 3.0:
        return "#f59e0b"
    else:
        return "#ef4444"


def truncate_text(text: str, max_len: int = 80) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text


CATEGORY_ICONS = {
    "Smartphones": "📱",
    "Laptops": "💻",
    "Electronics": "🎧",
    "Home & Kitchen": "🏠",
    "Fashion": "👕",
    "Books": "📚",
    "Gaming": "🎮",
    "All": "🛍️",
}

CATEGORY_COLORS = {
    "Smartphones": "#6366f1",
    "Laptops": "#8b5cf6",
    "Electronics": "#0ea5e9",
    "Home & Kitchen": "#10b981",
    "Fashion": "#f43f5e",
    "Books": "#f59e0b",
    "Gaming": "#ef4444",
    "All": "#7c3aed",
}
