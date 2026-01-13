import streamlit as st
from pymed import PubMed # Hinweis: Für Deployment 'pymed' in requirements.txt
import pandas as pd
import graphviz

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NTX Guideline App",
    page_icon="😷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- EVIDENCE DATABASE (Zentrales Gehirn der App) ---
# Hier werden Aussagen mit Studien verknüpft.
evidence_db = {
    # -- ALLGEMEIN / PHARMA --
    "heparin_donor": {
        "Aussage": "Systemische Heparinisierung (3000-5000 IE) vor Arterien-Abklemmung.",
        "Quelle": "Cochrane Database Syst Rev. 2021; Pan et al.",
        "Evidenz": "Level 1b (Strong Recommendation)"
    },
    "mannitol": {
        "Aussage": "Mannitol als Radikalfänger und zur Diurese-Förderung.",
        "Quelle": "EAU Guidelines 2025; Section 3.4",
        "Evidenz": "Level 2a"
    },
    # -- RDN (ROBOTIC DONOR) --
    "rdn_safety": {
        "Aussage": "RDN ist der offenen und laparoskopischen Entnahme gleichwertig bzgl. Sicherheit, bei besserer Erholung.",
        "Quelle": "Giulianotti et al. (Arch Surg); EAU Guidelines",
        "Evidenz": "Level 1a (Meta-Analysis)"
    },
    "stapler_safety": {
        "Aussage": "Verwendung von Gefäß-Stapler für A. renalis (statt Polymer-Clips) zur Vermeidung von Clip-Dysfunktion.",
        "Quelle": "FDA Safety Communication (Hem-o-lok); Friedman et al.",
        "Evidenz": "Critical Safety Warning"
    },
    "icg_ureter": {
        "Aussage": "ICG-Fluoreszenz verhindert distale Ureter-Nekrosen durch Visualisierung der Perfusion.",
        "Quelle": "Breda et al. (Eur Urol Focus 2024)",
        "Evidenz": "Level 2b"
    },
    "extraction_site": {
        "Aussage": "Pfannenstiel-Inzision hat signifikant niedrigere Hernienrate als mediane Laparotomie.",
        "Quelle": "Meta-Analyse: Orcutt et al.",
        "Evidenz": "Level 1a"
    },
    # -- DECEASED / NACHSORGE --
    "machine_perfusion": {
        "Aussage": "Hypotherme Maschinenperfusion (HMP) > Statische Kälte (SCS) bei Marginalspendern.",
        "Quelle": "COMPARE Trial (Lancet)",
        "Evidenz": "Level 1a"
    },
    "dd_cfdna": {
        "Aussage": "dd-cfDNA als Biomarker für frühe Abstoßung.",
        "Quelle": "Bloom et al. (JASN)",
        "Evidenz": "Level 2b"
    }
}

# --- HELPER FUNCTIONS ---
def get_evidence_badge(key):
    """Zeigt eine formatierte Evidenz-Box an"""
    data = evidence_db.get(key)
    if data:
        if "Warning" in data['Evidenz']:
            st.error(f"🛑 **Sicherheits-Warnung:** {data['Aussage']}\n\n*Ref: {data['Quelle']}*")
        else:
            st.info(f"📚 **Evidenz:** {data['Aussage']}\n\n*Ref: {data['Quelle']} ({data['Evidenz']})*")

def render_rdn_detailed_workflow():
    """Detaillierter RDN Workflow mit Safety Checks"""
    dot = graphviz.Digraph(comment='RDN Detailed')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled', fillcolor='#f0f2f6', fontname='Sans-Serif')

    # Phasen
    dot.node('Start', '1. Lagerung & Zugang\n(Seitenlage 60°, 4 Arme)')
    
    dot.node('Colon', '2. Mobilisation\n(Toldt\'sche Linie, Kolon nach medial)')
    dot.node('Ureter', '3. Ureter Identifikation\n(Cave: A. gonadalis schonen!)')
    dot.node('Hilus', '4. Hilus Präparation\n(Arterie/Vene freilegen)')
    
    # Critical Steps
    dot.node('Pharma', '5. PHARMA CHECK\n(Heparin/Mannitol)', fillcolor='#ffcdd2', style='filled,bold')
    dot.node('ICG', '6. ICG Perfusion Check\n(Ureter Durchblutung?)', fillcolor='#fff9c4')
    
    dot.node('Stapler', '7. Gefäß-Durchtrennung\n(Vascular Stapler - KEINE CLIPS auf A.!)', fillcolor='#ff8a80', style='filled,bold')
    dot.node('Extract', '8. Extraktion\n(Pfannenstiel/Endobag)')

    # Edges
    dot.edge('Start', 'Colon')
    dot.edge('Colon', 'Ureter', label=' Gonadal Vein Sparing')
    dot.edge('Ureter', 'Hilus')
    dot.edge('Hilus', 'Pharma', label=' 3 min vor Clip')
    dot.edge('Pharma', 'ICG')
    dot.edge('ICG', 'Stapler', label=' Safety View')
    dot.edge('Stapler', 'Extract', label=' WARM ISCHEMIA START')

    return dot

