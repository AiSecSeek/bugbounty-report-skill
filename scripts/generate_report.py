#!/usr/bin/env python3
"""
generate_report.py — Bug Bounty Report Generator (HackerOne / Bugcrowd / Intigriti / YesWeHack)

Адаптация идеи shaniidev/bug-reaper (MIT) + шаблоны ZephrFish/BugBountyTemplates.
Принимает находку в JSON или интерактивно, выдаёт готовый Markdown-отчёт
в формате конкретной платформы.

Usage:
    python3 generate_report.py --platform hackerone --vuln-type xss --input finding.json
    python3 generate_report.py --platform bugcrowd --vuln-type idor --interactive
    python3 generate_report.py --platform intigriti --vuln-type ssrf --input finding.json -o report.md

Platforms: hackerone, bugcrowd, intigriti, yeswehack
Vuln types: xss, sqli, nosqli, ssrf, idor, auth, biz-logic, rce, lfi, xxe, ssti,
            open-redirect, cors, csrf, subdomain-takeover, prototype-pollution,
            http-smuggling, api-graphql
"""

import json
import re
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ─── Platform Templates ──────────────────────────────────────────────────────

HACKERONE_TEMPLATE = """# {vuln_display}: {title}

## Summary
{summary}

## Impact
- **Security property violated:** {cia_impact}
- **Attacker achieves:** {attacker_achieves}
- **Who is affected:** {affected_scope}
- **Worst case:** {worst_case}

## Steps to Reproduce

{steps}

## Proof of Concept

```
{poc}
```

## Root Cause
{root_cause}

## Remediation
{remediation}

---
*CVSS: {cvss} | Severity: {severity} | {date}*"""

BUGCROWD_TEMPLATE = """## Summary
{summary}

## Technical Details
**Vulnerable Endpoint:** `{endpoint}`
**Input Vector:** {input_vector}
**Missing Control:** {missing_control}
**Why Exploitable:** {why_exploitable}

## Steps to Reproduce

{steps}

## Proof of Concept

```
{poc}
```

## Impact
- **Attacker capability:** {attacker_achieves}
- **Data exposure:** {data_exposure}
- **Privilege escalation:** {priv_escalation}
- **Business risk:** {business_risk}
- **Why not self-XSS / low impact:** {why_not_low}

## CWE Classification
**{cwe}**
{cwe_reason}

## Remediation
{remediation}

---
*VRT Priority: {severity} | {date}*"""

INTIGRITI_TEMPLATE = """### Description
{summary}

*Affected Component:* `{endpoint}`

### Technical Analysis

**How the vulnerability works:**
{how_it_works}

**Why the security control fails:**
{why_control_fails}

**Trust boundary violated:**
{trust_boundary}

### Steps to Reproduce

{steps}

### Proof of Concept

```
{poc}
```

### Impact

**Data exposure / Access escalation:**
{attacker_achieves}

**Attack preconditions:**
{prerequisites}

**Realistic abuse scenario:**
{realistic_scenario}

### Recommendation
{remediation}

---
*CVSS: {cvss} | Severity: {severity} | {date}*"""

YESWEHACK_TEMPLATE = """# Vulnerability Overview
{summary}

# Affected Endpoint / Component
**Endpoint:** `{endpoint}`
**Component:** {component}
**Environment:** {environment}

# Technical Details

**Root cause:**
{root_cause}

**Exploit mechanism:**
{how_it_works}

**Security assumption broken:**
{trust_boundary}

# Steps to Reproduce

{steps}

# Proof of Concept

```
{poc}
```

# Security Impact

**Confidentiality:** {confidentiality}
**Integrity:** {integrity}
**Availability:** {availability}

**Practical attack scenario:**
{realistic_scenario}

**Worst-case business outcome:**
{worst_case}

# Suggested Fix
{remediation}

---
*Severity: {severity} | {date}*"""

# ─── Vulnerability Type Metadata (CWE + CIA по умолчанию) ────────────────────

