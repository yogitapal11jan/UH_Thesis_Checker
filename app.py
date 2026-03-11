from pathlib import Path

content = """import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
from openai import OpenAI

st.write("App started successfully")

MODEL_NAME = "gpt-5.4"
DEFAULT_VECTOR_STORE_ID = "vs_69b077b2002c819196aa0b1bca0716e0"

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

RULES = [
    {"rule_id": "TITLE_DATE", "item": "Title page shows the correct end-of-semester date for the selected graduation term.", "category": "front_matter", "severity": "error", "instructions": "Check ONLY the date itself. Ignore other title-page formatting issues for this rule."},
    {"rule_id": "TITLE_PAGE_FORMAT", "item": "Title page exists and appears to follow the UH format/template.", "category": "front_matter", "severity": "warning", "instructions": "Check overall title-page structure and required elements. If exact template conformity is unclear, use WARNING or MANUAL_REVIEW, not FAIL."},
    {"rule_id": "FRONT_MATTER_ORDER", "item": "Front matter appears in the correct order.", "category": "front_matter", "severity": "error", "instructions": "Check order such as Title Page, optional Copyright, optional Dedication, optional Acknowledgments, Abstract, Table of Contents, List of Tables, List of Figures, optional Nomenclature, Text, References, optional Appendices."},
    {"rule_id": "TOC_REQUIRED_SECTIONS", "item": "Table of Contents includes the required sections, including References and all Appendices if present.", "category": "toc", "severity": "error", "instructions": "Check that the ToC includes expected front matter and main sections. If no ToC exists, FAIL."},
    {"rule_id": "TOC_PAGE_MATCH", "item": "Table of Contents page numbers match the actual pages/section starts as best as can be verified.", "category": "toc", "severity": "error", "instructions": "Use FAIL only if there is clear mismatch evidence. If the file does not expose enough evidence, use MANUAL_REVIEW."},
    {"rule_id": "LIST_TABLES_SEPARATE_PAGE", "item": "List of Tables is on a separate page if present/required.", "category": "toc", "severity": "warning", "instructions": "Use WARNING if likely wrong, MANUAL_REVIEW if not clear."},
    {"rule_id": "LIST_FIGURES_SEPARATE_PAGE", "item": "List of Figures is on a separate page if present/required.", "category": "toc", "severity": "warning", "instructions": "Use WARNING if likely wrong, MANUAL_REVIEW if not clear."},
    {"rule_id": "LIST_CAPTIONS_MATCH_BODY", "item": "Entries in List of Tables/Figures appear to match captions used in the body.", "category": "toc", "severity": "warning", "instructions": "Use WARNING for likely mismatches; MANUAL_REVIEW if you cannot compare confidently."},
    {"rule_id": "ABSTRACT_PRESENT", "item": "Abstract is present.", "category": "abstract", "severity": "error", "instructions": "FAIL if no abstract section is found."},
    {"rule_id": "ABSTRACT_UNDER_350", "item": "Abstract does not exceed 350 words.", "category": "abstract", "severity": "error", "instructions": "Estimate carefully from the visible text; FAIL if clearly over 350 words."},
    {"rule_id": "ABSTRACT_CONTENT", "item": "Abstract includes problem, methods/procedure, results, and conclusions.", "category": "abstract", "severity": "warning", "instructions": "Use PASS, WARNING, or MANUAL_REVIEW."},
    {"rule_id": "FRONT_MATTER_ROMAN", "item": "Front matter uses lowercase Roman numerals if visible/checkable.", "category": "page_numbering", "severity": "error", "instructions": "If numbering is not visible enough, use MANUAL_REVIEW."},
    {"rule_id": "FIRST_VISIBLE_FRONT_MATTER_PAGE", "item": "The first visible front-matter page number begins correctly (usually iii if dedication/epigraph is present, otherwise abstract may begin the visible sequence).", "category": "page_numbering", "severity": "warning", "instructions": "Use WARNING or MANUAL_REVIEW when partial evidence exists."},
    {"rule_id": "CHAPTER1_PAGE1", "item": "Chapter 1 begins on page 1.", "category": "page_numbering", "severity": "error", "instructions": "PASS if clearly shown, FAIL if clearly not, otherwise MANUAL_REVIEW."},
    {"rule_id": "PAGE_NUM_BOTTOM_CENTER", "item": "Page numbers are bottom-centered within the required margin if visible/checkable.", "category": "page_numbering", "severity": "warning", "instructions": "Usually use MANUAL_REVIEW unless the file view makes this obvious."},
    {"rule_id": "PAGE_NUM_NO_SUFFIXES", "item": "Page numbers do not use suffixes such as 10a or 10b.", "category": "page_numbering", "severity": "error", "instructions": "FAIL only if such suffixes are clearly present."},
    {"rule_id": "PARAGRAPH_INDENT", "item": "New paragraphs use first-line indentation and do not rely on extra blank lines.", "category": "body_format", "severity": "warning", "instructions": "Use WARNING if clear examples violate this. Use MANUAL_REVIEW if paragraph formatting cannot be seen reliably."},
    {"rule_id": "NO_EXTRA_BLANK_LINES", "item": "Normal paragraphs do not have skipped blank lines between them.", "category": "body_format", "severity": "warning", "instructions": "Use WARNING if clearly present, otherwise MANUAL_REVIEW if not observable."},
    {"rule_id": "NO_LARGE_WHITE_SPACE", "item": "There are no suspicious large white spaces at page ends unless justified by layout.", "category": "body_format", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless the issue is obvious."},
    {"rule_id": "NO_ORPHAN_WIDOWS", "item": "There are no orphan headings/widows where checkable.", "category": "body_format", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless the issue is obvious."},
    {"rule_id": "BODY_DOUBLE_SPACED", "item": "Main body text is double-spaced where checkable.", "category": "body_format", "severity": "error", "instructions": "Usually MANUAL_REVIEW unless the file view makes spacing obvious."},
    {"rule_id": "BODY_FONT_RANGE", "item": "Main text font appears uniform and within the allowed 10–12 pt range where checkable.", "category": "body_format", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless the file view makes this obvious."},
    {"rule_id": "CHAPTER_SECTION_HEADING_STYLE", "item": "Chapter and section heading style broadly follows advisor/UH expectations.", "category": "body_format", "severity": "warning", "instructions": "Check for obvious problems such as underlined chapter headings, very oversized headings, or section headings that are clearly not left-justified when that can be inferred."},
    {"rule_id": "FIGURE_CAPTION_BELOW", "item": "Figure captions appear below figures where checkable.", "category": "captions", "severity": "error", "instructions": "FAIL only if clearly wrong; otherwise MANUAL_REVIEW."},
    {"rule_id": "TABLE_CAPTION_ABOVE", "item": "Table captions appear above tables where checkable.", "category": "captions", "severity": "error", "instructions": "FAIL only if clearly wrong; otherwise MANUAL_REVIEW."},
    {"rule_id": "CAPTION_SINGLE_SPACED", "item": "Figure and table captions are single-spaced where checkable.", "category": "captions", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless clearly visible."},
    {"rule_id": "CAPTION_FONT_RANGE", "item": "Caption font appears uniform and within the allowed 10–12 pt range where checkable.", "category": "captions", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless clearly visible."},
    {"rule_id": "CAPTION_MULTILINE_INDENT", "item": "Multi-line captions appear properly indented where checkable.", "category": "captions", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless clearly visible."},
    {"rule_id": "CAPTION_MAX_3_LINES", "item": "Captions are not excessively long; more than 3 lines should be flagged.", "category": "captions", "severity": "warning", "instructions": "Use WARNING if captions clearly exceed 3 lines."},
    {"rule_id": "FIG_TABLE_NEAR_MENTION", "item": "Figures and tables appear at the point of mention or on the following page.", "category": "captions", "severity": "warning", "instructions": "Use PASS, WARNING, or MANUAL_REVIEW."},
    {"rule_id": "TABLE_CONTINUED", "item": "Tables split across pages use a continuation label such as 'Table X (continued)' where applicable.", "category": "captions", "severity": "warning", "instructions": "If no continued tables are present, PASS with a short note or use MANUAL_REVIEW if not clear."},
    {"rule_id": "REFERENCES_BEFORE_APPENDICES", "item": "References appear before appendices.", "category": "references", "severity": "error", "instructions": "FAIL if appendices appear before references."},
    {"rule_id": "REFERENCES_HEADING_PLURAL", "item": "The references section heading uses 'References' (plural).", "category": "references", "severity": "error", "instructions": "FAIL if the heading is singular or otherwise clearly wrong."},
    {"rule_id": "REFERENCES_NOT_NUMBERED_AS_CHAPTER", "item": "The references section is not numbered as a chapter.", "category": "references", "severity": "error", "instructions": "FAIL if references are clearly numbered as a chapter."},
    {"rule_id": "REFERENCES_DOUBLE_SPACED", "item": "The references section is double-spaced where checkable.", "category": "references", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless clearly visible."},
    {"rule_id": "REFERENCES_NO_ET_AL", "item": "The reference list does not use 'et al.' and instead lists all authors.", "category": "references", "severity": "error", "instructions": "Check ONLY the reference list, not the body text. FAIL if any reference entry uses 'et al.'."},
    {"rule_id": "REFERENCES_CONSISTENT_STYLE", "item": "References use one consistent acceptable style.", "category": "references", "severity": "warning", "instructions": "Use WARNING for inconsistencies."},
    {"rule_id": "REFERENCES_HEADING_CONTENT_STYLE", "item": "Reference entries broadly follow advisor-style details (author first, titles/journal/book treatment) where checkable.", "category": "references", "severity": "warning", "instructions": "Use WARNING if obvious issues exist; do not overstate certainty."},
    {"rule_id": "REFERENCES_CITED_IN_TEXT", "item": "References listed appear to be cited in the text where checkable.", "category": "references", "severity": "warning", "instructions": "Use MANUAL_REVIEW unless there is clear evidence of missing linkage."},
    {"rule_id": "AMERICAN_ENGLISH", "item": "Writing appears to use American English.", "category": "writing", "severity": "warning", "instructions": "Use PASS, WARNING, or MANUAL_REVIEW."},
    {"rule_id": "COMPLETE_SENTENCES", "item": "Writing uses complete sentences and avoids one-sentence-fragment style.", "category": "writing", "severity": "warning", "instructions": "Use WARNING if clear repeated issues exist."},
    {"rule_id": "NO_NUMERAL_SENTENCE_STARTS", "item": "Sentences do not begin with numerals, symbols, or abbreviations where avoidable.", "category": "writing", "severity": "warning", "instructions": "Use WARNING if obvious examples exist."},
    {"rule_id": "LEADING_ZERO_DECIMALS", "item": "Decimals less than one use a leading zero where applicable.", "category": "writing", "severity": "warning", "instructions": "Use WARNING if examples like .05 are clearly present."},
    {"rule_id": "COLON_USAGE", "item": "Colons are used appropriately and not at the end of section/subsection headings.", "category": "writing", "severity": "warning", "instructions": "Use WARNING if clear heading-colon misuse exists."},
    {"rule_id": "EQUATIONS_IN_SENTENCES", "item": "Equations are treated as part of sentences and punctuated properly where checkable.", "category": "equations", "severity": "warning", "instructions": "Use PASS, WARNING, or MANUAL_REVIEW."},
    {"rule_id": "EQUATION_NUMBER_STYLE", "item": "Equation numbers appear right-aligned and in parentheses where checkable.", "category": "equations", "severity": "warning", "instructions": "Usually MANUAL_REVIEW unless obvious."},
    {"rule_id": "UNITS_ABBREVIATIONS_CONSISTENT", "item": "Units and abbreviations appear consistent throughout.", "category": "consistency", "severity": "warning", "instructions": "Use WARNING for inconsistency patterns."},
    {"rule_id": "BLANK_PAGE_FLAG", "item": "No suspicious unintended blank pages are present where checkable.", "category": "layout", "severity": "warning", "instructions": "Use WARNING if an obvious blank page is present; otherwise MANUAL_REVIEW if not clear."},
]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["overall_status", "document_type", "graduation_term", "department", "checks"],
    "properties": {
        "overall_status": {"type": "string", "enum": ["pass", "fail", "pass_with_warnings"]},
        "document_type": {"type": "string"},
        "graduation_term": {"type": "string"},
        "department": {"type": "string"},
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["rule_id", "item", "category", "severity", "status", "page", "reason", "fix"],
                "properties": {
                    "rule_id": {"type": "string"},
                    "item": {"type": "string"},
                    "category": {"type": "string"},
                    "severity": {"type": "string", "enum": ["error", "warning"]},
                    "status": {"type": "string", "enum": ["PASS", "FAIL", "WARNING", "MANUAL_REVIEW"]},
                    "page": {"type": "string"},
                    "reason": {"type": "string"},
                    "fix": {"type": "string"},
                },
            },
        },
    },
}


def build_rules_text() -> str:
    return "\\n".join(
        f"{idx}. [{rule['rule_id']}] ({rule['severity']} / {rule['category']}) {rule['item']} Instruction: {rule['instructions']}"
        for idx, rule in enumerate(RULES, start=1)
    )


def build_prompt(document_type: str, graduation_term: str, department: str) -> str:
    return f\"\"\"
You are a strict UH thesis formatting/content checker.
Context:
- document_type: {document_type}
- graduation_term: {graduation_term}
- department: {department}
Use the UH guideline documents in file_search as the source of truth.
Behave like a careful graduate-format reviewer, not a casual essay reviewer.
Scope:
- Check ONLY thesis/dissertation formatting and content-compliance issues in the uploaded document.
- Do NOT check deadlines, ETD upload, committee workflow, approvals, or other administrative items.
Critical behavior:
- Evaluate EACH rule independently.
- Do not fail one rule because of a problem that belongs to another rule.
- Be conservative. If a rule depends on exact visual layout, spacing, font measurement, margin geometry, page placement, or other formatting that the current file view does not make reliable, use MANUAL_REVIEW.
- Use FAIL only for clear objective violations.
- Use WARNING for likely style/format issues that are not certain enough or are softer expectations.
- For reference-list checks, inspect the reference list itself, not citations in the body text.
- Include the most useful page/page-range you can infer; if unavailable, use 'not clearly available'.
- Keep reasons short, concrete, and evidence-based.
- Every check must include a specific fix.
Return EXACTLY one check object for every rule listed below. Do not skip any rule.
Rules:
{build_rules_text()}
Status guidance:
- PASS = rule appears satisfied
- FAIL = clear objective violation
- WARNING = likely issue / softer formatting concern
- MANUAL_REVIEW = cannot be verified reliably from current file view
Overall status guidance:
- fail = any check has status FAIL
- pass_with_warnings = no FAIL, but at least one WARNING or MANUAL_REVIEW
- pass = all checks PASS
Return ONLY valid JSON matching the schema.
\"\"\".strip()


def normalize_checks(report: dict) -> dict:
    by_rule = {c.get("rule_id"): c for c in report.get("checks", []) if c.get("rule_id")}
    normalized = []
    for rule in RULES:
        existing = by_rule.get(rule["rule_id"])
        if existing:
            existing["item"] = existing.get("item", rule["item"])
            existing["category"] = existing.get("category", rule["category"])
            existing["severity"] = existing.get("severity", rule["severity"])
            normalized.append(existing)
        else:
            normalized.append({
                "rule_id": rule["rule_id"],
                "item": rule["item"],
                "category": rule["category"],
                "severity": rule["severity"],
                "status": "MANUAL_REVIEW",
                "page": "not clearly available",
                "reason": "The model did not return this rule, so it has been marked for manual review.",
                "fix": "Review this rule manually and update the document if needed.",
            })
    report["checks"] = normalized
    return report


def recompute_report(report: dict) -> dict:
    report = normalize_checks(report)
    statuses = [c["status"] for c in report["checks"]]
    report["counts"] = {
        "PASS": statuses.count("PASS"),
        "FAIL": statuses.count("FAIL"),
        "WARNING": statuses.count("WARNING"),
        "MANUAL_REVIEW": statuses.count("MANUAL_REVIEW"),
    }
    if report["counts"]["FAIL"] > 0:
        report["overall_status"] = "fail"
    elif report["counts"]["WARNING"] > 0 or report["counts"]["MANUAL_REVIEW"] > 0:
        report["overall_status"] = "pass_with_warnings"
    else:
        report["overall_status"] = "pass"
    return report


def build_text_report(report: dict) -> str:
    lines = [
        "UH Thesis Checker Report",
        "=" * 28,
        f"Overall status: {report['overall_status']}",
        f"Document type: {report.get('document_type', '')}",
        f"Graduation term: {report.get('graduation_term', '')}",
        f"Department: {report.get('department', '')}",
        "",
        "Summary counts:",
        f"PASS: {report['counts']['PASS']}",
        f"FAIL: {report['counts']['FAIL']}",
        f"WARNING: {report['counts']['WARNING']}",
        f"MANUAL_REVIEW: {report['counts']['MANUAL_REVIEW']}",
        "",
    ]
    for check in report["checks"]:
        lines += [
            f"{check['rule_id']} - {check['item']}",
            f"Status: {check['status']}",
            f"Severity: {check['severity']}",
            f"Category: {check['category']}",
            f"Page: {check['page']}",
            f"Reason: {check['reason']}",
            f"Fix: {check['fix']}",
            "-" * 50,
        ]
    return "\\n".join(lines)


def build_dataframe(report: dict) -> pd.DataFrame:
    df = pd.DataFrame(report["checks"])
    return df[["rule_id", "item", "category", "severity", "status", "page", "reason", "fix"]]


def run_checker(file_path: str, document_type: str, graduation_term: str, department: str, vector_store_id: str) -> dict:
    with open(file_path, "rb") as f:
        thesis_file = client.files.create(file=f, purpose="user_data")
    response = client.responses.create(
        model=MODEL_NAME,
        tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
        input=[{
            "role": "user",
            "content": [
                {"type": "input_file", "file_id": thesis_file.id},
                {"type": "input_text", "text": build_prompt(document_type, graduation_term, department)},
            ],
        }],
        text={"format": {"type": "json_schema", "name": "uh_rigorous_thesis_check_report", "schema": SCHEMA, "strict": True}},
    )
    return recompute_report(json.loads(response.output_text))


st.set_page_config(page_title="UH Thesis Checker — Rigorous", layout="wide")
st.title("UH Thesis Checker — Rigorous")
st.write("Upload a thesis Word document or PDF and run a stricter UH/advisor-style compliance check.")

with st.sidebar:
    st.header("Settings")
    vector_store_id = st.text_input("Vector store ID", value=DEFAULT_VECTOR_STORE_ID)
    st.caption("Leave this as-is unless you replace your UH guideline vector store.")
    st.markdown("**Status meanings**")
    st.write("- PASS = satisfied")
    st.write("- FAIL = objective violation")
    st.write("- WARNING = likely issue")
    st.write("- MANUAL_REVIEW = not reliably verifiable from the file view")

with st.form("checker_form"):
    col1, col2 = st.columns(2)
    with col1:
        document_type = st.selectbox("Document type", ["ms_thesis", "dissertation", "bs_honors_thesis"])
        graduation_term = st.selectbox("Graduation term", ["spring_2026", "summer_2026", "fall_2026"])
    with col2:
        department = st.text_input("Department", value="Material Science and Engineering")
        uploaded_file = st.file_uploader("Upload thesis file", type=["docx", "pdf"])
    submitted = st.form_submit_button("Run rigorous check")

if submitted:
    if uploaded_file is None:
        st.error("Please upload a thesis file first.")
    elif not department.strip():
        st.error("Please enter the department.")
    elif not vector_store_id.strip():
        st.error("Please enter a vector store ID.")
    else:
        with st.spinner("Running rigorous check..."):
            suffix = Path(uploaded_file.name).suffix.lower()
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    temp_path = tmp.name
                st.session_state["latest_report"] = run_checker(temp_path, document_type, graduation_term, department.strip(), vector_store_id.strip())
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if temp_path:
                    try:
                        Path(temp_path).unlink(missing_ok=True)
                    except Exception:
                        pass

if "latest_report" in st.session_state:
    report = st.session_state["latest_report"]
    st.subheader("Overall status")
    if report["overall_status"] == "fail":
        st.error("FAIL")
    elif report["overall_status"] == "pass_with_warnings":
        st.warning("PASS WITH WARNINGS")
    else:
        st.success("PASS")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PASS", report["counts"]["PASS"])
    c2.metric("FAIL", report["counts"]["FAIL"])
    c3.metric("WARNING", report["counts"]["WARNING"])
    c4.metric("MANUAL_REVIEW", report["counts"]["MANUAL_REVIEW"])

    df = build_dataframe(report)
    st.subheader("Results table")
    status_filter = st.multiselect("Filter by status", ["PASS", "FAIL", "WARNING", "MANUAL_REVIEW"], default=["FAIL", "WARNING", "MANUAL_REVIEW", "PASS"])
    st.dataframe(df[df["status"].isin(status_filter)], use_container_width=True, hide_index=True)

    st.subheader("Detailed checks")
    for check in report["checks"]:
        if check["status"] not in status_filter:
            continue
        label = f"{check['rule_id']} — {check['status']} — {check['item']}"
        with st.expander(label, expanded=(check["status"] == "FAIL")):
            st.write(f"**Category:** {check['category']}")
            st.write(f"**Severity:** {check['severity']}")
            st.write(f"**Page:** {check['page']}")
            st.write(f"**Reason:** {check['reason']}")
            st.write(f"**Fix:** {check['fix']}")

    st.subheader("JSON report")
    st.json(report)
    json_text = json.dumps(report, indent=2, ensure_ascii=False)
    text_report = build_text_report(report)
    with open("latest_thesis_report.json", "w", encoding="utf-8") as f:
        f.write(json_text)
    st.success("Report saved to latest_thesis_report.json")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Download JSON report", json_text, "latest_thesis_report.json", "application/json")
    with d2:
        st.download_button("Download text report", text_report, "latest_thesis_report.txt", "text/plain")
"""
# try alternate writable path in current workspace
out = Path("app_updated.py")
out.write_text(content, encoding="utf-8")
print(str(out.resolve()))
