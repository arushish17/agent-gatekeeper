
"""
Persistent JSON Storage Manager for Agent Gatekeeper.
Manages agents, audit logs, and company-specific configuration.
Includes configurable storage paths for automated test isolation.
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

COMPANY_CONFIG = {
    "name": "Wells Fargo",
    "sector": "Bank",
    "enrolment_last_digit": "6",
    "currency_symbol": "₹",
    "default_transaction_limit": 10000.0,
    "limit_explanation": (
        "The prototype uses ₹10,000 as its configured transaction threshold. "
        "Bill payments up to this amount require explicit customer "
        "pre-authorisation to be allowed automatically. Other sensitive "
        "transactions require customer approval."
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
    """Reconfigures storage paths for isolated testing."""
    global AGENTS_FILE, AUDIT_LOGS_FILE

    if agents_path:
        AGENTS_FILE = os.path.abspath(agents_path)
    if audit_logs_path:
        AUDIT_LOGS_FILE = os.path.abspath(audit_logs_path)


def reset_storage_paths():
    """Restores default storage paths."""
    global AGENTS_FILE, AUDIT_LOGS_FILE
    AGENTS_FILE = DEFAULT_AGENTS_FILE
    AUDIT_LOGS_FILE = DEFAULT_AUDIT_LOGS_FILE


def _read_json_file(file_path, default_data):
    """Reads JSON data, returning a default if missing or corrupted."""
    if not os.path.exists(file_path):
        _write_json_file(file_path, default_data)
        return default_data

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_data


def _write_json_file(file_path, data):
    """Writes JSON data with readable formatting."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def init_storage(seed_if_empty=True):
    """Initializes storage and creates demonstration records when needed."""
    os.makedirs(os.path.dirname(os.path.abspath(AGENTS_FILE)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(AUDIT_LOGS_FILE)), exist_ok=True)

    if not os.path.exists(AGENTS_FILE) or (
        seed_if_empty and os.path.getsize(AGENTS_FILE) < 10
    ):
        seed_agents = [
            {
                "agent_id": "WF-AGT-101",
                "customer_id": "CUST-64166",
                "customer_name": "Rajesh Kumar",
                "agent_name": "FinancePilot AI",
                "registration_timestamp": "2026-11-10 10:30:00",
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
                "agent_id": "WF-AGT-102",
                "customer_id": "CUST-88231",
                "customer_name": "Priya Sharma",
                "agent_name": "WealthBot Assist",
                "registration_timestamp": "2026-11-11 14:15:20",
                "permitted_actions": ["View balance"],
                "transaction_limit": 5000.0,
                "bill_payment_pre_authorized": False,
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
                "bill_payment_pre_authorized": False,
                "status": "REVOKED",
                "revoked_at": "2026-11-12 16:45:10",
                "revocation_reason": (
                    "Customer security advisory: AI credentials suspected "
                    "of third-party exposure"
                )
            }
        ]
        _write_json_file(AGENTS_FILE, seed_agents)

    if not os.path.exists(AUDIT_LOGS_FILE) or (
        seed_if_empty and os.path.getsize(AUDIT_LOGS_FILE) < 10
    ):
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
                "reason": (
                    "Agent is registered and active. View balance is a "
                    "permitted read-only action."
                )
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
                "rule_number": "RULE 2",
                "rule_name": "Revocation Enforcement",
                "reason": "Agent access was revoked."
            }
        ]
        _write_json_file(AUDIT_LOGS_FILE, seed_logs)


def get_agents():
    """Returns all stored agents."""
    init_storage()
    return _read_json_file(AGENTS_FILE, [])


def save_agents(agents_list):
    """Saves the complete agent list."""
    _write_json_file(AGENTS_FILE, agents_list)


def find_agent_by_id(agent_id):
    """Finds an agent using its unique ID."""
    for agent in get_agents():
        if agent.get("agent_id") == agent_id:
            return agent
    return None


def find_agent(customer_id, agent_name):
    """Finds an agent by customer ID and case-insensitive agent name."""
    agents = get_agents()
    c_id = customer_id.strip().upper() if customer_id else ""
    a_name = agent_name.strip().lower() if agent_name else ""

    for agent in agents:
        if agent.get("customer_id", "").strip().upper() == c_id:
            if agent.get("agent_name", "").strip().lower() == a_name:
                return agent

    return None


