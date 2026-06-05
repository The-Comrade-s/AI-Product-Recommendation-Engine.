"""
SmartRecommend - Search & Product Detail Page
"""
import streamlit as st
import pandas as pd
from utils.helpers import (
    format_naira, CATEGORY_ICONS, CATEGORY_COLORS,
    get_star_display, truncate_text, log_activity
)


def render_product_detail(p, engine, products_df):
    """Full product detail view"""
    col_img, col_info = st.columns([1, 2])
    
    with col_img:
        icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1e1040,#2d1860);border-radius:20px;
             height:300px;display:flex;align-items:center;justify-content:center;
             font-size:6rem;border:1px solid #2e1f5e;position:relative;">
          {icon}
          <div style="position:absolute;top:12px;right:12px;font-size:0.75rem;
               background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.3);
               border-radius:8px;padding:3px 8px;font-weight:600;">
            {'● In Stock' if p.get('in_stock', True) else '● Out of Stock'}
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🛒 Add to Cart", key="detail_cart", use_container_width=True):
                log_activity(st.session_state.user_id, p["product_id"], "purchase")
                st.toast("Added to cart! 🛒")
        with b2:
            in_wishlist = p["product_id"] in st.session_state.wishlist
            label = "💜 Saved" if in_wishlist else "🤍 Wishlist"
            if st.button(label, key="detail_wish", use_container_width=True):
                if not in_wishlist:
                    st.session_state.wishlist.append(p["product_id"])
                    log_activity(st.session_state.user_id, p["product_id"], "wishlist")
                    st.toast("Added to wishlist! 💜")
                else:
                    st.session_state.wishlist.remove(p["product_id"])
                    st.toast("Removed from wishlist")
                st.rerun()

        # Rating
        st.markdown("**Rate this product:**")
        rating_val = st.slider("Your rating", 1.0, 5.0, 4.0, 0.5, key="user_rating", label_visibility="collapsed")
        if st.button("⭐ Submit Rating", key="submit_rating", use_container_width=True):
            st.session_state.rated_products[p["product_id"]] = rating_val
            log_activity(st.session_state.user_id, p["product_id"], "like")
            st.toast(f"Rating submitted: {rating_val}⭐")
    
    with col_info:
        # Breadcrumb
        st.markdown(f"""
        <div style="font-size:0.78rem;color:#9f87c4;margin-bottom:0.8rem;">
          Home › {p.get('category','')} › {truncate_text(str(p.get('name','')), 30)}
        </div>
        """, unsafe_allow_html=True)
        
        cat_color = CATEGORY_COLORS.get(p.get("category", ""), "#6c3fe0")
        st.markdown(f"""
        <div>
          <span style="background:rgba(108,63,224,0.15);color:#a78bfa;border:1px solid rgba(108,63,224,0.3);
                border-radius:6px;padding:2px 10px;font-size:0.72rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.08em;">
            {p.get('category','')}
          </span>
          <h2 style="font-family:'Sora',sans-serif;font-weight:800;color:#f0eaff;margin:0.7rem 0 0.4rem 0;line-height:1.2;">
            {p.get('name','')}
          </h2>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.8rem;">
            <span style="color:#f59e0b;font-size:1rem;">{'⭐' * int(p.get('rating',4))}</span>
            <span style="font-weight:700;color:#f59e0b;">{p.get('rating',4.0):.1f}</span>
            <span style="color:#9f87c4;font-size:0.82rem;">({int(p.get('num_reviews',0))} Reviews)</span>
          </div>
          <div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;
               color:#a78bfa;margin-bottom:0.5rem;">
            {format_naira(p.get('price', 0))}
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        st.markdown(f"""
        <div style="background:rgba(108,63,224,0.06);border-radius:14px;padding:1rem;margin:0.8rem 0;">
          <div style="font-size:0.78rem;color:#9f87c4;text-transform:uppercase;letter-spacing:0.08em;
               margin-bottom:0.5rem;font-weight:600;">Key Features</div>
          <div style="font-size:0.85rem;color:#c4b5e8;line-height:1.7;">
            {"".join(f'<div>✓ {f.strip()}</div>' for f in str(p.get('description','')).split(',')[:4])}
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Why we recommend
        if engine:
            try:
                explanation = engine.explain_recommendation(
                    p["product_id"],
                    user_id=st.session_state.user_id,
                    viewed_products=st.session_state.viewed_products,
                    liked_categories=st.session_state.preferred_categories
                )
                
                reasons = explanation.get("reasons", [])
                tags = explanation.get("tags", [])
                confidence = explanation.get("confidence", 80)
                
                if reasons:
                    tags_html = " ".join(f'<span class="reason-chip">✓ {r}</span>' for r in reasons[:3])
                    chips_html = " ".join(f'<span class="badge badge-primary">{t}</span>' for t in tags[:3])
                    st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);
                         border-radius:14px;padding:1rem;margin:0.8rem 0;">
                      <div style="font-size:0.82rem;font-weight:700;color:#34d399;margin-bottom:0.6rem;">
                        🤖 Why we recommend this?
                      </div>
                      <div style="font-size:0.8rem;color:#9f87c4;margin-bottom:0.6rem;">
                        Based on your interest in similar products and users with similar preferences.
                      </div>
                      <div style="margin-bottom:0.5rem;">{chips_html}</div>
                      <div style="font-size:0.78rem;color:#9f87c4;margin-top:0.4rem;">
                        Confidence Score: <strong style="color:#34d399;">{confidence}%</strong>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                pass
    
    # ── Similar Products ────────────────────────────────────────────────────
    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
      <div class="section-title">You May Also Like</div>
    </div>
    """, unsafe_allow_html=True)
    
    if engine and not products_df.empty:
        try:
            similar = engine.recommend_similar(p["product_id"], n=4)
        except:
            similar = products_df[products_df["category"] == p.get("category")].head(4)
    else:
        similar = products_df.head(4)
    
    sim_cols = st.columns(4)
    for i, (_, sp) in enumerate(similar.head(4).iterrows()):
        with sim_cols[i]:
            icon2 = CATEGORY_ICONS.get(sp.get("category", ""), "🛍️")
            st.markdown(f"""
            <div class="product-card">
              <div style="height:110px;background:linear-gradient(135deg,#1e1040,#2a1860);
                   display:flex;align-items:center;justify-content:center;font-size:2.5rem;">
                {icon2}
              </div>
              <div class="product-body">
                <div class="product-name">{truncate_text(str(sp.get('name','')), 40)}</div>
                <div class="product-rating">⭐ {sp.get('rating',4.0):.1f}</div>
                <div class="product-price">{format_naira(sp.get('price',0))}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View", key=f"sim_{sp['product_id']}_{i}", use_container_width=True):
                st.session_state.current_product = sp.to_dict()
                log_activity(st.session_state.user_id, sp["product_id"], "view")
                if sp["product_id"] not in st.session_state.viewed_products:
                    st.session_state.viewed_products.append(sp["product_id"])
                st.rerun()


