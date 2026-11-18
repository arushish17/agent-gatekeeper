"""
tests/test_decision_engine.py - Automated Unit & Integration Tests for Agent Gatekeeper
Implements the six required assignment test scenarios against the actual decision engine.
Can be executed via standard unittest/pytest and invoked programmatically by Flask web route.
Ensures complete test data isolation without modifying production agents.json or audit_logs.json.
"""

import json
import os
import sys
import tempfile
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import storage
from decision_engine import evaluate_request


def run_assignment_scenarios():
    """
    Executes all six required test cases deterministically in a temporary isolated
    sandbox without modifying permanent customer records in agents.json or audit_logs.json.
    
    Returns:
        list of dict: Detailed execution results for each test scenario.
    """
    # Define dedicated test agents in a clean sandbox context
    test_agents = [
        {
            "agent_id": "TEST-AGT-001",
            "customer_id": "CUST-TEST-100",
            "customer_name": "Test Customer Alpha",
            "agent_name": "FinanceActiveBot",
            "registration_timestamp": "2026-11-14 09:00:00",
            "permitted_actions": ["View balance", "Pay a bill", "Transfer money"],
            "transaction_limit": 10000.0,
            "status": "ACTIVE",
            "revoked_at": None,
            "revocation_reason": None
        },
        {
            "agent_id": "TEST-AGT-002",
            "customer_id": "CUST-TEST-200",
            "customer_name": "Test Customer Beta",
            "agent_name": "ReadOnlyBot",
            "registration_timestamp": "2026-11-14 09:15:00",
            "permitted_actions": ["View balance"],
            "transaction_limit": 10000.0,
            "status": "ACTIVE",
            "revoked_at": None,
            "revocation_reason": None
        },
        {
            "agent_id": "TEST-AGT-003",
            "customer_id": "CUST-TEST-300",
            "customer_name": "Test Customer Gamma",
            "agent_name": "RevokedZombieBot",
            "registration_timestamp": "2026-11-01 10:00:00",
            "permitted_actions": ["View balance", "Transfer money"],
            "transaction_limit": 10000.0,
            "status": "REVOKED",
            "revoked_at": "2026-11-10 14:00:00",
            "revocation_reason": "Customer security audit - third party AI revocation proof filed"
        }
    ]

    orig_agents_path = storage.AGENTS_FILE
    orig_audit_path = storage.AUDIT_LOGS_FILE

    results = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_agents_file = os.path.join(tmp_dir, "test_agents.json")
        tmp_audit_file = os.path.join(tmp_dir, "test_audit_logs.json")

        with open(tmp_agents_file, "w", encoding="utf-8") as f:
            json.dump(test_agents, f, indent=2)

        try:
            storage.set_storage_paths(tmp_agents_file, tmp_audit_file)

            # -------------------------------------------------------------
            # TEST 1: Known registered active agent performing read-only action
            # -------------------------------------------------------------
            res1 = evaluate_request(
                customer_id="CUST-TEST-100",
                agent_name="FinanceActiveBot",
                action="View balance",
                amount=0.0,
                description="Automated balance check before daily financial brief",
                record_audit=False
            )
            passed1 = (res1["decision"] == "ALLOW")
            results.append({
                "test_number": 1,
                "title": "Registered Active Agent - Read-Only Action",
                "scenario": "Known registered active agent (FinanceActiveBot) performing safe 'View balance'.",
                "inputs": {"customer_id": "CUST-TEST-100", "agent_name": "FinanceActiveBot", "action": "View balance", "amount": 0.0},
                "expected": "ALLOW",
                "actual": res1["decision"],
                "rule": f"{res1['rule_number']}: {res1['rule_name']}",
                "reason": res1["reason"],
                "status": "PASS" if passed1 else "FAIL"
            })

            # -------------------------------------------------------------
            # TEST 2: Unknown agent attempting an action
            # -------------------------------------------------------------
            res2 = evaluate_request(
                customer_id="CUST-TEST-999",
                agent_name="ShadowHackerAI",
                action="Transfer money",
                amount=500.0,
                description="Attempted balance drain from unverified autonomous bot",
                record_audit=False
            )
            passed2 = (res2["decision"] == "BLOCK")
            results.append({
                "test_number": 2,
                "title": "Unknown Agent Attempt",
                "scenario": "Unknown agent (ShadowHackerAI) attempting money transfer for unregistered customer.",
                "inputs": {"customer_id": "CUST-TEST-999", "agent_name": "ShadowHackerAI", "action": "Transfer money", "amount": 500.0},
                "expected": "BLOCK",
                "actual": res2["decision"],
                "rule": f"{res2['rule_number']}: {res2['rule_name']}",
                "reason": res2["reason"],
                "status": "PASS" if passed2 else "FAIL"
            })

            # -------------------------------------------------------------
            # TEST 3: Registered active agent transaction ABOVE configured limit
            # -------------------------------------------------------------
            res3 = evaluate_request(
                customer_id="CUST-TEST-100",
                agent_name="FinanceActiveBot",
                action="Transfer money",
                amount=15000.0,  # Exceeds ₹10,000 threshold
                description="High-value international vendor wire transfer",
                record_audit=False
            )
            passed3 = (res3["decision"] == "ASK CUSTOMER")
            results.append({
                "test_number": 3,
                "title": "Transaction Exceeding Threshold (Above Limit)",
                "scenario": "Registered active agent attempting ₹15,000 transfer, exceeding ₹10,000 limit.",
                "inputs": {"customer_id": "CUST-TEST-100", "agent_name": "FinanceActiveBot", "action": "Transfer money", "amount": 15000.0},
                "expected": "ASK CUSTOMER",
                "actual": res3["decision"],
                "rule": f"{res3['rule_number']}: {res3['rule_name']}",
                "reason": res3["reason"],
                "status": "PASS" if passed3 else "FAIL"
            })

            # -------------------------------------------------------------
            # TEST 4: Registered active agent transaction BELOW configured limit
            # -------------------------------------------------------------
            res4 = evaluate_request(
                customer_id="CUST-TEST-100",
                agent_name="FinanceActiveBot",
                action="Pay a bill",
                amount=2500.0,  # Below ₹10,000 threshold, but sensitive financial operation
                description="Routine electric utility payment",
                record_audit=False
            )
            passed4 = (res4["decision"] == "ASK CUSTOMER")
            results.append({
                "test_number": 4,
                "title": "Sensitive Action Below Limit (Mandatory Customer Approval)",
                "scenario": "Registered active agent attempting ₹2,500 bill payment (sensitive action below limit).",
                "inputs": {"customer_id": "CUST-TEST-100", "agent_name": "FinanceActiveBot", "action": "Pay a bill", "amount": 2500.0},
                "expected": "ASK CUSTOMER",
                "actual": res4["decision"],
                "rule": f"{res4['rule_number']}: {res4['rule_name']}",
                "reason": res4["reason"],
                "status": "PASS" if passed4 else "FAIL"
            })

            # -------------------------------------------------------------
            # TEST 5: Revoked agent attempting an action
            # -------------------------------------------------------------
            res5 = evaluate_request(
                customer_id="CUST-TEST-300",
                agent_name="RevokedZombieBot",
                action="View balance",
                amount=0.0,
                description="Revoked agent attempting read-only balance check",
                record_audit=False
            )
            passed5 = (res5["decision"] == "BLOCK")
            results.append({
                "test_number": 5,
                "title": "Revoked Agent Block Enforcement",
                "scenario": "Permanently revoked agent (RevokedZombieBot) attempting even a read-only inquiry.",
                "inputs": {"customer_id": "CUST-TEST-300", "agent_name": "RevokedZombieBot", "action": "View balance", "amount": 0.0},
                "expected": "BLOCK",
                "actual": res5["decision"],
                "rule": f"{res5['rule_number']}: {res5['rule_name']}",
                "reason": res5["reason"],
                "status": "PASS" if passed5 else "FAIL"
            })

            # -------------------------------------------------------------
            # TEST 6: Action outside agent's registered permissions (Least Privilege)
            # -------------------------------------------------------------
            res6 = evaluate_request(
                customer_id="CUST-TEST-200",
                agent_name="ReadOnlyBot",
                action="Transfer money",
                amount=500.0,
                description="Agent registered exclusively for 'View balance' attempting 'Transfer money'",
                record_audit=False
            )
            passed6 = (res6["decision"] == "BLOCK")
            results.append({
                "test_number": 6,
                "title": "Action Outside Permitted Scope (Least Privilege)",
                "scenario": "Active agent registered only for 'View balance' attempting 'Transfer money'.",
                "inputs": {"customer_id": "CUST-TEST-200", "agent_name": "ReadOnlyBot", "action": "Transfer money", "amount": 500.0},
                "expected": "BLOCK",
                "actual": res6["decision"],
                "rule": f"{res6['rule_number']}: {res6['rule_name']}",
                "reason": res6["reason"],
                "status": "PASS" if passed6 else "FAIL"
            })

        finally:
            # Restore original storage file paths
            storage.set_storage_paths(orig_agents_path, orig_audit_path)

    return results


class TestDecisionEngine(unittest.TestCase):
    """Unittest test suite executing the 6 core scenarios."""

    def test_all_six_scenarios(self):
        results = run_assignment_scenarios()
        self.assertEqual(len(results), 6)
        for res in results:
            with self.subTest(scenario=res["title"]):
                self.assertEqual(
                    res["actual"],
                    res["expected"],
                    f"Test {res['test_number']} Failed: Expected {res['expected']}, Got {res['actual']}. Reason: {res['reason']}"
                )
                self.assertEqual(res["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
