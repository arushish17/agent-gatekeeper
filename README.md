# Agent Gatekeeper: Security & Permission-Management Rail
### University Assignment Project — Enterprise AI Agent Governance
**Student Enrolment Number:** `PGD202564166`  
**Target Enterprise:** **Wells Fargo (Bank)** (Determined by Enrolment Last Digit `6`)  
**Core Technologies:** Python 3, Flask, HTML5, CSS3, JavaScript, Persistent JSON Storage, ReportLab, Unittest  

---

## 1. Project Introduction

**Agent Gatekeeper** is a high-assurance security and permission-management gateway designed to protect retail banking infrastructure from unauthorized, rogue, or unvetted autonomous AI agents. 

As consumers adopt autonomous personal finance agents (such as budgeting co-pilots and browser-driven transaction bots), they delegate credentials to third-party models. These agents interact with banking endpoints without the physical presence of a human, introducing unprecedented attack vectors including prompt injections, non-deterministic action drift, and zombie access.

Agent Gatekeeper acts as an intelligent intermediary. It intercepts every incoming request from a customer's personal AI agent, evaluates it against eight deterministic business rules, and renders one of three unambiguous decisions:

1. <span style="color:green">**ALLOW**</span> – Permit the safe read-only operation (e.g., `View balance`).
2. <span style="color:orange">**ASK CUSTOMER**</span> – Halt execution and require explicit step-up customer confirmation (e.g., `Pay a bill`, `Transfer money`, or transactions exceeding ₹10,000).
3. <span style="color:red">**BLOCK**</span> – Immediately reject the request with a detailed audit justification (e.g., unknown agents, revoked agents, or scope violations).

---

## 2. Key Features

- **Executive Analytics Dashboard:** Real-time visibility into total, active, and revoked agents, total requests processed, and counters for ALLOW, ASK CUSTOMER, and BLOCK decisions.
- **Eight Deterministic Business Rules:** Formulated specifically for Wells Fargo's banking rails, enforcing strict precedence where unknown and revoked agents are rejected before any permission checks.
- **Calibrated Transaction Ceiling (₹10,000):** Establishes an initial risk containment boundary to guard against automated liquidity drain while accommodating routine utility payments.
- **Verifiable Agent Revocation:** Implements Wells Fargo's real-world regulatory mandate (reported in *American Banker*) requiring customers to preserve verifiable, timestamped proof of revoked third-party AI access. Revoked agents are never deleted.
- **Immutable Persistent Audit Trail:** Every request, decision, registration, and revocation is recorded with a unique UUID request ID and timestamp in `audit_logs.json`, surviving application restarts.
- **Automated Verification Suite:** Six rigorous test scenarios executed directly against the live decision engine via both CLI unittest and an interactive web testing portal.
- **Two-Page Executive PDF Report:** Auto-compiled using ReportLab Platypus, strictly calibrated to span exactly two pages with tables, citations, and risk analyses.
- **Modern Responsive UI/UX:** Styled in an executive dark navy theme (`#0A192F`) with Wells Fargo red (`#D12640`) and gold (`#FFB81C`) branding, white cards, and full mobile adaptability.

---

## 3. Technology Stack

- **Backend:** Python 3.10+ & Flask Framework
- **Frontend:** Semantic HTML5, Custom CSS3, Asynchronous Vanilla JavaScript (AJAX)
- **Persistence:** Local JSON flat files (`agents.json`, `audit_logs.json`) — Zero external cloud databases or paid APIs required.
- **PDF Generation:** ReportLab Platypus
- **Testing:** Python standard `unittest` and `pytest` compatible

---

## 4. Folder Structure

```
agent-gatekeeper/
│
├── app.py                         # Flask web application controller & API routes
├── decision_engine.py             # Core 8-rule deterministic policy evaluation engine
├── storage.py                     # Persistent JSON storage & audit manager
├── generate_report.py             # Two-page executive PDF report compiler
├── requirements.txt               # Python package dependencies
├── agents.json                    # Persistent agent registry (active & revoked)
├── audit_logs.json                # Immutable audit ledger of all requests and events
├── README.md                      # Comprehensive project documentation
├── PROMPTS.md                     # AI collaboration & student verification log
├── .gitignore                     # Git ignore specifications
│
├── report/
│   └── Agent_Gatekeeper_Report.pdf  # Generated 2-page academic assignment report
│
├── tests/
│   └── test_decision_engine.py    # Automated test suite for the 6 required scenarios
│
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Master layout with sidebar & live clock
│   ├── dashboard.html             # Executive summary & metrics cards
│   ├── request.html               # Request evaluation form with autofill chips
│   ├── register.html              # Agent onboarding & permission assignment
│   ├── agents.html                # Agent directory with revocation triggers
│   ├── revoke.html                # Dedicated compliance revocation gateway
│   ├── audit_logs.html            # Searchable & filterable audit ledger
│   ├── rules.html                 # Business policy matrix & threshold explanation
│   ├── tests.html                 # Interactive test suite execution dashboard
│   └── about.html                 # Architecture overview & viva preparation
│
└── static/                        # Static UI assets
    ├── css/
    │   └── style.css              # Custom dark navy & Wells Fargo theme stylesheet
    └── js/
        └── app.js                 # Live clock & UI interactivity scripts
```

