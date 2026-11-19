# PROMPTS & AI COLLABORATION LOG
## Project: Agent Gatekeeper — Wells Fargo AI Permission Management Prototype

**Coding Agent Used:** Google Antigravity  
**Selected Company:** Wells Fargo  
**Enrolment Category:** Banking (selected using the last digit of the enrolment number)  
**Technology Stack:** Python 3, Flask, HTML5, CSS3, JavaScript, JSON Storage, ReportLab and Pytest

---

## 1. Initial Prompt and Problem Formulation

### Main Prompt Given to the AI Coding Assistant

I instructed Google Antigravity to act as a senior full-stack developer, UI/UX designer, software architect and programming tutor.

The main objective was to build a complete, functional academic project called **Agent Gatekeeper**, rather than a static design or demonstration mock-up.

The original prompt instructed the coding agent to:

- Use the last digit of my enrolment number to select the company for the assignment. My category was banking, so the selected company was Wells Fargo.
- Develop a working local application using Python, Flask, HTML, CSS and JavaScript.
- Use JSON files for persistent data storage.
- Build a dashboard displaying the project, company information and request statistics.
- Create a request-processing form accepting customer details, AI agent name, requested action and transaction amount.
- Implement three possible decisions: ALLOW, ASK CUSTOMER and BLOCK.
- Create 6–8 understandable business rules.
- Implement agent registration, permission management and revocation.
- Maintain timestamped audit records for requests, decisions, registrations and revocations.
- Implement six test scenarios using the actual decision engine.
- Generate a professional PDF report with a maximum length of two pages.
- Include project documentation, a README, automated tests and a suitable folder structure.
- Prepare the project for GitHub and explain the application so that I could demonstrate it during an academic assessment.

The original instructions also specified that the prototype must not connect to real bank accounts, payment systems or external banking services.

---

## 2. Architectural Design and Development

The project was developed using four main architectural components.

### 2.1 Decision Engine — `decision_engine.py`

The decision engine evaluates requests made by registered AI agents.

Its responsibilities include:

- Checking whether an agent is registered.
- Checking whether an agent has been revoked or is inactive.
- Checking the agent's permitted actions.
- Applying the transaction limit.
- Determining whether customer confirmation is required.
- Returning a decision with a rule number and explanation.
- Recording the decision in the audit log.

The system follows a rule-based approach so that decisions are consistent and understandable.

### 2.2 Storage Layer — `storage.py`

The storage component manages the application's JSON-based data.

Its responsibilities include:

- Registering agents.
- Finding and retrieving agent information.
- Recording agent permissions and transaction limits.
- Revoking agents while preserving their history.
- Recording audit events.
- Maintaining dashboard statistics.
- Supporting separate test data storage so automated tests do not modify normal application data.

### 2.3 Flask Application and User Interface — `app.py`

The Flask application connects the frontend to the backend logic.

It handles:

- Application routes.
- Agent registration and management.
- Request processing.
- Agent revocation.
- Audit log access.
- Test execution.
- Dashboard information.

The frontend uses HTML templates, CSS styling and JavaScript to provide a responsive interface.

### 2.4 Automated Testing and PDF Report

The project includes automated tests for decision-making and application functionality.

The test suite checks the decision engine, registration process, revocation lifecycle and other application features.

A two-page PDF report is included in the `report/` directory.

---

## 3. Business Policy Development

The original instructions required 6–8 business rules suitable for the selected banking company.

The project uses the following policy principles:

1. Unknown agents must be blocked.
2. Revoked agents must be blocked.
3. Only registered and active agents can make requests.
4. Read-only actions may be allowed when permission exists.
5. Sensitive financial actions may require customer confirmation.
6. Transactions above the configured limit require customer confirmation.
7. Actions outside the registered permission scope must be blocked.
8. All decisions and important events must be recorded with timestamps.

### Transaction Limit

The prototype uses an initial transaction threshold of **₹10,000**.

This is an academic demonstration setting used to illustrate how a bank could apply transaction controls. It is not represented as an actual Wells Fargo transaction policy.

### Additional Policy Refinement

The policy was further refined to distinguish between bill payments and money transfers:

