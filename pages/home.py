"""
SmartRecommend - Home Page
"""
import streamlit as st
import pandas as pd
import random
from utils.helpers import (
    format_naira, CATEGORY_ICONS, CATEGORY_COLORS,
    get_star_display, truncate_text, log_activity
)


def product_card_html(p, show_rank=False, rank=None):
    icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
    stock_html = '<span class="in-stock">● In Stock</span>' if p.get("in_stock", True) else '<span class="out-stock">● Out of Stock</span>'
    rank_html = f'<span class="rank-badge">{rank}</span>' if show_rank else ""
    return f"""
    <div class="product-card">
      <div class="product-img" style="height:160px;display:flex;align-items:center;justify-content:center;
           background:linear-gradient(135deg,#1e1040 0%,#2a1860 100%);font-size:3.5rem;">
        {icon}{rank_html}
      </div>
      <div class="product-body">
        <div class="product-category">{p.get('category','')}</div>
        <div class="product-name">{truncate_text(str(p.get('name','')), 45)}</div>
        <div class="product-rating">⭐ {p.get('rating', 4.0):.1f} <span style="color:#9f87c4;">({int(p.get('num_reviews',0))})</span></div>
        <div class="product-price">{format_naira(p.get('price', 0))}</div>
        <div style="margin-top:6px;">{stock_html}</div>
      </div>
    </div>
    """


