"""
SmartRecommend - Admin Panel
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import format_naira, CATEGORY_ICONS

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9f87c4", size=11),
    margin=dict(l=10, r=10, t=35, b=10),
    xaxis=dict(gridcolor="#2e1f5e", linecolor="#2e1f5e"),
    yaxis=dict(gridcolor="#2e1f5e", linecolor="#2e1f5e"),
)


def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    users_df = st.session_state.get("users_df", pd.DataFrame())
    activities_df = st.session_state.get("activities_df", pd.DataFrame())

    st.markdown("""
    <h2 style="font-family:'Sora',sans-serif;color:#f0eaff;margin-bottom:0.3rem;">⚙️ Admin Panel</h2>
    <div style="font-size:0.85rem;color:#9f87c4;margin-bottom:1.5rem;">
      System overview, data management, and model controls
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🛍️ Products", "👥 Users", "🤖 ML Model"])

    # ── Overview ──────────────────────────────────────────────────────────────
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Products", f"{len(products_df):,}")
        with c2:
            st.metric("Total Users", f"{len(users_df):,}")
        with c3:
            st.metric("Total Interactions", f"{len(activities_df):,}")
        with c4:
            st.metric("Categories", "7")

        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)

        if not products_df.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;margin-bottom:0.5rem;">Products per Category</div>""", unsafe_allow_html=True)
                cat_cnt = products_df["category"].value_counts()
                fig = go.Figure(go.Bar(
                    x=cat_cnt.index, y=cat_cnt.values,
                    marker=dict(color="#6c3fe0", line=dict(width=0)),
                    text=cat_cnt.values, textposition="outside",
                    textfont=dict(color="#9f87c4"),
                ))
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;margin-bottom:0.5rem;">In-Stock vs Out-of-Stock</div>""", unsafe_allow_html=True)
                stock = products_df["in_stock"].value_counts()
                fig2 = go.Figure(go.Pie(
                    labels=["In Stock", "Out of Stock"],
                    values=stock.values,
                    hole=0.55,
                    marker=dict(colors=["#10b981", "#ef4444"]),
                ))
                fig2.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

    # ── Products Management ────────────────────────────────────────────────────
    with tab2:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">🛍️ Product Management</div>""", unsafe_allow_html=True)

        search = st.text_input("Search products", placeholder="Search by name, category...", key="admin_search")
        cat_filter = st.selectbox("Filter by category", ["All"] + list(CATEGORY_ICONS.keys())[:-1], key="admin_cat")

        filtered = products_df.copy()
        if search:
            filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
        if cat_filter != "All":
            filtered = filtered[filtered["category"] == cat_filter]

        if not filtered.empty:
            display_cols = ["product_id", "name", "category", "price", "rating", "in_stock", "views", "purchases"]
            available = [c for c in display_cols if c in filtered.columns]
            
            show_df = filtered[available].head(50).copy()
            show_df["price"] = show_df["price"].apply(lambda x: format_naira(x))
            
            st.dataframe(
                show_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_id": st.column_config.NumberColumn("ID", width="small"),
                    "name": st.column_config.TextColumn("Product Name", width="large"),
                    "in_stock": st.column_config.CheckboxColumn("In Stock"),
                    "rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                }
            )
            st.caption(f"Showing {min(50, len(filtered))} of {len(filtered):,} products")

        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;margin-bottom:0.8rem;">➕ Add New Product</div>""", unsafe_allow_html=True)

        ac1, ac2 = st.columns(2)
        with ac1:
            new_name = st.text_input("Product Name", key="new_prod_name")
            new_cat = st.selectbox("Category", list(CATEGORY_ICONS.keys())[:-1], key="new_prod_cat")
            new_price = st.number_input("Price (₦)", min_value=0, value=50000, key="new_prod_price")
        with ac2:
            new_desc = st.text_area("Description", key="new_prod_desc", height=100)
            new_rating = st.slider("Initial Rating", 1.0, 5.0, 4.0, 0.1, key="new_prod_rating")
            new_stock = st.checkbox("In Stock", value=True, key="new_prod_stock")

        if st.button("➕ Add Product", use_container_width=False, key="add_product"):
            if new_name:
                st.success(f"✅ Product '{new_name}' added successfully! (Demo mode - not persisted)")
            else:
                st.warning("Please enter a product name")

    # ── Users Management ────────────────────────────────────────────────────
    with tab3:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">👥 User Management</div>""", unsafe_allow_html=True)

        if not users_df.empty:
            display_users = ["user_id", "name", "email", "city", "age", "date_joined"]
            available_u = [c for c in display_users if c in users_df.columns]
            st.dataframe(users_df[available_u].head(100), use_container_width=True, hide_index=True)
            st.caption(f"Showing 100 of {len(users_df):,} users")

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if "city" in users_df.columns:
                    city_dist = users_df["city"].value_counts().head(8)
                    fig_city = go.Figure(go.Bar(
                        x=city_dist.values, y=city_dist.index, orientation="h",
                        marker=dict(color="#0ea5e9", line=dict(width=0)),
                        text=city_dist.values, textposition="outside",
                        textfont=dict(color="#9f87c4"),
                    ))
                    fig_city.update_layout(**PLOTLY_LAYOUT, title="Users by City",
                                           title_font=dict(color="#f0eaff", size=13))
                    st.plotly_chart(fig_city, use_container_width=True)
            with col_u2:
                if "age" in users_df.columns:
                    import numpy as np
                    age_bins = pd.cut(users_df["age"], bins=[17, 25, 35, 45, 60],
                                       labels=["18-25", "26-35", "36-45", "46-60"])
                    age_dist = age_bins.value_counts().sort_index()
                    fig_age = go.Figure(go.Bar(
                        x=age_dist.index.astype(str), y=age_dist.values,
                        marker=dict(color=["#6c3fe0", "#a78bfa", "#0ea5e9", "#10b981"],
                                     line=dict(width=0)),
                        text=age_dist.values, textposition="outside",
                        textfont=dict(color="#9f87c4"),
                    ))
                    fig_age.update_layout(**PLOTLY_LAYOUT, title="Users by Age Group",
                                          title_font=dict(color="#f0eaff", size=13))
                    st.plotly_chart(fig_age, use_container_width=True)

    # ── ML Model Management ────────────────────────────────────────────────
    with tab4:
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">🤖 ML Model Management</div>""", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
            <div class="sr-card" style="text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.5rem;">📝</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;">Content-Based</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin:0.4rem 0;">TF-IDF + Cosine Similarity</div>
              <div style="background:rgba(16,185,129,0.15);color:#34d399;border-radius:8px;padding:3px 10px;font-size:0.75rem;font-weight:600;display:inline-block;">● Active</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class="sr-card" style="text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.5rem;">👥</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;">Collaborative</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin:0.4rem 0;">KNN + Matrix Factorization</div>
              <div style="background:rgba(16,185,129,0.15);color:#34d399;border-radius:8px;padding:3px 10px;font-size:0.75rem;font-weight:600;display:inline-block;">● Active</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="sr-card" style="text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.5rem;">⚡</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;">Hybrid Engine</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin:0.4rem 0;">0.6 Content + 0.4 Collab</div>
              <div style="background:rgba(16,185,129,0.15);color:#34d399;border-radius:8px;padding:3px 10px;font-size:0.75rem;font-weight:600;display:inline-block;">● Active</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;margin-bottom:0.8rem;">⚙️ Model Configuration</div>""", unsafe_allow_html=True)

        cfg1, cfg2 = st.columns(2)
        with cfg1:
            content_weight = st.slider("Content-Based Weight", 0.0, 1.0, 0.6, 0.05, key="cfg_cw")
            st.caption(f"Collaborative weight: {1 - content_weight:.2f} (auto-adjusted)")
        with cfg2:
            n_neighbors = st.slider("KNN Neighbors", 5, 50, 20, 5, key="cfg_nn")
            max_features = st.selectbox("TF-IDF Max Features", [500, 1000, 2000, 5000], index=1, key="cfg_mf")

        if st.button("🔄 Retrain Model", key="retrain_model", use_container_width=False):
            with st.spinner("Retraining model..."):
                import time; time.sleep(2)
            st.success("✅ Model retrained successfully! (Demo mode)")

        if st.button("💾 Export Model", key="export_model", use_container_width=False):
            st.info("Model export triggered. Check /models/recommendation_model.pkl")
