import streamlit as st
from pymed import PubMed
import pandas as pd
import graphviz
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NTX Master Guide 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LANGUAGE SETTINGS ---
def t(de, en):
    if st.session_state.get('lang', 'Deutsch') == 'Deutsch':
        return de
    return en

# --- PLOTTING FUNCTION (THE "ALWAYS AVAILABLE" GRAPHIC) ---
def render_biomarker_chart(lang):
    """
    Generates the Red vs Blue kinetics chart programmatically.
    This ensures the graphic is always available without external downloads.
    """
    # 1. Create Data
    # X-Axis: Weeks relative to clinical rejection (0)
    weeks = np.arange(-6, 5, 1) 
    
    # Y-Axis Data (Mock values for visualization)
    # dd-cfDNA (Red): Spikes early (Week -3 to -1)
    dna_levels = [0.2, 0.25, 0.4, 1.2, 2.8, 1.9, 1.2, 0.8, 0.5, 0.3, 0.2]
    # Creatinine (Blue): Spikes late (Week 0 to +1)
    krea_levels = [1.0, 1.0, 1.0, 1.0, 1.05, 1.1, 1.5, 2.2, 2.5, 2.0, 1.6]

    # 2. Plotting
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Plot Lines
    ax.plot(weeks, dna_levels, color='#d32f2f', label='dd-cfDNA (Injury)', linewidth=3, marker='o') # RED
    ax.plot(weeks, krea_levels, color='#1976d2', label='Creatinine (Function)', linewidth=3, linestyle='--', marker='x') # BLUE
    
    # Annotations
    ax.axvline(x=0, color='gray', linestyle=':', alpha=0.6)
    label_rejection = "Clinical Rejection (Biopsy)" if lang != "Deutsch" else "Klinische Abstoßung (Biopsie)"
    ax.text(0.1, 2.8, label_rejection, fontsize=9, color='gray')

    # Styling
    ax.set_xlabel("Weeks relative to Diagnosis" if lang != "Deutsch" else "Wochen relativ zur Diagnose")
    ax.set_ylabel("Relative Level (Normalized)")
    ax.set_title("Kinetics: Molecular Injury vs. Functional Loss")
    ax.legend()
    ax.grid(True, alpha=0.2)
    
    # 3. Return Figure
    return fig

# --- EVIDENCE DATABASE ---
evidence_db = {
    "heparin_donor": {
        "DE": {"Aussage": "Systemische Heparinisierung (3000-5000 IE) vor Abklemmung verhindert Thrombosen.", "Evidenz": "Level 1b"},
        "EN": {"Aussage": "Systemic heparinization (3000-5000 IU) prior to clamping prevents thrombosis.", "Evidenz": "Level 1b"},
        "Quelle": "Cochrane Database Syst Rev. 2021; Pan et al."
    },
    "mannitol": {
        "DE": {"Aussage": "Mannitol expandiert Volumen und fängt freie Radikale.", "Evidenz": "Level 2a"},
        "EN": {"Aussage": "Mannitol expands volume and acts as a free radical scavenger.", "Evidenz": "Level 2a"},
        "Quelle": "EAU Guidelines 2025"
    },
    "rakt_safety": {
        "DE": {"Aussage": "RAKT reduziert Wundinfektionen bei adipösen Patienten (BMI >30) signifikant.", "Evidenz": "Level 2a"},
        "EN": {"Aussage": "RAKT significantly reduces surgical site infections in obese patients (BMI >30).", "Evidenz": "Level 2a"},
        "Quelle": "ERUS-RAKT Working Group; Breda et al."
    },
    "stapler_safety": {
        "DE": {"Aussage": "Vascular Stapler sicherer als Clips für A. renalis.", "Evidenz": "Safety Alert"},
        "EN": {"Aussage": "Vascular staplers are safer than clips for the renal artery.", "Evidenz": "Safety Alert"},
        "Quelle": "FDA Warning / Friedman et al."
    },
    "machine_perfusion": {
        "DE": {"Aussage": "HMP überlegen gegenüber statischer Kälte bei ECD-Spenden.", "Evidenz": "Level 1a"},
        "EN": {"Aussage": "HMP is superior to static cold storage for ECD donations.", "Evidenz": "Level 1a"},
        "Quelle": "COMPARE Trial (Lancet)"
    },
    "dd_cfdna": {
        "DE": {"Aussage": "Früherkennung von Abstoßung durch dd-cfDNA.", "Evidenz": "Level 2b"},
        "EN": {"Aussage": "Early detection of rejection via dd-cfDNA.", "Evidenz": "Level 2b"},
        "Quelle": "Bloom et al."
    },
    "cardio_workup": {
        "DE": {"Aussage": "Nicht-invasive Belastungstests alle 1-3 Jahre für asymptomatische Kandidaten auf Warteliste.", "Evidenz": "KDIGO 2020 / AHA"},
        "EN": {"Aussage": "Non-invasive stress testing every 1-3 years for asymptomatic candidates on waitlist.", "Evidenz": "KDIGO 2020 / AHA"},
        "Quelle": "Lentine et al. (Circulation 2012); KDIGO"
    },
    "dd_cfdna_kinetics": {
        "DE": {"Aussage": "dd-cfDNA steigt 1-3 Monate VOR dem Kreatinin an (molekulare Schädigung).", "Evidenz": "Level 2a"},
        "EN": {"Aussage": "dd-cfDNA rises 1-3 months BEFORE Creatinine (molecular injury).", "Evidenz": "Level 2a"},
        "Quelle": "Bloom et al. (JASN)"
    }
}