---

## 5. Installation & Setup Instructions

The application runs entirely locally on standard Python without external cloud dependencies or paid API keys.

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd c:\Users\HP\Downloads\agent-gatekeeper
```

### Step 2: (Optional) Create and Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```
*(Dependencies: `Flask`, `reportlab`, `pytest`)*

### Step 4: Run the Application Server
```powershell
python app.py
```

### Step 5: Open in Your Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. How to Run the Automated Tests

The six mandatory test scenarios can be executed via terminal or through the web interface.

### Running via Terminal (CLI):
```powershell
python tests/test_decision_engine.py
```
Or with pytest:
```powershell
pytest tests/test_decision_engine.py -v
```

### Running via Web Interface:
1. Start `app.py`.
2. Open `http://127.0.0.1:5000/tests` in your browser.
3. Click the **"🧪 Run All 6 Scenarios Now"** button.
4. The page will dynamically execute `decision_engine.py` against all six test cases and render a detailed execution table showing inputs, expected outputs, actual outputs, and `✔ PASS` badges.

---

## 7. How to Generate the PDF Report

The 2-page executive report can be compiled at any time using:
```powershell
python generate_report.py
```
Or by clicking the **"📥 Download PDF Report"** button in the application sidebar.

---

## 8. Explanation of the Decision Engine & Business Rules

The decision engine in `decision_engine.py` applies 8 business rules in strict precedence order:

1. **RULE 1 (Unknown Agent):** If the agent is not registered for the customer, immediately return **BLOCK**.
2. **RULE 2 (Revoked Agent):** If the agent's status is `REVOKED`, return **BLOCK** unconditionally.
3. **RULE 3 (Active Authorization):** Verifies that the agent is in `ACTIVE` standing.
4. **RULE 7 (Permission Scope):** If the requested action is not in the agent's registered `permitted_actions`, return **BLOCK** (Principle of Least Privilege).
5. **RULE 4 (Read-Only Actions):** If the action is `View balance`, return **ALLOW**.
6. **RULE 6 (Transaction Limit):** If the transaction amount exceeds ₹10,000, return **ASK CUSTOMER** for step-up verification.
7. **RULE 5 (Customer Confirmation for Sensitive Actions):** Sensitive actions (`Pay a bill`, `Transfer money`) within the ₹10,000 limit still require affirmative customer confirmation (**ASK CUSTOMER**).
8. **RULE 8 (Auditability & Immutability):** Every evaluation and event is recorded into `audit_logs.json`.

---

## 9. GitHub & Academic Integrity Instructions

To prepare this project for your GitHub repository and demonstrate genuine personal proof-of-work:

1. **Initialize Git Repository:**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit: Agent Gatekeeper architecture for Wells Fargo"
   ```
2. **Push to GitHub:**
   - Create a new private/public repository on [GitHub](https://github.com).
   - Link and push your commits:
     ```powershell
     git remote add origin https://github.com/YOUR_USERNAME/agent-gatekeeper.git
     git branch -M main
     git push -u origin main
     ```
3. **Demonstrate Genuine Development Across Multiple Days:**
   - Make at least 5 meaningful commits across at least 3 distinct days.
   - Example commit sequence:
     - *Day 1:* "Implement decision engine business rules and persistent storage"
     - *Day 1:* "Add Flask routes, dashboard UI, and registration view"
     - *Day 2:* "Implement agent revocation modal and Wells Fargo compliance workflow"
     - *Day 2:* "Add automated unit tests for 6 core assignment scenarios"
     - *Day 3:* "Calibrate 2-page ReportLab PDF generation and finalize documentation"
4. **Session Screenshots & Video Recording:**
   - Capture screenshots of your Antigravity / IDE sessions displaying your system clock and enrolment number.
   - Record a 2-minute demonstration video showing:
     - Registering a new agent.
     - Evaluating a `View balance` request (**ALLOW**).
     - Evaluating an over-limit transfer (**ASK CUSTOMER**).
     - Revoking an agent and proving subsequent requests are **BLOCKED**.
     - Running the 6 test scenarios.
