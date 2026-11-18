
"""
Core Security and Policy Decision Engine for Agent Gatekeeper.
Evaluates AI agent requests and returns ALLOW, ASK CUSTOMER, or BLOCK.
"""

import storage


BUSINESS_RULES = [
    {
        "number": "RULE 1",
        "title": "Unknown Agent Block",
        "description": "Unregistered agents are blocked immediately.",
        "business_reason": "Only registered agents may access customer banking actions.",
        "target_decision": "BLOCK"
    },
    {
        "number": "RULE 2",
        "title": "Revoked Agent Block",
        "description": "Revoked agents are blocked regardless of action or amount.",
        "business_reason": "Revocation prevents further use of delegated access.",
        "target_decision": "BLOCK"
    },
    {
        "number": "RULE 3",
        "title": "Registered and Active Authorization",
        "description": "Only registered agents with ACTIVE status may proceed.",
        "business_reason": "Inactive agents must not access banking services.",
        "target_decision": "BLOCK if not ACTIVE"
    },
    {
        "number": "RULE 4",
        "title": "Read-Only Actions",
        "description": "Permitted read-only inquiries are allowed for active agents.",
        "business_reason": "Read-only actions do not initiate financial debits.",
        "target_decision": "ALLOW"
    },
    {
        "number": "RULE 5",
        "title": "Pre-authorised Bill Payments",
        "description": (
            "Bill payments up to ₹10,000 are allowed only when the customer "
            "has explicitly pre-authorised bill payments."
        ),
        "business_reason": (
            "Explicit customer consent allows limited routine bill payments "
            "without requiring confirmation for every transaction."
        ),
        "target_decision": "ALLOW when pre-authorised; otherwise ASK CUSTOMER"
    },
    {
        "number": "RULE 6",
        "title": "Transaction Limit and Customer Confirmation",
        "description": (
            "Bill payments above ₹10,000 or above the agent's configured "
            "limit require customer confirmation. All money transfers "
            "require customer confirmation."
        ),
        "business_reason": (
            "Higher-value transactions and money transfers require "
            "additional customer oversight."
        ),
        "target_decision": "ASK CUSTOMER"
    },
    {
        "number": "RULE 7",
        "title": "Permission Scope Enforcement",
        "description": "Actions outside the agent's registered permissions are blocked.",
        "business_reason": "Enforces the Principle of Least Privilege.",
        "target_decision": "BLOCK"
    },
    {
        "number": "RULE 8",
        "title": "Auditability",
        "description": "Every request decision is recorded in the audit log.",
        "business_reason": "Maintains a timestamped record of system decisions.",
        "target_decision": "LOGGED"
    }
]