# --- SIDEBAR ---
st.sidebar.title("NTX Guide 2026")
st.sidebar.warning("Medical Professional Use Only")
module = st.sidebar.radio("Navigation:", 
    [
        "1. Empfänger-Evaluation", 
        "2. Leichenspende (Deceased)", 
        "3. Lebendspende & Robotik (RDN)", 
        "4. Nachsorge & Follow-Up",
        "5. Live-Suche (PubMed)"
    ]
)

# --- MAIN CONTENT ---

# ========================================================
# 1. EMPFÄNGER EVALUATION
# ========================================================
if module == "1. Empfänger-Evaluation":
    st.title("Präoperative Evaluation (Recipient)")
    st.markdown("Workup nach **KDIGO** und **Eurotransplant** Standards.")

    tab1, tab2, tab3 = st.tabs(["Immunologie", "Kardiovaskulär", "Infektiologie"])

    with tab1:
        st.subheader("Immunologisches Risiko")
        st.write("Das Matching entscheidet über das Langzeitüberleben.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("* **HLA-Typisierung:** A, B, C, DR, DQ, DP")
            st.markdown("* **Luminex-Assay:** Suche nach HLA-Antikörpern (DSA)")
            st.markdown("* **Virtuelles Crossmatch:** Verpflichtend vor Listung")
        with col2:
            st.warning("Bei PRA > 20% intensiviertes Protokoll notwendig.")

    with tab2:
        st.subheader("Kardiovaskulärer 'Stress-Test'")
        check_data = {
            "Check": ["Belastungs-EKG / Echo", "Koronarangiographie", "Becken-Bein-Angio"],
            "Indikation": ["Alle Pat. > 50J / Diabetiker", "Patholog. Stress-Test", "Ausschluss pAVK (Anastomose)"]
        }
        st.table(pd.DataFrame(check_data))

    with tab3:
        st.write("CMV, EBV, HIV, Hep B/C Status zwingend erforderlich.")

# ========================================================
# 2. LEICHENSPENDE
# ========================================================
elif module == "2. Leichenspende (Deceased)":
    st.title("Postmortale Spende (DBD/DCD)")
    
    col_proc, col_evid = st.columns([2, 1])
    with col_proc:
        st.subheader("Ablauf & Perfusion")
        st.markdown("1. **Explantation:** En-bloc Entnahme.")
        st.markdown("2. **Perfusion:** Sofortige Spülung (HTK/UW).")
        st.markdown("3. **Back-Table:** Trennung, Entfettung, Ligatur.")
    
    with col_evid:
        st.subheader("Evidenz")
        get_evidence_badge("machine_perfusion")
        get_evidence_badge("mannitol")

# ========================================================
# 3. LEBENDSPENDE & ROBOTIK (EXPANDED!)
# ========================================================
elif module == "3. Lebendspende & Robotik (RDN)":
    st.title("Robotische Spendernephrektomie (RDN)")
    st.markdown("Evidenzbasierter Standard für Lebendspender (Living Donor Nephrectomy).")

    # TABS FÜR STRUKTUR
    tab_workflow, tab_steps, tab_pharma, tab_studies = st.tabs([
        "Workflow Diagramm", 
        "Schritt-für-Schritt (Technik)", 
        "Pharmakologie",
        "Studienlage"
    ])

    # --- TAB 1: VISUELLER WORKFLOW ---
    with tab_workflow:
        st.subheader("Operations-Ablauf (Visualisiert)")
        st.graphviz_chart(render_rdn_detailed_workflow())
        st.caption("Diagramm basierend auf EAU Guidelines Robotic Surgery.")

    # --- TAB 2: SCHRITT FÜR SCHRITT DETAILS ---
    with tab_steps:
        st.subheader("Detaillierte OP-Schritte & 'Surgical Pearls'")
        
        with st.expander("1. Lagerung & Trokare", expanded=True):
            st.write("**Lagerung:** Strikte Seitenlage (60°), Tisch knicken (Jack-knife).")
            st.write("**Trokare (DaVinci Xi):** 4 Arme in einer Linie ('Line of sight' zur Niere).")
            st.write("*Tipp:* 8mm Trokare reichen, 12mm nur für Stapler/Clip-Applikator.")

        with st.expander("2. Präparation & Gefäßdarstellung"):
            st.write("**Vorgehen:** Mobilisation des Colon descendens/ascendens an der Toldt'schen Linie.")
            st.warning("**Cave:** Gonadalvene (links) schonen! Dient oft als anatomische Landmarke.")
            st.write("**Hilus:** Skelettierung von Arterie und Vene. Lymphgefäße immer clippen (Lymphozelen-Prophylaxe).")

        with st.expander("3. Ureter & ICG (Wichtig!)"):
            st.write("Der Ureter wird mit dem peri-ureteralen Gewebe ('Golden Triangle') präpariert, um die Vaskularisation zu erhalten.")
            get_evidence_badge("icg_ureter")

        with st.expander("4. Gefäßdurchtrennung (Safety First)"):
            st.error("CRITICAL STEP: Niemals nur Polymer-Clips (Hem-o-lok) auf die Hauptarterie!")
            st.write("**Standard:** Vascular Stapler oder Hem-o-lok + Titan-Clip + Nahtsicherung.")
            get_evidence_badge("stapler_safety")

        with st.expander("5. Extraktion"):
            st.write("Bergebeutel (Endobag) zwingend.")
            st.write("Schnitt: Pfannenstiel (Suprapubisch) bevorzugt.")
            get_evidence_badge("extraction_site")

    # --- TAB 3: PHARMA ---
    with tab_pharma:
        st.subheader("Intraoperative Pharmakologie (Spender)")
        st.markdown("Das Timing ist entscheidend für die Organqualität.")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### Protokoll")
            st.write("⏰ **Zeitpunkt:** 3-5 Min vor Gefäß-Stapler.")
            st.table(pd.DataFrame({
                "Medikament": ["Heparin", "Mannitol", "Lasix"],
                "Dosis": ["3000-5000 IE", "25 g (125ml 20%)", "20-40 mg"]
            }))
        with col_p2:
            st.markdown("#### Evidenz")
            get_evidence_badge("heparin_donor")

    # --- TAB 4: STUDIENLAGE ---
    with tab_studies:
        st.subheader("Wissenschaftliche Basis")
        st.markdown("Warum Robotisch? Warum Stapler?")
        
        st.markdown("##### 1. Vergleich: Robotisch vs. Laparoskopisch")
        get_evidence_badge("rdn_safety")
        
        st.markdown("##### 2. Sicherheit der Gefäßversorgung")
        get_evidence_badge("stapler_safety")

# ========================================================
# 4. NACHSORGE (FIXED)
# ========================================================
elif module == "4. Nachsorge & Follow-Up":
    st.title("Langzeit-Betreuung")
    
    tabs = st.tabs(["Zeitstrahl", "Biomarker 2026", "Biopsie"])
    
    with tabs[0]:
        st.subheader("Timeline")
        st.info("Woche 0-4: Fokus auf Chirurgische Komplikationen & DGF.")
        st.info("Monat 1-6: Fokus auf Infektionen (CMV/BKV) & Abstoßung.")
        
    with tabs[1]:
        st.subheader("Diagnostik")
        # FIX: st.secondary wurde entfernt
        st.subheader("Standard: Kreatinin & Proteinurie")
        st.write("Goldstandard, aber reagiert verzögert.")
        
        st.success("Neu: dd-cfDNA (Donor-derived cell-free DNA)")
        get_evidence_badge("dd_cfdna")

    with tabs[2]:
        st.write("**Biopsie-Indikation:** Krea-Anstieg >20%, Proteinurie >1g, de-novo DSA.")

# ========================================================
# 5. LIVE SUCHE
# ========================================================
elif module == "5. Live-Suche (PubMed)":
    st.title("PubMed Suche")
    q = st.text_input("Suche", "robotic donor nephrectomy safety 2026")
    st.button("Suchen")
