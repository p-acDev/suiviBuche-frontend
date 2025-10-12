import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px
import json

# =====================
# 🔐 Authentification simple
# =====================
secrets = st.secrets["auth"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Sidebar login
with st.sidebar:
    st.title("Connexion 🔒")
    if not st.session_state.logged_in:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if username == secrets["username"] and password == secrets["password"]:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Connecté !")
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")
        st.stop()
    else:
        st.markdown(f"✅ Connecté en tant que **{st.session_state.username}**")
        if st.button("Se déconnecter"):
            st.session_state.clear()
            st.rerun()

# =====================
# 🌐 Config API
# =====================
API_BASE = st.secrets["api"]["base_url"]
API_KEY = st.secrets["api"]["key"]
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

# =====================
# ⚙️ Fonctions utilitaires
# =====================
def parse_date(d):
    if not d:
        return datetime.min
    if isinstance(d, str):
        try:
            return datetime.fromisoformat(d)
        except ValueError:
            return datetime.min
    if isinstance(d, datetime):
        return d
    return datetime.min

def safe_json(resp):
    try:
        data = resp.json()
        if isinstance(data, dict) and "body" in data:
            return json.loads(data["body"])
        return data
    except ValueError:
        st.error(f"Erreur API : {resp.text}")
        return {}

# =====================
# 🔗 Fonctions API
# =====================
def post_api(path, payload):
    payload["username"] = st.session_state.get("username")
    resp = requests.post(f"{API_BASE}/{path}", json=payload, headers=HEADERS)
    return safe_json(resp)

def get_stock():
    return post_api("get-stock", {})

def get_history():
    data = post_api("history", {})
    return data.get("Items", []) if isinstance(data, dict) else data

def add_stock(quantity, date=None):
    payload = {"quantity": quantity}
    if date:
        payload["date"] = date
    return post_api("add-stock", payload)

def consume_stock(quantity, date=None):
    payload = {"quantity": quantity}
    if date:
        payload["date"] = date
    return post_api("consume", payload)

# =====================
# 🖥️ Interface principale
# =====================
st.title("🔥 Suivi de consommation de bûches")

# --- Stock actuel ---
stock = get_stock()
stock_total = stock.get("total", 0)
st.metric("Bûches disponibles", stock_total)

@st.dialog("Ajout de bûches")
def add_stock_dialog():
    st.subheader("➕ Ajouter des bûches")
    qty_add = st.number_input("Quantité à ajouter", min_value=1, value=5, key="add_qty")
    date_add = st.date_input("Date", value=datetime.today(), key="add_date")
    if st.button("Ajouter au stock"):
        dt_str = date_add.isoformat() + "T00:00:00"
        result = add_stock(qty_add, dt_str)
        st.success(f"Stock mis à jour : {result.get('total', '?')} bûches")
        st.rerun()


st.subheader("🔥 Consommer des bûches")
cols = st.columns(2)
with cols[0]:
    qty_consume = st.number_input("Quantité consommée", min_value=1, value=2, key="consume_qty")
with cols[1]:
    date_consume = st.date_input("Date", value=datetime.today(), key="consume_date")

if st.button("Soustraire du stock"):
    dt_str = date_consume.isoformat() + "T00:00:00"
    result = consume_stock(qty_consume, dt_str)
    st.success(f"Stock mis à jour : {result.get('total', '?')} bûches")
    st.rerun()

if st.button("➕ Ajouter des bûches"):
    add_stock_dialog()