def register_agent(
    customer_id,
    customer_name,
    agent_name,
    permitted_actions,
    transaction_limit=10000.0,
    bill_payment_pre_authorized=False
):
    """
    Registers a new agent.
    Bill-payment pre-authorisation is stored separately from permission scope.
    """
    agents = get_agents()

    c_id = customer_id.strip()
    c_name = customer_name.strip()
    a_name = agent_name.strip()

    existing = find_agent(c_id, a_name)
    if existing:
        return False, (
            f"Agent '{a_name}' is already registered for Customer ID '{c_id}'."
        )

    new_num = 101 + len(agents)
    agent_id = f"WF-AGT-{new_num}"

    while any(agent.get("agent_id") == agent_id for agent in agents):
        new_num += 1
        agent_id = f"WF-AGT-{new_num}"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    actions = (
        permitted_actions
        if isinstance(permitted_actions, list)
        else [permitted_actions]
    )

    # Pre-authorisation only applies when bill payment is in permitted scope.
    pre_authorized = (
        bool(bill_payment_pre_authorized)
        and "Pay a bill" in actions
    )

    new_agent = {
        "agent_id": agent_id,
        "customer_id": c_id,
        "customer_name": c_name,
        "agent_name": a_name,
        "registration_timestamp": now_str,
        "permitted_actions": actions,
        "transaction_limit": float(transaction_limit),
        "bill_payment_pre_authorized": pre_authorized,
        "status": "ACTIVE",
        "revoked_at": None,
        "revocation_reason": None
    }

    agents.append(new_agent)
    save_agents(agents)

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
        "reason": (
            "Agent registered with permitted actions: "
            f"{', '.join(actions)}. "
            f"Bill payment pre-authorised: {pre_authorized}."
        )
    })

    return True, new_agent


def revoke_agent(
    agent_id,
    reason="Customer or Administrator initiated revocation"
):
    """Revokes an agent without deleting its record or audit history."""
    agents = get_agents()
    target = None

    for agent in agents:
        if agent.get("agent_id") == agent_id:
            target = agent
            break

    if not target:
        return False, f"Agent with ID '{agent_id}' not found."

    if target.get("status") == "REVOKED":
        return False, (
            f"Agent '{target.get('agent_name')}' ({agent_id}) is already REVOKED."
        )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    target["status"] = "REVOKED"
    target["revoked_at"] = now_str
    target["revocation_reason"] = reason

    save_agents(agents)

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
        "reason": f"Access revoked. Reason: {reason}"
    })

    return True, target


def get_audit_logs():
    """Returns persistent audit logs."""
    init_storage()
    return _read_json_file(AUDIT_LOGS_FILE, [])


def log_audit_event(entry):
    """Adds a timestamped event with a unique request ID."""
    logs = get_audit_logs()
    now = datetime.now()

    if not entry.get("request_id"):
        entry["request_id"] = (
            f"REQ-{now.strftime('%Y%m%d%H%M%S')}-"
            f"{uuid.uuid4().hex[:6].upper()}"
        )

    if not entry.get("timestamp"):
        entry["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")

    logs.insert(0, entry)
    _write_json_file(AUDIT_LOGS_FILE, logs)

    return entry


def get_dashboard_metrics():
    """Calculates dashboard statistics."""
    agents = get_agents()
    logs = get_audit_logs()

    request_logs = [
        log for log in logs
        if log.get("event_type") == "REQUEST"
    ]

    return {
        "total_agents": len(agents),
        "active_agents": sum(
            1 for agent in agents if agent.get("status") == "ACTIVE"
        ),
        "revoked_agents": sum(
            1 for agent in agents if agent.get("status") == "REVOKED"
        ),
        "total_requests": len(request_logs),
        "allow_count": sum(
            1 for log in request_logs if log.get("decision") == "ALLOW"
        ),
        "ask_count": sum(
            1 for log in request_logs if log.get("decision") == "ASK CUSTOMER"
        ),
        "block_count": sum(
            1 for log in request_logs if log.get("decision") == "BLOCK"
        )
    }

