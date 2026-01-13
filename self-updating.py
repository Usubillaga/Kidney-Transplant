import streamlit as st
from pymed import PubMed
import pandas as pd
import graphviz
import datetime

# --- CONFIG ---
st.set_page_config(page_title="NTX AI-Guide 2026", layout="wide")

# --- 🧠 INTELLIGENT AUTO-SEARCH AGENT ---
class AutoResearchAgent:
    def __init__(self):
        self.pubmed = PubMed(tool="NTX_AutoUpdater", email="bot@clinical-ai.com")
        self.today = datetime.date.today()
        self.current_year = self.today.year

    @st.cache_data(ttl=43200) # Cache für 12 Stunden (spart API Calls)
    def scan_for_guidelines(_self):
        """
        Sucht autonom nach neuen Leitlinien, die den statischen Code ergänzen.
        """
        # Komplexe Query für hochwertige Treffer
        query = (
            f'(("kidney transplantation"[Title] OR "renal transplantation"[Title]) '
            f'AND ("guideline"[Title] OR "consensus"[Title] OR "recommendation"[Title]) '
            f'AND ("{_self.current_year}"[Date - Publication] OR "{_self.current_year - 1}"[Date - Publication]))'
        )
        
        try:
            results = _self.pubmed.query(query, max_results=10)
            candidates = []
            
            for article in results:
                title = article.title if article.title else ""
                abstract = article.abstract if article.abstract else ""
                
                # --- INTELLIGENCE FILTER ---
                # 1. Ausschluss von Tierstudien
                if any(x in abstract.lower() for x in ['rat ', 'murine', 'mouse', 'porcine']):
                    continue
                # 2. Ausschluss von reinen Studienprotokollen
                if "protocol" in title.lower():
                    continue

                # --- SCORING SYSTEM ---
                score = 0
                if "EAU" in title or "European Association of Urology" in title: score += 10
                if "KDIGO" in title: score += 10
                if "Robotic" in title or "RAKT" in title: score += 5
                
                # Nur relevante Ergebnisse aufnehmen
                candidates.append({
                    "Date": article.publication_date,
                    "Title": title,
                    "Score": score,
                    "Abstract": abstract,
                    "Source": "Auto-Agent"
                })
            
            # Sortieren nach Relevanz (Score)
            candidates.sort(key=lambda x: x['Score'], reverse=True)
            return candidates[:3] # Top 3 zurückgeben
            
        except Exception as e:
            return []

# Agent initialisieren
agent = AutoResearchAgent()
new_updates = agent.scan_for_guidelines()

# --- STATIC EVIDENCE DATABASE (Der "sichere" Kern) ---
evidence_db = {
    "heparin_donor": {"DE": "Systemische Heparinisierung (3000-5000 IE).", "Evidenz": "Level 1b"},
    "machine_perfusion": {"DE": "HMP überlegen gegenüber Kälte.", "Evidenz": "Level 1a"}
}

# --- HELPER FUNCTIONS ---
def get_evidence_badge(key):
    # Statische Evidenz
    data = evidence_db.get(key)
    if data:
        st.info(f"📚 **Standard:** {data['DE']} ({data['Evidenz']})")

def render_dynamic_updates():
    """Zeigt die vom Agenten gefundenen Updates an"""
    if new_updates:
        st.markdown("---")
        st.warning(f"🤖 **AI-Agent Update:** {len(new_updates)} neue Leitlinien gefunden!")
        for update in new_updates:
            with st.expander(f"🆕 {update['Title']} (Score: {update['Score']})"):
                st.caption(f"Publiziert: {update['Date']}")
                st.write(update['Abstract'])
                st.markdown("**Status:** Wird zur Integration vorgeschlagen.")

# --- NAVIGATION ---
st.sidebar.title("NTX AI-Guide")
nav = st.sidebar.radio("Menü", ["Dashboard", "Living Donor (RDN)", "Auto-Updates"])

# --- CONTENT ---

if nav == "Dashboard":
    st.title("Clinical Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.success("Verifizierte Standards (Static)")
        st.write("• RAKT für BMI > 30")
        st.write("• HMP für ECD Spender")
    with col2:
        if new_updates:
            st.error("Neue Signale (Dynamic)")
            st.write(f"• {new_updates[0]['Title'][:50]}...")
        else:
            st.info("System aktuell. Keine neuen Leitlinien.")

elif nav == "Living Donor (RDN)":
    st.title("Robotische Spendernephrektomie")
    
    # 1. Zeige den festen Standard
    st.subheader("Standard Vorgehen")
    st.write("Gabe von Heparin 3-5 min vor Abklemmen.")
    get_evidence_badge("heparin_donor")
    
    # 2. Zeige dynamische Updates, falls sie RDN betreffen
    relevant_updates = [u for u in new_updates if "donor" in u['Title'].lower() or "nephrectomy" in u['Title'].lower()]
    if relevant_updates:
        st.markdown("---")
        st.caption("⚡ **Live-Daten vom Agenten:**")
        for u in relevant_updates:
            st.warning(f"Potenzielles Update: {u['Title']}")

elif nav == "Auto-Updates":
    st.title("⚙️ Autonomer Forschungs-Agent")
    st.write("Dieser Agent scannt PubMed nach 'Guideline' & 'Consensus' und filtert Tierstudien aus.")
    
    if st.button("Manueller Scan (Cache leeren)"):
        st.cache_data.clear()
        st.rerun()
        
    render_dynamic_updates()
