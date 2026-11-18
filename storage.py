"""
storage.py - Persistent JSON Storage Manager for Agent Gatekeeper
Manages agents, audit logs, and company-specific configurations for Wells Fargo.
Includes test isolation support for configurable data directories.
"""

import json
import os
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_AGENTS_FILE = os.path.join(BASE_DIR, "agents.json")
DEFAULT_AUDIT_LOGS_FILE = os.path.join(BASE_DIR, "audit_logs.json")

AGENTS_FILE = os.environ.get("AGENTS_FILE", DEFAULT_AGENTS_FILE)
AUDIT_LOGS_FILE = os.environ.get("AUDIT_LOGS_FILE", DEFAULT_AUDIT_LOGS_FILE)

# Company and assignment configuration
COMPANY_CONFIG = {
    "name": "Wells Fargo",
    "sector": "Bank",
    "enrolment_number": "PGD202564166",
    "currency_symbol": "₹",
    "default_transaction_limit": 10000.0,
    "limit_explanation": (
        "Configured initially at ₹10,000 as a calibrated security threshold. "
        "It protects retail banking customers against automated liquidity drain "
        "and unauthorized batch transfers while accommodating routine utility payments "
        "with required step-up verification."
    ),
    "available_actions": [
        "View balance",
        "Pay a bill",
        "Transfer money"
    ],
    "read_only_actions": [
        "View balance"
    ],
    "sensitive_actions": [
        "Pay a bill",
        "Transfer money"
    ]
}


def set_storage_paths(agents_path=None, audit_logs_path=None):
    """
    Dynamically reconfigures storage file paths.
    Enables complete data isolation during automated integration testing.
    """
    global AGENTS_FILE, AUDIT_LOGS_FILE
    if agents_path:
        AGENTS_FILE = os.path.abspath(agents_path)
    if audit_logs_path:
        AUDIT_LOGS_FILE = os.path.abspath(audit_logs_path)


def reset_storage_paths():
    """Resets storage file paths back to default production files."""
    global AGENTS_FILE, AUDIT_LOGS_FILE
    AGENTS_FILE = DEFAULT_AGENTS_FILE
    AUDIT_LOGS_FILE = DEFAULT_AUDIT_LOGS_FILE


def _read_json_file(file_path, default_data):
    """Safely reads a JSON file, returning default_data if it does not exist or is corrupted."""
    if not os.path.exists(file_path):
        _write_json_file(file_path, default_data)
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default_data


