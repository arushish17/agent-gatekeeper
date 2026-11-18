
"""
Comprehensive End-to-End System Integration Tests for Agent Gatekeeper.

Tests application routes, registration, revocation, decision scenarios,
audit persistence, AJAX test execution, and PDF report delivery.

Uses temporary storage to protect production data.
"""

import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import storage
from decision_engine import evaluate_request
from app import app


class FullSystemIntegrationTest(unittest.TestCase):

    def setUp(self):
        """Create isolated temporary storage for each test."""

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_agents = os.path.join(
            self.temp_dir.name, "test_agents.json"
        )
        self.temp_audit = os.path.join(
            self.temp_dir.name, "test_audit_logs.json"
        )

        self.orig_agents = storage.AGENTS_FILE
        self.orig_audit = storage.AUDIT_LOGS_FILE

        storage.set_storage_paths(
            self.temp_agents, self.temp_audit
        )
        storage.init_storage(seed_if_empty=True)

        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        """Restore original storage paths and remove temporary files."""

        storage.set_storage_paths(
            self.orig_agents, self.orig_audit
        )
        self.temp_dir.cleanup()

    def test_01_all_web_routes_render(self):
        """Checks that all nine application navigation pages return HTTP 200."""

        routes = [
            "/",
            "/request",
            "/register",
            "/agents",
            "/revoke",
            "/audit-logs",
            "/rules",
            "/tests",
            "/about"
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)

                self.assertEqual(
                    response.status_code,
                    200,
                    f"Route {route} failed."
                )
                self.assertIn(b"Wells Fargo", response.data)

    def test_02_agent_registration_lifecycle(self):
        """Tests registration, persistence, pre-authorisation, and duplicate rejection."""

        test_cust_id = "CUST-E2E-TEST"
        test_cust_name = "Kavita Rao"
        test_agent_name = "AutonomyDebitGuard"

        success, new_agent = storage.register_agent(
            customer_id=test_cust_id,
            customer_name=test_cust_name,
            agent_name=test_agent_name,
            permitted_actions=["View balance", "Pay a bill"],
            transaction_limit=8000.0,
            bill_payment_pre_authorized=True
        )

        self.assertTrue(
            success,
            f"Registration failed: {new_agent}"
        )
        self.assertEqual(new_agent["status"], "ACTIVE")
        self.assertIsNotNone(new_agent["agent_id"])
        self.assertTrue(
            new_agent["bill_payment_pre_authorized"]
        )

        retrieved = storage.find_agent(
            test_cust_id, test_agent_name
        )

        self.assertIsNotNone(retrieved)
        self.assertEqual(
            retrieved["customer_name"], test_cust_name
        )
        self.assertTrue(
            retrieved["bill_payment_pre_authorized"]
        )

        # Verify that pre-authorised bill payments within the agent's
        # ₹8,000 limit are allowed.
        result = evaluate_request(
            customer_id=test_cust_id,
            agent_name=test_agent_name,
            action="Pay a bill",
            amount=2500.0,
            record_audit=False
        )
        self.assertEqual(result["decision"], "ALLOW")

        # Duplicate registration must be rejected.
        duplicate_success, message = storage.register_agent(
            customer_id=test_cust_id,
            customer_name=test_cust_name,
            agent_name=test_agent_name,
            permitted_actions=["View balance"]
        )

        self.assertFalse(duplicate_success)

    def test_03_agent_revocation_lifecycle_and_rule_enforcement(self):
        """Tests that revoked agents are immediately blocked."""

        test_cust_id = "CUST-REV-TEST"
        test_agent_name = "ExpiringBot"

        reg_success, new_agent = storage.register_agent(
            customer_id=test_cust_id,
            customer_name="Sanjay Gupta",
            agent_name=test_agent_name,
            permitted_actions=["View balance", "Transfer money"],
            transaction_limit=10000.0
        )

        self.assertTrue(
            reg_success,
            f"Initial registration failed: {new_agent}"
        )

        agent = storage.find_agent(
            test_cust_id, test_agent_name
        )
        agent_id = agent["agent_id"]

        # Before revocation, balance checking should be allowed.
        result_before = evaluate_request(
            customer_id=test_cust_id,
            agent_name=test_agent_name,
            action="View balance",
            amount=0.0
        )

        self.assertEqual(result_before["decision"], "ALLOW")

        # Revoke the agent.
        success, revoked = storage.revoke_agent(
            agent_id=agent_id,
            reason="Customer initiated security revocation"
        )

        self.assertTrue(success)
        self.assertEqual(revoked["status"], "REVOKED")
        self.assertIsNotNone(revoked["revoked_at"])

        # Verify persisted revocation.
        agent_after = storage.find_agent_by_id(agent_id)
        self.assertEqual(agent_after["status"], "REVOKED")

        # After revocation, the request must be blocked under Rule 2.
        result_after = evaluate_request(
            customer_id=test_cust_id,
            agent_name=test_agent_name,
            action="View balance",
            amount=0.0
        )

        self.assertEqual(result_after["decision"], "BLOCK")
        self.assertEqual(result_after["rule_number"], "RULE 2")

    def test_04_six_test_scenarios_execution(self):
        """Tests all six required assignment scenarios."""

        from tests.test_decision_engine import run_assignment_scenarios

        results = run_assignment_scenarios()

        self.assertEqual(len(results), 6)

        for result in results:
            with self.subTest(scenario=result["title"]):
                self.assertEqual(
                    result["status"], "PASS",
                    f"Scenario failed: {result['title']}"
                )

    def test_05_ajax_api_run_tests(self):
        """Tests the POST /api/run-tests endpoint."""

        response = self.client.post("/api/run-tests")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertTrue(data["all_passed"])
        self.assertEqual(len(data["results"]), 6)

    def test_06_request_form_post_evaluation(self):
        """Tests submitting a read-only request through the web form."""

        form_data = {
            "customer_id": "CUST-64166",
            "agent_name": "FinancePilot AI",
            "action": "View balance",
            "amount": "0",
            "description": "Integration test check"
        }

        response = self.client.post(
            "/request", data=form_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ALLOW", response.data)
        self.assertIn(b"RULE 4", response.data)

    def test_07_pdf_report_download(self):
        """Tests PDF report delivery."""

        response = self.client.get("/download-report")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content_type, "application/pdf"
        )
        self.assertTrue(len(response.data) > 1000)

        response.close()


if __name__ == "__main__":
    unittest.main()