def render():
    engine = st.session_state.get("engine")
    products_df = st.session_state.get("products_df", pd.DataFrame())

    if products_df.empty:
        st.error("⚠️ Data not loaded. Please restart the app.")
        return

    # ── Hero Banner ─────────────────────────────────────────────────────────
    col_hero, col_why = st.columns([3, 1])
    
    with col_hero:
        st.markdown("""
        <div class="hero-banner">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div style="flex:1;">
              <div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:white;line-height:1.2;margin-bottom:0.7rem;">
                Discover Products<br><span style="color:#a78bfa;">You'll Love</span>
              </div>
              <div style="font-size:0.88rem;color:rgba(255,255,255,0.7);max-width:340px;margin-bottom:1.2rem;line-height:1.6;">
                Our AI engine analyzes your preferences and behavior to recommend the best products just for you.
              </div>
              <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(108,63,224,0.8);
                   backdrop-filter:blur(10px);border:1px solid rgba(108,63,224,0.5);border-radius:12px;
                   padding:0.6rem 1.2rem;cursor:pointer;font-weight:600;color:white;font-size:0.88rem;">
                🚀 Explore Recommendations &nbsp;›
              </div>
            </div>
            <div style="font-size:5rem;opacity:0.85;display:flex;gap:1rem;flex-wrap:wrap;max-width:200px;justify-content:center;">
              🎧🖥️📱⌚
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Explore Recommendations", key="hero_cta", use_container_width=False):
            st.session_state.current_page = "Recommendations"
            st.rerun()

    with col_why:
        st.markdown("""
        <div class="sr-card" style="height:100%;">
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">Why This Recommendation?</div>
          <div style="font-size:0.82rem;color:#9f87c4;margin-bottom:1rem;">We recommended these products based on:</div>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;align-items:center;gap:8px;font-size:0.82rem;color:#c4b5e8;">👁️ Products you viewed</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.82rem;color:#c4b5e8;">💜 Items in your wishlist</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.82rem;color:#c4b5e8;">👥 Users with similar interests</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.82rem;color:#c4b5e8;">📂 Your preferred categories</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Search bar ───────────────────────────────────────────────────────────
    search_col, _ = st.columns([2, 1])
    with search_col:
        query = st.text_input("", placeholder="🔍  Search for products, brands, and more...",
                               key="home_search", label_visibility="collapsed")
        if query:
            st.session_state.search_query = query
            st.session_state.current_page = "Search"
            st.rerun()

    # ── Featured Categories ──────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">Featured Categories</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    categories = ["Smartphones", "Laptops", "Electronics", "Fashion", "Home & Kitchen", "Books", "Gaming"]
    cat_cols = st.columns(len(categories) + 1)
    
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            icon = CATEGORY_ICONS.get(cat, "🛍️")
            color = CATEGORY_COLORS.get(cat, "#6c3fe0")
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;
                 padding:1rem 0.5rem;text-align:center;cursor:pointer;transition:all 0.2s;">
              <div style="font-size:1.8rem;margin-bottom:4px;">{icon}</div>
              <div style="font-size:0.7rem;color:#9f87c4;font-weight:500;">{cat.replace(' & ',' &\n')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(cat, key=f"cat_{cat}", use_container_width=True, help=f"Browse {cat}"):
                st.session_state.selected_category = cat
                st.session_state.current_page = "Search"
                st.rerun()

    with cat_cols[-1]:
        st.markdown("""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;
             padding:1rem 0.5rem;text-align:center;">
          <div style="font-size:1.8rem;margin-bottom:4px;">⋯</div>
          <div style="font-size:0.7rem;color:#9f87c4;font-weight:500;">More</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Recommended For You ──────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">🤖 Recommended for You</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    viewed = st.session_state.get("viewed_products", [])
    if engine and not products_df.empty:
        try:
            recs = engine.recommend_for_user(
                st.session_state.user_id,
                viewed_products=viewed,
                n=5
            )
        except:
            recs = products_df.nlargest(5, "rating")
    else:
        recs = products_df.nlargest(5, "rating")

    rec_cols = st.columns(5)
    for i, (_, p) in enumerate(recs.head(5).iterrows()):
        with rec_cols[i]:
            st.markdown(product_card_html(p), unsafe_allow_html=True)
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("View", key=f"rec_view_{p['product_id']}_{i}", use_container_width=True):
                    st.session_state.current_product = p.to_dict()
                    log_activity(st.session_state.user_id, p["product_id"], "view")
                    if p["product_id"] not in st.session_state.viewed_products:
                        st.session_state.viewed_products.append(p["product_id"])
                    st.session_state.current_page = "Search"
                    st.rerun()
            with b_col2:
                if st.button("💜", key=f"rec_like_{p['product_id']}_{i}", use_container_width=True):
                    if p["product_id"] not in st.session_state.wishlist:
                        st.session_state.wishlist.append(p["product_id"])
                    log_activity(st.session_state.user_id, p["product_id"], "like")
                    st.toast(f"Added to wishlist! 💜")

    # ── Trending Now ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">🔥 Trending Now</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    if engine and not products_df.empty:
        try:
            trending = engine.get_trending(n=5)
        except:
            trending = products_df.nlargest(5, "purchases")
    else:
        trending = products_df.nlargest(5, "purchases")

    trend_cols = st.columns(5)
    for i, (_, p) in enumerate(trending.head(5).iterrows()):
        with trend_cols[i]:
            st.markdown(product_card_html(p, show_rank=True, rank=i+1), unsafe_allow_html=True)
            if st.button("View Product", key=f"trend_{p['product_id']}_{i}", use_container_width=True):
                st.session_state.current_product = p.to_dict()
                log_activity(st.session_state.user_id, p["product_id"], "view")
                st.session_state.current_page = "Search"
                st.rerun()

    # ── New Arrivals ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">✨ New Arrivals</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    if engine and not products_df.empty:
        try:
            new_arr = engine.get_new_arrivals(n=4)
        except:
            new_arr = products_df.tail(4)
    else:
        new_arr = products_df.tail(4)

    arr_cols = st.columns(4)
    for i, (_, p) in enumerate(new_arr.head(4).iterrows()):
        with arr_cols[i]:
            st.markdown(product_card_html(p), unsafe_allow_html=True)
            if st.button("View Product", key=f"arr_{p['product_id']}_{i}", use_container_width=True):
                st.session_state.current_product = p.to_dict()
                log_activity(st.session_state.user_id, p["product_id"], "view")
                st.session_state.current_page = "Search"
                st.rerun()

    # ── Activity summary ─────────────────────────────────────────────────────
    col_act, col_acc = st.columns([1, 2])
    with col_act:
        st.markdown("""
        <div class="sr-card">
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">Your Activity</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        """, unsafe_allow_html=True)
        
        activity_stats = [
            ("👁️", "Products Viewed", st.session_state.products_viewed),
            ("⭐", "Products Rated", st.session_state.ratings_given),
            ("💜", "Wishlist Items", len(st.session_state.wishlist) + st.session_state.wishlist_count),
            ("🛒", "Purchases", st.session_state.orders_count),
        ]
        
        act_cols = st.columns(2)
        for i, (icon, label, val) in enumerate(activity_stats):
            with act_cols[i % 2]:
                st.metric(f"{icon} {label}", val)
        
        if st.button("View Full Activity →", key="full_activity", use_container_width=True):
            st.session_state.current_page = "Profile"
            st.rerun()

    with col_acc:
        st.markdown("""
        <div class="sr-card">
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:0.8rem;">Recommendation Accuracy</div>
          <div class="gauge-wrap">
            <div class="gauge-value">92%</div>
            <div class="conf-bar"><div class="conf-fill" style="width:92%;"></div></div>
            <div style="font-size:0.82rem;color:#9f87c4;margin-top:0.5rem;">
              Great! Our AI recommendations are working well for you.
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:1rem;">
            <div style="background:rgba(108,63,224,0.1);border-radius:10px;padding:0.6rem;text-align:center;">
              <div style="font-size:0.7rem;color:#9f87c4;">Content-Based</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#a78bfa;font-size:1rem;">60%</div>
            </div>
            <div style="background:rgba(16,185,129,0.1);border-radius:10px;padding:0.6rem;text-align:center;">
              <div style="font-size:0.7rem;color:#9f87c4;">Collaborative</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#34d399;font-size:1rem;">40%</div>
            </div>
            <div style="background:rgba(245,158,11,0.1);border-radius:10px;padding:0.6rem;text-align:center;">
              <div style="font-size:0.7rem;color:#9f87c4;">Hybrid</div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#fcd34d;font-size:1rem;">✓</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 See Analytics", key="see_analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:2rem;">
    <div class="sr-divider"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;text-align:center;padding:1rem 0;">
      <div>
        <div style="font-size:1.5rem;margin-bottom:4px;">🚚</div>
        <div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;font-size:0.82rem;">Fast & Secure Delivery</div>
        <div style="font-size:0.72rem;color:#9f87c4;">We get your products delivered fast and securely</div>
      </div>
      <div>
        <div style="font-size:1.5rem;margin-bottom:4px;">🎧</div>
        <div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;font-size:0.82rem;">24/7 Customer Support</div>
        <div style="font-size:0.72rem;color:#9f87c4;">We're here to help you anytime you need us</div>
      </div>
      <div>
        <div style="font-size:1.5rem;margin-bottom:4px;">✅</div>
        <div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;font-size:0.82rem;">100% Satisfaction</div>
        <div style="font-size:0.72rem;color:#9f87c4;">We guarantee the best shopping experience</div>
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
