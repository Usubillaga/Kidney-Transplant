import streamlit as st
from pymed import PubMed
import pandas as pd
import graphviz
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NTX Guide 2026: Clinical & Pharma",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER FUNCTIONS ---

@st.cache_data(ttl=3600)
def fetch_pubmed_data(query, max_results=5):
    try:
        pubmed = PubMed(tool="StreamlitNTXApp", email="medical_user@example.com")
        results = pubmed.query(query, max_results=max_results)
        data = []
        for article in results:
            data.append({
                "Titel": article.title,
                "Publiziert": article.publication_date,
                "Abstract": article.abstract[:500] + "..." if article.abstract else "N/A",
                "DOI": article.doi
            })
        return data
    except:
        return []

def render_rdn_workflow_pharma():
    """Workflow: Spender (Entnahme) + MEDIKAMENTE"""
    dot = graphviz.Digraph(comment='RDN Workflow Pharma')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled', fillcolor='#e8f5e9', fontname='Sans-Serif')

    # Nodes
    dot.node('Pos', '1. Lagerung & Zugang')
    dot.node('Hilus', '2. Hilus-Präparation')
    dot.node('Meds', '3. Pharmakologie Bolus\n(3-5 Min vor Clip!)', fillcolor='#ff8a80', style='filled,bold') # ROT für WICHTIG
    dot.node('Clip', '4. Clipping & Schnitt')
    dot.node('Ext', '5. Extraktion (Endobag)')
    dot.node('Perf', '6. Back-Table Perfusion\n(HTK/Custodiol)')

    # Edges
    dot.edge('Pos', 'Hilus')
    dot.edge('Hilus', 'Meds', label=' Kommunikation Anästhesie')
    dot.edge('Meds', 'Clip', label=' Heparin wirkt (ACT Check)')
    dot.edge('Clip', 'Ext', label=' Start Warm-Ischämie')
    dot.edge('Ext', 'Perf')

    return dot

def render_rakt_workflow_pharma():
    """Workflow: Empfänger + MEDIKAMENTE"""
    dot = graphviz.Digraph(comment='RAKT Workflow Pharma')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled', fillcolor='#e1f5fe', fontname='Sans-Serif')
    
    # Nodes
    dot.node('Prep', '1. Zugang & Gefäße')
    dot.node('Anast', '2. Anastomose (Vene -> Arterie)')
    dot.node('Bolus', '3. Reperfusions-Bolus\n(Klemme noch drauf)', fillcolor='#ff8a80', style='filled,bold')
    dot.node('Open', '4. Freigabe (Reperfusion)')
    dot.node('Diurese', '5. Diurese-Check\n(Lasix Gabe?)', fillcolor='#fff9c4')

    # Edges
    dot.edge('Prep', 'Anast')
    dot.edge('Anast', 'Bolus')
    dot.edge('Bolus', 'Open', label=' Solu-Decortin drin?')
    dot.edge('Open', 'Diurese', label=' ICG Check')
    
    return dot

# --- SIDEBAR ---
st.sidebar.title("🏥 NTX-Guide 2026")
st.sidebar.caption("Inkl. Pharmakologie-Protokolle")
mode = st.sidebar.radio("Navigation:", 
    ["Dashboard", "Intraop. Pharmakologie", "Technik: Robotik (Workflows)", "Leitlinien", "Live-Suche"])

# --- MAIN CONTENT ---

# 1. DASHBOARD
if mode == "Dashboard":
    st.title("NTX Update 2026: Übersicht")
    st.info("Fokus: Robotische Präzision und pharmakologische Konditionierung.")
    st.write("Wählen Sie 'Intraop. Pharmakologie' für spezifische Dosierungsanleitungen.")

# 2. PHARMAKOLOGIE (NEU!)
elif mode == "Intraop. Pharmakologie":
    st.title("💊 Intraoperative Medikation & Dosierung")
    st.markdown("Kritische Medikamente für Spender (LNTX) und Empfänger.")

    

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🅰️ Spender (Donor)")
        st.error("WICHTIG: Gabe 3-5 Minuten VOR Gefäß-Abklemmen!")
        
        donor_meds = pd.DataFrame({
            "Medikament": ["Heparin", "Mannitol (Osmofundin)", "Furosemid (Lasix)"],
            "Dosis (Standard)": ["50-100 I.E./kg KG (oder fix 5000 I.E.)", "12.5 g - 25 g (i.v.)", "20 - 40 mg (i.v.)"],
            "Zweck": ["Verhinderung von Mikrothromben im Graft", "Osmotische Diurese / Radikalfänger", "Anregung der Diurese vor Ischämie"]
        })
        st.table(donor_meds)
        st.info("ℹ️ **Tipp:** Kommunikation 'Heparin ist drin' laut aussprechen und Uhrzeit dokumentieren.")

    with col2:
        st.subheader("🅱️ Empfänger (Recipient)")
        st.warning("Gabe VOR Öffnung der Gefäßklemmen (Reperfusion)")
        
        recip_meds = pd.DataFrame({
            "Medikament": ["Methylprednisolon", "Furosemid (Lasix)", "Mannitol", "Heparin (Spülung)"],
            "Dosis (Standard)": ["250 - 500 mg (Bolus)", "100 - 200 mg (hochdosiert)", "20% 125ml", "Gefäßspülung lokal"],
            "Zweck": ["Immunologische Abschirmung (Reperfusion injury)", "Anschubsen der Primärfunktion", "Vermeidung Delayed Graft Function (DGF)", "Lokale Antikoagulation"]
        })
        st.table(recip_meds)

# 3. TECHNIK
elif mode == "Technik: Robotik (Workflows)":
    st.title("Robotische Workflows (Inkl. Medikation)")
    
    tab1, tab2 = st.tabs(["Spender (RDN)", "Empfänger (RAKT)"])
    
    with tab1:
        st.subheader("Robotische Spendernephrektomie")
        st.write("Beachten Sie den **roten Knoten** für die Medikamentengabe im Ablauf.")
        st.graphviz_chart(render_rdn_workflow_pharma())
        
    with tab2:
        st.subheader("Robotische Implantation")
        st.write("Immunsuppressions-Bolus muss vor Reperfusion erfolgen.")
        st.graphviz_chart(render_rakt_workflow_pharma())

# 4. LEITLINIEN
elif mode == "Leitlinien":
    st.title("Post-Op Immunsuppression (Schema)")
    st.markdown("### Standard Triple-Therapie (Tag 0 - 14)")
    
    st.dataframe(pd.DataFrame({
        "Tag": ["Tag 0 (OP)", "Tag 1", "Tag 2", "Tag 3-14"],
        "Tacrolimus (Ziel)": ["-", "8-12 ng/ml", "8-12 ng/ml", "8-10 ng/ml"],
        "MMF (Cellcept)": ["1000mg pre-op", "2x 1000mg", "2x 1000mg", "2x 1000mg"],
        "Steroide (Prednisolon)": ["500mg intraop", "250mg", "125mg", "Tapering bis 20mg"]
    }))

# 5. SUCHE
elif mode == "Live-Suche":
    st.title("PubMed Suche")
    q = st.text_input("Suche", "heparin dosage kidney donor nephrectomy")
    if st.button("Suchen"):
        res = fetch_pubmed_data(q)
        for r in res:
            st.write(f"**{r['Titel']}**")
            st.caption(r['Abstract'])
            st.divider()
