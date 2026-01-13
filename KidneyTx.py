import streamlit as st
from pymed import PubMed
import pandas as pd
import graphviz

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NTX Pro Guide 2026",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA: EVIDENCE DATABASE ---
# Hier hinterlegen wir die harte Evidenz für die App
evidence_db = {
    "heparin_donor": {
        "Aussage": "Systemische Heparinisierung (3000-5000 IE) vor Abklemmung vermindert Thromboserisiko und DGF (Delayed Graft Function).",
        "Quelle": "Cochrane Database Syst Rev. 2021; Pan et al.",
        "Evidenz": "Level 1b (Strong Recommendation)"
    },
    "mannitol": {
        "Aussage": "Mannitol expandiert das Plasmavolumen und fängt freie Radikale. Reduziert Inzidenz von akutem Nierenversagen post-Tx.",
        "Quelle": "EAU Guidelines 2025; Section 3.4.1",
        "Evidenz": "Level 2a"
    },
    "machine_perfusion": {
        "Aussage": "Hypotherme Maschinenperfusion (HMP) ist der statischen Kältekonservierung (SCS) bei Marginalspenden überlegen.",
        "Quelle": "COMPARE Trial (Lancet); Moers et al. (NEJM)",
        "Evidenz": "Level 1a (Goldstandard für ECD-Nieren)"
    },
    "dd_cfdna": {
        "Aussage": "Donor-derived cell-free DNA (dd-cfDNA) erkennt Abstoßungen früher als Kreatinin.",
        "Quelle": "Bloom et al. (JASN); TRIFCTA Study",
        "Evidenz": "Level 2b (Emerging Standard 2026)"
    }
}

# --- HELPER FUNCTIONS ---
def get_evidence_badge(key):
    """Erstellt eine Info-Box mit der Quelle"""
    data = evidence_db.get(key)
    if data:
        st.info(f"📚 **Evidenz:** {data['Aussage']}\n\n*Quelle: {data['Quelle']} ({data['Evidenz']})*")

def fetch_pubmed(query):
    # (Mock-Funktion für Stabilität, im echten Einsatz try/except Block nutzen wie zuvor)
    return [] 

# --- SIDEBAR ---
st.sidebar.title("🏥 NTX Pro 2026")
st.sidebar.caption("Evidence-Based Clinical Support")
module = st.sidebar.radio("Modul wählen:", 
    [
        "1. Empfänger-Evaluation (Pre-Tx)", 
        "2. Leichenspende (Deceased Donor)", 
        "3. Lebendspende & Robotik", 
        "4. Nachsorge & Follow-Up",
        "5. Live-Evidenz Suche"
    ]
)

# --- MAIN CONTENT ---