def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    engine = st.session_state.get("engine")
    
    if products_df.empty:
        st.error("⚠️ Data not loaded.")
        return

    # ── Check if viewing a product detail ───────────────────────────────────
    if st.session_state.get("current_product"):
        p = st.session_state.current_product
        
        col_back, col_title = st.columns([1, 5])
        with col_back:
            if st.button("← Back", key="back_from_detail"):
                st.session_state.current_product = None
                st.rerun()
        with col_title:
            st.markdown(f"""
            <h2 style="font-family:'Sora',sans-serif;color:#f0eaff;margin:0;">Product Detail</h2>
            """, unsafe_allow_html=True)
        
        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        render_product_detail(p, engine, products_df)
        return

    # ── Search & Filter layout ───────────────────────────────────────────────
    st.markdown("""
    <h2 style="font-family:'Sora',sans-serif;color:#f0eaff;margin-bottom:1rem;">🔍 Search Products</h2>
    """, unsafe_allow_html=True)

    search_col, filter_col = st.columns([3, 1])
    with search_col:
        query = st.text_input("", placeholder="🔍  Search for products...",
                               value=st.session_state.get("search_query", ""),
                               key="search_input", label_visibility="collapsed")
    with filter_col:
        sort_by = st.selectbox("Sort", ["Most Popular", "Highest Rated", "Price: Low→High", "Price: High→Low", "Newest"],
                                key="sort_select", label_visibility="collapsed")

    # ── Category pills ───────────────────────────────────────────────────────
    st.markdown("<div style='margin:0.8rem 0 0.5rem;font-size:0.82rem;color:#9f87c4;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;'>Categories</div>", unsafe_allow_html=True)
    
    all_cats = ["All"] + list(CATEGORY_ICONS.keys())[:-1]
    cat_cols = st.columns(len(all_cats))
    
    selected_cat = st.session_state.get("selected_category", "All")
    
    for i, cat in enumerate(all_cats):
        with cat_cols[i]:
            icon = CATEGORY_ICONS.get(cat, "🛍️")
            is_active = selected_cat == cat
            border_color = "#a78bfa" if is_active else "#2e1f5e"
            bg_color = "rgba(108,63,224,0.2)" if is_active else "var(--bg-card)"
            st.markdown(f"""
            <div style="background:{bg_color};border:1px solid {border_color};border-radius:12px;
                 padding:0.6rem 0.3rem;text-align:center;cursor:pointer;">
              <div style="font-size:1.4rem;">{icon}</div>
              <div style="font-size:0.65rem;color:{'#f0eaff' if is_active else '#9f87c4'};font-weight:500;">{cat}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(cat, key=f"scat_{cat}", use_container_width=True, label_visibility="collapsed" if True else "visible"):
                st.session_state.selected_category = cat
                st.rerun()

    # ── Filters sidebar (within main area) ───────────────────────────────────
    filter_expand, results_area = st.columns([1, 3])
    
    with filter_expand:
        st.markdown("""
        <div class="sr-card">
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">🎛️ Filters</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Price Range (₦)**")
        max_price = int(products_df["price"].max()) if not products_df.empty else 3000000
        price_range = st.slider("Price", 0, max_price, (0, max_price // 2),
                                 format="₦%d", key="price_filter", label_visibility="collapsed")
        
        st.markdown("**Minimum Rating**")
        min_rating = st.select_slider("Rating", options=[1.0, 2.0, 3.0, 4.0, 4.5],
                                       value=1.0, key="rating_filter",
                                       format_func=lambda x: f"{'⭐'*int(x)} & above",
                                       label_visibility="collapsed")
        
        st.markdown("**Sort By**")
        sort_opt = st.radio("Sort", ["Most Popular", "Highest Rated", "Price ↑", "Price ↓"],
                             key="sort_radio", label_visibility="collapsed")
        
        if st.button("🔄 Reset Filters", use_container_width=True, key="reset_filters"):
            st.session_state.selected_category = "All"
            st.session_state.search_query = ""
            st.rerun()

    with results_area:
        # Apply filters
        filtered = products_df.copy()
        
        if selected_cat != "All":
            filtered = filtered[filtered["category"] == selected_cat]
        
        if query:
            mask = (
                filtered["name"].str.contains(query, case=False, na=False) |
                filtered["description"].str.contains(query, case=False, na=False) |
                filtered["category"].str.contains(query, case=False, na=False) |
                filtered["brand"].str.contains(query, case=False, na=False)
            )
            filtered = filtered[mask]
        
        filtered = filtered[
            (filtered["price"] >= price_range[0]) &
            (filtered["price"] <= price_range[1]) &
            (filtered["rating"] >= min_rating)
        ]
        
        # Sort
        if sort_opt == "Most Popular":
            filtered = filtered.sort_values("purchases", ascending=False)
        elif sort_opt == "Highest Rated":
            filtered = filtered.sort_values("rating", ascending=False)
        elif sort_opt == "Price ↑":
            filtered = filtered.sort_values("price", ascending=True)
        elif sort_opt == "Price ↓":
            filtered = filtered.sort_values("price", ascending=False)
        
        st.markdown(f"""
        <div style="font-family:'Sora',sans-serif;font-weight:600;color:#9f87c4;font-size:0.85rem;margin-bottom:1rem;">
          Products ({len(filtered):,})
        </div>
        """, unsafe_allow_html=True)
        
        # Products grid
        PAGE_SIZE = 12
        if "search_page" not in st.session_state:
            st.session_state.search_page = 0
        
        start = st.session_state.search_page * PAGE_SIZE
        page_products = filtered.iloc[start:start + PAGE_SIZE]
        
        grid_cols = st.columns(3)
        for i, (_, p) in enumerate(page_products.iterrows()):
            with grid_cols[i % 3]:
                icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
                in_wishlist = p["product_id"] in st.session_state.wishlist
                
                st.markdown(f"""
                <div class="product-card">
                  <div style="height:140px;background:linear-gradient(135deg,#1e1040,#2a1860);
                       display:flex;align-items:center;justify-content:center;font-size:3.5rem;
                       position:relative;">
                    {icon}
                  </div>
                  <div class="product-body">
                    <div class="product-category">{p.get('category','')}</div>
                    <div class="product-name">{truncate_text(str(p.get('name','')), 42)}</div>
                    <div class="product-rating">⭐ {p.get('rating',4.0):.1f}
                      <span style="color:#9f87c4;">({int(p.get('num_reviews',0))})</span>
                    </div>
                    <div class="product-price">{format_naira(p.get('price',0))}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                
                btn1, btn2 = st.columns(2)
                with btn1:
                    if st.button("View", key=f"s_view_{p['product_id']}_{i}", use_container_width=True):
                        st.session_state.current_product = p.to_dict()
                        log_activity(st.session_state.user_id, p["product_id"], "view")
                        if p["product_id"] not in st.session_state.viewed_products:
                            st.session_state.viewed_products.append(p["product_id"])
                        st.rerun()
                with btn2:
                    heart = "💜" if in_wishlist else "🤍"
                    if st.button(heart, key=f"s_wish_{p['product_id']}_{i}", use_container_width=True):
                        if not in_wishlist:
                            st.session_state.wishlist.append(p["product_id"])
                            log_activity(st.session_state.user_id, p["product_id"], "wishlist")
                            st.toast("Added to wishlist! 💜")
                        else:
                            st.session_state.wishlist.remove(p["product_id"])
                        st.rerun()
        
        # Pagination
        total_pages = max(1, len(filtered) // PAGE_SIZE + (1 if len(filtered) % PAGE_SIZE else 0))
        if total_pages > 1:
            p_cols = st.columns(5)
            with p_cols[1]:
                if st.button("◀ Prev", use_container_width=True, disabled=st.session_state.search_page == 0):
                    st.session_state.search_page -= 1
                    st.rerun()
            with p_cols[2]:
                st.markdown(f"""<div style="text-align:center;color:#9f87c4;padding:0.5rem 0;font-size:0.82rem;">
                  Page {st.session_state.search_page + 1} / {total_pages}
                </div>""", unsafe_allow_html=True)
            with p_cols[3]:
                if st.button("Next ▶", use_container_width=True, disabled=st.session_state.search_page >= total_pages - 1):
                    st.session_state.search_page += 1
                    st.rerun()
