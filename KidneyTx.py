import streamlit as st
from pymed import PubMed
import pandas as pd
import graphviz

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NTX Master Guide 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LANGUAGE SETTINGS ---
# Helper function for simple text switching
def t(de, en):
    if st.session_state.get('lang', 'Deutsch') == 'Deutsch':
        return de
    return en

# --- EVIDENCE DATABASE (BILINGUAL) ---
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

# --- GRAPHVIZ WORKFLOWS (BILINGUAL) ---

def render_donor_workflow(lang):
    """SPENDER Workflow (RDN)"""
    is_de = lang == "Deutsch"
    dot = graphviz.Digraph(comment='RDN')
    dot.attr(rankdir='TB', size='8')
    dot.attr('node', shape='box', style='filled', fillcolor='#e8f5e9') # Green tint
    
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
    dot.attr('node', shape='box', style='filled', fillcolor='#e3f2fd') # Blue tint

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
# Language Selector
st.session_state['lang'] = st.sidebar.selectbox("Language / Sprache", ["Deutsch", "English"])
current_lang = st.session_state['lang']

# Define navigation options based on language
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
            "Patienten auf der Warteliste müssen 'transplantabel' bleiben. Abgelaufene Untersuchungen führen zur temporären Sperre (NT-Status).",
            "Patients on the waitlist must remain 'transplantable'. Expired exams lead to temporary suspension (NT status)."
        ))
        
        # Detailed Clinical Workup Data
        if current_lang == "Deutsch":
            workup_data = {
                "Bereich": ["Labor/Virologie", "Labor/Virologie", "Kardiovaskulär", "Kardiovaskulär", "Bildgebung", "Bildgebung", "Vorsorge"],
                "Untersuchung": ["HIV, HCV, HBV (PCR)", "CMV, EBV, VZV (IgG/IgM)", "EKG + TTE (Echo)", "Stress-Test (Dobutamin/Ergo)", "Röntgen Thorax", "Abdomen Sono (Nieren/Leber)", "Tumorscreening (Gyn/Uro/Haut)"],
                "Gültigkeit (Update)": ["3 Monate (bzw. akut vor TX)", "Einmalig (außer Status ändert sich)", "12 Monate", "12-24 Monate (je nach Risiko)", "12 Monate", "12 Monate", "12 Monate (Altersabhängig)"],
                "Kommentar": ["Entscheidend für High-Urgency", "Bestimmt Prophylaxe (Valcyte)", "EF < 30% ist Kontraindikation", "Bei Diabetikern/KHK zwingend", "Infektfokus ausschließen", "Steine/Tumore ausschließen", "Nach Tumorfreiheit (Warnecke-Kriterien)"]
            }
        else:
            workup_data = {
                "Category": ["Labs/Virology", "Labs/Virology", "Cardiovascular", "Cardiovascular", "Imaging", "Imaging", "Screening"],
                "Exam": ["HIV, HCV, HBV (PCR)", "CMV, EBV, VZV (IgG/IgM)", "ECG + TTE (Echo)", "Stress Test (Dobutamine/Ergo)", "CXR (Chest X-Ray)", "Abd. Ultrasound", "Cancer Screening (Gyn/Uro/Skin)"],
                "Validity (Update)": ["3 Months (or pre-Tx)", "Once (unless seroconversion)", "12 Months", "12-24 Months (Risk dependent)", "12 Months", "12 Months", "12 Months (Age dependent)"],
                "Comment": ["Crucial for High-Urgency", "Determines Prophylaxis", "EF < 30% is contraindication", "Mandatory for Diabetics/CAD", "Rule out infection", "Rule out stones/masses", "Wait times apply (Warnecke)"]
            }
        
        df_workup = pd.DataFrame(workup_data)
        st.dataframe(df_workup, use_container_width=True)

    with tab2:
        st.subheader(t("Kardiovaskuläres Risiko-Management", "Cardiovascular Risk Management"))
        st.write(t(
            "Kardiovaskuläre Ereignisse sind die häufigste Todesursache nach NTX. Ein striktes Screening ist essenziell.",
            "CV events are the leading cause of death post-KTx. Strict screening is essential."
        ))
        get_evidence_badge("cardio_workup")
        
        st.markdown(t("#### Algorithmus: Wann Herzkatheter (Coro)?", "#### Algorithm: When Angiography?"))
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.error(t("**Indikation zur Angio:**", "**Indication for Angio:**"))
            st.write("- Pathologischer Stress-Test")
            st.write("- Bekannte KHK / Stents")
            st.write("- Diabetes + >50 Jahre + Raucher (High Risk)")
        with col_c2:
            st.success(t("**Keine Angio nötig wenn:**", "**No Angio needed if:**"))
            st.write("- Belastbarkeit > 100 Watt (asymptomatisch)")
            st.write("- Stress-Echo unauffällig")
            st.write("- Keine kardialen Vorerkrankungen")

    with tab3:
        st.subheader(t("Immunologie (HLA)", "Immunology (HLA)"))
        st.write("• **HLA-A/B/C/DR/DQ/DP:** High-Res Typisierung.")
        st.write("• **PRA (Panel Reactive Antibodies):** " + t("Update alle 3 Monate nötig für Eurotransplant.", "Update every 3 months required for Eurotransplant."))
        st.write("• **Virtuelles Crossmatch:** " + t("Ersetzt physisches XM.", "Replaces physical XM."))