VULN_META = {
    "xss": {
        "display": "Cross-Site Scripting (XSS)",
        "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation",
        "cia": "Confidentiality (session tokens), Integrity (page content)",
    },
    "sqli": {
        "display": "SQL Injection",
        "cwe": "CWE-89: Improper Neutralization of Special Elements Used in SQL Command",
        "cia": "Confidentiality (database data), Integrity (data modification)",
    },
    "nosqli": {
        "display": "NoSQL Injection",
        "cwe": "CWE-943: Improper Neutralization of Special Elements in Data Query Logic",
        "cia": "Confidentiality (data extraction), Authentication Bypass",
    },
    "ssrf": {
        "display": "Server-Side Request Forgery (SSRF)",
        "cwe": "CWE-918: Server-Side Request Forgery",
        "cia": "Confidentiality (internal services, cloud credentials)",
    },
    "idor": {
        "display": "Insecure Direct Object Reference (IDOR)",
        "cwe": "CWE-639: Authorization Bypass Through User-Controlled Key",
        "cia": "Confidentiality (other users' data), Integrity (unauthorized modification)",
    },
    "auth": {
        "display": "Authentication/Authorization Bypass",
        "cwe": "CWE-287: Improper Authentication",
        "cia": "Confidentiality, Integrity (full account compromise)",
    },
    "biz-logic": {
        "display": "Business Logic Vulnerability",
        "cwe": "CWE-840: Business Logic Errors",
        "cia": "Integrity (price manipulation, workflow bypass), Financial impact",
    },
    "rce": {
        "display": "Remote Code Execution (RCE)",
        "cwe": "CWE-78: OS Command Injection / CWE-94: Code Injection",
        "cia": "Confidentiality, Integrity, Availability (full server compromise)",
    },
    "lfi": {
        "display": "Local File Inclusion (LFI) / Path Traversal",
        "cwe": "CWE-22: Improper Limitation of a Pathname to a Restricted Directory",
        "cia": "Confidentiality (file system access, credentials)",
    },
    "open-redirect": {
        "display": "Open Redirect",
        "cwe": "CWE-601: URL Redirection to Untrusted Site",
        "cia": "Integrity (trust abuse), phishing chain",
    },
    "ssti": {
        "display": "Server-Side Template Injection (SSTI)",
        "cwe": "CWE-94: Improper Control of Generation of Code",
        "cia": "Confidentiality, Integrity, Availability (RCE potential)",
    },
    "xxe": {
        "display": "XML External Entity Injection (XXE)",
        "cwe": "CWE-611: Improper Restriction of XML External Entity Reference",
        "cia": "Confidentiality (file read, SSRF via XML)",
    },
    "cors": {
        "display": "CORS Misconfiguration",
        "cwe": "CWE-346: Origin Validation Error",
        "cia": "Confidentiality (cross-origin data theft)",
    },
    "csrf": {
        "display": "Cross-Site Request Forgery (CSRF)",
        "cwe": "CWE-352: Cross-Site Request Forgery",
        "cia": "Integrity (unauthorized state change)",
    },
    "subdomain-takeover": {
        "display": "Subdomain Takeover",
        "cwe": "CWE-350: Reliance on Reverse DNS Resolution for Security-Critical Action",
        "cia": "Integrity (content under trusted domain), Confidentiality (cookie theft)",
    },
    "prototype-pollution": {
        "display": "Prototype Pollution",
        "cwe": "CWE-1321: Improperly Controlled Modification of Object Prototype Attributes",
        "cia": "Integrity (property injection), RCE via gadget chains",
    },
    "http-smuggling": {
        "display": "HTTP Request Smuggling",
        "cwe": "CWE-444: Inconsistent Interpretation of HTTP Requests",
        "cia": "Confidentiality (victim requests), Integrity (access control bypass)",
    },
    "api-graphql": {
        "display": "API / GraphQL Security Issue",
        "cwe": "CWE-285: Improper Authorization",
        "cia": "Confidentiality (unauthorized data access), Integrity",
    },
}

# ─── Severity Mapping (наша оценка → платформенная шкала) ─────────────────────

