import streamlit as st
from pymed import PubMed
import pandas as pd
import graphviz

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NTX Guide",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- EVIDENCE DATABASE ---
evidence_db = {
    "heparin_donor": {
        "Aussage": "Systemische Heparinisierung (3000-5000 IE) vor Abklemmung verhindert Thrombosen.",
        "Quelle": "Cochrane Database Syst Rev. 2021; Pan et al.",
        "Evidenz": "Level 1b"
    },
    "mannitol": {
        "Aussage": "Mannitol expandiert Volumen und fängt freie Radikale.",
        "Quelle": "EAU Guidelines 2025",
        "Evidenz": "Level 2a"
    },
    "rakt_safety": {
        "Aussage": "RAKT reduziert Wundinfektionen bei adipösen Patienten (BMI >30) signifikant.",
        "Quelle": "ERUS-RAKT Working Group; Breda et al.",
        "Evidenz": "Level 2a"
    },
    "stapler_safety": {
        "Aussage": "Vascular Stapler sicherer als Clips für A. renalis.",
        "Quelle": "FDA Warning / Friedman et al.",
        "Evidenz": "Safety Alert"
    },
    "machine_perfusion": {
        "Aussage": "HMP überlegen gegenüber statischer Kälte bei ECD-Spenden.",
        "Quelle": "COMPARE Trial (Lancet)",
        "Evidenz": "Level 1a"
    },
    "dd_cfdna": {
        "Aussage": "Früherkennung von Abstoßung durch dd-cfDNA.",
        "Quelle": "Bloom et al.",
        "Evidenz": "Level 2b"
    }
}

# --- HELPER FUNCTIONS ---
def get_evidence_badge(key):
    data = evidence_db.get(key)
    if data:
        if "Alert" in data['Evidenz']:
            st.error(f"🛑 **Safety:** {data['Aussage']} ({data['Quelle']})")
        else:
            st.info(f"📚 **Evidenz:** {data['Aussage']}\n\n*Ref: {data['Quelle']} ({data['Evidenz']})*")

def fetch_pubmed_data(query):
    try:
        pubmed = PubMed(tool="StreamlitApp", email="mail@example.com")
        results = pubmed.query(query, max_results=3)
        return [{"Titel": r.title, "Abstract": r.abstract, "Date": r.publication_date} for r in results]
    except:
        return []

# --- GRAPHVIZ WORKFLOWS ---

def render_donor_workflow():
    """SPENDER Workflow (RDN)"""
    dot = graphviz.Digraph(comment='RDN')
    dot.attr(rankdir='TB', size='8')
    dot.attr('node', shape='box', style='filled', fillcolor='#e8f5e9') # Green tint
    
    dot.node('A', '1. Lagerung (60°)')
    dot.node('B', '2. Präparation (Hilus)')
    dot.node('C', '3. PHARMA BOLUS\n(Heparin/Mannitol)', fillcolor='#ff8a80', style='bold') # RED
    dot.node('D', '4. ICG Check (Ureter)', fillcolor='#fff9c4') # YELLOW
    dot.node('E', '5. Stapling (Arterie)')
    dot.node('F', '6. Extraktion (Pfannenstiel)')
    
    dot.edge('A', 'B')
    dot.edge('B', 'C', label=' 3-5 min vor Clip')
    dot.edge('C', 'D')
    dot.edge('D', 'E', label=' Safety View')
    dot.edge('E', 'F', label=' Warm Ischemia Start')
    return dot

def render_recipient_workflow():
    """EMPFÄNGER Workflow (RAKT)"""
    dot = graphviz.Digraph(comment='RAKT')
    dot.attr(rankdir='TB', size='8')
    dot.attr('node', shape='box', style='filled', fillcolor='#e3f2fd') # Blue tint

    dot.node('1', '1. Zugang (Pfannenstiel + GelPoint)')
    dot.node('2', '2. Gefäß-Exposure (Iliaca ext.)')
    dot.node('3', '3. Niere Andocken')
    dot.node('4', '4. Regionale Hypothermie\n(Eis-Matsch)', fillcolor='#b3e5fc')
    dot.node('5', '5. Anastomosen (Vene -> Arterie)')
    dot.node('6', '6. REPERFUSIONS-BOLUS\n(Steroid/Lasix)', fillcolor='#ff8a80', style='bold') # RED
    dot.node('7', '7. Freigabe & ICG')
    dot.node('8', '8. Ureter-Implantation')

    dot.edge('1', '2')
    dot.edge('2', '3')
    dot.edge('3', '4', label=' Time critical')
    dot.edge('4', '5')
    dot.edge('5', '6', label=' Vor Klemmenöffnung')
    dot.edge('6', '7')
    dot.edge('7', '8')
    return dot

# --- NAVIGATION ---
st.sidebar.title("NTX Master 2026")
nav = st.sidebar.radio("Navigation", [
    "Dashboard (News)",
    "1. Preparation (Evaluation)",
    "2. Deceased Donor (Leiche)",
    "3. Living Donor (RDN)",
    "4. Recipient Surgery (RAKT)",
    "5. Follow-Up & Guidelines",
    "6. Search (PubMed)"
])

# --- CONTENT ---

