"""
decision_engine.py - Core Security & Policy Decision Engine for Agent Gatekeeper
Evaluates incoming AI agent requests against Wells Fargo security policies.
Produces deterministic decisions: ALLOW, ASK CUSTOMER, or BLOCK.
"""

import storage

# Canonical Business Rules Definition for Wells Fargo Banking Domain
BUSINESS_RULES = [
    {
        "number": "RULE 1",
        "title": "Unknown Agent Block",
        "description": "If an AI agent is not registered for the customer, immediately BLOCK the request.",
        "business_reason": (
            "Prevents unauthorized, rogue, or unverified autonomous entities from interfacing "
            "with customer bank accounts, eliminating credential stuffing and synthetic identity attacks."
        ),
        "target_decision": "BLOCK"
    },
    {
        "number": "RULE 2",
        "title": "Revoked Agent Block",
        "description": "If an AI agent has been revoked, BLOCK every request regardless of action, amount, or history.",
        "business_reason": (
            "Enforces strict adherence to Wells Fargo policy mandating provable, permanent revocation "
            "of customer-delegated AI credentials to eliminate latent liability and zombie access."
        ),
        "target_decision": "BLOCK"
    },
    {
        "number": "RULE 3",
        "title": "Registered & Active Authorization",
        "description": "Only verified agents in an ACTIVE status may proceed to policy evaluation.",
        "business_reason": (
            "Guarantees that suspended, expired, or pending agents cannot execute commands or query records."
        ),
        "target_decision": "BLOCK if not ACTIVE"
    },
    {
        "number": "RULE 4",
        "title": "Read-Only Actions (Low-Risk Delegation)",
        "description": "Permit safe, read-only inquiries (e.g., 'View balance') if the agent is registered, active, and holds permission.",
        "business_reason": (
            "Enables genuine utility for financial dashboarding and automated budgeting while exposing zero capital to transactional risk."
        ),
        "target_decision": "ALLOW"
    },
    {
        "number": "RULE 5",
        "title": "Customer Confirmation for Sensitive Actions",
        "description": "Sensitive financial actions (e.g., 'Pay a bill', 'Transfer money') require step-up customer approval.",
        "business_reason": (
            "Precludes unauthorized automated debiting. AI agents may prepare transactions, but final execution requires the customer's affirmative consent."
        ),
        "target_decision": "ASK CUSTOMER"
    },
    {
        "number": "RULE 6",
        "title": "Transaction Limit Threshold",
        "description": "Any transaction exceeding the configured threshold (₹10,000) or individual agent limit mandates ASK CUSTOMER.",
        "business_reason": (
            "Establishes a strict safety cap against catastrophic automated loss or malicious prompt injection drains."
        ),
        "target_decision": "ASK CUSTOMER"
    },
    {
        "number": "RULE 7",
        "title": "Permission Scope Enforcement",
        "description": "If an agent requests an action outside its registered permissions, BLOCK the request.",
        "business_reason": (
            "Applies the Principle of Least Privilege (PoLP). An agent authorized strictly for balance tracking cannot attempt fund transfers."
        ),
        "target_decision": "BLOCK"
    },
    {
        "number": "RULE 8",
        "title": "Auditability & Immutability",
        "description": "Every evaluation, decision, revocation, and registration must be logged with an immutable timestamp and rule reference.",
        "business_reason": (
            "Provides non-repudiation and regulatory compliance with banking oversight bodies (such as RBI, CFPB, and OCC guidelines)."
        ),
        "target_decision": "LOGGED"
    }
]


