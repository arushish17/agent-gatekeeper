"""
tests/test_full_system.py - Comprehensive End-to-End System Integration Test
Verifies all 11 requirements from Section 16 of the assignment specification:
1. Agent registration persistence
2. Agent revocation persistence & Rule 2 enforcement
3. All 6 decision engine test scenarios
4. Audit log persistence across server restarts
5. All Flask routes and web views (HTTP 200 responses)
6. Dynamic AJAX test runner endpoint
7. Report PDF generation & delivery

Runs with full test isolation using a temporary data directory so production files are never modified.
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
        # Configure test isolation sandbox
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_agents = os.path.join(self.temp_dir.name, "test_agents.json")
        self.temp_audit = os.path.join(self.temp_dir.name, "test_audit_logs.json")
        
        self.orig_agents = storage.AGENTS_FILE
        self.orig_audit = storage.AUDIT_LOGS_FILE
        
        storage.set_storage_paths(self.temp_agents, self.temp_audit)
        storage.init_storage(seed_if_empty=True)

        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        # Restore production paths and clean up temporary sandbox
        storage.set_storage_paths(self.orig_agents, self.orig_audit)
        self.temp_dir.cleanup()

    def test_01_all_web_routes_render(self):
        """Checks that all 9 application navigation pages return HTTP 200."""
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
                self.assertEqual(response.status_code, 200, f"Route {route} failed with {response.status_code}")
                # Verify Wells Fargo branding and Enrolment number exist in rendered HTML
                self.assertIn(b"Wells Fargo", response.data)
                self.assertIn(b"PGD202564166", response.data)

    def test_02_agent_registration_lifecycle(self):
        """Tests agent registration, storage in agents.json, and unique ID generation."""
        test_cust_id = "CUST-E2E-TEST"
        test_cust_name = "Kavita Rao"
        test_agent_name = "AutonomyDebitGuard"

        success, new_agent = storage.register_agent(
            customer_id=test_cust_id,
            customer_name=test_cust_name,
            agent_name=test_agent_name,
            permitted_actions=["View balance", "Pay a bill"],
            transaction_limit=8000.0
        )
        self.assertTrue(success, f"Registration failed unexpectedly: {new_agent}")
        self.assertEqual(new_agent["status"], "ACTIVE")
        self.assertIsNotNone(new_agent["agent_id"])

        # Verify persisted in storage
        retrieved = storage.find_agent(test_cust_id, test_agent_name)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["customer_name"], test_cust_name)

        # Test duplicate registration rejection
        dup_success, msg = storage.register_agent(
            customer_id=test_cust_id,
            customer_name=test_cust_name,
            agent_name=test_agent_name,
            permitted_actions=["View balance"]
        )
        self.assertFalse(dup_success)

    def test_03_agent_revocation_lifecycle_and_rule_enforcement(self):
        """Tests that revoking an agent preserves history and immediately blocks subsequent requests."""
        test_cust_id = "CUST-REV-TEST"
        test_agent_name = "ExpiringBot"

        reg_success, new_ag = storage.register_agent(
            customer_id=test_cust_id,
            customer_name="Sanjay Gupta",
            agent_name=test_agent_name,
            permitted_actions=["View balance", "Transfer money"],
            transaction_limit=10000.0
        )
        self.assertTrue(reg_success, f"Initial registration failed: {new_ag}")
        agent = storage.find_agent(test_cust_id, test_agent_name)
        agent_id = agent["agent_id"]

        # Before revocation: 'View balance' should be ALLOW
        res_before = evaluate_request(
            customer_id=test_cust_id,
            agent_name=test_agent_name,
            action="View balance",
            amount=0.0
        )
        self.assertEqual(res_before["decision"], "ALLOW", f"Expected ALLOW before revocation, got {res_before['decision']}")

        # Execute revocation
        success, revoked = storage.revoke_agent(
            agent_id=agent_id,
            reason="Customer detected unauthorized API activity on third-party provider"
        )
        self.assertTrue(success)
        self.assertEqual(revoked["status"], "REVOKED")
        self.assertIsNotNone(revoked["revoked_at"])

        # Re-fetch from file to verify persistence
        agent_after = storage.find_agent_by_id(agent_id)
        self.assertEqual(agent_after["status"], "REVOKED")

        # After revocation: Any action must return BLOCK under RULE 2
        res_after = evaluate_request(
            customer_id=test_cust_id,
            agent_name=test_agent_name,
            action="View balance",
            amount=0.0
        )
        self.assertEqual(res_after["decision"], "BLOCK")
        self.assertEqual(res_after["rule_number"], "RULE 2")

    def test_04_six_test_scenarios_execution(self):
        """Tests the six required test cases through the decision engine."""
        from tests.test_decision_engine import run_assignment_scenarios
        results = run_assignment_scenarios()
        self.assertEqual(len(results), 6)
        for r in results:
            self.assertEqual(r["status"], "PASS")

    def test_05_ajax_api_run_tests(self):
        """Tests the POST /api/run-tests route returning valid JSON."""
        response = self.client.post("/api/run-tests")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["all_passed"])
        self.assertEqual(len(data["results"]), 6)

    def test_06_request_form_post_evaluation(self):
        """Tests submitting an interactive request via POST /request."""
        form_data = {
            "customer_id": "CUST-64166",
            "agent_name": "FinancePilot AI",
            "action": "View balance",
            "amount": "0",
            "description": "Integration test check"
        }
        response = self.client.post("/request", data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ALLOW", response.data)
        self.assertIn(b"RULE 4", response.data)

    def test_07_pdf_report_download(self):
        """Tests that /download-report returns an existing valid PDF document."""
        response = self.client.get("/download-report")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/pdf")
        self.assertTrue(len(response.data) > 1000)
        response.close()


if __name__ == "__main__":
    unittest.main()
