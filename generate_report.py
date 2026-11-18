"""
generate_report.py - Professional 2-Page Executive PDF Report Generator
Uses ReportLab to generate 'report/Agent_Gatekeeper_Report.pdf'.
Strictly formatted to span exactly two pages with comprehensive academic depth.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

from tests.test_decision_engine import run_assignment_scenarios


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y' in the running footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Header rule & title
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 756, 576, 756)
        self.drawString(36, 760, "Agent Gatekeeper — Technical & Security Architecture Report | Wells Fargo")
        self.drawRightString(576, 760, "Enrolment: PGD202564166")

        # Footer rule & pagination
        self.line(36, 36, 576, 36)
        self.drawString(36, 26, "CONFIDENTIAL — Academic Evaluation Prototype — Zero External Network Binding")
        self.drawRightString(576, 26, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf_report(output_path=None):
    if not output_path:
        output_path = os.path.join(PROJECT_ROOT, "report", "Agent_Gatekeeper_Report.pdf")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Custom typography
    navy = colors.HexColor("#0A2540")
    wf_red = colors.HexColor("#B71234")
    dark_gray = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=navy,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=wf_red,
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=navy,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "BodyTextCompact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=9.8,
        textColor=dark_gray,
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        "BulletCompact",
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-8,
        spaceAfter=2
    )

    story = []

    # =========================================================================
    # PAGE 1
    # =========================================================================

    story.append(Paragraph("PROJECT: AGENT GATEKEEPER — SECURITY & PERMISSION MANAGEMENT", title_style))
    story.append(Paragraph("University Assignment Technical Architecture Report | Enrolment No: <b>PGD202564166</b> | Sector: <b>Banking (Wells Fargo)</b>", meta_style))

    # 1. Company & Problem
    story.append(Paragraph("1. Target Company Profile & Business Problem", h1_style))
    story.append(Paragraph(
        "Wells Fargo operates as one of the largest multinational banking institutions, holding hundreds of billions in customer deposits. "
        "With the proliferation of consumer-facing autonomous AI agents (such as personal finance co-pilots and browser-driven shopping bots), "
        "customers increasingly grant autonomous models delegated authority to check account balances, schedule bill payments, and transfer funds. "
        "Unlike human users governed by multi-factor authentication (MFA) and interactive CAPTCHAs, AI agents operate continuously, at scale, "
        "and with non-deterministic reasoning. The primary business problem is preventing unauthorized capital flight, credential misuse, "
        "and regulatory compliance breaches while still allowing controlled, secure agent interactions.",
        body_style
    ))

    # 2. Security & Liability Risks
    story.append(Paragraph("2. Why Autonomous AI Agents Create Unprecedented Security & Liability Risks", h1_style))
    story.append(Paragraph(
        "• <b>Prompt Injection & Goal Hijacking:</b> Autonomous agents ingesting unstructured external content (invoices, emails) can be tricked into executing unintended fund transfers.<br/>"
        "• <b>Credential Leakage & Zombie Access:</b> When customers grant API tokens or session cookies to third-party AI platforms, the bank loses perimeter visibility. If the user revokes the app in their mind, the agent may retain token refresh rights indefinitely.<br/>"
        "• <b>Non-Repudiation Breakdown:</b> In traditional electronic banking, transactions are cryptographically bound to customer consent. If an AI agent executes an unauthorized wire, establishing whether the customer, the agent developer, or the model provider bears legal liability is fraught under federal banking regulations (e.g., EFTA / Reg E).",
        body_style
    ))

    # 3. Selected Company's Stance
    story.append(Paragraph("3. Wells Fargo's Position on Third-Party AI Agents", h1_style))
    story.append(Paragraph(
        "As reported by <i>American Banker</i>, Wells Fargo has adopted an assertive security posture regarding autonomous AI intermediaries. "
        "The bank has taken active measures to block unverified automated aggregators and demands that customers provide verifiable proof "
        "when third-party AI permissions have been revoked. Wells Fargo emphasizes that financial institutions cannot absorb the unquantified liability "
        "of third-party algorithmic actors operating on open account rails without explicit authorization standards.",
        body_style
    ))

    # 4. Business Rules Matrix
    story.append(Paragraph("4. Core Decision Engine & Business Rules Matrix (Rules 1 – 8)", h1_style))
    
    rules_table_data = [
        [
            Paragraph("<b>Rule</b>", body_style),
            Paragraph("<b>Policy Title</b>", body_style),
            Paragraph("<b>Evaluation Condition & Principle</b>", body_style),
            Paragraph("<b>Action</b>", body_style)
        ],
        [
            Paragraph("<b>RULE 1</b>", body_style),
            Paragraph("Unknown Agent", body_style),
            Paragraph("Agent not registered for customer ID. Blocks unverified entities immediately.", body_style),
            Paragraph("<font color='#B71234'><b>BLOCK</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 2</b>", body_style),
            Paragraph("Revoked Agent", body_style),
            Paragraph("Agent has status REVOKED. Blocks all inquiries and transactions permanently.", body_style),
            Paragraph("<font color='#B71234'><b>BLOCK</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 3</b>", body_style),
            Paragraph("Active Status", body_style),
            Paragraph("Agent must maintain verified ACTIVE status to proceed to action checks.", body_style),
            Paragraph("<font color='#B71234'><b>BLOCK*</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 4</b>", body_style),
            Paragraph("Read-Only Action", body_style),
            Paragraph("Safe non-transactional actions ('View balance') within permitted scope.", body_style),
            Paragraph("<font color='#16A34A'><b>ALLOW</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 5</b>", body_style),
            Paragraph("Customer Confirmation", body_style),
            Paragraph("Sensitive financial actions ('Pay a bill', 'Transfer money') require approval.", body_style),
            Paragraph("<font color='#D97706'><b>ASK CUST</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 6</b>", body_style),
            Paragraph("Transaction Limit", body_style),
            Paragraph("Transactions exceeding threshold (₹10,000) mandate step-up authentication.", body_style),
            Paragraph("<font color='#D97706'><b>ASK CUST</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 7</b>", body_style),
            Paragraph("Scope Enforcement", body_style),
            Paragraph("Requested action outside agent's registered scope (Least Privilege).", body_style),
            Paragraph("<font color='#B71234'><b>BLOCK</b></font>", body_style)
        ],
        [
            Paragraph("<b>RULE 8</b>", body_style),
            Paragraph("Persistent Audit", body_style),
            Paragraph("All decisions, registrations, and revocations logged immutably with timestamp.", body_style),
            Paragraph("<font color='#0A2540'><b>LOGGED</b></font>", body_style)
        ]
    ]

    rules_table = Table(rules_table_data, colWidths=[50, 95, 335, 60])
    rules_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(rules_table)

    # 5. Transaction Limit
    story.append(Paragraph("5. Configurable Transaction Limit & Justification", h1_style))
    story.append(Paragraph(
        "The system enforces a baseline transaction limit of <b>₹10,000</b>. "
        "<b>Justification:</b> In retail banking, ₹10,000 corresponds to a well-established micro-transaction boundary. "
        "It accommodates routine consumer utility bills and small transfers while acting as a hard containment ceiling. "
        "If an agent is compromised or hallucinates, the maximum single exposure before human intervention is strictly bounded. "
        "Amounts exceeding ₹10,000 automatically trigger <b>ASK CUSTOMER</b> step-up confirmation under Rule 6.",
        body_style
    ))

    # Force PageBreak to strictly enforce 2-page constraint
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2
    # =========================================================================

    # 6. Test Cases Table (Live Execution Results)
    test_results = run_assignment_scenarios()
    story.append(Paragraph("6. Automated Decision Engine Verification — 6 Test Scenarios", h1_style))
    story.append(Paragraph(
        "The six mandatory test cases were executed directly against the live <code>decision_engine.py</code> module. "
        "The table below reflects genuine execution outputs without simulated or hardcoded results:",
        body_style
    ))

    test_table_data = [
        [
            Paragraph("<b>#</b>", body_style),
            Paragraph("<b>Scenario Description</b>", body_style),
            Paragraph("<b>Input Condition</b>", body_style),
            Paragraph("<b>Expected</b>", body_style),
            Paragraph("<b>Actual</b>", body_style),
            Paragraph("<b>Status</b>", body_style)
        ]
    ]

    for tr in test_results:
        exp_color = "#16A34A" if tr["expected"] == "ALLOW" else ("#D97706" if tr["expected"] == "ASK CUSTOMER" else "#B71234")
        act_color = "#16A34A" if tr["actual"] == "ALLOW" else ("#D97706" if tr["actual"] == "ASK CUSTOMER" else "#B71234")
        test_table_data.append([
            Paragraph(f"<b>T{tr['test_number']}</b>", body_style),
            Paragraph(tr["scenario"], body_style),
            Paragraph(f"Act: {tr['inputs']['action']} | ₹{tr['inputs']['amount']:,.0f}", body_style),
            Paragraph(f"<font color='{exp_color}'><b>{tr['expected']}</b></font>", body_style),
            Paragraph(f"<font color='{act_color}'><b>{tr['actual']}</b></font>", body_style),
            Paragraph(f"<font color='#16A34A'><b>{tr['status']}</b></font>", body_style)
        ])

    test_table = Table(test_table_data, colWidths=[24, 210, 140, 68, 68, 30])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 4))

    # 7. Strategic Gains of Complete Blocking
    story.append(Paragraph("7. Strategic Payoffs of Blanket AI Agent Blocking (What the Bank Gains)", h1_style))
    story.append(Paragraph(
        "• <b>Complete Attack Surface Elimination:</b> Blanket blocking removes automated scraping, credential stuffing, and bot-driven prompt manipulation entirely.<br/>"
        "• <b>Zero Ambiguity in Legal Liability:</b> With no automated agent access, any dispute defaults cleanly to traditional unauthorized user activity under Regulation E.<br/>"
        "• <b>Infrastructure Protection:</b> Protects banking web servers and API endpoints from synthetic traffic surges caused by thousands of querying agents.",
        body_style
    ))

    # 8. Strategic Penalties of Complete Blocking
    story.append(Paragraph("8. Strategic Penalties of Blanket AI Agent Blocking (What the Bank Loses)", h1_style))
    story.append(Paragraph(
        "• <b>Severe Customer Churn Risk:</b> Modern tech-savvy consumers demand automated budgeting and interoperability with tools like Copilot, Claude, and Gemini.<br/>"
        "• <b>Drive to Insecure Screen-Scraping:</b> If clean API access is denied, users resort to handing raw banking passwords to unvetted browser automation scripts.<br/>"
        "• <b>Loss of Ecosystem Leadership:</b> Forward-thinking banks that offer secure, standardized permission gateways will capture younger demographic market share.",
        body_style
    ))

    # 9. Sources & Credible References
    story.append(Paragraph("9. Verified Sources & Authoritative References", h1_style))
    story.append(Paragraph(
        "1. <b>American Banker:</b> <i>'Wells Fargo wants customers to prove they've revoked AI agents'</i> (Reporting on banking liability, third-party revocation verification, and credential exposure policies).<br/>"
        "2. <b>OfficeChai Tech Analysis:</b> <i>'Amazon, JPMorgan, Schwab, and Delta Are All Blocking AI Agents — Here's Why'</i> (Examining enterprise scraping bans and security boundaries).<br/>"
        "3. <b>Consumer Financial Protection Bureau (CFPB) & US Treasury:</b> <i>'Managing Artificial Intelligence Risks in the Financial Services Sector'</i> (Policy circulars on algorithmic liability, non-repudiation, and consumer data rights under Dodd-Frank Section 1033).",
        body_style
    ))

    # 10. Repository Link Placeholder
    story.append(Paragraph("10. Source Code Repository & Academic Integrity Declaration", h1_style))
    story.append(Paragraph(
        "<b>GitHub Repository:</b> <code>https://github.com/USERNAME_PLACEHOLDER/agent-gatekeeper</code> (Replace with your actual public repository URL).<br/>"
        "<b>Integrity Statement:</b> This project is built using standard Python 3 and Flask without external paid APIs or mock shortcuts. "
        "All business logic, persistent JSON storage, agent revocation records, and test scenarios are fully functional and verifiable locally.",
        body_style
    ))

    # Build the document with two-pass NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path


if __name__ == "__main__":
    out = build_pdf_report()
    print(f"Report successfully generated at: {out}")