# --------------------------------------------------------
# 1. EMPFÄNGER EVALUATION (RECIPIENT EXAM)
# --------------------------------------------------------
if module == "1. Empfänger-Evaluation (Pre-Tx)":
    st.title("Präoperative Evaluation (Recipient)")
    st.markdown("Detailliertes Workup nach **KDIGO** und **Eurotransplant** Standards.")

    tab1, tab2, tab3 = st.tabs(["Immunologie", "Kardiovaskulär & Malignom", "Infektiologie"])

    with tab1:
        st.subheader("Immunologisches Risiko-Profiling")
        st.write("Das Matching entscheidet über das Langzeitüberleben.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Labor-Parameter")
            st.checkbox("Blutgruppe (AB0) + Rhesus")
            st.checkbox("HLA-Typisierung (A, B, C, DR, DQ, DP)")
            st.checkbox("Luminex-Assay (Suche nach HLA-Antikörpern)")
            st.checkbox("Virtuelles Crossmatch (verpflichtend vor Listung)")
        
        with col2:
            st.markdown("#### Interpretation")
            st.warning("⚠️ **Vorsicht:** Bei PRA (Panel Reactive Antibodies) > 20% ist ein intensiviertes Protokoll (z.B. Desensibilisierung) notwendig.")
            st.info("💡 **Update 2026:** Epitop-Matching gewinnt an Bedeutung gegenüber reinem Antigen-Matching.")

    with tab2:
        st.subheader("Kardiovaskulär & Onkologie")
        st.markdown("**Ziel:** 'Fit for Surgery' & Ausschluss von Kontraindikationen.")
        
        check_data = {
            "Untersuchung": ["Belastungs-EKG / Stress-Echo", "Koronarangiographie", "Becken-Bein-Angio (CT)", "Tumorscreening"],
            "Indikation": ["Alle Patienten > 50J oder Diabetiker", "Bei patholog. Stress-Test", "Ausschluss AVK der Iliakalgefäße (Anastomosen-Ort!)", "Nach altersentsprechenden Richtlinien"],
            "Gültigkeit": ["12 Monate", "Nach Befund", "Einmalig (ggf. Update)", "Aktuell"]
        }
        st.table(pd.DataFrame(check_data))

    with tab3:
        st.subheader("Infektiologisches Screening")
        st.write("Entscheidend für die Prophylaxe-Strategie (z.B. Valganciclovir).")
        st.markdown("""
        * **CMV (Cytomegalie):** IgG/IgM Status (D+/R- ist High Risk).
        * **EBV (Epstein-Barr):** PTLD-Risiko bei seronegativen Empfängern.
        * **Hepatitis B/C & HIV:** Quantitative PCR bei positivem Suchtest.
        * **Tuberkulose:** Quantiferon-Test (bei pos. Befund: Isoniazid-Prophylaxe).
        """)

# --------------------------------------------------------
# 2. LEICHENSPENDE (DECEASED DONOR)
# --------------------------------------------------------
elif module == "2. Leichenspende (Deceased Donor)":
    st.title("Postmortale Spende (DBD / DCD)")
    st.markdown("Prozesse von der Entnahme bis zur Implantation.")
    
    col_proc, col_evid = st.columns([2, 1])
    
    with col_proc:
        st.subheader("Ablauf & Perfusion")
        st.markdown("""
        1.  **Explantation:** En-bloc Entnahme der Nieren inkl. Aorta/Vena Cava Patch.
        2.  **Perfusion:** Sofortige Spülung mit 4°C kalter Lösung (z.B. HTK-Custodiol oder UW-Lösung).
        3.  **Lagerung:** Entscheidung Statisch vs. Maschine.
        """)
        
        st.markdown("#### Workflow: Back-Table Präparation")
        # Visualisierung Backtable
        st.code("""
        1. Trennung der Nieren (Split)
        2. Entfettung des Hilus (Vorsicht: Ureter-Vaskularisation!)
        3. Ligatur kleiner Seitenäste (Hemo-Clips)
        4. Biopsie (bei marginalen Spendern / "Rescue Allocation")
        """, language="text")

    with col_evid:
        st.subheader("🔬 Evidenz-Check")
        st.write("Warum Maschinenperfusion?")
        get_evidence_badge("machine_perfusion")
        
        st.write("Warum Mannitol beim Empfänger?")
        get_evidence_badge("mannitol")

    st.divider()
    
    st.subheader("Vergleich: Lagerungsmethoden")
    comp_df = pd.DataFrame({
        "Methode": ["Statische Kältelagerung (SCS)", "Hypotherme Maschinenperfusion (HMP)"],
        "Prinzip": ["Eisbox (4°C)", "Pulsatile Durchspülung (Druckgesteuert)"],
        "Vorteil": ["Einfach, Billig, Standard", "Geringere Rate an DGF, Bessere Bewertung der Organqualität (Resistenz)"],
        "Indikation": ["Standard-Spender (SCD)", "Marginale Spender (ECD), DCD, Lange Ischämiezeit"]
    })
    st.table(comp_df)