- Bill payments up to ₹10,000 can be allowed when explicitly pre-authorised.
- Bill payments without pre-authorisation require customer confirmation.
- Bill payments above the effective limit require customer confirmation.
- Money transfers always require customer confirmation.
- Requests from unknown, revoked or inactive agents are blocked.

The effective transaction limit considers both the agent's configured limit and the application's global limit.

---

## 4. Follow-up Prompt: Registration and Test Data Isolation

During development, an initial automated test run reported two failures.

I provided the following follow-up instruction to Antigravity:

> My Python and packages are working. I ran:
>
> `python -m pytest tests/ -v`
>
> Result: 6 passed, 2 failed.
>
> Failures:
> 1. `test_02_agent_registration_lifecycle`: storage.register_agent() returned success=False.
> 2. `test_03_agent_revocation_lifecycle_and_rule_enforcement`: the test agent's View balance request returned BLOCK instead of ALLOW.
>
> Please inspect the actual code in storage.py, decision_engine.py, and tests/test_full_system.py.
>
> Fix the underlying registration and test data isolation problems. Ensure integration tests use a separate temporary test data directory and do not modify my real agents.json or audit_logs.json.
>
> Then rerun:
>
> `python -m pytest tests/ -v`
>
> Do not change the expected outcomes just to make tests pass. Do not claim success until all tests pass. Explain the fix in simple language and show the actual test results.

### Purpose of This Follow-up

The purpose was to fix the underlying problems instead of changing expected test outcomes.

It also required integration tests to use temporary test data so that test registration, revocation and audit events would not modify the application's normal local data.

---

## 5. What the Coding Agent Generated

The development work included the following components:

### Backend

- `app.py` — Flask application and routes.
- `decision_engine.py` — Rule-based request evaluation.
- `storage.py` — JSON storage and audit logging.

### Frontend

- HTML templates for the dashboard, request form, registration, agent management, audit logs, rules and test scenarios.
- CSS styles for the application interface.
- JavaScript for frontend interactions.

### Testing

- `tests/test_decision_engine.py` — Decision engine tests.
- `tests/test_full_system.py` — Application integration tests.

### Documentation and Submission Files

- `README.md` — Project introduction and instructions.
- `requirements.txt` — Python dependencies.
- `.gitignore` — Files excluded from Git tracking.
- `DEMO_GUIDE.md` — Demonstration instructions.
- `SUBMISSION_CHECKLIST.md` — Submission preparation checklist.
- `report/Agent_Gatekeeper_Report.pdf` — Two-page project report.

---

## 6. What I Personally Checked

The following checks were performed during project development:

- [x] Confirmed the banking category and selected Wells Fargo for the project.
- [x] Started the Flask application locally.
- [x] Opened the application dashboard in a browser.
- [x] Ran the automated test suite using pytest.
- [x] Reviewed the registration and permission workflow.
- [x] Reviewed the business policy, including pre-authorised bill payments and customer confirmation for money transfers.
- [x] Opened and inspected the generated PDF report.
- [x] Checked the Git repository and commit history.

### Automated Test Result

The latest recorded test run was:

`python -m pytest -v`

**Result: 12 passed, with 21 subtests passed.**

This result was recorded after the registration and test-isolation improvements.

---

## 7. My Decisions and Contributions

My contributions during the project included:

- Selecting Wells Fargo based on the banking category determined by my enrolment-number digit.
- Reviewing the banking-specific business rules.
- Developing the distinction between pre-authorised bill payments and payments requiring customer confirmation.
- Deciding that money transfers should always require customer confirmation in this prototype.
- Reviewing the ₹10,000 transaction threshold as an academic demonstration setting.
- Reviewing the automated test results rather than relying only on the application's displayed output.
- Asking the coding agent to fix registration and test-data isolation problems without changing expected outcomes.
- Reviewing the application and project documentation for the university submission.

The application was developed with AI coding assistance. I reviewed the requirements, guided the policy decisions, tested the application and checked the resulting project.

---

## 8. Academic Integrity Statement

Google Antigravity was used as an AI-assisted development tool.

This document records the main development instructions, follow-up debugging instruction, project architecture and verification work.

The purpose of the project is to demonstrate an understandable and testable prototype. The final application is an academic simulation and does not represent an operational Wells Fargo banking system.

I will be prepared to explain the decision engine, business rules, agent registration, revocation process, audit logging and automated tests during the assessment.

