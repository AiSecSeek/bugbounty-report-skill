---
name: bugbounty-report
description: "Оформление отчётов по уязвимостям для HackerOne, Bugcrowd, Intigriti и YesWeHack: форматы платформ, severity-маппинг, генератор отчётов из JSON."
version: 1.0.0
author: admin
metadata:
  safe_agent:
    title: "bugbounty-report"
    when_to_use: "Когда пользователь нашёл уязвимость и хочет оформить/сабмитить отчёт на платформу bug bounty (HackerOne, Bugcrowd, Intigriti, YesWeHack); когда просит шаблон отчёта, пример заполнения, маппинг severity (CVSS/VRT/P1-P5); когда нужно сгенерировать отчёт из находки в JSON."
    tags: [bugbounty, security, отчеты, hackerone, bugcrowd, intigriti, yeswehack, pentest]
---

# bugbounty-report

Оформление отчётов по уязвимостям для HackerOne, Bugcrowd, Intigriti и YesWeHack: форматы платформ, severity-маппинг, генератор отчётов из JSON.

## Когда использовать

Когда пользователь нашёл уязвимость и хочет оформить/сабмитить отчёт на платформу bug bounty (HackerOne, Bugcrowd, Intigriti, YesWeHack); когда просит шаблон отчёта, пример заполнения, маппинг severity (CVSS/VRT/P1-P5); когда нужно сгенерировать отчёт из находки в JSON.

## Когда НЕ использовать

Не использовать для активного тестирования вне scope программы; не генерировать фейковые/теоретические находки без подтверждённого PoC.

## Шаги

1. Уточни платформу (HackerOne / Bugcrowd / Intigriti / YesWeHack) и класс уязвимости (XSS, SQLi, IDOR, SSRF, RCE и т.д.). Если платформа не указана — предложи формат по умолчанию HackerOne.
2. Проверь, что цель в scope программы: scope — юридический контракт, активное тестирование вне scope запрещено. Если сомневаешься — остановись и попроси подтверждение.
3. Собери находку по единой схеме: заголовок (тип + место + эффект), endpoint, severity, CVSS-вектор (для H1/Intigriti), пронумерованные шаги воспроизведения с raw HTTP request/response, минимальный PoC, root cause, реалистичный impact (что конкретно получает атакующий), рекомендация по фиксу.
4. Выбери формат платформы:
   - HackerOne: Title → Summary → Impact (отдельное поле) → Steps to Reproduce → PoC → Root Cause → Remediation. Тон инженерный, без прилагательных «devastating» без обоснования CVSS.
   - Bugcrowd: Summary → Technical Details (Endpoint/Input Vector/Missing Control/Why Exploitable) → Steps → PoC → Impact (Attacker capability/Data exposure/Privilege escalation/Business risk/Why not low) → CWE Classification → Remediation. Severity по VRT P1–P5.
   - Intigriti: Description → Technical Analysis (How it works/Why control fails/Trust boundary violated) → Steps → PoC → Impact (preconditions + realistic scenario) → Recommendation. Главный критерий — точная воспроизводимость; UI/UX-баги отклоняют.
   - YesWeHack: Vulnerability Overview → Affected Endpoint/Component → Technical Details (Root cause/Exploit mechanism/Security assumption broken) → Steps → PoC → Security Impact по CIA (Confidentiality/Integrity/Availability + business outcome) → Suggested Fix. Тон «внутренний security-тикет», консервативно.
5. Сконвертируй severity: Critical→(H1: 9.0-10.0 / BC: P1 / INT: Critical / YWH: Critical), High→(7.0-8.9 / P2 / High / High), Medium→(4.0-6.9 / P3 / Medium / Medium), Low→(0.1-3.9 / P4 / Low / Low), Info→(N/A / P5 / Informational / Informational).
6. Прогони отчёт через «triager-режим»: проверь чеклист (реальная уязвимость? граница доверия нарушена? impact демонстрируем, не гипотетичен? нет social engineering как единственного вектора? severity не завышен?). Слабые места перепиши.
7. Выдай готовый Markdown-отчёт пользователю. Если есть доступ к скрипту — предложи сгенерировать через `python3 scripts/generate_report.py --platform <платформа> --vuln-type <класс> --input finding.json -o report.md` (скрипт в проекте bugbounty-report-skill).
8. Перед сабмитом прогони универсальный чеклист: заголовок = тип+место+эффект; шаги пронумерованы с точными URL/параметрами; raw HTTP на каждом шаге; PoC минимальный; дубликат проверен по disclosed-репортам; скриншоты аннотированы, чувствительные данные замазаны.
9. Не оформляй как репорт: self-XSS, CSRF на login/logout, missing headers без PoC, rate limiting без bypass, version disclosure, теоретические атаки без демонстрации.
10. После сабмита: отвечай на вопросы триажа быстро, не дави по баунти (severity оценивает программа), следи за responsible disclosure.
