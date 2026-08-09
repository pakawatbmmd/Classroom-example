# TECHNICAL DESIGN DOCUMENT

## Diabetes Risk Scoring System

---

## 1. System Architecture Overview

The Diabetes Risk Scoring System adheres to a strict 4-Tier Architecture, isolating concerns into data management, core clinical rules, programmatic layout, and workflow orchestration.

The text-based sequence diagrams below illustrate the behavioral flow of class and method executions from left to right, maintaining the explicit tier boundaries:
`[User]` $\rightarrow$ `[Presentation Layer]` $\rightarrow$ `[Orchestration Layer]` $\rightarrow$ `[Business Logic Layer]` $\rightarrow$ `[Data Access Layer]`.

### Core Workflow 01: Assess Patient Risk

This workflow charts the collection of the patient identity, active retrieval and profiling of data, step-by-step user confirmation for modification metrics, and the eventual clinical evaluation generation.

```text
[User]            [Presentation Layer]      [Orchestration Layer]      [Business Logic Layer]       [Data Access Layer]
  |                   (ConsoleView)       (RiskAssessmentController)   (ClinicalRiskService)         (PatientModel)
  |                        |                         |                           |                          |
  |--- Select Option 1 --->|                         |                           |                          |
  |                        |--- display_main_menu() >|                           |                          |
  |                        |                         |--- handle_assessment_workflow()                      |
  |                        |                         |                           |                          |
  |                        |                         |----------------------- get_all_ids() --------------->|
  |                        |<-- display_patient_ids()|                           |                          |
  |                        |                         |                           |                          |
  |--- Enter Patient ID -->|                         |                           |                          |
  |                        |--- prompt_patient_id() >|                           |                          |
  |                        |                         |----------------------- get_patient(id) ------------->|
  |                        |<-- display_profile() ---|                           |                          |
  |                        |                         |                           |                          |
  |--- Modify? (y/n) ----->|                         |                           |                          |
  |                        |--- prompt_mod_choice() >|                           |                          |
  |                        |                         |                           |                          |
  |   [If 'y' (Yes)]       |                         |                           |                          |
  |--- Input Metrics ----->|                         |                           |                          |
  |                        |-- prompt_metric_update()|                           |                          |
  |                        |                         |----------------------- update_patient() ------------>|
  |                        |                         |                           |                          |
  |                        |                         |--- evaluate_patient_risk()                           |
  |                        |                         |                           |-- calc_metric_score()    |
  |                        |<-- display_diagnostic_report()                      |                          |
  |                        |                         |                           |                          |

```

### Core Workflow 02: Exit System

This workflow traces the command teardown loop initiated by the user when choosing to disconnect from the operational runtime application interface safely.

```text
[User]            [Presentation Layer]      [Orchestration Layer]      [Business Logic Layer]       [Data Access Layer]
  |                   (ConsoleView)       (RiskAssessmentController)   (ClinicalRiskService)         (PatientModel)
  |                        |<----------------run()---|                           |                          |
  |<-- display_main_menu()-|                         |                           |                          |
  |--- Select Option 2 --->|                         |                           |                          |
  |                        |--- return 2 ----------> |                           |                          |
  |<-- Prints "Goodbye" ---|-------------------------|                           |                          |

```

---

## 2. Method Specification

### Data Access Layer (The Model)

**Class:** `PatientModel`

Responsible for hosting mock operational datasets, scrubbing fields during program startup to rectify missing boundaries, and maintaining database sync operations.