# === 2. DECEASED DONOR ===
elif nav_selection == nav_options["Deceased"]:
    st.title(t("Postmortale Spende (DBD / DCD)", "Deceased Donor (DBD / DCD)"))
    st.markdown(t("Prozesse von der Entnahme bis zur Implantation.", "Processes from retrieval to implantation."))
    
    col_proc, col_evid = st.columns([2, 1])
    
    with col_proc:
        st.subheader(t("Ablauf & Perfusion", "Workflow & Perfusion"))
        
        st.markdown(t(
            """
            1.  **Explantation:** En-bloc Entnahme der Nieren inkl. Aorta/Vena Cava Patch.
            2.  **Perfusion:** Sofortige Spülung mit 4°C kalter Lösung (z.B. HTK).
            3.  **Lagerung:** Entscheidung Statisch vs. Maschine.
            """,
            """
            1.  **Explantation:** En-bloc extraction including Aorta/Vena Cava patch.
            2.  **Perfusion:** Immediate flush with 4°C solution (e.g., HTK).
            3.  **Storage:** Decision Static vs. Machine.
            """
        ))
        
        st.markdown("---")
        st.markdown("")
        st.markdown("---")

        st.markdown(t("#### Workflow: Back-Table Präparation", "#### Workflow: Back-Table Preparation"))
        
        # Visualisierung Backtable
        st.code(t(
            """
            1. Trennung der Nieren (Split)
            2. Entfettung des Hilus (Vorsicht: Ureter-Vaskularisation!)
            3. Ligatur kleiner Seitenäste (Hemo-Clips)
            4. Biopsie (bei marginalen Spendern)
            """,
            """
            1. Splitting the kidneys
            2. Hilar defatting (Caution: Ureter vascularity!)
            3. Ligation of small branches (Hemo-clips)
            4. Biopsy (for marginal donors)
            """
        ), language="text")
        
        st.markdown("")

    with col_evid:
        st.subheader(t("🔬 Evidenz-Check", "🔬 Evidence Check"))
        st.write(t("Warum Maschinenperfusion?", "Why Machine Perfusion?"))
        get_evidence_badge("machine_perfusion")
        st.markdown("")
        
        st.write(t("Warum Mannitol?", "Why Mannitol?"))
        get_evidence_badge("mannitol")

    st.divider()
    
    st.subheader(t("Vergleich: Lagerungsmethoden", "Comparison: Storage Methods"))
    if current_lang == "Deutsch":
        comp_df = pd.DataFrame({
            "Methode": ["Statische Kältelagerung (SCS)", "Hypotherme Maschinenperfusion (HMP)"],
            "Prinzip": ["Eisbox (4°C)", "Pulsatile Durchspülung"],
            "Vorteil": ["Einfach, Billig", "Geringere DGF Rate, Qualitätscheck"],
            "Indikation": ["Standard-Spender (SCD)", "Marginale Spender (ECD)"]
        })
    else:
        comp_df = pd.DataFrame({
            "Method": ["Static Cold Storage (SCS)", "Hypothermic Machine Perfusion (HMP)"],
            "Principle": ["Ice box (4°C)", "Pulsatile Flow"],
            "Benefit": ["Simple, Cheap", "Lower DGF rate, Quality Assessment"],
            "Indication": ["Standard Donor (SCD)", "Marginal Donor (ECD)"]
        })
    st.table(comp_df)

