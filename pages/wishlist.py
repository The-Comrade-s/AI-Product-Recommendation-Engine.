"""
SmartRecommend - Wishlist Page
"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, truncate_text, log_activity


def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    engine = st.session_state.get("engine")
    
    col_title, col_edit = st.columns([4, 1])
    with col_title:
        st.markdown("""
        <h2 style="font-family:'Sora',sans-serif;color:#f0eaff;margin-bottom:0.3rem;">💝 Wishlist</h2>
        """, unsafe_allow_html=True)
    with col_edit:
        editing = st.button("✏️ Edit", key="edit_wishlist")
    
    wishlist_ids = st.session_state.get("wishlist", [])
    
    # Add some demo items if empty
    if not wishlist_ids and not products_df.empty:
        demo_ids = products_df.head(4)["product_id"].tolist()
        st.session_state.wishlist = demo_ids
        wishlist_ids = demo_ids
    
    if not wishlist_ids or products_df.empty:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#9f87c4;">
          <div style="font-size:3rem;margin-bottom:1rem;">💝</div>
          <div style="font-family:'Sora',sans-serif;font-size:1.2rem;color:#f0eaff;">Your wishlist is empty</div>
          <div style="font-size:0.85rem;margin-top:0.5rem;">Start adding products you love!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Browse Products", use_container_width=False):
            st.session_state.current_page = "Search"
            st.rerun()
        return
    
    wish_products = products_df[products_df["product_id"].isin(wishlist_ids)]
    
    st.markdown(f"""
    <div style="font-size:0.82rem;color:#9f87c4;margin-bottom:1rem;">
      {len(wish_products)} items saved
    </div>
    """, unsafe_allow_html=True)
    
    total_value = wish_products["price"].sum()
    st.markdown(f"""
    <div style="background:rgba(108,63,224,0.08);border:1px solid rgba(108,63,224,0.15);
         border-radius:12px;padding:0.8rem 1rem;margin-bottom:1rem;
         display:flex;justify-content:space-between;align-items:center;">
      <div style="font-size:0.82rem;color:#9f87c4;">Total wishlist value:</div>
      <div style="font-family:'Sora',sans-serif;font-weight:700;color:#a78bfa;font-size:1.1rem;">
        {format_naira(total_value)}
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    for _, p in wish_products.iterrows():
        icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
        
        col_img, col_info, col_actions = st.columns([1, 4, 2])
        
        with col_img:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e1040,#2a1860);border-radius:12px;
                 height:80px;width:80px;display:flex;align-items:center;justify-content:center;
                 font-size:2rem;border:1px solid #2e1f5e;">
              {icon}
            </div>
            """, unsafe_allow_html=True)
        
        with col_info:
            st.markdown(f"""
            <div>
              <div style="font-family:'Sora',sans-serif;font-weight:600;color:#f0eaff;font-size:0.92rem;">
                {p.get('name','')}
              </div>
              <div style="font-size:0.75rem;color:#9f87c4;margin:2px 0;">
                {p.get('category','')} · ⭐ {p.get('rating',4.0):.1f}
              </div>
              <div style="font-family:'Sora',sans-serif;font-weight:700;color:#a78bfa;font-size:1rem;">
                {format_naira(p.get('price',0))}
              </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            a1, a2 = st.columns(2)
            with a1:
                if st.button("🛒 Buy", key=f"wish_buy_{p['product_id']}", use_container_width=True):
                    log_activity(st.session_state.user_id, p["product_id"], "purchase")
                    st.toast("Added to cart! 🛒")
            with a2:
                if st.button("🗑️", key=f"wish_del_{p['product_id']}", use_container_width=True):
                    st.session_state.wishlist.remove(p["product_id"])
                    st.toast("Removed from wishlist")
                    st.rerun()
        
        st.markdown("""<div class="sr-divider" style="margin:0.6rem 0;"></div>""", unsafe_allow_html=True)