def evaluate_request(
    customer_id,
    agent_name,
    action,
    amount=0.0,
    description="",
    record_audit=True
):
    """
    Evaluates an AI agent request against the configured business rules.

    Returns a dictionary containing decision, rule, reason, and request details.
    """

    clean_cust_id = (customer_id or "").strip()
    clean_agent_name = (agent_name or "").strip()
    clean_action = (action or "").strip()

    try:
        clean_amount = float(amount or 0.0)
    except (ValueError, TypeError):
        clean_amount = 0.0

    if clean_amount < 0:
        clean_amount = -1.0

    agent = storage.find_agent(clean_cust_id, clean_agent_name)

    def make_result(decision, rule_number, rule_name, reason):
        """Creates a consistent evaluation result."""
        return {
            "decision": decision,
            "rule_number": rule_number,
            "rule_name": rule_name,
            "reason": reason,
            "customer_id": clean_cust_id,
            "customer_name": (
                agent.get("customer_name", clean_cust_id)
                if agent else clean_cust_id
            ),
            "agent_id": agent.get("agent_id", "UNKNOWN") if agent else "UNKNOWN",
            "agent_name": clean_agent_name,
            "requested_action": clean_action,
            "amount": clean_amount,
            "description": description
        }

    def finish(result):
        """Records the decision when audit logging is enabled."""
        if record_audit:
            _persist_request_audit(result)
        return result

    # RULE 1: Unknown agent
    if not agent:
        return finish(make_result(
            "BLOCK",
            "RULE 1",
            "Unknown Agent",
            (
                f"Agent '{clean_agent_name}' is not registered for customer "
                f"'{clean_cust_id}'. Unknown agents are blocked."
            )
        ))

    agent_id = agent.get("agent_id", "UNKNOWN")
    status = str(agent.get("status", "INACTIVE")).upper()
    permitted_actions = agent.get("permitted_actions", [])

    # RULE 2: Revoked agent
    if status == "REVOKED":
        return finish(make_result(
            "BLOCK",
            "RULE 2",
            "Revoked Agent",
            (
                f"Agent '{clean_agent_name}' ({agent_id}) has been revoked. "
                "All future requests are blocked."
            )
        ))

    # RULE 3: Active status
    if status != "ACTIVE":
        return finish(make_result(
            "BLOCK",
            "RULE 3",
            "Inactive Agent Status",
            (
                f"Agent '{clean_agent_name}' has status '{status}'. "
                "Only ACTIVE agents may proceed."
            )
        ))

    # Reject invalid amounts
    if clean_amount < 0:
        return finish(make_result(
            "BLOCK",
            "RULE 6",
            "Invalid Transaction Amount",
            "Transaction amount cannot be negative."
        ))

    # RULE 7: Permission scope
    normalized_perms = [
        str(permission).strip().lower()
        for permission in permitted_actions
    ]

    if clean_action.lower() not in normalized_perms:
        return finish(make_result(
            "BLOCK",
            "RULE 7",
            "Permission Scope Violation",
            (
                f"Action '{clean_action}' is outside the agent's registered "
                f"permissions ({', '.join(permitted_actions)}). Request blocked."
            )
        ))

    # RULE 4: Read-only actions
    read_only_actions = [
        item.lower()
        for item in storage.COMPANY_CONFIG["read_only_actions"]
    ]

    if clean_action.lower() in read_only_actions:
        return finish(make_result(
            "ALLOW",
            "RULE 4",
            "Read-Only Action Authorized",
            (
                f"Agent '{clean_agent_name}' is registered and active. "
                f"'{clean_action}' is a permitted read-only action."
            )
        ))

    # RULE 5 and RULE 6: Bill payments
    if clean_action.lower() == "pay a bill":
        global_limit = float(
            storage.COMPANY_CONFIG["default_transaction_limit"]
        )
        agent_limit = float(
            agent.get("transaction_limit", global_limit)
        )
        effective_limit = min(global_limit, agent_limit)

        # Above the applicable transaction limit: ask customer.
        if clean_amount > effective_limit:
            return finish(make_result(
                "ASK CUSTOMER",
                "RULE 6",
                "Bill Payment Limit Exceeded",
                (
                    f"Bill payment of ₹{clean_amount:,.2f} exceeds the "
                    f"applicable limit of ₹{effective_limit:,.2f}. "
                    "Customer confirmation is required."
                )
            ))

        # At or below limit: require explicit pre-authorisation.
        if agent.get("bill_payment_pre_authorized", False) is True:
            return finish(make_result(
                "ALLOW",
                "RULE 5",
                "Pre-authorised Bill Payment",
                (
                    f"Bill payment of ₹{clean_amount:,.2f} is within the "
                    f"₹{effective_limit:,.2f} limit and the customer has "
                    "explicitly pre-authorised bill payments."
                )
            ))

        return finish(make_result(
            "ASK CUSTOMER",
            "RULE 5",
            "Bill Payment Confirmation Required",
            (
                "The bill payment is within the transaction limit, but "
                "the customer has not explicitly pre-authorised bill payments. "
                "Customer confirmation is required."
            )
        ))

    # RULE 6: Money transfers always require customer confirmation.
    if clean_action.lower() == "transfer money":
        return finish(make_result(
            "ASK CUSTOMER",
            "RULE 6",
            "Money Transfer Confirmation Required",
            (
                f"Money transfer of ₹{clean_amount:,.2f} requires explicit "
                "customer confirmation regardless of amount or transaction limit."
            )
        ))

    # Any action not recognized by the policy is blocked.
    return finish(make_result(
        "BLOCK",
        "RULE 7",
        "Unrecognized Banking Action",
        f"Action '{clean_action}' is not a recognized banking operation."
    ))


def _persist_request_audit(eval_result):
    """Writes the evaluation result to the persistent audit log."""

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