def _write_json_file(file_path, data):
    """Safely writes Python data structure to a JSON file with pretty formatting."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_storage(seed_if_empty=True):
    """Initializes the persistent JSON storage with baseline seed data if files are empty."""
    os.makedirs(os.path.dirname(os.path.abspath(AGENTS_FILE)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(AUDIT_LOGS_FILE)), exist_ok=True)

    if not os.path.exists(AGENTS_FILE) or (seed_if_empty and os.path.getsize(AGENTS_FILE) < 10):
        seed_agents = [
            {
                "agent_id": "WF-AGT-101",
                "customer_id": "CUST-64166",
                "customer_name": "Rajesh Kumar",
                "agent_name": "FinancePilot AI",
                "registration_timestamp": "2026-11-10 10:30:00",
                "permitted_actions": ["View balance", "Pay a bill", "Transfer money"],
                "transaction_limit": 10000.0,
                "status": "ACTIVE",
                "revoked_at": None,
                "revocation_reason": None
            },
            {
                "agent_id": "WF-AGT-102",
                "customer_id": "CUST-88231",
                "customer_name": "Priya Sharma",
                "agent_name": "WealthBot Assist",
                "registration_timestamp": "2026-11-11 14:15:20",
                "permitted_actions": ["View balance"],
                "transaction_limit": 5000.0,
                "status": "ACTIVE",
                "revoked_at": None,
                "revocation_reason": None
            },
            {
                "agent_id": "WF-AGT-103",
                "customer_id": "CUST-99042",
                "customer_name": "Amitabh Sen",
                "agent_name": "SpendMaster Agent",
                "registration_timestamp": "2026-11-05 09:00:00",
                "permitted_actions": ["View balance", "Transfer money"],
                "transaction_limit": 10000.0,
                "status": "REVOKED",
                "revoked_at": "2026-11-12 16:45:10",
                "revocation_reason": "Customer security advisory: AI credentials suspected of third-party exposure"
            }
        ]
        _write_json_file(AGENTS_FILE, seed_agents)

    if not os.path.exists(AUDIT_LOGS_FILE) or (seed_if_empty and os.path.getsize(AUDIT_LOGS_FILE) < 10):
        seed_logs = [
            {
                "request_id": "REQ-20261112-001",
                "timestamp": "2026-11-12 11:20:15",
                "event_type": "REQUEST",
                "customer_id": "CUST-64166",
                "customer_name": "Rajesh Kumar",
                "agent_id": "WF-AGT-101",
                "agent_name": "FinancePilot AI",
                "requested_action": "View balance",
                "amount": 0.0,
                "decision": "ALLOW",
                "rule_number": "RULE 4",
                "rule_name": "Read-Only Actions",
                "reason": "Agent is registered and active. 'View balance' is a safe read-only action within permitted scope."
            },
            {
                "request_id": "REQ-20261112-002",
                "timestamp": "2026-11-12 16:45:10",
                "event_type": "REVOCATION",
                "customer_id": "CUST-99042",
                "customer_name": "Amitabh Sen",
                "agent_id": "WF-AGT-103",
                "agent_name": "SpendMaster Agent",
                "requested_action": "REVOCATION",
                "amount": 0.0,
                "decision": "REVOKED",
                "rule_number": "RULE 8",
                "rule_name": "Auditability & Revocation",
                "reason": "Customer security advisory: AI credentials suspected of third-party exposure"
            }
        ]
        _write_json_file(AUDIT_LOGS_FILE, seed_logs)


def get_agents():
    """Returns the list of all agents stored in the currently configured agents file."""
    init_storage()
    return _read_json_file(AGENTS_FILE, [])


def save_agents(agents_list):
    """Persists the full agents list to the currently configured agents file."""
    _write_json_file(AGENTS_FILE, agents_list)


def find_agent_by_id(agent_id):
    """Finds an agent by its unique agent_id."""
    agents = get_agents()
    for ag in agents:
        if ag.get("agent_id") == agent_id:
            return ag
    return None


def find_agent(customer_id, agent_name):
    """Finds an agent matching both customer_id and agent_name (case-insensitive for agent_name)."""
    agents = get_agents()
    c_id = customer_id.strip().upper() if customer_id else ""
    a_name = agent_name.strip().lower() if agent_name else ""
    for ag in agents:
        if ag.get("customer_id", "").strip().upper() == c_id:
            if ag.get("agent_name", "").strip().lower() == a_name:
                return ag
    return None


def register_agent(customer_id, customer_name, agent_name, permitted_actions, transaction_limit=10000.0):
    """
    Registers a new AI agent and saves it to agents.json.
    Prevents duplicate agent registration for the same customer.
    """
    agents = get_agents()
    c_id = customer_id.strip()
    c_name = customer_name.strip()
    a_name = agent_name.strip()

    # Check for duplicate
    existing = find_agent(c_id, a_name)
    if existing:
        return False, f"Agent '{a_name}' is already registered for Customer ID '{c_id}'."

    # Generate unique Agent ID
    new_num = 101 + len(agents)
    agent_id = f"WF-AGT-{new_num}"
    # Verify uniqueness
    while any(ag.get("agent_id") == agent_id for ag in agents):
        new_num += 1
        agent_id = f"WF-AGT-{new_num}"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_agent = {
        "agent_id": agent_id,
        "customer_id": c_id,
        "customer_name": c_name,
        "agent_name": a_name,
        "registration_timestamp": now_str,
        "permitted_actions": permitted_actions if isinstance(permitted_actions, list) else [permitted_actions],
        "transaction_limit": float(transaction_limit),
        "status": "ACTIVE",
        "revoked_at": None,
        "revocation_reason": None
    }

    agents.append(new_agent)
    save_agents(agents)

    # Log registration event
    log_audit_event({
        "event_type": "REGISTRATION",
        "customer_id": c_id,
        "customer_name": c_name,
        "agent_id": agent_id,
        "agent_name": a_name,
        "requested_action": "AGENT_REGISTRATION",
        "amount": 0.0,
        "decision": "REGISTERED",
        "rule_number": "RULE 3",
        "rule_name": "Agent Registration",
        "reason": f"Agent registered successfully with permitted actions: {', '.join(new_agent['permitted_actions'])} and limit ₹{transaction_limit:,.2f}"
    })

    return True, new_agent


def revoke_agent(agent_id, reason="Customer or Administrator initiated revocation"):
    """
    Revokes an agent permanently in agents.json.
    Never deletes the record; preserves audit history.
    """
    agents = get_agents()
    target = None
    for ag in agents:
        if ag.get("agent_id") == agent_id:
            target = ag
            break

    if not target:
        return False, f"Agent with ID '{agent_id}' not found."

    if target.get("status") == "REVOKED":
        return False, f"Agent '{target.get('agent_name')}' ({agent_id}) is already REVOKED."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target["status"] = "REVOKED"
    target["revoked_at"] = now_str
    target["revocation_reason"] = reason

    save_agents(agents)

    # Log revocation event
    log_audit_event({
        "event_type": "REVOCATION",
        "customer_id": target.get("customer_id"),
        "customer_name": target.get("customer_name"),
        "agent_id": target.get("agent_id"),
        "agent_name": target.get("agent_name"),
        "requested_action": "AGENT_REVOCATION",
        "amount": 0.0,
        "decision": "REVOKED",
        "rule_number": "RULE 2",
        "rule_name": "Revocation Enforcement",
        "reason": f"Access revoked permanently. Reason: {reason}"
    })

    return True, target


def get_audit_logs():
    """Returns the persistent audit logs from the configured audit file."""
    init_storage()
    return _read_json_file(AUDIT_LOGS_FILE, [])


def log_audit_event(entry):
    """Appends an event to audit_logs.json with timestamp and unique request ID."""
    logs = get_audit_logs()
    now = datetime.now()
    if "request_id" not in entry or not entry["request_id"]:
        entry["request_id"] = f"REQ-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    if "timestamp" not in entry or not entry["timestamp"]:
        entry["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")

    logs.insert(0, entry)  # Prepend for reverse chronological view
    _write_json_file(AUDIT_LOGS_FILE, logs)
    return entry


def get_dashboard_metrics():
    """Calculates all key statistics required by the dashboard."""
    agents = get_agents()
    logs = get_audit_logs()

    total_agents = len(agents)
    active_agents = sum(1 for ag in agents if ag.get("status") == "ACTIVE")
    revoked_agents = sum(1 for ag in agents if ag.get("status") == "REVOKED")

    # Filter request events
    request_logs = [log for log in logs if log.get("event_type") == "REQUEST"]
    total_requests = len(request_logs)

    allow_count = sum(1 for log in request_logs if log.get("decision") == "ALLOW")
    ask_count = sum(1 for log in request_logs if log.get("decision") == "ASK CUSTOMER")
    block_count = sum(1 for log in request_logs if log.get("decision") == "BLOCK")

    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "revoked_agents": revoked_agents,
        "total_requests": total_requests,
        "allow_count": allow_count,
        "ask_count": ask_count,
        "block_count": block_count
    }