SEVERITY_MAP = {
    "critical": {"hackerone": "Critical (9.0-10.0)", "bugcrowd": "P1", "intigriti": "Critical", "yeswehack": "Critical"},
    "high":     {"hackerone": "High (7.0-8.9)",       "bugcrowd": "P2", "intigriti": "High",     "yeswehack": "High"},
    "medium":   {"hackerone": "Medium (4.0-6.9)",     "bugcrowd": "P3", "intigriti": "Medium",   "yeswehack": "Medium"},
    "low":      {"hackerone": "Low (0.1-3.9)",        "bugcrowd": "P4", "intigriti": "Low",      "yeswehack": "Low"},
    "info":     {"hackerone": "N/A",                  "bugcrowd": "P5", "intigriti": "Informational", "yeswehack": "Informational"},
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_field(data: dict, field: str, default: str = "[Not provided]") -> str:
    value = data.get(field)
    return value if value else default


def format_steps(steps_input) -> str:
    if isinstance(steps_input, list):
        return "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps_input))
    if isinstance(steps_input, str):
        lines = [l.strip() for l in steps_input.strip().split("\n") if l.strip()]
        out = []
        for i, line in enumerate(lines):
            out.append(line if re.match(r"^\d+\.", line) else f"{i+1}. {line}")
        return "\n".join(out)
    return "1. [Steps to reproduce not provided]"


def load_finding(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def interactive_collect() -> dict:
    print("\n=== Bug Bounty Report Generator (interactive) ===\n")
    data = {}
    fields = [
        ("title", "Заголовок (напр. Stored XSS in Profile Bio)", True),
        ("endpoint", "Endpoint (напр. POST /api/user/profile)", True),
        ("severity", "Severity: critical/high/medium/low/info", True),
        ("summary", "Краткое техническое описание", True),
        ("steps", "Шаги воспроизведения (по одному, пустая строка = конец)", True),
        ("poc", "PoC: payload или HTTP-запрос", True),
        ("root_cause", "Root cause (причина на уровне кода/логики)", True),
        ("remediation", "Рекомендация по исправлению", True),
        ("attacker_achieves", "Что получает атакующий", True),
        ("cvss", "CVSS-вектор (напр. AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N)", False),
        ("input_vector", "Вектор ввода (параметр/header/поле)", False),
        ("missing_control", "Отсутствующий контроль безопасности", False),
        ("why_exploitable", "Почему защиты не мешают", False),
        ("data_exposure", "Какие данные раскрываются", False),
        ("priv_escalation", "Повышение привилегий", False),
        ("business_risk", "Бизнес-риск", False),
        ("why_not_low", "Почему это не self-XSS/low impact", False),
        ("how_it_works", "Механизм эксплуатации (пошагово)", False),
        ("why_control_fails", "Почему контроль безопасности не срабатывает", False),
        ("trust_boundary", "Нарушенная граница доверия", False),
        ("prerequisites", "Предусловия атаки", False),
        ("realistic_scenario", "Реалистичный сценарий атаки", False),
        ("affected_scope", "Кто затронут", False),
        ("worst_case", "Худший сценарий", False),
        ("component", "Компонент/фича", False),
        ("environment", "Окружение (Production/Staging)", False),
        ("confidentiality", "Влияние на Confidentiality", False),
        ("integrity", "Влияние на Integrity", False),
        ("availability", "Влияние на Availability", False),
        ("cwe_reason", "Почему применим этот CWE", False),
    ]
    for name, prompt, required in fields:
        if name == "steps":
            print(f"{prompt}:")
            lines, n = [], 1
            while True:
                line = input(f"  Step {n}: ").strip()
                if not line:
                    break
                lines.append(f"{n}. {line}")
                n += 1
            data["steps"] = "\n".join(lines) if lines else "1. [Steps]"
        else:
            mark = " *" if required else ""
            val = input(f"{prompt}{mark}: ").strip()
            if val:
                data[name] = val
    return data


# ─── Generators ──────────────────────────────────────────────────────────────

def generate_hackerone(d: dict, meta: dict) -> str:
    return HACKERONE_TEMPLATE.format(
        vuln_display=meta["display"], title=get_field(d, "title"),
        summary=get_field(d, "summary"),
        cia_impact=get_field(d, "cia_impact", meta["cia"]),
        attacker_achieves=get_field(d, "attacker_achieves"),
        affected_scope=get_field(d, "affected_scope"),
        worst_case=get_field(d, "worst_case"),
        steps=format_steps(d.get("steps")),
        poc=get_field(d, "poc"), root_cause=get_field(d, "root_cause"),
        remediation=get_field(d, "remediation"),
        cvss=get_field(d, "cvss"),
        severity=get_field(d, "severity_display"),
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


def generate_bugcrowd(d: dict, meta: dict) -> str:
    return BUGCROWD_TEMPLATE.format(
        summary=get_field(d, "summary"), endpoint=get_field(d, "endpoint"),
        input_vector=get_field(d, "input_vector"),
        missing_control=get_field(d, "missing_control"),
        why_exploitable=get_field(d, "why_exploitable"),
        steps=format_steps(d.get("steps")), poc=get_field(d, "poc"),
        attacker_achieves=get_field(d, "attacker_achieves"),
        data_exposure=get_field(d, "data_exposure"),
        priv_escalation=get_field(d, "priv_escalation"),
        business_risk=get_field(d, "business_risk"),
        why_not_low=get_field(d, "why_not_low", "Impact demonstrable on other users, not self-only."),
        cwe=meta["cwe"], cwe_reason=get_field(d, "cwe_reason", "The vulnerability class directly matches this CWE."),
        remediation=get_field(d, "remediation"),
        severity=get_field(d, "severity_display"),
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


def generate_intigriti(d: dict, meta: dict) -> str:
    return INTIGRITI_TEMPLATE.format(
        summary=get_field(d, "summary"), endpoint=get_field(d, "endpoint"),
        how_it_works=get_field(d, "how_it_works", get_field(d, "root_cause")),
        why_control_fails=get_field(d, "why_control_fails", get_field(d, "missing_control")),
        trust_boundary=get_field(d, "trust_boundary"),
        steps=format_steps(d.get("steps")), poc=get_field(d, "poc"),
        attacker_achieves=get_field(d, "attacker_achieves"),
        prerequisites=get_field(d, "prerequisites"),
        realistic_scenario=get_field(d, "realistic_scenario"),
        remediation=get_field(d, "remediation"),
        cvss=get_field(d, "cvss"),
        severity=get_field(d, "severity_display"),
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


def generate_yeswehack(d: dict, meta: dict) -> str:
    return YESWEHACK_TEMPLATE.format(
        summary=get_field(d, "summary"), endpoint=get_field(d, "endpoint"),
        component=get_field(d, "component"),
        environment=get_field(d, "environment", "Production"),
        root_cause=get_field(d, "root_cause"),
        how_it_works=get_field(d, "how_it_works", get_field(d, "root_cause")),
        trust_boundary=get_field(d, "trust_boundary"),
        steps=format_steps(d.get("steps")), poc=get_field(d, "poc"),
        confidentiality=get_field(d, "confidentiality", get_field(d, "data_exposure")),
        integrity=get_field(d, "integrity", get_field(d, "priv_escalation")),
        availability=get_field(d, "availability", "None"),
        realistic_scenario=get_field(d, "realistic_scenario"),
        worst_case=get_field(d, "worst_case", get_field(d, "business_risk")),
        remediation=get_field(d, "remediation"),
        severity=get_field(d, "severity_display"),
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


GENERATORS = {
    "hackerone": generate_hackerone,
    "bugcrowd": generate_bugcrowd,
    "intigriti": generate_intigriti,
    "yeswehack": generate_yeswehack,
}


def main():
    ap = argparse.ArgumentParser(description="Bug Bounty Report Generator")
    ap.add_argument("--platform", required=True, choices=list(GENERATORS))
    ap.add_argument("--vuln-type", required=True, choices=list(VULN_META))
    ap.add_argument("--input", help="JSON-файл с находкой")
    ap.add_argument("--interactive", action="store_true", help="интерактивный ввод")
    ap.add_argument("-o", "--output", help="выходной .md файл")
    args = ap.parse_args()

    if args.interactive:
        data = interactive_collect()
    elif args.input:
        data = load_finding(args.input)
    else:
        ap.error("нужен --input <file.json> или --interactive")

    meta = VULN_META[args.vuln_type]
    sev_raw = str(data.get("severity", "medium")).lower()
    if sev_raw not in SEVERITY_MAP:
        sev_raw = "medium"
    data["severity_display"] = SEVERITY_MAP[sev_raw][args.platform]

    report = GENERATORS[args.platform](data, meta)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"OK: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
