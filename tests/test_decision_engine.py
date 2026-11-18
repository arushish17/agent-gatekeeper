
"""
Automated Unit and Integration Tests for Agent Gatekeeper.

Runs the six required assignment scenarios in isolated temporary storage.
Also tests the additional bill-payment and money-transfer policy conditions.
"""

import json
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import storage
from decision_engine import evaluate_request


def run_assignment_scenarios():
    """Run the six required assignment scenarios in isolated storage."""

    test_agents = [
        {
            "agent_id": "TEST-AGT-001",
            "customer_id": "CUST-TEST-100",
            "customer_name": "Test Customer Alpha",
            "agent_name": "FinanceActiveBot",
            "registration_timestamp": "2026-11-14 09:00:00",
            "permitted_actions": [
                "View balance", "Pay a bill", "Transfer money"
            ],
            "transaction_limit": 10000.0,
            "bill_payment_pre_authorized": True,
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
            "bill_payment_pre_authorized": False,
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
            "bill_payment_pre_authorized": False,
            "status": "REVOKED",
            "revoked_at": "2026-11-10 14:00:00",
            "revocation_reason": "Customer security audit",
        }
    ]

    orig_agents_path = storage.AGENTS_FILE
    orig_audit_path = storage.AUDIT_LOGS_FILE
    results = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        agents_file = os.path.join(tmp_dir, "test_agents.json")
        audit_file = os.path.join(tmp_dir, "test_audit_logs.json")

        with open(agents_file, "w", encoding="utf-8") as file:
            json.dump(test_agents, file, indent=2)

        try:
            storage.set_storage_paths(agents_file, audit_file)

            scenarios = [
                {
                    "customer_id": "CUST-TEST-100",
                    "agent_name": "FinanceActiveBot",
                    "action": "View balance",
                    "amount": 0.0,
                    "description": "Automated balance check",
                    "expected": "ALLOW",
                    "title": "Registered Active Agent - Read-Only Action",
                    "scenario": "Active registered agent performing a permitted balance check."
                },
                {
                    "customer_id": "CUST-TEST-999",
                    "agent_name": "ShadowHackerAI",
                    "action": "Transfer money",
                    "amount": 500.0,
                    "description": "Unregistered agent transfer attempt",
                    "expected": "BLOCK",
                    "title": "Unknown Agent Attempt",
                    "scenario": "Unknown agent attempting a money transfer."
                },
                {
                    "customer_id": "CUST-TEST-100",
                    "agent_name": "FinanceActiveBot",
                    "action": "Transfer money",
                    "amount": 15000.0,
                    "description": "High-value vendor transfer",
                    "expected": "ASK CUSTOMER",
                    "title": "Transaction Exceeding Threshold",
                    "scenario": "Active agent attempting a ₹15,000 money transfer."
                },
                {
                    "customer_id": "CUST-TEST-100",
                    "agent_name": "FinanceActiveBot",
                    "action": "Pay a bill",
                    "amount": 2500.0,
                    "description": "Pre-authorised electric utility payment",
                    "expected": "ALLOW",
                    "title": "Pre-authorised Bill Payment Below Limit",
                    "scenario": "Active agent making a ₹2,500 bill payment with explicit pre-authorisation."
                },
                {
                    "customer_id": "CUST-TEST-300",
                    "agent_name": "RevokedZombieBot",
                    "action": "View balance",
                    "amount": 0.0,
                    "description": "Revoked agent balance check attempt",
                    "expected": "BLOCK",
                    "title": "Revoked Agent Block Enforcement",
                    "scenario": "Revoked agent attempting a read-only inquiry."
                },
                {
                    "customer_id": "CUST-TEST-200",
                    "agent_name": "ReadOnlyBot",
                    "action": "Transfer money",
                    "amount": 500.0,
                    "description": "Out-of-scope transfer attempt",
                    "expected": "BLOCK",
                    "title": "Action Outside Permitted Scope",
                    "scenario": "Read-only agent attempting a money transfer."
                }
            ]

            for number, scenario in enumerate(scenarios, start=1):
                result = evaluate_request(
                    customer_id=scenario["customer_id"],
                    agent_name=scenario["agent_name"],
                    action=scenario["action"],
                    amount=scenario["amount"],
                    description=scenario["description"],
                    record_audit=False
                )

                passed = result["decision"] == scenario["expected"]

                results.append({
                    "test_number": number,
                    "title": scenario["title"],
                    "scenario": scenario["scenario"],
                    "inputs": {
                        "customer_id": scenario["customer_id"],
                        "agent_name": scenario["agent_name"],
                        "action": scenario["action"],
                        "amount": scenario["amount"]
                    },
                    "expected": scenario["expected"],
                    "actual": result["decision"],
                    "rule": (
                        f"{result['rule_number']}: {result['rule_name']}"
                    ),
                    "reason": result["reason"],
                    "status": "PASS" if passed else "FAIL"
                })

        finally:
            storage.set_storage_paths(orig_agents_path, orig_audit_path)

    return results