# === 3. LIVING DONOR (RDN) ===
elif nav_selection == nav_options["Living"]:
    st.title(t("Robotische Spendernephrektomie (RDN)", "Robotic Donor Nephrectomy (RDN)"))
    
    t1, t2, t3 = st.tabs([
        t("Workflow (Diagramm)", "Workflow (Diagram)"), 
        t("Schritte & Technik", "Steps & Technique"), 
        t("Pharmakologie", "Pharmacology")
    ])
    
    with t1:
        st.graphviz_chart(render_donor_workflow(current_lang))
        st.caption(t("Fokus: Sicherheit & Minimale Ischämie", "Focus: Safety & Minimal Ischemia"))
    
    with t2:
        st.subheader(t("Detaillierte Schritte", "Detailed Steps"))
        st.markdown(t("**1. Lagerung:** 60° Seitenlage.", "**1. Positioning:** 60° Flank position."))
        st.markdown("")
        
        st.markdown(t("**2. ICG-Check:** Vor Ureter-Schnitt Perfusion prüfen.", "**2. ICG-Check:** Verify perfusion before ureter cut."))
        get_evidence_badge("icg_ureter")
        
        st.markdown(t("**3. Stapling:** Vascular Stapler verwenden.", "**3. Stapling:** Use Vascular Stapler."))
        get_evidence_badge("stapler_safety")
        
    with t3:
        st.subheader(t("Spender-Medikation (Intra-Op)", "Donor Medication (Intra-Op)"))
        st.error(t("Gabe 3-5 min vor Abklemmen!", "Administer 3-5 min before clamping!"))
        
        if current_lang == "Deutsch":
            pharma_df = pd.DataFrame({
                "Medikament": ["Heparin", "Mannitol", "Furosemid"],
                "Dosis": ["5000 IE", "25g (125ml)", "20-40mg"],
                "Effekt": ["Thromboseprophylaxe", "Radikalfänger", "Diurese"]
            })
        else:
            pharma_df = pd.DataFrame({
                "Drug": ["Heparin", "Mannitol", "Furosemide"],
                "Dose": ["5000 IU", "25g (125ml)", "20-40mg"],
                "Effect": ["Thrombosis Prophylaxis", "Radical Scavenger", "Diuresis"]
            })
        st.table(pharma_df)
        get_evidence_badge("heparin_donor")

# === 4. RECIPIENT SURGERY (RAKT) ===
elif nav_selection == nav_options["Recipient"]:
    st.title(t("Robotische Implantation (RAKT)", "Robotic Implantation (RAKT)"))
    st.info(t("Detaillierter Workflow & Vergleich", "Detailed Workflow & Comparison"))

    t1, t2, t3 = st.tabs([
        t("Workflow (Diagramm)", "Workflow (Diagram)"), 
        t("Vergleich (Offen vs. RAKT)", "Comparison (Open vs. RAKT)"), 
        t("Pharmakologie", "Pharmacology")
    ])
    
    with t1:
        st.subheader(t("Implantations-Workflow", "Implantation Workflow"))
        st.write(t("Beachten Sie die **Regionale Hypothermie**.", "Note the **Regional Hypothermia**."))
        st.graphviz_chart(render_recipient_workflow(current_lang))
    
    with t2:
        st.subheader(t("Warum Robotisch? (Vergleichsdaten)", "Why Robotic? (Comparison Data)"))
        st.markdown("")
        
        if current_lang == "Deutsch":
            comp_df = pd.DataFrame({
                "Parameter": ["Inzisionslänge", "Wundinfektion (SSI)", "Lymphozelen", "Warm-Ischämie"],
                "Offene NTX": ["15-20 cm", "10-15% (bei BMI>30)", "Häufig", "30-40 min"],
                "Robotische NTX": ["6 cm", "< 4%", "Selten", "45-55 min"]
            })
        else:
            comp_df = pd.DataFrame({
                "Parameter": ["Incision Length", "Infection (SSI)", "Lymphoceles", "Warm Ischemia"],
                "Open KTx": ["15-20 cm", "10-15% (if BMI>30)", "Frequent", "30-40 min"],
                "Robotic KTx": ["6 cm", "< 4%", "Rare", "45-55 min"]
            })
        st.table(comp_df)
        get_evidence_badge("rakt_safety")
        
    with t3:
        st.subheader(t("Empfänger-Medikation", "Recipient Medication"))
        st.warning(t("Timing: Bevor die Gefäßklemmen geöffnet werden.", "Timing: Before unclamping."))
        
        if current_lang == "Deutsch":
            rec_meds = pd.DataFrame({
                "Medikament": ["Methylprednisolon", "Furosemid"],
                "Dosis": ["250-500 mg", "200 mg"],
                "Ziel": ["Schutz vor Reperfusionsschaden", "Anregung Primärfunktion"]
            })
        else:
            rec_meds = pd.DataFrame({
                "Drug": ["Methylprednisolone", "Furosemide"],
                "Dose": ["250-500 mg", "200 mg"],
                "Goal": ["Reperfusion Injury Protection", "Kickstart Function"]
            })
        st.table(rec_meds)

