# Agent Gatekeeper - Demo Guide

## 1. Start the Application
Open PowerShell in the project folder and run:

python app.py

Open http://127.0.0.1:5000 in your browser.

## 2. Demonstrate Agent Registration
- Open the registration page.
- Enter the demo agent details.
- Select the bill payment pre-authorisation checkbox only when intended.
- Submit the registration form.

## 3. Demonstrate Authorization Decisions
Show these policy examples:
- Registered agent: permitted read-only balance check is allowed.
- Pre-authorised bill payment within the configured limit: allowed.
- Bill payment without pre-authorisation: customer approval required.
- Bill payment above the configured limit: customer approval required.
- Money transfer: customer approval always required.
- Unknown, revoked, inactive, or out-of-scope agent: blocked.

## 4. Run Automated Tests
Run:

python -m pytest -v

The test suite checks decision-engine rules and application workflows.

## 5. Project Report
The generated project report is available at:

report/Agent_Gatekeeper_Report.pdf

Note: This is an academic prototype. Its ₹10,000 threshold is a demonstration setting, not an actual Wells Fargo banking policy.
