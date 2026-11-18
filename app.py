
"""
Main Flask Application Server for Agent Gatekeeper.
Implements web routes, REST endpoints, and UI views.
"""

import os
import sys
import secrets
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify,
    send_file, redirect, url_for, flash
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import storage
from decision_engine import evaluate_request, BUSINESS_RULES
from tests.test_decision_engine import run_assignment_scenarios
from generate_report import build_pdf_report

app = Flask(__name__)

# Use an environment-provided secret, or generate a local development secret.
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

# Initialize storage with demonstration records when required.
storage.init_storage()


@app.context_processor
def inject_global_data():
    """Provides common company metadata to templates."""
    return {
        "company": storage.COMPANY_CONFIG,
        "enrolment_last_digit": storage.COMPANY_CONFIG["enrolment_last_digit"],
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# =========================================================================
# WEB PAGE ROUTES
# =========================================================================

@app.route("/")
def index():
    """Main dashboard route."""
    metrics = storage.get_dashboard_metrics()
    recent_logs = storage.get_audit_logs()[:6]
    agents = storage.get_agents()

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        metrics=metrics,
        recent_logs=recent_logs,
        agents=agents
    )


@app.route("/request", methods=["GET", "POST"])
def request_check():
    """Checks an AI agent's requested banking action."""
    result = None

    if request.method == "POST":
        customer_id = request.form.get("customer_id", "").strip()
        agent_name = request.form.get("agent_name", "").strip()
        action = request.form.get("action", "").strip()
        amount_raw = request.form.get("amount", "0").strip()
        description = request.form.get("description", "").strip()

        try:
            amount = float(amount_raw) if amount_raw else 0.0
        except ValueError:
            amount = 0.0

        if not customer_id or not agent_name or not action:
            flash(
                "Please fill in Customer ID, Agent Name, and Requested Action.",
                "error"
            )
        else:
            result = evaluate_request(
                customer_id=customer_id,
                agent_name=agent_name,
                action=action,
                amount=amount,
                description=description,
                record_audit=True
            )

    agents = storage.get_agents()

    return render_template(
        "request.html",
        active_page="request",
        result=result,
        agents=agents,
        actions=storage.COMPANY_CONFIG["available_actions"]
    )


@app.route("/register", methods=["GET", "POST"])
def register_agent_view():
    """Registers an AI agent and saves its customer permissions."""

    if request.method == "POST":
        customer_id = request.form.get("customer_id", "").strip()
        customer_name = request.form.get("customer_name", "").strip()
        agent_name = request.form.get("agent_name", "").strip()
        permitted_actions = request.form.getlist("permitted_actions")
        limit_raw = request.form.get("transaction_limit", "10000").strip()

        # An unchecked HTML checkbox is not included in the submitted form.
        bill_payment_pre_authorized = (
            request.form.get("bill_payment_pre_authorized") == "on"
        )

        try:
            limit = float(limit_raw) if limit_raw else 10000.0
        except ValueError:
            limit = 10000.0

        if not customer_id or not customer_name or not agent_name or not permitted_actions:
            flash(
                "Please provide Customer ID, Customer Name, Agent Name, "
                "and at least one permitted action.",
                "error"
            )
            return redirect(url_for("register_agent_view"))

        if limit < 0:
            flash("Transaction limit cannot be negative.", "error")
            return redirect(url_for("register_agent_view"))

        success, res = storage.register_agent(
            customer_id=customer_id,
            customer_name=customer_name,
            agent_name=agent_name,
            permitted_actions=permitted_actions,
            transaction_limit=limit,
            bill_payment_pre_authorized=bill_payment_pre_authorized
        )

        if success:
            flash(
                f"Agent '{agent_name}' ({res['agent_id']}) registered "
                f"successfully for {customer_name}!",
                "success"
            )
            return redirect(url_for("manage_agents_view"))

        flash(f"Registration failed: {res}", "error")

    return render_template(
        "register.html",
        active_page="register",
        available_actions=storage.COMPANY_CONFIG["available_actions"],
        default_limit=storage.COMPANY_CONFIG["default_transaction_limit"]
    )