# === 5. FOLLOW UP (EXPANDED) ===
elif nav_selection == nav_options["FollowUp"]:
    st.title(t("Nachsorge & Guidelines", "Follow-Up & Guidelines"))
    
    # New Tabs for better structure
    f_tab1, f_tab2 = st.tabs([t("Diagnostik: Kreatinin vs. dd-cfDNA", "Diagnostics: Creatinine vs. dd-cfDNA"), t("Immunsuppression", "Immunosuppression")])

    with f_tab1:
        st.subheader(t("Paradigmenwechsel: Von Funktion zu Molekularer Schädigung", "Paradigm Shift: From Function to Molecular Injury"))
        
        col_dd1, col_dd2 = st.columns([1, 1])
        
        with col_dd1:
            st.markdown(t("### 📉 Der Standard: Kreatinin", "### 📉 The Standard: Creatinine"))
            st.write(t(
                "Kreatinin ist ein **Funktionsmarker**. Er steigt erst an, wenn bereits ~50% der Nephrone geschädigt sind.",
                "Creatinine is a **functional marker**. It only rises once ~50% of nephrons are already compromised."
            ))
            st.warning(t("Problem: 'Lag Time' (Verzögerung). Eine Abstoßung läuft oft schon seit Wochen, bevor das Kreatinin steigt.", 
                         "Problem: 'Lag Time'. Rejection often proceeds for weeks before Creatinine rises."))

        with col_dd2:
            st.markdown(t("### 🧬 Die Zukunft: dd-cfDNA", "### 🧬 The Future: dd-cfDNA"))
            st.write(t(
                "Donor-derived cell-free DNA ist ein **Schädigungsmarker** (Injury Marker). Zellen des Spenders sterben ab und setzen DNA ins Blut frei.",
                "Donor-derived cell-free DNA is an **injury marker**. Donor cells die and release DNA into the bloodstream."
            ))
            st.success(t("Vorteil: Hoher Negativer Prädiktiver Wert (NPV). Wenn dd-cfDNA niedrig ist (<0.5%), ist eine Abstoßung sehr unwahrscheinlich -> Biopsie gespart.",
                         "Benefit: High Negative Predictive Value (NPV). If dd-cfDNA is low (<0.5%), rejection is highly unlikely -> Biopsy avoided."))

        st.markdown("---")
        st.markdown("")
        st.caption(t("Grafik: dd-cfDNA (Rot) steigt Wochen vor dem Kreatinin (Blau).", "Graph: dd-cfDNA (Red) rises weeks before Creatinine (Blue)."))
        st.markdown("---")

        st.subheader(t("Vergleichstabelle", "Comparison Table"))
        
        if current_lang == "Deutsch":
            comp_markers = pd.DataFrame({
                "Marker": ["Serum Kreatinin", "Proteinurie", "dd-cfDNA (Blut)"],
                "Was wird gemessen?": ["Filtrationsleistung (GFR)", "Glomeruläre Integrität", "Zelluntergang (Nekrose/Apoptose)"],
                "Detektionszeitpunkt": ["Spät (Funktionsverlust)", "Mittel", "Früh (Aktive Entzündung)"],
                "Cut-Off": ["Trend > 20% Anstieg", "> 0.5 - 1.0 g/g", "> 0.5% - 1.0% (Assay-abhängig)"]
            })
        else:
            comp_markers = pd.DataFrame({
                "Marker": ["Serum Creatinine", "Proteinuria", "dd-cfDNA (Blood)"],
                "Measures": ["Filtration Power (GFR)", "Glomerular Integrity", "Cell Death (Necrosis/Apoptosis)"],
                "Detection Time": ["Late (Function Loss)", "Medium", "Early (Active Inflammation)"],
                "Cut-Off": ["Trend > 20% rise", "> 0.5 - 1.0 g/g", "> 0.5% - 1.0% (Assay dependent)"]
            })
        st.table(comp_markers)
        get_evidence_badge("dd_cfdna_kinetics")

    with f_tab2:
        st.subheader(t("Immunsuppression (Standard)", "Immunosuppression (Standard)"))
        st.code("Tacrolimus (Target 8-10 ng/ml) + MMF (2g/d) + Steroide (Tapering)")
        st.write(t(
            "Biopsie-Indikation bleibt Goldstandard bei unklarem Befund.",
            "Biopsy remains gold standard for unclear findings."
        ))

# === 6. SEARCH ===
elif nav_selection == nav_options["Search"]:
    st.title(t("Live Suche", "Live Search"))
    q = st.text_input(t("Suchbegriff", "Search Query"), "kidney transplantation guidelines 2026")
    if st.button(t("Suchen", "Search")):
        res = fetch_pubmed_data(q)
        for r in res:
            st.write(f"**{r['Titel']}** ({r['Date']})")
            st.caption(r['Abstract'])
            st.markdown("---")
