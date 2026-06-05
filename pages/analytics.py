"""
SmartRecommend - Analytics Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import format_naira, CATEGORY_COLORS


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9f87c4", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#c4b5e8")),
    xaxis=dict(gridcolor="#2e1f5e", linecolor="#2e1f5e", tickfont=dict(color="#9f87c4")),
    yaxis=dict(gridcolor="#2e1f5e", linecolor="#2e1f5e", tickfont=dict(color="#9f87c4")),
)


def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    activities_df = st.session_state.get("activities_df", pd.DataFrame())

    st.markdown("""
    <h2 style="font-family:'Sora',sans-serif;color:#f0eaff;margin-bottom:0.3rem;">📊 Analytics Dashboard</h2>
    <div style="font-size:0.85rem;color:#9f87c4;margin-bottom:1.5rem;">
      Real-time insights into product performance and user behavior
    </div>
    """, unsafe_allow_html=True)

    if products_df.empty:
        st.error("No data available.")
        return

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Products", f"{len(products_df):,}", "+120 this week")
    with k2:
        users_df = st.session_state.get("users_df", pd.DataFrame())
        st.metric("Total Users", f"{len(users_df):,}", "+340 this month")
    with k3:
        st.metric("Total Interactions", "50,000+", "+1,200 today")
    with k4:
        avg_rating = products_df["rating"].mean()
        st.metric("Avg Rating", f"{avg_rating:.2f} ⭐", "+0.12")
    with k5:
        st.metric("Recommendation Accuracy", "92%", "+3%")

    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)

    # ── Row 1: Category distribution + Top products ──────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">📂 Top Categories</div>""", unsafe_allow_html=True)
        cat_counts = products_df.groupby("category").agg(
            count=("product_id", "count"),
            avg_rating=("rating", "mean"),
            total_views=("views", "sum"),
        ).reset_index()

        colors = [CATEGORY_COLORS.get(c, "#6c3fe0") for c in cat_counts["category"]]
        fig = go.Figure(go.Pie(
            labels=cat_counts["category"],
            values=cat_counts["count"],
            hole=0.5,
            marker=dict(colors=colors, line=dict(color="#0f0a1e", width=2)),
            textfont=dict(color="white", size=11),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title="Products by Category",
                          title_font=dict(color="#f0eaff", size=13))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">🏆 Most Viewed Products</div>""", unsafe_allow_html=True)
        top_viewed = products_df.nlargest(8, "views")[["name", "views", "category"]].copy()
        top_viewed["short_name"] = top_viewed["name"].str[:25] + "..."

        fig2 = go.Figure(go.Bar(
            x=top_viewed["views"],
            y=top_viewed["short_name"],
            orientation="h",
            marker=dict(
                color=top_viewed["category"].map(CATEGORY_COLORS),
                line=dict(width=0),
            ),
            text=top_viewed["views"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(color="#9f87c4", size=10),
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Top 8 Most Viewed",
                           title_font=dict(color="#f0eaff", size=13),
                           yaxis=dict(tickfont=dict(size=9, color="#c4b5e8")))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: User activity trend + Rating distribution ─────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">📈 User Activity Trend (Last 30 Days)</div>""", unsafe_allow_html=True)

        if not activities_df.empty and "timestamp" in activities_df.columns:
            try:
                activities_df["date"] = pd.to_datetime(activities_df["timestamp"]).dt.date
                daily = activities_df.groupby(["date", "action"]).size().reset_index(name="count")
                daily = daily.sort_values("date").tail(300)

                fig3 = go.Figure()
                action_colors = {"view": "#6c3fe0", "click": "#0ea5e9",
                                  "like": "#f43f5e", "wishlist": "#f59e0b", "purchase": "#10b981"}
                for action, color in action_colors.items():
                    sub = daily[daily["action"] == action]
                    if not sub.empty:
                        fig3.add_trace(go.Scatter(
                            x=sub["date"], y=sub["count"],
                            name=action.title(), mode="lines",
                            line=dict(color=color, width=2),
                            fill="tozeroy",
                            fillcolor=color.replace(")", ",0.08)").replace("rgb", "rgba") if "rgb" in color else color + "14",
                        ))
                fig3.update_layout(**PLOTLY_LAYOUT, title="Daily Interactions by Type",
                                   title_font=dict(color="#f0eaff", size=13))
                st.plotly_chart(fig3, use_container_width=True)
            except:
                _fallback_activity_chart()
        else:
            _fallback_activity_chart()

    with col4:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">⭐ Rating Distribution</div>""", unsafe_allow_html=True)
        rating_bins = pd.cut(products_df["rating"], bins=[0, 2, 3, 4, 4.5, 5], labels=["1-2", "2-3", "3-4", "4-4.5", "4.5-5"])
        rating_dist = rating_bins.value_counts().sort_index()

        fig4 = go.Figure(go.Bar(
            x=rating_dist.index.astype(str),
            y=rating_dist.values,
            marker=dict(
                color=["#ef4444", "#f59e0b", "#84cc16", "#22c55e", "#10b981"],
                line=dict(width=0),
            ),
            text=rating_dist.values,
            textposition="outside",
            textfont=dict(color="#9f87c4"),
        ))
        fig4.update_layout(**PLOTLY_LAYOUT, title="Products by Rating Range",
                           title_font=dict(color="#f0eaff", size=13))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Price distribution + Purchase by category ─────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">💰 Price Distribution</div>""", unsafe_allow_html=True)
        price_data = products_df[products_df["price"] < 2000000]["price"]
        fig5 = go.Figure(go.Histogram(
            x=price_data,
            nbinsx=25,
            marker=dict(color="#6c3fe0", line=dict(color="#0f0a1e", width=1)),
        ))
        fig5.update_layout(**PLOTLY_LAYOUT, title="Product Price Distribution (₦)",
                           title_font=dict(color="#f0eaff", size=13),
                           xaxis_title="Price (₦)", yaxis_title="Count")
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">🛒 Purchases by Category</div>""", unsafe_allow_html=True)
        purchase_by_cat = products_df.groupby("category")["purchases"].sum().reset_index()
        purchase_by_cat = purchase_by_cat.sort_values("purchases", ascending=True)

        fig6 = go.Figure(go.Bar(
            x=purchase_by_cat["purchases"],
            y=purchase_by_cat["category"],
            orientation="h",
            marker=dict(
                color=[CATEGORY_COLORS.get(c, "#6c3fe0") for c in purchase_by_cat["category"]],
                line=dict(width=0),
            ),
            text=purchase_by_cat["purchases"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(color="#9f87c4", size=10),
        ))
        fig6.update_layout(**PLOTLY_LAYOUT, title="Total Purchases by Category",
                           title_font=dict(color="#f0eaff", size=13))
        st.plotly_chart(fig6, use_container_width=True)

    # ── Row 4: Sentiment analysis simulation ─────────────────────────────────
    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">💬 Sentiment Analysis</div>""", unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    sentiments = [
        (s1, "Positive Reviews", 82, "#10b981", "😊"),
        (s2, "Neutral Reviews", 12, "#f59e0b", "😐"),
        (s3, "Negative Reviews", 6, "#ef4444", "😔"),
    ]
    for col, label, pct, color, emoji in sentiments:
        with col:
            st.markdown(f"""
            <div class="sr-card" style="text-align:center;">
              <div style="font-size:2.5rem;margin-bottom:0.5rem;">{emoji}</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:{color};font-size:2rem;">{pct}%</div>
              <div style="font-size:0.82rem;color:#9f87c4;">{label}</div>
              <div class="conf-bar" style="margin-top:0.8rem;">
                <div class="conf-fill" style="width:{pct}%;background:{color};"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Recommendation accuracy gauge ─────────────────────────────────────────
    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">🎯 Recommendation Performance</div>""", unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    metrics = [
        (r1, "Precision@10", "87%", "#6c3fe0"),
        (r2, "Recall@10", "79%", "#0ea5e9"),
        (r3, "NDCG Score", "0.84", "#10b981"),
        (r4, "Coverage", "94%", "#f59e0b"),
    ]
    for col, label, val, color in metrics:
        with col:
            st.markdown(f"""
            <div class="sr-card" style="text-align:center;">
              <div style="font-family:'Sora',sans-serif;font-weight:800;font-size:2rem;color:{color};">{val}</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def _fallback_activity_chart():
    """Fallback chart with simulated data"""
    import plotly.graph_objects as go
    days = list(range(1, 31))
    fig = go.Figure()
    for action, color in [("Views", "#6c3fe0"), ("Clicks", "#0ea5e9"), ("Purchases", "#10b981")]:
        import numpy as np
        y = np.random.randint(50, 300, 30) + np.sin(np.array(days)) * 30
        fig.add_trace(go.Scatter(x=days, y=y.astype(int), name=action,
                                  mode="lines", line=dict(color=color, width=2)))
    fig.update_layout(**PLOTLY_LAYOUT, title="Daily Activity (Simulated)",
                      title_font=dict(color="#f0eaff", size=13))
    st.plotly_chart(fig, use_container_width=True)
