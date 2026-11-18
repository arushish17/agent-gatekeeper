# PROMPTS & AI COLLABORATION LOG
## Project: Agent Gatekeeper (Wells Fargo AI Permission Rail)
**Student Enrolment Number:** `PGD202564166`  
**Target Enterprise Sector:** Banking (`Wells Fargo` — Determined by Last Digit `6`)  
**Technology Stack:** Python 3, Flask, HTML5, CSS3, JavaScript, JSON Storage, ReportLab, Unittest  

---

## 1. Initial Prompt & Problem Formulation

### Prompt Given to AI Coding Assistant:
> "Act as a senior full-stack developer, UI/UX designer, software architect and programming tutor. Build a complete, functional academic project called **Agent Gatekeeper** for my university assignment.
> 
> IMPORTANT: Before starting development, ask me for my enrolment number. Use its LAST DIGIT to select the correct company:
> - 0–3: Airline (Delta Air Lines)
> - 4–6: Bank (Wells Fargo)
> - 7–9: Online store
> 
> Enrolment provided: **PGD202564166** (Last digit: 6 -> Wells Fargo).
> 
> Build a working application with functional features, persistent JSON storage, 8 business rules, audit logging, agent registration, agent revocation, automated tests for 6 specific scenarios, a strict 2-page PDF report citing American Banker and OfficeChai, and a comprehensive viva teaching guide."

---

## 2. Architectural Design & Step-by-Step Evolution

The project architecture was developed across four clear layers:

1. **Deterministic Decision Engine (`decision_engine.py`):**
   - Implemented 8 distinct business rules reflecting Wells Fargo's banking policies.
   - Enforced strict precedence order: **Rule 1 (Unknown Agent)** and **Rule 2 (Revoked Agent)** are evaluated before any permission or action checks.
   - Applied the Principle of Least Privilege: actions outside registered scope are blocked under Rule 7.
   - Configured an initial transaction limit of ₹10,000 for retail debit safety.

2. **Persistent Storage Layer (`storage.py`):**
   - Built zero-cloud, lightweight local storage using `agents.json` and `audit_logs.json`.
   - Guaranteed permanent retention of revoked agents with timestamped justification (vital for Wells Fargo's legal compliance).
   - Designed auto-generation of unique Agent IDs (`WF-AGT-XXX`) and UUID-backed Request IDs (`REQ-YYYYMMDD-XXXXXX`).

3. **Application Controller & Web UI (`app.py`, `templates/`, `static/`):**
   - Implemented 9 distinct navigation sections: Dashboard, Check Request, Register Agent, Manage Agents, Revoke Agent, Audit Logs, Rules & Policies, Test Scenarios, and About Project.
   - Applied an executive dark navy theme (`#0A192F`) with Wells Fargo red (`#D12640`) and gold (`#FFB81C`) branding.
   - Color-coded decision banners: Green for **ALLOW**, Orange for **ASK CUSTOMER**, and Red for **BLOCK**.

4. **Automated Testing & 2-Page Executive PDF Report:**
   - Implemented `tests/test_decision_engine.py` validating all 6 core scenarios with zero mocks.
   - Engineered `generate_report.py` using ReportLab Platypus with a dynamic two-pass canvas (`NumberedCanvas`) to strictly guarantee a 2-page document.

---

## 3. What the Coding Agent Generated

- **Backend Logic:**
  - `app.py`: Full Flask application with routes, context processors, flash alerts, and AJAX API endpoints.
  - `decision_engine.py`: 8-rule deterministic banking evaluation engine.
  - `storage.py`: JSON CRUD manager, metrics calculator, and audit event logger.
  - `generate_report.py`: Programmatic PDF compiler generating `report/Agent_Gatekeeper_Report.pdf`.
  - `tests/test_decision_engine.py`: Test suite for the 6 assignment scenarios.

- **Frontend Assets:**
  - `templates/base.html`: Master layout with sidebar navigation, live clock, and student enrolment banner.
  - `templates/dashboard.html`: Executive metrics dashboard with counters for ALLOW, ASK CUSTOMER, and BLOCK.
  - `templates/request.html`: Interactive request form with 6 quick autofill test scenario buttons.
  - `templates/register.html`: Agent onboarding portal with permission checklists and transaction ceilings.
  - `templates/agents.html`: Directory table with live badges, revocation details, and modal confirmation.
  - `templates/revoke.html`: Dedicated compliance revocation interface detailing the Wells Fargo precedent.
  - `templates/audit_logs.html`: Filterable and searchable persistent audit log with inspection modal.
  - `templates/rules.html`: Plain-language explanation of all 8 rules and the ₹10,000 threshold justification.
  - `templates/tests.html`: Live interactive testing dashboard with an AJAX "Run All 6 Tests" button.
  - `templates/about.html`: Architectural breakdown, student metadata, and viva preparation.
  - `static/css/style.css`: Comprehensive responsive styles with custom typography and color codes.
  - `static/js/app.js`: Live clock, mobile navigation drawer, and UI animations.

- **Data & Configuration:**
  - `agents.json`: Pre-seeded with realistic baseline active and revoked agent profiles.
  - `audit_logs.json`: Pre-seeded audit history preserving system events.
  - `requirements.txt`: Python dependencies (`Flask`, `reportlab`, `pytest`).
  - `.gitignore`: Production-ready Git ignore file.

---

## 4. What I Personally Checked (Student Verification Section)

*Please record your personal verification actions here during testing:*

- [ ] Verified that my enrolment number `PGD202564166` ends in digit `6`, correctly selecting **Wells Fargo (Bank)**.
- [ ] Confirmed that all banking actions are domain-specific (`View balance`, `Pay a bill`, `Transfer money`).
- [ ] Started the Flask server locally at `http://127.0.0.1:5000` and navigated through all 9 sections.
- [ ] Submitted a test request through the Check Agent Request form and verified that the output card renders with correct colors and rule numbers.
- [ ] Tested registering a new agent and verified that it appeared immediately in `agents.json` and on the Manage Agents page.
- [ ] Tested revoking an active agent and verified that:
  - The status turned to `REVOKED` with a timestamp.
  - Subsequent requests from that agent immediately returned `BLOCK` under Rule 2.
  - The agent was preserved in `agents.json` rather than deleted.
- [ ] Ran the automated test suite via command line (`python tests/test_decision_engine.py`) and through the web UI (`/tests`), confirming that all 6 tests returned `PASS`.
- [ ] Opened `report/Agent_Gatekeeper_Report.pdf` and confirmed it spans exactly 2 pages with headers, footers, tables, and citations.
- [ ] Verified that audit records in `audit_logs.json` remained intact after restarting the Flask application.

---

## 5. What I Personally Changed or Improved (Student Contribution Section)

*Document any personal customizations, styling refinements, or additional edge cases you added:*

- *[Student contribution placeholder — add your own notes, e.g.:]*
  - *Adjusted transaction limit threshold descriptions or tested additional amounts.*
  - *Customized UI color shades or added additional sample agents for testing.*
  - *Reviewed and personalized viva question explanations in the About section.*
