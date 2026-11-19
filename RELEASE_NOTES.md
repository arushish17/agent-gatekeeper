# Agent Gatekeeper - Release Notes

## Project Status
Academic prototype completed for demonstration and evaluation.

## Main Features
- Agent registration and permission management.
- Agent revocation.
- Bill payment pre-authorisation.
- Transaction authorization decisions.
- Audit logging and dashboard functionality.
- PDF report generation.

## Authorization Rules
- Pre-authorised bill payments within the effective limit: ALLOW.
- Bill payments without pre-authorisation: ASK CUSTOMER.
- Bill payments above the effective limit: ASK CUSTOMER.
- Money transfers: ASK CUSTOMER.
- Unknown, revoked, inactive, or out-of-scope agents: BLOCK.
- Permitted read-only balance checks: ALLOW.

## Verification
Automated test suite previously completed successfully:
12 passed, 21 subtests passed.

## Important Note
The ₹10,000 threshold is an academic demonstration setting and does not represent an actual Wells Fargo banking policy.

## Project Deliverables
Refer to DEMO_GUIDE.md and SUBMISSION_CHECKLIST.md for demonstration and submission instructions.