# --- HELPER FUNCTIONS ---
def get_evidence_badge(key):
    lang_key = st.session_state.get('lang', 'Deutsch')
    lang_code = "DE" if lang_key == "Deutsch" else "EN"
    
    data = evidence_db.get(key)
    if data:
        content = data[lang_code]
        if "Alert" in content['Evidenz']:
            st.error(f"🛑 **Safety:** {content['Aussage']} ({data['Quelle']})")
        else:
            st.info(f"📚 **Evidenz/Evidence:** {content['Aussage']}\n\n*Ref: {data['Quelle']} ({content['Evidenz']})*")

def fetch_pubmed_data(query):
    try:
        pubmed = PubMed(tool="StreamlitApp", email="mail@example.com")
        results = pubmed.query(query, max_results=3)
        return [{"Titel": r.title, "Abstract": r.abstract, "Date": r.publication_date} for r in results]
    except:
        return []

# --- GRAPHVIZ WORKFLOWS ---
def render_donor_workflow(lang):
    """SPENDER Workflow (RDN)"""
    is_de = lang == "Deutsch"
    dot = graphviz.Digraph(comment='RDN')
    dot.attr(rankdir='TB', size='8')
    dot.attr('node', shape='box', style='filled', fillcolor='#e8f5e9')
    
    dot.node('A', '1. Lagerung (60°)' if is_de else '1. Positioning (60°)')
    dot.node('B', '2. Präparation (Hilus)' if is_de else '2. Dissection (Hilus)')
    dot.node('C', '3. PHARMA BOLUS\n(Heparin/Mannitol)', fillcolor='#ff8a80', style='bold')
    dot.node('D', '4. ICG Check (Ureter)', fillcolor='#fff9c4')
    dot.node('E', '5. Stapling (Arterie)' if is_de else '5. Stapling (Artery)')
    dot.node('F', '6. Extraktion (Pfannenstiel)' if is_de else '6. Extraction (Pfannenstiel)')
    
    dot.edge('A', 'B')
    dot.edge('B', 'C', label=' 3-5 min vor/pre Clip')
    dot.edge('C', 'D')
    dot.edge('D', 'E', label=' Safety View')
    dot.edge('E', 'F', label=' Warm Ischemia Start')
    return dot

