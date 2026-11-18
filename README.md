# Agent Gatekeeper: Security & Permission-Management Rail

**University Assignment Project — Enterprise AI Agent Governance**

- **Target Enterprise:** Wells Fargo (Bank), selected using enrolment last digit `6`
- **Core Technologies:** Python, Flask, HTML5, CSS3, JavaScript, JSON Storage, ReportLab and Pytest
- **Project Type:** Academic prototype

---

## 1. Project Introduction

**Agent Gatekeeper** is an academic prototype of a security and permission-management gateway designed to control access by third-party AI agents to banking operations.

As customers increasingly use autonomous AI assistants for personal finance tasks, it is important to ensure that these agents can perform only authorised actions.

Agent Gatekeeper evaluates incoming agent requests against eight deterministic business rules and returns one of three decisions:

1. **ALLOW** – Permit an authorised and permitted action, such as viewing an account balance or making an explicitly pre-authorised bill payment within the configured limit.
2. **ASK CUSTOMER** – Pause a sensitive action and require customer confirmation, such as a money transfer or an over-limit transaction.
3. **BLOCK** – Reject requests from unknown or revoked agents, or requests outside the agent's permitted scope.

This project is an educational simulation and is not an official Wells Fargo product or production banking system.

## 2. Key Features

- **Dashboard:** Displays agent counts, request activity and decision statistics.
- **Eight Business Rules:** Enforces registration, active status, permissions, transaction limits and customer confirmation.
- **Transaction Threshold:** Uses ₹10,000 as the configurable demonstration threshold.
- **Agent Registration:** Allows agents to be registered with customer details and permitted actions.
- **Agent Revocation:** Revokes agent access while retaining the agent's record and revocation information.
- **Persistent Audit Trail:** Records requests, decisions, registrations and revocations in `audit_logs.json`.
- **Automated Tests:** Includes six assignment scenarios and an interactive test page.
- **PDF Report:** Generates a two-page executive report using ReportLab.
- **Responsive Interface:** Provides a dashboard and management pages using HTML, CSS and JavaScript.

## 3. Business Rules

The decision engine is designed around the following eight rules:

1. **Unknown Agent:** Block requests from agents not registered to the customer.
2. **Revoked Agent:** Block requests from revoked agents.
3. **Active Authorisation:** Verify that the agent is active.
4. **Read-Only Actions:** Allow permitted read-only actions such as viewing a balance.
5. **Customer Confirmation:** Require customer confirmation for money transfers and other sensitive actions.
6. **Transaction Limit:** Require customer confirmation for transactions exceeding ₹10,000.
7. **Permission Scope:** Block actions that are not included in the agent's permitted actions.
8. **Auditability:** Record every decision and important agent-management event.

### Intended payment policy

- Bill payments up to ₹10,000 may be allowed only when explicitly pre-authorised by the customer.
- Bill payments above ₹10,000 require customer confirmation.
- Money transfers require customer confirmation.
- Unknown agents, revoked agents and unauthorised actions are blocked.

The ₹10,000 threshold is a demonstration setting for this academic project, not a real Wells Fargo banking limit.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3 and Flask |
| Frontend | HTML5, CSS3 and JavaScript |
| Templates | Jinja2 |
| Storage | JSON files |
| PDF Generation | ReportLab |
| Testing | Pytest and Python unittest |

## 5. Project Structure

```text
agent-gatekeeper/
│
├── app.py
├── decision_engine.py
├── storage.py
├── generate_report.py
├── requirements.txt
├── agents.json
├── audit_logs.json
├── README.md
├── PROMPTS.md
├── .gitignore
│
├── report/
│   └── Agent_Gatekeeper_Report.pdf
│
├── screenshots/
│   └── Application and testing evidence
│
├── tests/
│   ├── test_decision_engine.py
│   └── test_full_system.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── request.html
│   ├── register.html
│   ├── agents.html
│   ├── revoke.html
│   ├── audit_logs.html
│   ├── rules.html
│   ├── tests.html
│   └── about.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## 6. Installation and Setup

The application runs locally and does not require paid APIs.

### Step 1: Navigate to the project directory

```powershell
cd C:\Users\HP\Downloads\agent-gatekeeper
```

### Step 2: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run the application

```powershell
python app.py
```

### Step 4: Open the application

Visit:

```text
http://127.0.0.1:5000
```

## 7. Running the Tests

Run the complete test suite from the project directory:

```powershell
python -m pytest tests/ -v
```

The assignment includes six core scenarios:

1. Registered active agent performing a permitted read-only action.
2. Unknown agent attempting an action.
3. Transaction exceeding the configured threshold.
4. Sensitive action requiring customer confirmation.
5. Revoked agent attempting an action.
6. Agent attempting an action outside its permitted scope.

The application also includes an interactive test page at:

```text
http://127.0.0.1:5000/tests
```

## 8. Generating the PDF Report

Generate the report using:

```powershell
python generate_report.py
```

The generated report is saved in:

```text
report/Agent_Gatekeeper_Report.pdf
```

## 9. GitHub Repository

The source code, documentation, tests, report and screenshots are maintained in the project repository:

https://github.com/arushish17/agent-gatekeeper

The repository documents the development and testing work for this academic assignment.

## 10. Project Scope and Limitations

- This is an academic prototype and not a production banking gateway.
- JSON files provide local persistence and are not a substitute for a secure banking database.
- The transaction threshold is configurable demonstration logic.
- Customer confirmation is simulated; no actual banking transaction is performed.
- The system does not connect to real Wells Fargo accounts or banking infrastructure.

---

**Project:** Agent Gatekeeper  
**Target Enterprise:** Wells Fargo  
**Purpose:** Demonstration of AI agent governance, access control, revocation and auditability.