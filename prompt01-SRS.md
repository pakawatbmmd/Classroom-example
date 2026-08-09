# Role 
Act as an expert software architect and developer.

# Context
I need to build a "Diabetes Risk Scoring System".  I want you to design, structure, and fully implement a complete, working Python program based on the 4-Tier Architecture as follows.

# Architecture 
Separate the code cleanly into these 4 distinct layers:
1. Data Access Layer (The Model): Manages raw data and initial cleanup.
2. Business Logic Layer (The Service): Handles pure clinical decision rules and scoring.
3. Presentation Layer (The View): Handles the user interface layout and captures inputs.
4. Orchestration Layer (The Controller): Manages the workflow and coordinates between the layers.

# High-Level Requirements & Use Cases

## Data Mockup: Start with 4 samp	le patients containing these baseline metrics: Glucose, BMI, 
Age, and BloodPressure. If a patient's BMI is 0, automatically fix it by replacing it with the median BMI of the other patients during initialization.

## Core Workflow 01
1. Display a main menu to either "1. Assess Patient Risk" or "2. Exit".
2. If '1', display a list of valid Patient IDs.
3. Ask the user to select an ID. Show an error if the ID doesn't exist or isn't a number.
4. Display that patient's current clinical profile.
5. Ask the user if they want to modify any metrics before running the risk calculation. If yes, let them input new data (or hit Enter to keep current values) and save it.
6. Calculate a risk score and category, then display a "Diagnostic Risk Report".

## Core Workflow 02
1. Display a main menu to either "1. Assess Patient Risk" or "2. Exit".
2. If '2', exit the program.

# Domain Knowledge

## Clinical Decision Scoring Rules:
- For each metric (Glucose, BMI, Age, BloodPressure), define three ranges: Low (scores 0), Medium (scores 1), and High (scores 2).
- Add up the scores of all 4 metrics to get a total score.
- Categorize the total score: Low Risk (0-2), Moderate Risk (3-5), High Risk (6+).

# 3-Tier Testing Suite
At the bottom of the script, include an automated testing section. Autonomously design and implement:
- Unit Tests: Comprehensive test cases verifying individual components, data cleaning, and scoring logic. 
- End-to-End (E2E) Tests: A simulated user journey loop proving all 4 layers interact correctly. 
- Performance Tests: A speed benchmark that measures and logs evaluation processing times.

# Deliverables
- Provide the complete, production-ready code in a single file so I can copy and run it immediately.
- Include a RUN_TEST_SUITE switch to toggle between running the 3-tier testing suite and launching the application.
- Add comments where necessary to improve code readability and maintainability.