def render_recipient_workflow(lang):
    """EMPFÄNGER Workflow (RAKT)"""
    is_de = lang == "Deutsch"
    dot = graphviz.Digraph(comment='RAKT')
    dot.attr(rankdir='TB', size='8')
    dot.attr('node', shape='box', style='filled', fillcolor='#e3f2fd')

    dot.node('1', '1. Zugang' if is_de else '1. Access (Pfannenstiel)')
    dot.node('2', '2. Gefäß-Exposure' if is_de else '2. Vessel Exposure')
    dot.node('3', '3. Niere Andocken' if is_de else '3. Docking Kidney')
    dot.node('4', '4. Regionale Hypothermie' if is_de else '4. Regional Hypothermia', fillcolor='#b3e5fc')
    dot.node('5', '5. Anastomosen' if is_de else '5. Anastomosis')
    dot.node('6', '6. REPERFUSIONS-BOLUS', fillcolor='#ff8a80', style='bold')
    dot.node('7', '7. Freigabe & ICG' if is_de else '7. Unclamp & ICG')
    dot.node('8', '8. Ureter-Implantation' if is_de else '8. Ureter Reimplantation')

    dot.edge('1', '2')
    dot.edge('2', '3')
    dot.edge('3', '4', label=' Time critical')
    dot.edge('4', '5')
    dot.edge('5', '6', label=' Pre-Unclamp')
    dot.edge('6', '7')
    dot.edge('7', '8')
    return dot

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("NTX Master 2026")
st.session_state['lang'] = st.sidebar.selectbox("Language / Sprache", ["Deutsch", "English"])
current_lang = st.session_state['lang']

nav_options = {
    "Dashboard": "Dashboard (News)",
    "Prep": "1. Preparation (Evaluation)",
    "Deceased": "2. Deceased Donor" if current_lang == "English" else "2. Leichenspende",
    "Living": "3. Living Donor (RDN)" if current_lang == "English" else "3. Lebendspende (RDN)",
    "Recipient": "4. Recipient Surgery (RAKT)" if current_lang == "English" else "4. Empfänger (RAKT)",
    "FollowUp": "5. Follow-Up & Guidelines",
    "Search": "6. Search (PubMed)"
}
nav_selection = st.sidebar.radio("Navigation", list(nav_options.values()))

# --- CONTENT ---