# === DASHBOARD ===
if nav == "Dashboard (News)":
    st.title("Nierentransplantation: Update")
    st.markdown("### Was gibt es neues?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("🤖 **Robotik (RAKT)**")
        st.write("Standard für BMI > 30. Reduziert Wundinfektionen von 15% auf <4%.")
    with col2:
        st.info("❄️ **Maschinenperfusion**")
        st.write("HMP ist neuer Standard für ECD-Nieren (Leichenspende).")
    with col3:
        st.warning("🧬 **Biomarker**")
        st.write("dd-cfDNA ersetzt zunehmend Biopsien im Frühstadium.")

# === 1. PREPARATION ===
if nav == "1. Preparation (Evaluation)":
    st.title("Patientenvorbereitung & Evaluation")
    tab1, tab2 = st.tabs(["Empfänger Workup", "Immunologie"])
    
    with tab1:
        st.subheader("Kardiovaskulär & Infektiologie")
        st.table(pd.DataFrame({
            "Untersuchung": ["Stress-Echo", "CT-Becken", "Zahnstatus"],
            "Intervall": ["12 Monate", "Einmalig", "Jährlich"],
            "Rationale": ["Ischämie-Risiko", "Anastomosen-Planung", "Infekt-Fokus"]
        }))
    with tab2:
        st.subheader("Immunologische Risikostratifizierung")
        st.write("• **HLA-A/B/C/DR/DQ/DP:** High-Res Typisierung.")
        st.write("• **Virtuelles Crossmatch:** Ersetzt physisches XM bei Lebendspende.")

# === 2. DECEASED DONOR ===
if nav == "2. Deceased Donor (Leiche)":
    st.title("Postmortale Spende (Deceased Donor)")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Konservierung")
        st.write("Vergleich: Statische Kälte (SCS) vs. Hypotherme Maschinenperfusion (HMP)")
        st.table(pd.DataFrame({
            "Methode": ["Eisbox (SCS)", "Maschine (HMP)"],
            "DGF-Rate": ["Hoch (ca. 30%)", "Reduziert (ca. 20%)"],
            "Evidenz": ["Standard", "Empfohlen für ECD"]
        }))
    with col2:
        st.subheader("Evidenz")
        get_evidence_badge("machine_perfusion")

# === 3. LIVING DONOR (RDN) ===
if nav == "3. Living Donor (RDN)":
    st.title("Robotische Spendernephrektomie (RDN)")
    
    t1, t2, t3 = st.tabs(["Workflow (Diagramm)", "Schritte & Technik", "Pharmakologie"])
    
    with t1:
        st.graphviz_chart(render_donor_workflow())
        st.caption("Fokus: Sicherheit & Minimale Ischämie")
    
    with t2:
        st.subheader("Detaillierte Schritte")
        st.markdown("**1. Lagerung:** 60° Seitenlage.")
        st.markdown("**2. ICG-Check:** Vor Ureter-Schnitt Perfusion prüfen.")
        get_evidence_badge("icg_ureter")
        st.markdown("**3. Stapling:** Vascular Stapler verwenden.")
        get_evidence_badge("stapler_safety")
        
    with t3:
        st.subheader("Spender-Medikation (Intra-Op)")
        st.error("Gabe 3-5 min vor Abklemmen!")
        st.table(pd.DataFrame({
            "Medikament": ["Heparin", "Mannitol", "Furosemid"],
            "Dosis": ["5000 IE", "25g (125ml)", "20-40mg"],
            "Effekt": ["Thromboseprophylaxe", "Radikalfänger", "Diurese"]
        }))
        get_evidence_badge("heparin_donor")

# === 4. RECIPIENT SURGERY (RAKT) ===
if nav == "4. Recipient Surgery (RAKT)":
    st.title("Robotische Implantation (RAKT)")
    st.info("RESTORED FEATURE: Detailed Recipient Workflow & Comparison")

    t1, t2, t3 = st.tabs(["Workflow (Diagramm)", "Vergleich (Offen vs. RAKT)", "Pharmakologie"])
    
    with t1:
        st.subheader("Implantations-Workflow")
        st.write("Beachten Sie die **Regionale Hypothermie** und den **Reperfusions-Bolus**.")
        st.graphviz_chart(render_recipient_workflow())
    
    with t2:
        st.subheader("Warum Robotisch? (Vergleichsdaten)")
        comp_df = pd.DataFrame({
            "Parameter": ["Inzisionslänge", "Wundinfektion (SSI)", "Lymphozelen", "Warm-Ischämie"],
            "Offene NTX": ["15-20 cm", "10-15% (bei BMI>30)", "Häufig", "30-40 min"],
            "Robotische NTX": ["6 cm", "< 4%", "Selten", "45-55 min"]
        })
        st.table(comp_df)
        get_evidence_badge("rakt_safety")
        
    with t3:
        st.subheader("Empfänger-Medikation (Vor Reperfusion)")
        st.warning("Timing: Bevor die Gefäßklemmen geöffnet werden.")
        st.table(pd.DataFrame({
            "Medikament": ["Methylprednisolon", "Furosemid"],
            "Dosis": ["250-500 mg", "200 mg"],
            "Ziel": ["Schutz vor Reperfusionsschaden", "Anregung Primärfunktion"]
        }))

# === 5. FOLLOW UP ===
if nav == "5. Follow-Up & Guidelines":
    st.title("Nachsorge & Guidelines")
    st.subheader("Diagnostik 2026")
    st.write("Neben Kreatinin gewinnt **dd-cfDNA** an Bedeutung.")
    get_evidence_badge("dd_cfdna")
    
    st.subheader("Immunsuppression (Standard)")
    st.code("Tacrolimus (Ziel 8-10) + MMF (2g) + Steroide (Tapering)")

# === 6. SEARCH ===
if nav == "6. Search (PubMed)":
    st.title("Live Search")
    q = st.text_input("PubMed Query", "kidney transplantation guidelines 2026")
    if st.button("Search"):
        res = fetch_pubmed_data(q)
        for r in res:
            st.write(f"**{r['Titel']}** ({r['Date']})")
            st.caption(r['Abstract'])
            st.markdown("---")
