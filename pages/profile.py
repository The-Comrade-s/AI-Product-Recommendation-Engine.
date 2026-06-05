"""
SmartRecommend - User Profile Page
"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, CATEGORY_COLORS, truncate_text


def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#4c1d95,#6c3fe0,#7c3aed);border-radius:24px;
         padding:2rem;margin-bottom:1.5rem;position:relative;overflow:hidden;">
      <div style="display:flex;align-items:center;gap:1.2rem;position:relative;z-index:1;">
        <div style="width:72px;height:72px;border-radius:50%;background:rgba(255,255,255,0.2);
             backdrop-filter:blur(10px);border:3px solid rgba(255,255,255,0.3);
             display:flex;align-items:center;justify-content:center;font-size:2rem;">👤</div>
        <div>
          <div style="font-family:'Sora',sans-serif;font-weight:800;color:white;font-size:1.4rem;">
            {st.session_state.user_name}
          </div>
          <div style="font-size:0.82rem;color:rgba(255,255,255,0.7);">
            {st.session_state.user_email}
          </div>
        </div>
        <div style="margin-left:auto;display:flex;gap:2rem;">
          <div style="text-align:center;">
            <div style="font-family:'Sora',sans-serif;font-weight:700;color:white;font-size:1.3rem;">{st.session_state.orders_count}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.7);">Orders</div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'Sora',sans-serif;font-weight:700;color:white;font-size:1.3rem;">{len(st.session_state.wishlist) + st.session_state.wishlist_count}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.7);">Wishlist</div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'Sora',sans-serif;font-weight:700;color:white;font-size:1.3rem;">{st.session_state.products_viewed}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.7);">Viewed</div>
          </div>
          <div style="text-align:center;">
            <div style="font-family:'Sora',sans-serif;font-weight:700;color:white;font-size:1.3rem;">{st.session_state.ratings_given}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.7);">Ratings</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Account section
        st.markdown("""
        <div class="sr-card">
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">Account</div>
        """, unsafe_allow_html=True)

        menu_items = [
            ("👤", "Personal Information"),
            ("💳", "Payment Methods"),
            ("📍", "Address Book"),
            ("📦", "Order History"),
        ]
        for icon, label in menu_items:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:0.7rem 0;border-bottom:1px solid #2e1f5e;cursor:pointer;">
              <div style="display:flex;align-items:center;gap:10px;font-size:0.85rem;color:#c4b5e8;">
                <span>{icon}</span><span>{label}</span>
              </div>
              <span style="color:#9f87c4;">›</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;
             margin:1.2rem 0 0.8rem 0;">Preferences</div>
        """, unsafe_allow_html=True)

        pref_items = [
            ("🏷️", "Category Interests"),
            ("🔔", "Notification Settings"),
            ("🔒", "Privacy & Security"),
        ]
        for icon, label in pref_items:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:0.7rem 0;border-bottom:1px solid #2e1f5e;cursor:pointer;">
              <div style="display:flex;align-items:center;gap:10px;font-size:0.85rem;color:#c4b5e8;">
                <span>{icon}</span><span>{label}</span>
              </div>
              <span style="color:#9f87c4;">›</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.toast("Logged out (demo mode - staying logged in)")

    with col_right:
        # User Preferences / Intelligence
        st.markdown("""
        <div class="sr-card" style="margin-bottom:1rem;">
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">
            🧠 User Preference Intelligence
          </div>
          <div style="font-size:0.8rem;color:#9f87c4;margin-bottom:1rem;">
            Built from your browsing, ratings, and purchase history
          </div>
        """, unsafe_allow_html=True)

        category_prefs = [
            ("Technology", 70, "#6c3fe0"),
            ("Gaming", 20, "#ef4444"),
            ("Books", 10, "#f59e0b"),
            ("Fashion", 5, "#f43f5e"),
        ]
        for cat, pct, color in category_prefs:
            st.markdown(f"""
            <div class="pref-bar-wrap">
              <div class="pref-label"><span>{cat}</span><span style="color:{color};font-weight:600;">{pct}%</span></div>
              <div class="pref-bar"><div class="pref-fill" style="width:{pct}%;background:{color};"></div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Recently Viewed
        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;
             margin:1rem 0 0.8rem;">Recently Viewed</div>
        """, unsafe_allow_html=True)

        viewed_ids = st.session_state.get("viewed_products", [])
        if viewed_ids and not products_df.empty:
            viewed_prods = products_df[products_df["product_id"].isin(viewed_ids[:4])]
        else:
            viewed_prods = products_df.head(4) if not products_df.empty else pd.DataFrame()

        if not viewed_prods.empty:
            v_cols = st.columns(4)
            for i, (_, p) in enumerate(viewed_prods.iterrows()):
                with v_cols[i]:
                    icon = CATEGORY_ICONS.get(p.get("category",""), "🛍️")
                    st.markdown(f"""
                    <div style="background:#1a1035;border:1px solid #2e1f5e;border-radius:12px;
                         padding:0.7rem;text-align:center;">
                      <div style="font-size:1.8rem;margin-bottom:4px;">{icon}</div>
                      <div style="font-size:0.7rem;color:#c4b5e8;font-weight:500;">
                        {truncate_text(str(p.get('name','')), 20)}
                      </div>
                      <div style="font-size:0.75rem;color:#a78bfa;font-weight:600;">
                        {format_naira(p.get('price',0))}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No recently viewed products yet. Start browsing!")

        # Edit profile form
        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Sora',sans-serif;font-weight:700;color:#f0eaff;margin-bottom:1rem;">
          ✏️ Edit Profile
        </div>
        """, unsafe_allow_html=True)

        new_name = st.text_input("Full Name", value=st.session_state.user_name)
        new_city = st.selectbox("City", ["Lagos", "Abuja", "Port Harcourt", "Ibadan", "Kano", "Enugu"],
                                 index=0)
        new_cats = st.multiselect("Preferred Categories",
                                   list(CATEGORY_ICONS.keys())[:-1],
                                   default=st.session_state.preferred_categories)

        if st.button("💾 Save Changes", use_container_width=True, key="save_profile"):
            st.session_state.user_name = new_name
            st.session_state.user_city = new_city
            st.session_state.preferred_categories = new_cats
            st.success("✅ Profile updated successfully!")
            st.rerun()
