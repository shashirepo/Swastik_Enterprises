"""
auth.py — Authentication module for SWASTIK ENTERPRISES
"""

import hashlib
import streamlit as st

# ─── Login-page-specific CSS (injected before any widget is rendered) ─────────
_LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}
/* Full-screen dark background */
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 45%, #1a1a2e 100%) !important;
  background-attachment: fixed !important;
}
/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
/* Remove top padding */
section.main > div { padding-top: 24px !important; }

/* ── Login card ─────────────────────────────────────────────────────── */
.login-wrap {
  max-width: 440px;
  margin: 48px auto 0;
  background: white;
  border-radius: 24px;
  padding: 44px 40px 38px;
  box-shadow: 0 24px 64px rgba(0,0,0,.40), 0 8px 24px rgba(0,0,0,.20);
  position: relative;
}
.login-icon-wrap {
  width: 64px; height: 64px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; font-weight: 800; color: white;
  margin: 0 auto 18px;
  box-shadow: 0 8px 20px rgba(37,99,235,.45);
}
.login-company { text-align: center; margin-bottom: 28px; }
.login-company-name {
  font-size: 20px; font-weight: 800; color: #0f172a;
  letter-spacing: .2px; margin-bottom: 5px;
}
.login-company-sub { font-size: 13px; color: #94a3b8; font-weight: 400; }
.login-divider {
  height: 1.5px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  margin: 0 -40px 28px;
}
.login-error {
  background: #fef2f2;
  border: 1.5px solid #fecaca;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  color: #991b1b;
  font-weight: 500;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.login-footer {
  text-align: center;
  font-size: 11.5px;
  color: #94a3b8;
  margin-top: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* Override Streamlit inputs inside login */
.stTextInput > div > div > input {
  background: #f8fafc !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 10px !important;
  font-size: 14px !important;
  padding: 12px 14px !important;
  color: #0f172a !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:focus {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
  background: white !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #94a3b8 !important; }
.stTextInput > label {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: #475569 !important;
  letter-spacing: .3px !important;
  text-transform: none !important;
}
/* Sign In button */
.stFormSubmitButton > button {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  font-size: 15px !important;
  font-weight: 700 !important;
  padding: 13px 24px !important;
  width: 100% !important;
  margin-top: 6px !important;
  box-shadow: 0 4px 14px rgba(37,99,235,.40) !important;
  transition: all .2s ease !important;
  letter-spacing: .2px !important;
  font-family: 'Inter', sans-serif !important;
}
.stFormSubmitButton > button:hover {
  box-shadow: 0 8px 24px rgba(37,99,235,.55) !important;
  transform: translateY(-2px) !important;
}
.stFormSubmitButton > button:active { transform: translateY(0) !important; }

/* Troubleshoot expander */
div[data-testid="stExpander"] {
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  margin-top: 10px !important;
}
div[data-testid="stExpander"] summary {
  font-size: 12.5px !important;
  font-weight: 600 !important;
  color: #64748b !important;
  padding: 12px 14px !important;
}
</style>
"""


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    defaults = {
        "admin":    {"name": "Administrator",  "password_hash": "cfad5ccaf32fb8765202858e5a6d7f6b2e88b9ca8f4d0cd433590163fd384f7e"},
        "ravindra": {"name": "Ravindra Singh", "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
        "veer":     {"name": "Veer Singh",     "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
    }
    try:
        us = st.secrets["auth"]["users"]
        loaded = {
            u.strip().lower(): {
                "name": str(d["name"]).strip(),
                "password_hash": str(d["password_hash"]).strip(),
            }
            for u, d in us.items()
        }
        return loaded if loaded else defaults
    except Exception:
        return defaults


def check_login(username: str, password: str) -> tuple[bool, str]:
    user = _load_users().get(username.strip().lower())
    if user and user["password_hash"] == _hash(password.strip()):
        return True, user["name"]
    return False, ""


def show_login_page() -> None:
    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        st.markdown("""
<div class="login-wrap">
  <div class="login-icon-wrap">S</div>
  <div class="login-company">
    <div class="login-company-name">SWASTIK ENTERPRISES</div>
    <div class="login-company-sub">Sales &amp; Invoice Management Portal</div>
  </div>
  <div class="login-divider"></div>
</div>""", unsafe_allow_html=True)

        if st.session_state.get("login_error"):
            st.markdown("""
<div class="login-error">
  <span>⚠️</span> Invalid username or password. Please try again.
</div>""", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In  →", use_container_width=True)

        if submitted:
            ok, name = check_login(username, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.user_name     = name
                st.session_state.login_error   = False
                import base64
                st.query_params["session"] = base64.b64encode(f"auth:{name}".encode()).decode()
                st.rerun()
            else:
                st.session_state.login_error = True
                st.rerun()

        with st.expander("🔧 Troubleshoot login"):
            dp = st.text_input("Type password to get its hash", type="password", key="dbg")
            if dp:
                st.code(_hash(dp.strip()), language=None)
            if st.button("Show loaded users"):
                for u, d in _load_users().items():
                    st.write(f"• **{u}** → {d['name']}  |  hash: `{d['password_hash'][:16]}…`")

        st.markdown("""
<div class="login-footer">
  🔒&nbsp; Secured access &nbsp;·&nbsp; SWASTIK ENTERPRISES © 2025
</div>""", unsafe_allow_html=True)
