import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px
import json

# =====================
# Authentification dans la sidebar
# =====================
secrets = st.secrets["auth"]
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.title("Connexion")
    if not st.session_state.logged_in:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if username == secrets["username"] and password == secrets["password"]:
                st.session_state.logged_in = True
                st.success("Connecté !")
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")
        st.stop()
    else:
        if st.button("Se déconnecter"):
            st.session_state.logged_in = False
            st.rerun()

# =====================
# Config API
# =====================
API_BASE = st.secrets["api"]["base_url"]
API_KEY = st.secrets["api"]["key"]
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

# =====================
# Fonctions utilitaires
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
# Fonctions API
# =====================
def add_stock(quantity, date=None):
    payload = {"quantity": quantity}
    if date:
        payload["date"] = date
    resp = requests.post(f"{API_BASE}/add-stock", json=payload, headers=HEADERS)
    return safe_json(resp)

def consume_stock(quantity, date=None):
    payload = {"quantity": quantity}
    if date:
        payload["date"] = date
    resp = requests.post(f"{API_BASE}/consume", json=payload, headers=HEADERS)
    return safe_json(resp)

def get_stock():
    resp = requests.get(f"{API_BASE}/get-stock", headers=HEADERS)
    return safe_json(resp)

def get_history():
    resp = requests.get(f"{API_BASE}/history", headers=HEADERS)
    data = safe_json(resp)
    return data.get("Items", []) if isinstance(data, dict) else data

# =====================
# Interface principale
# =====================
st.title("Suivi du stock de bûches 🔥")

# --- Stock actuel ---
stock = get_stock()
st.metric("Bûches disponibles", stock.get("total", 0))


st.subheader("Consommer des bûches")
col1, col2 = st.columns(2)
with col1:
    qty_consume = st.number_input("Quantité à consommer", min_value=1, value=5, key="qty_consume")
with col2:
    date_consume = st.date_input("Date (optionnel)", value=datetime.today(), key="consume_date")
if st.button("Consommer des bûches"):
    dt_str = date_consume.isoformat() + "T00:00:00" if date_consume else None
    result = consume_stock(qty_consume, dt_str)
    st.success(f"Stock mis à jour : {result.get('total', '?')} bûches")
    st.rerun()

# --- Ajouter au stock ---
@st.dialog("Ajouter des bûches au stock")
def add_stock_dialog():
    st.subheader("Ajouter des bûches")
    col1, col2 = st.columns(2)
    with col1:
        qty_add = st.number_input("Quantité à ajouter", min_value=1, value=10)
    with col2:
        date_add = st.date_input("Date (optionnel)", value=datetime.today())
    if st.button("Ajouter des bûches"):
        dt_str = date_add.isoformat() + "T00:00:00" if date_add else None
        result = add_stock(qty_add, dt_str)
        st.success(f"Stock mis à jour : {result.get('total', '?')} bûches")
        st.rerun()

if st.button("Ajouter du stock"):
    add_stock_dialog()
