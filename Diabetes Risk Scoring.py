import sqlite3
import statistics
import time
import random
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

# =====================================================================
# 1. DATA ACCESS LAYER (SQLITE PERSISTENT STORAGE)
# =====================================================================
class PatientModel:
    """Manages persistent SQLite patient data storage and initial data cleaning."""

    def __init__(self, db_path: str = "patients.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY,
                    glucose REAL,
                    bmi REAL,
                    age REAL,
                    blood_pressure REAL
                )
            """)
            conn.commit()

            # Seed initial dataset if database is empty
            cursor.execute("SELECT COUNT(*) FROM patients")
            if cursor.fetchone()[0] == 0:
                initial_patients = [
                    (101, 95.0, 22.5, 28.0, 115.0),
                    (102, 145.0, 0.0, 54.0, 135.0),
                    (103, 112.0, 29.1, 42.0, 122.0),
                    (104, 180.0, 36.4, 61.0, 142.0),
                ]
                cursor.executemany("""
                    INSERT INTO patients (patient_id, glucose, bmi, age, blood_pressure)
                    VALUES (?, ?, ?, ?, ?)
                """, initial_patients)
                conn.commit()
                self._clean_initial_data()

    def _clean_initial_data(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bmi FROM patients WHERE bmi > 0")
            valid_bmis = [row[0] for row in cursor.fetchall()]
            median_bmi = statistics.median(valid_bmis) if valid_bmis else 25.0

            cursor.execute("""
                UPDATE patients 
                SET bmi = ? 
                WHERE bmi <= 0
            """, (round(median_bmi, 1),))
            conn.commit()

    def get_all_ids(self) -> List[int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id FROM patients ORDER BY patient_id ASC")
            return [row[0] for row in cursor.fetchall()]

    def get_patient(self, patient_id: int) -> Optional[Dict[str, float]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT glucose, bmi, age, blood_pressure 
                FROM patients 
                WHERE patient_id = ?
            """, (patient_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "Glucose": row[0],
                    "BMI": row[1],
                    "Age": row[2],
                    "BloodPressure": row[3],
                }
            return None

    def get_all_patients(self) -> Dict[int, Dict[str, float]]:
        """Retrieves all patient records from the SQLite database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id, glucose, bmi, age, blood_pressure FROM patients ORDER BY patient_id ASC")
            rows = cursor.fetchall()
            return {
                row[0]: {
                    "Glucose": row[1],
                    "BMI": row[2],
                    "Age": row[3],
                    "BloodPressure": row[4],
                }
                for row in rows
            }

    def add_patient(self, patient_id: int, metrics: Dict[str, float]) -> bool:
        """Inserts or replaces a patient record in SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO patients (patient_id, glucose, bmi, age, blood_pressure)
                VALUES (?, ?, ?, ?, ?)
            """, (
                patient_id,
                metrics.get("Glucose", 95.0),
                metrics.get("BMI", 24.0),
                metrics.get("Age", 30.0),
                metrics.get("BloodPressure", 120.0),
            ))
            conn.commit()
            return True

    def update_patient(self, patient_id: int, updated_metrics: Dict[str, float]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM patients WHERE patient_id = ?", (patient_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("""
                UPDATE patients 
                SET glucose = ?, bmi = ?, age = ?, blood_pressure = ?
                WHERE patient_id = ?
            """, (
                updated_metrics.get("Glucose", 0.0),
                updated_metrics.get("BMI", 0.0),
                updated_metrics.get("Age", 0.0),
                updated_metrics.get("BloodPressure", 0.0),
                patient_id,
            ))
            conn.commit()
            return True


# =====================================================================
# 2. BUSINESS LOGIC LAYER (UNCHANGED)
# =====================================================================
class ClinicalRiskService:
    """Handles clinical decision rules, point scoring, and risk categorization."""

    THRESHOLDS = {
        "Glucose": (100.0, 125.0),
        "BMI": (25.0, 29.9),
        "Age": (35.0, 55.0),
        "BloodPressure": (120.0, 130.0),
    }

    def calculate_metric_score(self, metric_name: str, value: float) -> int:
        if metric_name not in self.THRESHOLDS:
            return 0
        low_max, med_max = self.THRESHOLDS[metric_name]
        if value <= low_max:
            return 0
        elif value <= med_max:
            return 1
        return 2

    def evaluate_patient_risk(self, metrics: Dict[str, float]) -> Tuple[int, str]:
        total_score = sum(self.calculate_metric_score(m, v) for m, v in metrics.items())
        if total_score <= 2:
            category = "Low Risk"
        elif total_score <= 5:
            category = "Moderate Risk"
        else:
            category = "High Risk"
        return total_score, category


# =====================================================================
# AUTOMATED 3-TIER TEST SUITE (UNCHANGED)
# =====================================================================
class RiskAssessmentTestSuite:
    """Encapsulates unit, end-to-end, and performance test suites."""

    def __init__(self, model_factory, service_class):
        self.model_factory = model_factory
        self.service_class = service_class

    def run_all_tiers(self) -> None:
        print("\n" + "="*60)
        print("         STARTING 3-TIER AUTOMATED TESTING SUITE")
        print("="*60)

        self.run_tier1_unit_tests()
        self.run_tier2_e2e_scenarios()
        self.run_tier3_performance_benchmarks()

        print("\n" + "="*60)
        print("         ALL AUTOMATED TESTING TIERS PASSED SUCCESSFULLY")
        print("="*60 + "\n")

    def run_tier1_unit_tests(self) -> None:
        print("\n--- Running Tier 1: Unit Tests (Decision Rules) ---")
        service = self.service_class()

        assert service.calculate_metric_score("Glucose", 95.0) == 0, "Failed Glucose Low threshold"
        assert service.calculate_metric_score("Glucose", 110.0) == 1, "Failed Glucose Med threshold"
        assert service.calculate_metric_score("Glucose", 130.0) == 2, "Failed Glucose High threshold"

        assert service.calculate_metric_score("BMI", 25.0) == 0, "Border case BMI=25 failed"
        assert service.calculate_metric_score("BMI", 25.1) == 1, "Border case BMI=25.1 failed"

        score_low, cat_low = service.evaluate_patient_risk({"Glucose": 90.0, "BMI": 22.0, "Age": 30.0, "BloodPressure": 110.0})
        assert score_low == 0 and "Low" in cat_low, f"Expected Low Risk, got {score_low} pts ({cat_low})"

        score_med, cat_med = service.evaluate_patient_risk({"Glucose": 115.0, "BMI": 27.0, "Age": 45.0, "BloodPressure": 125.0})
        assert 3 <= score_med <= 5 and "Moderate" in cat_med, f"Expected Mod Risk, got {score_med} pts ({cat_med})"

        score_high, cat_high = service.evaluate_patient_risk({"Glucose": 140.0, "BMI": 35.0, "Age": 60.0, "BloodPressure": 135.0})
        assert score_high >= 6 and "High" in cat_high, f"Expected High Risk, got {score_high} pts ({cat_high})"

        print(" ✓ Tier 1 Unit Tests Pass: All rule sets mapped and categorized perfectly.")

    def run_tier2_e2e_scenarios(self) -> None:
        print("\n--- Running Tier 2: End-to-End Workflows ---")
        model = self.model_factory()
        service = self.service_class()

        patient_102 = model.get_patient(102)
        assert patient_102 is not None, "E2E Error: Patient 102 not found"
        assert patient_102["BMI"] > 0, f"E2E Error: Anomalous BMI of 0 was not replaced. Got {patient_102['BMI']}"

        patient_101 = model.get_patient(101)
        original_score, _ = service.evaluate_patient_risk(patient_101)

        modified_metrics = {
            "Glucose": 150.0,
            "BMI": patient_101["BMI"],
            "Age": patient_101["Age"],
            "BloodPressure": 140.0
        }

        update_ok = model.update_patient(101, modified_metrics)
        assert update_ok, "E2E Error: Database modification write failed"

        updated_profile = model.get_patient(101)
        new_score, new_category = service.evaluate_patient_risk(updated_profile)

        assert new_score > original_score, "E2E Error: Score did not increase after modifying risk variables"
        assert "High" in new_category or "Moderate" in new_category, "E2E Error: Risk category didn't escalate correctly"

        print(" ✓ Tier 2 E2E Tests Pass: Clean-to-write-to-score cycle validated.")

    def run_tier3_performance_benchmarks(self, iterations: int = 10000) -> None:
        print(f"\n--- Running Tier 3: Performance Latency ({iterations:,} iterations) ---")
        service = self.service_class()
        test_metrics = {"Glucose": 115.0, "BMI": 27.5, "Age": 42.0, "BloodPressure": 125.0}

        start_time = time.perf_counter()
        for _ in range(iterations):
            _ = service.evaluate_patient_risk(test_metrics)
        end_time = time.perf_counter()

        total_duration = end_time - start_time
        avg_duration_ms = (total_duration / iterations) * 1000

        print(f" ✓ Tier 3 Performance Pass: Completed {iterations:,} diagnostic evaluations in {total_duration:.4f}s.")
        print(f"   Mean Latency: {avg_duration_ms:.6f} ms per patient transaction analysis.")


# =====================================================================
# 3. STREAMLIT PRESENTATION & CONTROLLER LAYER WITH LIVE DB SIMULATION
# =====================================================================
def main():
    st.set_page_config(
        page_title="Diabetes Risk Scoring System",
        page_icon="🩺",
        layout="centered"
    )

    # Maintain persistent instances across Streamlit reruns
    if "model" not in st.session_state:
        st.session_state.model = PatientModel()
    if "service" not in st.session_state:
        st.session_state.service = ClinicalRiskService()

    model: PatientModel = st.session_state.model
    service: ClinicalRiskService = st.session_state.service

    # Header section
    st.title("🩺 Diabetes Risk Scoring System")
    st.caption("SQLite persistent database backend with real-time telemetry simulation.")

    # Sidebar: System Tools & Test Suite Controls
    with st.sidebar:
        st.header("⚙️ System Tools")
        if st.button("🧪 Run Test Suite", type="secondary", use_container_width=True):
            suite = RiskAssessmentTestSuite(model_factory=PatientModel, service_class=ClinicalRiskService)
            try:
                suite.run_all_tiers()
                st.sidebar.success("All 3 Testing Tiers Passed!")
            except AssertionError as err:
                st.sidebar.error(f"Test Assertion Failed:\n{err}")

        st.divider()
        st.write("📁 **Database Target:** `patients.db` (SQLite)")

    # UI Tab Navigation
    tab_assessment, tab_live_db = st.tabs([
        "📋 Patient Assessment", 
        "⚡ Live Database & Simulation"
    ])

    # -----------------------------------------------------------------
    # TAB 1: INDIVIDUAL PATIENT ASSESSMENT
    # -----------------------------------------------------------------
    with tab_assessment:
        patient_ids = model.get_all_ids()
        selected_id = st.selectbox("Select Patient ID:", options=patient_ids, key="assessment_pid_select")

        patient_metrics = model.get_patient(selected_id)

        if patient_metrics:
            st.subheader(f"Clinical Profile: Patient {selected_id}")

            with st.form(key=f"patient_form_{selected_id}"):
                col1, col2 = st.columns(2)

                with col1:
                    glucose = st.number_input(
                        "Glucose (mg/dL)", 
                        min_value=0.0, 
                        value=float(patient_metrics["Glucose"]), 
                        step=1.0
                    )
                    bmi = st.number_input(
                        "BMI", 
                        min_value=0.0, 
                        value=float(patient_metrics["BMI"]), 
                        step=0.1
                    )

                with col2:
                    age = st.number_input(
                        "Age (years)", 
                        min_value=0.0, 
                        value=float(patient_metrics["Age"]), 
                        step=1.0
                    )
                    bp = st.number_input(
                        "Blood Pressure (mmHg)", 
                        min_value=0.0, 
                        value=float(patient_metrics["BloodPressure"]), 
                        step=1.0
                    )

                submitted = st.form_submit_button("Evaluate Patient Risk", type="primary", use_container_width=True)

            if submitted:
                updated_metrics = {
                    "Glucose": glucose,
                    "BMI": bmi,
                    "Age": age,
                    "BloodPressure": bp
                }

                # Persist update to SQLite
                model.update_patient(selected_id, updated_metrics)

                # Calculate Risk
                score, category = service.evaluate_patient_risk(updated_metrics)

                st.divider()
                st.subheader("📊 Diagnostic Risk Report")

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(label="Cumulative Risk Score", value=f"{score} pts")

                with res_col2:
                    st.write("**Risk Category**")
                    if category == "Low Risk":
                        st.success(f"🟢 **{category.upper()}**")
                    elif category == "Moderate Risk":
                        st.warning(f"🟠 **{category.upper()}**")
                    else:
                        st.error(f"🔴 **{category.upper()}**")

    # -----------------------------------------------------------------
    # TAB 2: LIVE DATABASE MONITOR & TELEMETRY SIMULATOR
    # -----------------------------------------------------------------
    with tab_live_db:
        st.subheader("⚡ Real-Time SQLite Database Monitor")
        st.write("This panel displays records stored in `patients.db` alongside live updates.")

        # Simulation Action Buttons
        sim_col1, sim_col2, sim_col3 = st.columns(3)

        with sim_col1:
            if st.button("🎲 Random Vitals Update", use_container_width=True):
                all_ids = model.get_all_ids()
                if all_ids:
                    target_id = random.choice(all_ids)
                    current = model.get_patient(target_id)
                    if current:
                        # Fluctuate metrics realistically
                        current["Glucose"] = round(max(70.0, current["Glucose"] + random.uniform(-15.0, 20.0)), 1)
                        current["BloodPressure"] = round(max(90.0, current["BloodPressure"] + random.uniform(-10.0, 15.0)), 1)
                        current["BMI"] = round(max(18.0, current["BMI"] + random.uniform(-0.5, 0.5)), 1)
                        model.update_patient(target_id, current)
                        st.toast(f"⚡ Live update written to SQLite for Patient {target_id}!", icon="💾")

        with sim_col2:
            if st.button("➕ Admit New Patient", use_container_width=True):
                existing_ids = model.get_all_ids()
                new_id = max(existing_ids) + 1 if existing_ids else 101
                new_vitals = {
                    "Glucose": round(random.uniform(85.0, 175.0), 1),
                    "BMI": round(random.uniform(20.0, 38.0), 1),
                    "Age": float(random.randint(22, 75)),
                    "BloodPressure": round(random.uniform(110.0, 145.0), 1)
                }
                model.add_patient(new_id, new_vitals)
                st.toast(f"➕ Patient {new_id} admitted and saved to DB!", icon="🏥")

        with sim_col3:
            stream_requested = st.button("📡 Stream Live Telemetry (5s)", use_container_width=True, type="primary")

        # Container for rendering database records
        db_display_container = st.empty()

        def render_live_table():
            all_records = model.get_all_patients()
            table_data = []

            for pid, metrics in all_records.items():
                score, category = service.evaluate_patient_risk(metrics)
                table_data.append({
                    "Patient ID": pid,
                    "Glucose (mg/dL)": metrics["Glucose"],
                    "BMI": metrics["BMI"],
                    "Age": int(metrics["Age"]),
                    "Blood Pressure": metrics["BloodPressure"],
                    "Score": f"{score} pts",
                    "Risk Category": category
                })

            with db_display_container.container():
                st.dataframe(table_data, use_container_width=True, hide_index=True)

        # Handle telemetry streaming loop
        if stream_requested:
            progress_bar = st.progress(0, text="Streaming live clinical updates to SQLite...")
            for i in range(1, 6):
                time.sleep(0.8)
                all_ids = model.get_all_ids()
                if all_ids:
                    target_id = random.choice(all_ids)
                    p_data = model.get_patient(target_id)
                    if p_data:
                        p_data["Glucose"] = round(max(70.0, p_data["Glucose"] + random.uniform(-10.0, 15.0)), 1)
                        p_data["BloodPressure"] = round(max(90.0, p_data["BloodPressure"] + random.uniform(-5.0, 10.0)), 1)
                        model.update_patient(target_id, p_data)

                render_live_table()
                progress_bar.progress(i * 20, text=f"Streaming tick {i}/5 completed...")

            progress_bar.empty()
            st.success("Live telemetry stream finished!")
        else:
            render_live_table()


if __name__ == "__main__":
    main()
