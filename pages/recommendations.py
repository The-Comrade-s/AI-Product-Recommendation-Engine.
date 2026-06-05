"""
SmartRecommend - Recommendations Page
"""
import streamlit as st
import pandas as pd
from utils.helpers import (
    format_naira, CATEGORY_ICONS, truncate_text, log_activity
)


def render_rec_card(p, engine, idx, tab_key="rec"):
    icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
    in_wishlist = p["product_id"] in st.session_state.wishlist
    
    # Get explanation
    explanation = {"reasons": [], "tags": [], "confidence": 80}
    if engine:
        try:
            explanation = engine.explain_recommendation(
                p["product_id"],
                user_id=st.session_state.user_id,
                viewed_products=st.session_state.viewed_products,
                liked_categories=st.session_state.preferred_categories
            )
        except:
            pass
    
    confidence = explanation.get("confidence", 80)
    reasons = explanation.get("reasons", [])
    tags = explanation.get("tags", [])
    
    st.markdown(f"""
    <div class="product-card" style="margin-bottom:0.5rem;">
      <div style="height:150px;background:linear-gradient(135deg,#1e1040,#2a1860);
           display:flex;align-items:center;justify-content:center;font-size:3.5rem;
           position:relative;">
        {icon}
        <div style="position:absolute;bottom:8px;right:8px;background:rgba(16,185,129,0.85);
             color:white;border-radius:8px;padding:2px 8px;font-size:0.7rem;font-weight:700;">
          {confidence}% match
        </div>
      </div>
      <div class="product-body">
        <div class="product-category">{p.get('category','')}</div>
        <div class="product-name">{truncate_text(str(p.get('name','')), 42)}</div>
        <div class="product-rating">⭐ {p.get('rating',4.0):.1f}
          <span style="color:#9f87c4;font-size:0.72rem;">({int(p.get('num_reviews',0))})</span>
        </div>
        <div class="product-price">{format_naira(p.get('price',0))}</div>
        {''.join(f'<span class="badge badge-primary" style="font-size:0.65rem;">{t}</span>' for t in tags[:2])}
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("View", key=f"{tab_key}_v_{p['product_id']}_{idx}", use_container_width=True):
            st.session_state.current_product = p.to_dict()
            log_activity(st.session_state.user_id, p["product_id"], "view")
            if p["product_id"] not in st.session_state.viewed_products:
                st.session_state.viewed_products.append(p["product_id"])
            st.session_state.current_page = "Search"
            st.rerun()
    with b2:
        heart = "💜" if in_wishlist else "🤍"
        if st.button(heart, key=f"{tab_key}_w_{p['product_id']}_{idx}", use_container_width=True):
            if not in_wishlist:
                st.session_state.wishlist.append(p["product_id"])
                log_activity(st.session_state.user_id, p["product_id"], "wishlist")
                st.toast("Added to wishlist! 💜")
            else:
                st.session_state.wishlist.remove(p["product_id"])
            st.rerun()
    with b3:
        if st.button("🛒", key=f"{tab_key}_c_{p['product_id']}_{idx}", use_container_width=True):
            log_activity(st.session_state.user_id, p["product_id"], "purchase")
            st.toast("Added to cart! 🛒")


def render():
    engine = st.session_state.get("engine")
    products_df = st.session_state.get("products_df", pd.DataFrame())
    
    if products_df.empty:
        st.error("⚠️ Data not loaded.")
        return

    st.markdown("""
    <h2 style="font-family:'Sora',sans-serif;color:#f0eaff;margin-bottom:0.3rem;">🤖 Recommendations</h2>
    <div style="font-size:0.85rem;color:#9f87c4;margin-bottom:1.5rem;">
      Personalized product picks powered by our Hybrid AI Engine
    </div>
    """, unsafe_allow_html=True)

    # ── Algorithm info ───────────────────────────────────────────────────────
    with st.expander("ℹ️ How our recommendation engine works"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="sr-card">
              <div style="font-size:1.5rem;margin-bottom:0.5rem;">📝</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;font-size:0.88rem;">Content-Based (60%)</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin-top:0.4rem;">TF-IDF + Cosine Similarity on product descriptions, categories, and tags</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="sr-card">
              <div style="font-size:1.5rem;margin-bottom:0.5rem;">👥</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;font-size:0.88rem;">Collaborative (40%)</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin-top:0.4rem;">User×Product matrix, Nearest Neighbors, finds users with similar taste</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="sr-card">
              <div style="font-size:1.5rem;margin-bottom:0.5rem;">⚡</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;font-size:0.88rem;">Hybrid Score</div>
              <div style="font-size:0.78rem;color:#9f87c4;margin-top:0.4rem;">0.6 × Content Score + 0.4 × Collaborative Score = Final Recommendation</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 For You", "🔗 Similar Items", "🔥 Trending", "🆕 New Arrivals"])

    # ── TAB 1: For You ───────────────────────────────────────────────────────
    with tab1:
        viewed = st.session_state.get("viewed_products", [])
        
        if engine:
            try:
                for_you = engine.recommend_for_user(
                    st.session_state.user_id,
                    viewed_products=viewed,
                    n=12
                )
            except:
                for_you = products_df.nlargest(12, "rating")
        else:
            for_you = products_df.nlargest(12, "rating")
        
        st.markdown(f"""
        <div style="margin:1rem 0;padding:0.8rem;background:rgba(108,63,224,0.08);
             border-radius:12px;border:1px solid rgba(108,63,224,0.15);">
          <div style="font-size:0.82rem;color:#9f87c4;">
            🤖 Showing <strong style="color:#a78bfa;">{len(for_you)}</strong> personalized picks based on your activity
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, (_, p) in enumerate(for_you.head(8).iterrows()):
            with cols[i % 4]:
                render_rec_card(p, engine, i, "fy")
        
        # Explainer section
        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;font-size:1rem;margin-bottom:1rem;">
          Because you viewed Samsung Galaxy S24 Ultra
        </div>
        """, unsafe_allow_html=True)
        
        viewed_based = products_df[products_df["category"] == "Smartphones"].head(3)
        vb_cols = st.columns(3)
        for i, (_, p) in enumerate(viewed_based.iterrows()):
            with vb_cols[i]:
                render_rec_card(p, engine, i + 100, "vb")
        
        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;font-size:1rem;margin:1.5rem 0 1rem 0;">
          Customers also bought
        </div>
        """, unsafe_allow_html=True)
        
        also_bought = products_df.sample(min(3, len(products_df)), random_state=42)
        ab_cols = st.columns(3)
        for i, (_, p) in enumerate(also_bought.iterrows()):
            with ab_cols[i]:
                render_rec_card(p, engine, i + 200, "ab")

    # ── TAB 2: Similar Items ─────────────────────────────────────────────────
    with tab2:
        st.markdown("**Find similar products to what you've viewed:**")
        
        viewed_list = st.session_state.get("viewed_products", [])
        if viewed_list and not products_df.empty:
            viewed_names = products_df[products_df["product_id"].isin(viewed_list[:10])]["name"].tolist()
        else:
            viewed_names = products_df["name"].head(10).tolist()
        
        selected_name = st.selectbox("Select a product to find similar ones:", 
                                      viewed_names if viewed_names else ["No products viewed yet"],
                                      key="similar_select")
        
        if selected_name and selected_name != "No products viewed yet":
            sel_product = products_df[products_df["name"] == selected_name]
            if not sel_product.empty and engine:
                sel_pid = sel_product.iloc[0]["product_id"]
                try:
                    similar = engine.recommend_similar(sel_pid, n=8)
                    
                    st.markdown(f"""
                    <div style="font-size:0.82rem;color:#9f87c4;margin:0.8rem 0;">
                      Showing {len(similar)} products similar to <strong style="color:#a78bfa;">{selected_name}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    sim_cols = st.columns(4)
                    for i, (_, p) in enumerate(similar.head(8).iterrows()):
                        with sim_cols[i % 4]:
                            render_rec_card(p, engine, i + 300, "si")
                except Exception as e:
                    st.error(f"Could not find similar products: {e}")

    # ── TAB 3: Trending ──────────────────────────────────────────────────────
    with tab3:
        if engine:
            try:
                trending = engine.get_trending(n=12)
            except:
                trending = products_df.nlargest(12, "purchases")
        else:
            trending = products_df.nlargest(12, "purchases")
        
        st.markdown("""
        <div style="font-size:0.82rem;color:#9f87c4;margin-bottom:1rem;">
          🔥 Most viewed and purchased products this week
        </div>
        """, unsafe_allow_html=True)
        
        # Top 3 highlighted
        top3_cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        for i, (_, p) in enumerate(trending.head(3).iterrows()):
            with top3_cols[i]:
                icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
                st.markdown(f"""
                <div class="sr-card" style="text-align:center;background:linear-gradient(135deg,#1a0a3e,#2d1065);">
                  <div style="font-size:2rem;">{medals[i]}</div>
                  <div style="font-size:3rem;margin:0.5rem 0;">{icon}</div>
                  <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;font-size:0.9rem;">
                    {truncate_text(str(p.get('name','')), 35)}
                  </div>
                  <div style="color:#f59e0b;font-size:0.85rem;margin:0.3rem 0;">
                    ⭐ {p.get('rating',4.0):.1f}
                  </div>
                  <div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:700;color:#a78bfa;">
                    {format_naira(p.get('price',0))}
                  </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Product", key=f"top3_{p['product_id']}_{i}", use_container_width=True):
                    st.session_state.current_product = p.to_dict()
                    log_activity(st.session_state.user_id, p["product_id"], "view")
                    st.session_state.current_page = "Search"
                    st.rerun()
        
        st.markdown("""<div style="height:1.5rem;"></div>""", unsafe_allow_html=True)
        
        # Rest of trending
        trend_cols = st.columns(4)
        for i, (_, p) in enumerate(trending.iloc[3:11].iterrows()):
            with trend_cols[i % 4]:
                render_rec_card(p, engine, i + 400, "tr")

    # ── TAB 4: New Arrivals ──────────────────────────────────────────────────
    with tab4:
        if engine:
            try:
                new_arr = engine.get_new_arrivals(n=12)
            except:
                new_arr = products_df.tail(12)
        else:
            new_arr = products_df.tail(12)
        
        st.markdown("""
        <div style="font-size:0.82rem;color:#9f87c4;margin-bottom:1rem;">
          ✨ Freshly added products to our catalog
        </div>
        """, unsafe_allow_html=True)
        
        na_cols = st.columns(4)
        for i, (_, p) in enumerate(new_arr.head(12).iterrows()):
            with na_cols[i % 4]:
                render_rec_card(p, engine, i + 500, "na")