@app.route("/agents")
def manage_agents_view():
    """Displays registered agents."""
    agents = storage.get_agents()

    return render_template(
        "agents.html",
        active_page="agents",
        agents=agents
    )


@app.route("/revoke", methods=["GET", "POST"])
def revoke_agent_view():
    """Revokes an agent."""
    if request.method == "POST":
        agent_id = request.form.get("agent_id", "").strip()
        reason = request.form.get(
            "reason",
            "Customer requested immediate AI revocation"
        ).strip()

        if not agent_id:
            flash("Please specify an Agent ID to revoke.", "error")
            return redirect(url_for("revoke_agent_view"))

        success, target = storage.revoke_agent(agent_id, reason=reason)

        if success:
            flash(
                f"SUCCESS: Agent '{target['agent_name']}' ({agent_id}) "
                "has been permanently REVOKED. Future requests will be BLOCKED.",
                "success"
            )
            return redirect(url_for("manage_agents_view"))

        flash(f"Revocation failed: {target}", "error")

    agents = storage.get_agents()

    return render_template(
        "revoke.html",
        active_page="revoke",
        agents=agents
    )


@app.route("/audit-logs")
def audit_logs_view():
    """Displays audit logs."""
    logs = storage.get_audit_logs()
    agents = storage.get_agents()

    return render_template(
        "audit_logs.html",
        active_page="audit_logs",
        logs=logs,
        agents=agents
    )


@app.route("/rules")
def rules_view():
    """Displays business rules and policy documentation."""
    return render_template(
        "rules.html",
        active_page="rules",
        rules=BUSINESS_RULES,
        limit=storage.COMPANY_CONFIG["default_transaction_limit"],
        explanation=storage.COMPANY_CONFIG["limit_explanation"]
    )


@app.route("/tests")
def tests_view():
    """Displays assignment test scenarios."""
    test_results = run_assignment_scenarios()
    all_passed = all(
        result["status"] == "PASS" for result in test_results
    )

    return render_template(
        "tests.html",
        active_page="tests",
        test_results=test_results,
        all_passed=all_passed
    )


@app.route("/about")
def about_view():
    """Displays project information."""
    return render_template(
        "about.html",
        active_page="about"
    )


# =========================================================================
# API AND DOWNLOAD ROUTES
# =========================================================================

@app.route("/api/run-tests", methods=["POST"])
def api_run_tests():
    """Runs assignment scenarios and returns JSON results."""
    results = run_assignment_scenarios()

    return jsonify({
        "success": True,
        "results": results,
        "all_passed": all(
            result["status"] == "PASS" for result in results
        )
    })


@app.route("/api/revoke-agent", methods=["POST"])
def api_revoke_agent():
    """AJAX endpoint for agent revocation."""
    data = request.get_json() or {}
    agent_id = data.get("agent_id")
    reason = data.get(
        "reason",
        "Customer initiated revocation via web interface"
    )

    if not agent_id:
        return jsonify({
            "success": False,
            "error": "Agent ID is required"
        }), 400

    success, result = storage.revoke_agent(agent_id, reason)

    if success:
        return jsonify({
            "success": True,
            "agent": result
        })

    return jsonify({
        "success": False,
        "error": result
    }), 400


@app.route("/download-report")
def download_report():
    """Generates and serves the assignment PDF report."""
    report_path = os.path.join(
        PROJECT_ROOT,
        "report",
        "Agent_Gatekeeper_Report.pdf"
    )

    if not os.path.exists(report_path):
        build_pdf_report(report_path)

    return send_file(
        report_path,
        as_attachment=True,
        download_name="Agent_Gatekeeper_WellsFargo_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    print("==============================================================")
    print("  AGENT GATEKEEPER — Wells Fargo Security & Permission Gateway")
    print("  Local Server: http://127.0.0.1:5000")
    print("==============================================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