class TestDecisionEngine(unittest.TestCase):
    """Tests for the six assignment scenarios and additional policy rules."""

    def setUp(self):
        self.original_agents_path = storage.AGENTS_FILE
        self.original_audit_path = storage.AUDIT_LOGS_FILE
        self.temp_dir = tempfile.TemporaryDirectory()

        self.agents_file = os.path.join(
            self.temp_dir.name, "agents.json"
        )
        self.audit_file = os.path.join(
            self.temp_dir.name, "audit_logs.json"
        )

        agents = [
            {
                "agent_id": "TEST-PREAUTH",
                "customer_id": "CUST-PREAUTH",
                "customer_name": "Preauthorised Customer",
                "agent_name": "PreauthorisedBot",
                "permitted_actions": [
                    "View balance", "Pay a bill", "Transfer money"
                ],
                "transaction_limit": 10000.0,
                "bill_payment_pre_authorized": True,
                "status": "ACTIVE"
            },
            {
                "agent_id": "TEST-NO-PREAUTH",
                "customer_id": "CUST-NO-PREAUTH",
                "customer_name": "Customer Without Preauthorisation",
                "agent_name": "RegularBot",
                "permitted_actions": [
                    "View balance", "Pay a bill", "Transfer money"
                ],
                "transaction_limit": 10000.0,
                "bill_payment_pre_authorized": False,
                "status": "ACTIVE"
            }
        ]

        with open(self.agents_file, "w", encoding="utf-8") as file:
            json.dump(agents, file, indent=2)

        storage.set_storage_paths(self.agents_file, self.audit_file)

    def tearDown(self):
        storage.set_storage_paths(
            self.original_agents_path,
            self.original_audit_path
        )
        self.temp_dir.cleanup()

    def test_all_six_scenarios(self):
        results = run_assignment_scenarios()

        self.assertEqual(len(results), 6)

        for result in results:
            with self.subTest(scenario=result["title"]):
                self.assertEqual(
                    result["actual"],
                    result["expected"],
                    (
                        f"Test {result['test_number']} failed: "
                        f"Expected {result['expected']}, "
                        f"got {result['actual']}. "
                        f"Reason: {result['reason']}"
                    )
                )
                self.assertEqual(result["status"], "PASS")

    def test_bill_payment_without_pre_authorisation_asks_customer(self):
        result = evaluate_request(
            "CUST-NO-PREAUTH",
            "RegularBot",
            "Pay a bill",
            2500.0,
            record_audit=False
        )
        self.assertEqual(result["decision"], "ASK CUSTOMER")

    def test_pre_authorised_bill_payment_within_limit_is_allowed(self):
        result = evaluate_request(
            "CUST-PREAUTH",
            "PreauthorisedBot",
            "Pay a bill",
            2500.0,
            record_audit=False
        )
        self.assertEqual(result["decision"], "ALLOW")

    def test_pre_authorised_bill_payment_above_limit_asks_customer(self):
        result = evaluate_request(
            "CUST-PREAUTH",
            "PreauthorisedBot",
            "Pay a bill",
            12000.0,
            record_audit=False
        )
        self.assertEqual(result["decision"], "ASK CUSTOMER")

    def test_money_transfer_within_limit_still_asks_customer(self):
        result = evaluate_request(
            "CUST-PREAUTH",
            "PreauthorisedBot",
            "Transfer money",
            500.0,
            record_audit=False
        )
        self.assertEqual(result["decision"], "ASK CUSTOMER")


if __name__ == "__main__":
    unittest.main()