| Method Name | Inputs (What it needs) | Process (What it does inside) | Outputs (What it delivers) |
| --- | --- | --- | --- |
| `__init__` | None | Seeds four initial mock patient dictionary metrics and invokes internal data cleaning processes. | Instance initialization. |
| `_clean_initial_data` | None | Iterates through records, identifies any anomalies where `BMI == 0`, calculates the mathematical median of all other non-zero patient BMIs, and overrides anomalies using that median. | None (Modifies state in-place). |
| `get_all_ids` | None | Extracts primary keys representing known patients and sorts them sequentially. | List of patient ID integers (`List[int]`). |
| `get_patient` | Patient ID (`int`) | Performs a standard dictionary key query lookup to retrieve the target record and wraps it securely. | A deep copy of clinical metrics map (`Dict[str, float]` or `None`). |
| `update_patient` | Patient ID (`int`), Updated Metrics (`Dict[str, float]`) | Validates identifier existence inside memory storage; performs inline key updates matching incoming metrics values if the identifier exists. | Operation status boolean flag (`bool`). |

---

### Business Logic Layer (The Service)

**Class:** `ClinicalRiskService`

Houses the isolated logic boundaries governing the point scoring algorithm and diagnostic classifications based strictly on raw medical numerical vectors.

| Method Name | Inputs (What it needs) | Process (What it does inside) | Outputs (What it delivers) |
| --- | --- | --- | --- |
| `calculate_metric_score` | Metric Name (`str`), Value (`float`) | Validates variable name against configured system thresholds; evaluates boundaries into Low (0 points), Medium (1 point), or High (2 points) buckets. | Calculated ordinal scale metric point (`int`). |
| `evaluate_patient_risk` | Clinical Metrics (`Dict[str, float]`) | Iterates across the map of standard biomarkers, passing values through individual scoring engines; matches final aggregate points to safe risk classes. | Tuple consisting of the Cumulative Score (`int`) and Risk Category (`str`). |

---

### Presentation Layer (The View)

**Class:** `ConsoleView`

Manages interactive layout formatting, standard out/in system pipes, interface borders, and clean data text styling.

| Method Name | Inputs (What it needs) | Process (What it does inside) | Outputs (What it delivers) |
| --- | --- | --- | --- |
| `display_main_menu` | None | Renders menu design framework choices to the terminal and polls the active input buffer line. | Unsanitized menu selector string (`str`). |
| `display_patient_ids` | IDs List (`List[int]`) | Flattens the array of system identifiers into a unified string line for easy user visibility. | None (Prints output to stdout). |
| `prompt_patient_id` | None | Prompts user line interface specifically requesting target reference patient key identifier input. | Input identifier string line (`str`). |
| `display_error` | Error Message (`str`) | Encapsulates string feedback inside standardized console error formatting prefixes. | None (Prints output to stdout). |
| `display_profile` | Patient ID (`int`), Metrics (`Dict[str, float]`) | Traverses provided metric pairs to cleanly map current state numbers to the active console terminal view. | None (Prints output to stdout). |
| `prompt_modification_choice` | None | Prompts user to confirm if they wish to overwrite any baseline biomarker parameters before evaluation. | Binary boolean choice verification value (`bool`). |
| `prompt_metric_update` | Metric Name (`str`), Current Value (`float`) | Shows the user the current metric value and prompts for a change. If empty, it returns the current value. Valid entries are cast to float; malformed strings fallback safely. | Final processing parameter metric level (`float`). |
| `display_diagnostic_report` | Patient ID (`int`), Score (`int`), Category (`str`) | Constructs a framed visual block detailing clinical evaluation statistics and final aggregate risk groupings. | None (Prints output to stdout). |

---

### Orchestration Layer (The Controller)

**Class:** `RiskAssessmentController`

Maintains core lifecycle system states by passing contexts from views down into core processing services, saving states to data caches, and driving structural workflow loops.

| Method Name | Inputs (What it needs) | Process (What it does inside) | Outputs (What it delivers) |
| --- | --- | --- | --- |
| `__init__` | Model instance, Service instance, View instance | Interlinks architectural components locally through standard dependency injection patterns. | Instance initialization. |
| `run` | None | Powers continuous main application operational states routing execution threads dynamically based on main menu choices. | None (Terminates on option choice 2). |
| `handle_assessment_workflow` | None | Directs multi-tiered logic components through the complete five-stage step sequence framework comprising user identification, data mapping, modifications validation, scoring execution, and report delivery. | None. |