def evaluate_request(customer_id, agent_name, action, amount=0.0, description="", record_audit=True):
    """
    Evaluates an AI agent's request against Wells Fargo business rules.
    
    Parameters:
        customer_id (str): Customer ID or name (e.g., 'CUST-64166')
        agent_name (str): AI agent name (e.g., 'FinancePilot AI')
        action (str): Banking action ('View balance', 'Pay a bill', 'Transfer money')
        amount (float): Transaction amount in INR (₹)
        description (str): Optional context
        record_audit (bool): Whether to record this request into audit_logs.json
        
    Returns:
        dict: Evaluation result containing decision, rule_number, rule_name, reason, and context.
    """
    clean_cust_id = (customer_id or "").strip()
    clean_agent_name = (agent_name or "").strip()
    clean_action = (action or "").strip()

    try:
        clean_amount = float(amount or 0.0)
    except (ValueError, TypeError):
        clean_amount = 0.0

    # Retrieve agent record from persistent storage (uses currently configured storage path)
    agent = storage.find_agent(clean_cust_id, clean_agent_name)

    # -------------------------------------------------------------
    # RULE 1: UNKNOWN AGENT CHECK (Must be first before any permission checks)
    # -------------------------------------------------------------
    if not agent:
        result = {
            "decision": "BLOCK",
            "rule_number": "RULE 1",
            "rule_name": "Unknown Agent",
            "reason": (
                f"AI Agent '{clean_agent_name}' is not registered under Customer ID '{clean_cust_id}'. "
                f"Wells Fargo policy mandates blocking all unregistered autonomous entities."
            ),
            "customer_id": clean_cust_id,
            "customer_name": clean_cust_id,
            "agent_id": "UNKNOWN",
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }
        if record_audit:
            _persist_request_audit(result)
        return result

    # Agent is known
    agent_id = agent.get("agent_id", "WF-AGT-???")
    customer_name = agent.get("customer_name", clean_cust_id)
    status = agent.get("status", "INACTIVE").upper()
    permitted_actions = agent.get("permitted_actions", [])
    agent_limit = float(agent.get("transaction_limit", storage.COMPANY_CONFIG["default_transaction_limit"]))
    global_limit = storage.COMPANY_CONFIG["default_transaction_limit"]
    effective_limit = min(agent_limit, global_limit)

    # -------------------------------------------------------------
    # RULE 2: REVOKED AGENT CHECK (Must be evaluated before permissions)
    # -------------------------------------------------------------
    if status == "REVOKED":
        revoked_at = agent.get("revoked_at", "Unknown Date")
        rev_reason = agent.get("revocation_reason", "Customer/Administrator initiated revocation")
        result = {
            "decision": "BLOCK",
            "rule_number": "RULE 2",
            "rule_name": "Revoked Agent",
            "reason": (
                f"Agent '{clean_agent_name}' ({agent_id}) was permanently REVOKED on {revoked_at} "
                f"(Reason: {rev_reason}). Under Wells Fargo security policies, revoked agents are blocked from all actions."
            ),
            "customer_id": clean_cust_id,
            "customer_name": customer_name,
            "agent_id": agent_id,
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }
        if record_audit:
            _persist_request_audit(result)
        return result

    # -------------------------------------------------------------
    # RULE 3: ACTIVE STATUS CHECK
    # -------------------------------------------------------------
    if status != "ACTIVE":
        result = {
            "decision": "BLOCK",
            "rule_number": "RULE 3",
            "rule_name": "Inactive Agent Status",
            "reason": (
                f"Agent '{clean_agent_name}' ({agent_id}) is currently '{status}'. "
                f"Only verified agents in ACTIVE standing may interface with banking services."
            ),
            "customer_id": clean_cust_id,
            "customer_name": customer_name,
            "agent_id": agent_id,
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }
        if record_audit:
            _persist_request_audit(result)
        return result

    # -------------------------------------------------------------
    # RULE 7: PERMISSION SCOPE CHECK
    # -------------------------------------------------------------
    # Normalize permitted actions for comparison
    normalized_perms = [p.lower() for p in permitted_actions]
    if clean_action.lower() not in normalized_perms:
        result = {
            "decision": "BLOCK",
            "rule_number": "RULE 7",
            "rule_name": "Permission Scope Violation",
            "reason": (
                f"Requested action '{clean_action}' is outside the agent's registered permissions "
                f"({', '.join(permitted_actions)}). Access blocked under Least Privilege policy."
            ),
            "customer_id": clean_cust_id,
            "customer_name": customer_name,
            "agent_id": agent_id,
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }
        if record_audit:
            _persist_request_audit(result)
        return result

    # -------------------------------------------------------------
    # RULE 4: SAFE READ-ONLY ACTIONS
    # -------------------------------------------------------------
    if clean_action in storage.COMPANY_CONFIG["read_only_actions"]:
        result = {
            "decision": "ALLOW",
            "rule_number": "RULE 4",
            "rule_name": "Read-Only Action Authorized",
            "reason": (
                f"Agent '{clean_agent_name}' is verified and active. '{clean_action}' is a safe read-only "
                f"banking operation authorized under Rule 4."
            ),
            "customer_id": clean_cust_id,
            "customer_name": customer_name,
            "agent_id": agent_id,
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }
        if record_audit:
            _persist_request_audit(result)
        return result

    # -------------------------------------------------------------
    # SENSITIVE FINANCIAL ACTIONS (Pay a bill, Transfer money)
    # -------------------------------------------------------------
    if clean_action in storage.COMPANY_CONFIG["sensitive_actions"]:
        # RULE 6: Transaction Limit Check
        if clean_amount > effective_limit:
            result = {
                "decision": "ASK CUSTOMER",
                "rule_number": "RULE 6",
                "rule_name": "Transaction Limit Exceeded",
                "reason": (
                    f"Requested {clean_action} of ₹{clean_amount:,.2f} exceeds configured safety threshold "
                    f"of ₹{effective_limit:,.2f}. Step-up customer confirmation is required."
                ),
                "customer_id": clean_cust_id,
                "customer_name": customer_name,
                "agent_id": agent_id,
                "agent_name": clean_agent_name,
                "requested_action": clean_action,
                "amount": clean_amount,
                "description": description
            }
            if record_audit:
                _persist_request_audit(result)
            return result

        # RULE 5: Customer Confirmation for Sensitive Actions
        result = {
            "decision": "ASK CUSTOMER",
            "rule_number": "RULE 5",
            "rule_name": "Customer Confirmation Required",
            "reason": (
                f"'{clean_action}' involves debiting funds or modifying financial commitments. "
                f"Even though the amount (₹{clean_amount:,.2f}) is within limit (₹{effective_limit:,.2f}), "
                f"customer confirmation is mandatory under Wells Fargo security policy."
            ),
            "customer_id": clean_cust_id,
            "customer_name": customer_name,
            "agent_id": agent_id,
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }
        if record_audit:
            _persist_request_audit(result)
        return result

    # Fallback for unrecognized action
    result = {
        "decision": "BLOCK",
        "rule_number": "RULE 7",
        "rule_name": "Unrecognized Banking Action",
        "reason": f"Action '{clean_action}' is not a recognized Wells Fargo banking operation.",
        "customer_id": clean_cust_id,
        "customer_name": customer_name,
        "agent_id": agent_id,
        "agent_name": clean_agent_name,
        "requested_action": clean_action,
        "amount": clean_amount,
        "description": description
    }
    if record_audit:
        _persist_request_audit(result)
    return result


def _persist_request_audit(eval_result):
    """Formats and writes the request evaluation into the persistent audit trail (RULE 8)."""
    log_entry = {
        "event_type": "REQUEST",
        "customer_id": eval_result.get("customer_id"),
        "customer_name": eval_result.get("customer_name"),
        "agent_id": eval_result.get("agent_id"),
        "agent_name": eval_result.get("agent_name"),
        "requested_action": eval_result.get("requested_action"),
        "amount": eval_result.get("amount", 0.0),
        "decision": eval_result.get("decision"),
        "rule_number": eval_result.get("rule_number"),
        "rule_name": eval_result.get("rule_name"),
        "reason": eval_result.get("reason"),
        "description": eval_result.get("description", "")
    }
    storage.log_audit_event(log_entry)
    eval_result["timestamp"] = log_entry.get("timestamp")
    eval_result["request_id"] = log_entry.get("request_id")