# === DASHBOARD ===
if nav_selection == nav_options["Dashboard"]:
    st.title(t("Nierentransplantation: Update", "Kidney Transplantation: Update"))
    st.markdown(t("### Was gibt es neues?", "### What's New?"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("🤖 **Robotik (RAKT)**")
        st.write(t("Standard für BMI > 30. Reduziert Wundinfektionen.", "Standard for BMI > 30. Reduces SSI."))
    with col2:
        st.info("❄️ **Maschinenperfusion**")
        st.write(t("HMP ist neuer Standard für ECD-Nieren.", "HMP is the new standard for ECD kidneys."))
    with col3:
        st.warning("🧬 **Biomarker**")
        st.write(t("dd-cfDNA ersetzt Biopsien.", "dd-cfDNA replaces biopsies."))

# === 1. PREPARATION (EXPANDED) ===
elif nav_selection == nav_options["Prep"]:
    st.title(t("Patientenvorbereitung & Maintenance", "Patient Preparation & Maintenance"))
    
    tab1, tab2, tab3 = st.tabs([
        t("Workup Matrix (Tabelle)", "Workup Matrix (Table)"), 
        t("Kardiovaskulärer Fokus", "Cardiovascular Focus"),
        t("Immunologie", "Immunology")
    ])
    
    with tab1:
        st.subheader(t("Wartelisten-Maintenance: Was verfällt wann?", "Waitlist Maintenance: What expires when?"))
        st.info(t(
            "Patienten auf der Warteliste müssen 'transplantabel' bleiben.",
            "Patients on the waitlist must remain 'transplantable'."
        ))
        
        # General Workup Data
        if current_lang == "Deutsch":
            workup_data = {
                "Bereich": ["Labor/Virologie", "Kardiovaskulär", "Bildgebung"],
                "Untersuchung": ["HIV, HCV, HBV", "Stress-Test", "Röntgen Thorax"],
                "Gültigkeit": ["3 Monate", "12 Monate", "12 Monate"],
                "Kommentar": ["High-Urgency relevant", "Diabetiker!", "Infektfokus"]
            }
        else:
            workup_data = {
                "Category": ["Virology", "Cardio", "Imaging"],
                "Exam": ["HIV, HCV, HBV", "Stress Test", "CXR"],
                "Validity": ["3 Months", "12 Months", "12 Months"],
                "Comment": ["High-Urgency", "Diabetics!", "Infection"]
            }
        st.dataframe(pd.DataFrame(workup_data), use_container_width=True)

        # --- WARNECKE CRITERIA SECTION (NEW) ---
        st.markdown("---")
        with st.expander(t("⚠️ WARNECKE-KRITERIEN (Onkologische Wartezeiten)", "⚠️ WARNECKE CRITERIA (Oncological Wait Times)"), expanded=False):
            st.markdown(t(
                "Mindestwartezeit nach kurativer Therapie vor Listung (Rezidivfreiheit).",
                "Minimum wait time after curative therapy before listing (recurrence free)."
            ))
            
            if current_lang == "Deutsch":
                warnecke_data = {
                    "Tumor Entität": ["Basaliom (Haut)", "Nierenzellkarzinom (T1a)", "Blasenkarzinom (Ta/T1)", "Colon-Ca (Duke A/B)", "Mamma-Ca (Stadium I)", "Melanom (< 1mm)", "Melanom (> 1mm)", "Lungen-Ca (NSCLC)"],
                    "Wartezeit": ["0 Jahre", "0 Jahre", "0 Jahre", "2-5 Jahre", "2 Jahre", "2 Jahre", "5 Jahre", "2-5 Jahre"],
                    "Risiko": ["Niedrig", "Niedrig", "Niedrig", "Mittel", "Mittel", "Mittel", "Hoch", "Hoch"]
                }
            else:
                warnecke_data = {
                    "Tumor Entity": ["Basal Cell (Skin)", "RCC (T1a)", "Bladder (Ta/T1)", "Colon (Duke A/B)", "Breast (Stage I)", "Melanoma (< 1mm)", "Melanoma (> 1mm)", "Lung (NSCLC)"],
                    "Wait Time": ["0 Years", "0 Years", "0 Years", "2-5 Years", "2 Years", "2 Years", "5 Years", "2-5 Years"],
                    "Risk": ["Low", "Low", "Low", "Medium", "Medium", "Medium", "High", "High"]
                }
            st.table(pd.DataFrame(warnecke_data))
            st.caption("Ref: Warnecke et al. / Kasiske Guidelines")

    with tab2:
        st.subheader(t("Kardiovaskuläres Risiko-Management", "Cardiovascular Risk Management"))
        get_evidence_badge("cardio_workup")
        
        st.markdown(t("#### Algorithmus: Wann Herzkatheter (Coro)?", "#### Algorithm: When Angiography?"))
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.error(t("**Indikation zur Angio:**", "**Indication for Angio:**"))
            st.write("- Pathologischer Stress-Test")
            st.write("- Bekannte KHK / Stents")
            st.write("- Diabetes + >50 Jahre + Raucher")
        with col_c2:
            st.success(t("**Keine Angio nötig wenn:**", "**No Angio needed if:**"))
            st.write("- Belastbarkeit > 100 Watt")
            st.write("- Stress-Echo unauffällig")

    with tab3:
        st.subheader("Immunologie")
        st.write("• **HLA** High-Res")
        st.write("• **Virtuelles Crossmatch**")

# === 2. DECEASED DONOR ===
elif nav_selection == nav_options["Deceased"]:
    st.title(t("Postmortale Spende (DBD / DCD)", "Deceased Donor (DBD / DCD)"))
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Ablauf")
        st.write("1. Explantation (En-Bloc)")
        st.write("2. Perfusion (HTK)")
        st.markdown("")
        st.code("Back-Table: Split, Entfettung, Ligatur, Biopsie", language="text")
        st.markdown("")
    with col2:
        st.subheader("Evidenz")
        get_evidence_badge("machine_perfusion")
        st.markdown("")

# === 3. LIVING DONOR (RDN) ===
elif nav_selection == nav_options["Living"]:
    st.title("Robotische Spendernephrektomie (RDN)")
    t1, t2, t3 = st.tabs(["Workflow", "Technik", "Pharma"])
    
    with t1:
        st.graphviz_chart(render_donor_workflow(current_lang))
    with t2:
        st.subheader("Schritte")
        st.write("1. Lagerung 60°")
        st.markdown("")
        st.write("2. ICG Check")
        get_evidence_badge("icg_ureter")
        st.write("3. Stapling")
        get_evidence_badge("stapler_safety")
    with t3:
        st.error("Heparin 3-5 min vor Clip!")
        st.table(pd.DataFrame({"Drug": ["Heparin", "Mannitol"], "Dose": ["5000 IE", "25g"]}))

# === 4. RECIPIENT SURGERY (RAKT) ===
elif nav_selection == nav_options["Recipient"]:
    st.title("Robotische Implantation (RAKT)")
    t1, t2 = st.tabs(["Workflow", "Vergleich"])
    with t1:
        st.graphviz_chart(render_recipient_workflow(current_lang))
    with t2:
        st.markdown("")
        get_evidence_badge("rakt_safety")

# === 5. FOLLOW UP (UPDATED WITH GRAPHIC) ===
elif nav_selection == nav_options["FollowUp"]:
    st.title(t("Nachsorge & Guidelines", "Follow-Up & Guidelines"))
    
    f_tab1, f_tab2 = st.tabs([t("Diagnostik: Kreatinin vs. dd-cfDNA", "Diagnostics: Creatinine vs. dd-cfDNA"), t("Immunsuppression", "Immunosuppression")])

    with f_tab1:
        st.subheader(t("Paradigmenwechsel: Funktion vs. Schädigung", "Paradigm Shift: Function vs. Injury"))
        
        col_dd1, col_dd2 = st.columns([1, 1])
        with col_dd1:
            st.markdown(t("### 📉 Standard: Kreatinin", "### 📉 Standard: Creatinine"))
            st.warning(t("Problem: 'Lag Time'. Steigt erst spät.", "Problem: 'Lag Time'. Rises late."))
        with col_dd2:
            st.markdown(t("### 🧬 Zukunft: dd-cfDNA", "### 🧬 Future: dd-cfDNA"))
            st.success(t("Vorteil: Steigt Wochen früher.", "Benefit: Rises weeks earlier."))

        st.markdown("---")
        
        # --- NEW: PERSISTENT GRAPHIC GENERATION ---
        st.write(t("#### Kinetik: dd-cfDNA (Rot) vs. Kreatinin (Blau)", "#### Kinetics: dd-cfDNA (Red) vs. Creatinine (Blue)"))
        fig_biomarker = render_biomarker_chart(current_lang)
        st.pyplot(fig_biomarker)
        st.caption(t("Diese Grafik wird live generiert. Rot = Molekulare Schädigung (Früh). Blau = Funktionsverlust (Spät).", 
                     "This chart is generated live. Red = Molecular Injury (Early). Blue = Functional Loss (Late)."))
        # ------------------------------------------

        st.markdown("---")
        get_evidence_badge("dd_cfdna_kinetics")

    with f_tab2:
        st.code("Tacrolimus + MMF + Steroide")

# === 6. SEARCH ===
elif nav_selection == nav_options["Search"]:
    st.title("Live Search")
    q = st.text_input("Query", "kidney transplantation guidelines 2026")
    if st.button("Search"):
        res = fetch_pubmed_data(q)
        for r in res:
            st.write(f"**{r['Titel']}**")