# --------------------------------------------------------
# 3. LEBENDSPENDE (MIT HEPARIN DETAILS)
# --------------------------------------------------------
elif module == "3. Lebendspende & Robotik":
    st.title("Lebendspende & Intraoperative Pharmakologie")
    
    st.error("⚠️ Kritischer Punkt: Pharmakologisches Management des Spenders")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Protokoll: Spender (Vor Abklemmen)")
        st.markdown("""
        Die Gabe muss **3-5 Minuten vor der Gefäßklemme** erfolgen, um eine systemische Wirkung zu garantieren, bevor der Kreislauf unterbrochen wird.
        
        **Medikation:**
        1.  **Heparin:** 5000 IE (oder 50-100 IE/kg KG) i.v.
        2.  **Mannitol 20%:** 125 ml (25g) i.v.
        3.  **Furosemid:** 20-40 mg i.v.
        """)
    
    with col2:
        st.markdown("### Wissenschaftliche Begründung")
        get_evidence_badge("heparin_donor")
        st.markdown("> **Hinweis:** Protamin zur Antagonisierung wird beim Spender *selten* routinemäßig gegeben, außer bei Blutungskomplikationen (Halbwertszeit Heparin ca. 90 min).")

    st.markdown("---")
    st.subheader("Robotische Entnahme (Technik)")
    # Hier würde das Graphviz Diagramm aus der vorherigen Version stehen
    st.info("Siehe Workflow-Diagramm aus vorheriger Version (V3.0) für chirurgische Schritte.")

# --------------------------------------------------------
# 4. NACHSORGE (FOLLOW-UP)
# --------------------------------------------------------
elif module == "4. Nachsorge & Follow-Up":
    st.title("Langzeit-Betreuung & Komplikationen")
    
    tabs = st.tabs(["Zeitstrahl", "Biomarker 2026", "Biopsie-Indikation"])
    
    with tabs[0]:
        st.subheader("Post-Tx Zeitstrahl")
        timeline_data = {
            "Phase": ["Früh (Woche 0-4)", "Intermediär (Monat 1-6)", "Spät (> 6 Monate)"],
            "Fokus": ["Chirurgische Komplikationen, DGF, Akute Abstoßung (T-Zell)", "Infektionen (CMV/BKV), Dosisfindung Tacrolimus", "Chronische Abstoßung, CVD, Malignome (Haut)"],
            "Untersuchung": ["Sono täglich, Labor täglich", "Sono wöchentl., Spiegelbestimmung", "Alle 3-6 Monate, Hautscreening"]
        }
        st.table(pd.DataFrame(timeline_data))
        
    with tabs[1]:
        st.subheader("Moderne Diagnostik")
        col_new, col_old = st.columns(2)
        with col_new:
            st.success("🚀 Neu: dd-cfDNA")
            st.write("Donor-derived cell-free DNA im Plasma.")
            get_evidence_badge("dd_cfdna")
            st.write("**Vorteil:** Steigt VOR dem Kreatinin an (molekulare Schädigung).")
            
    with col_old:
            st.info("Standard: Kreatinin & Proteinurie") 
            
            st.write("Goldstandard, aber 'Lag-Time' (steigt erst bei ca. 50% Funktionsverlust).")

    with tabs[2]:
        st.subheader("Wann Biopsieren?")
        st.markdown("### Indikations-Biopsie (Goldstandard)")
        st.markdown("""
        * **Kreatinin-Anstieg:** > 15-20% über Baseline ohne prärenale Ursache.
        * **Proteinurie:** Neu aufgetreten > 0.5 - 1g/Tag.
        * **De-Novo DSA:** Nachweis neuer spenderspezifischer Antikörper.
        * **Verdacht auf BKV-Nephropathie:** Bei hoher Viruslast im Plasma (>10.000 Kopien).
        """)

# --------------------------------------------------------
# 5. LIVE SUCHE
# --------------------------------------------------------
elif module == "5. Live-Evidenz Suche":
    st.title("🔎 Suche nach Primärliteratur")
    st.write("Nutzen Sie PubMed für spezifische Fragestellungen.")
    q = st.text_input("Suche", "heparin living donor kidney transplantation systemic guidelines")
    st.button("Suchen (Demo)")
    # Hier würde der fetch_pubmed Code stehen
