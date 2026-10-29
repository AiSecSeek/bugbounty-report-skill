# Research: Bug Bounty Report Skill — как оформлять отчёты на HackerOne / Bugcrowd / Intigriti / YesWeHack

> **Дата исследования:** 29.10.2026
> **Задача:** найти готовые Agent Skills, шаблоны и скрипты на GitHub для оформления bug bounty отчётов на 4 основных платформах, извлечь форматы платформ и severity-маппинг, собрать рабочий генератор отчётов.
> **Результат:** этот репозиторий — скилл `bugbounty-report` + генератор `scripts/generate_report.py`, протестированный на всех 4 платформах.

---

## 1. Методология исследования

Поиск вёлся по трём направлениям:

1. **Agent Skills (AI-скиллы)** — готовые SKILL.md-бандлы для Claude Code / Cursor / OpenClaw / Hermes и других агентов, обученные на disclosed-репортах.
2. **Шаблоны отчётов** — Markdown-шаблоны с гайдами по заполнению.
3. **Скрипты-генераторы и автосабмит** — CLI-инструменты, превращающие находку (JSON/Markdown/frontmatter) в готовый отчёт или сразу сабмитящие его на платформу.

Параллельно изучена **официальная документация платформ** (docs.hackerone.com, docs.bugcrowd.com, kb.intigriti.com, helpcenter.yeswehack.io) — чтобы форматы в скилле соответствовали реальным требованиям триажа, а не «средней температуре» по блогам.

---

## 2. Найденные Agent Skills (AI-скиллы)

### 2.1 shaniidev/bug-reaper — основа этого проекта
- **URL:** https://github.com/shaniidev/bug-reaper · ⭐ 75 · MIT · Python
- **Что это:** Web2 bug bounty Agent Skill в открытом формате [agentskills.io](https://agentskills.io) (стандарт с декабря 2025). Совместим с OpenClaw, Cursor, Claude Code, Antigravity, Windsurf, Goose.
- **Структура:** 4-фазный workflow — RECON (7-фазная методология) → AUDIT (18 классов уязвимостей) → VALIDATE (трассировка input→sink + adversarial-чеклист против false positives) → REPORT (форматы платформ + генератор).
- **Ключевые файлы:** `references/platforms/` (HackerOne · Bugcrowd · Intigriti · YesWeHack), `references/severity-guide.md` (CVSS + маппинг tiers), `references/chaining.md` (8 шаблонов эскалации P3→P1), `scripts/generate_report.py`, `scripts/analyze_scope.py`.
- **Философия:** «evidence-based, no AI slop» — каждая находка остаётся **Theoretical**, пока не предоставлен рабочий PoC. Это правило перенесено в наш скилл.
- **Что взято:** структура отчётов 4 платформ, список 18 классов уязвимостей, принцип «валидация перед репортом».

### 2.2 elementalsouls/Claude-BugHunter — крупнейшая коллекция паттернов
- **URL:** https://github.com/elementalsouls/Claude-BugHunter · ⭐ 5339 · MIT · Python
- **Что это:** дроп-ин бандл для Claude Code: **83 скилла, 15 slash-команд, 681 паттерн из disclosed-репортов HackerOne** (433 процитированы и проверяемы) по 24 классам уязвимостей + enterprise-матрицы (M365/Entra, Okta, vCenter, SSL-VPN, SharePoint, cloud IAM).
- **4 слоя:** Think (`bb-methodology` + `redteam-mindset`) → Hunt webapps (58 `hunt-*` скиллов) → Hit the perimeter (CVE-цепочки 2024–2026) → Ship it (`triage-validation`, `evidence-hygiene`, «7-Question Gate», VRT-aware severity, OOS rebuttals, PII redaction).
- **Установка:** plugin (`/plugin marketplace add elementalsouls/Claude-BugHunter`) или copy-install в `~/.claude/skills/`. Поддерживает Claude Code, OpenCode, Codex CLI, **Hermes Agent** (`~/.hermes/skills/`), Google AntiGravity.
- **Что взято:** идея triager-режима (7 вопросов перед сабмитом) и evidence-hygiene (аннотированные скриншоты, замазанные PII).

### 2.3 BehiSecc/bugSkills — конвертация своих репортов в скиллы
- **URL:** https://github.com/BehiSecc/bugSkills · ⭐ 112
- **Что это:** подход «твои прошлые HackerOne-репорты → AI-скиллы»: скрипты парсят твои собственные сабмиты и превращают их в few-shot примеры для агента. Полезно для персонализации стиля под конкретную платформу/программу.

---

## 3. Шаблоны отчётов

### 3.1 ZephrFish/BugBountyTemplates
- **URL:** https://github.com/ZephrFish/BugBountyTemplates · ⭐ 514 · Apache-2.0
- **Шаблоны:** `Blank.md` (полный, с пояснениями к каждой секции), `HeadersOnly.md` (быстрый каркас), `short.md` (низкая severity / срочный сабмит), `Example.md` (эталонный пример на XSS), `SSRF.md` (специфика: протоколы, internal access, cloud metadata), `API.md` (BOLA/IDOR, broken auth, mass assignment).
- **Бонус:** гайд по CVSS 3.1 с таблицей Critical→Informational, чеклист сбора evidence (скриншоты аннотированы, полные HTTP pairs, таймстампы, точные payloads), список типичных ошибок («I found XSS» без места, self-XSS как XSS, logout CSRF, missing headers без PoC).
- **Что взято:** чеклист перед сабмитом и список «что почти всегда отклоняют» — вошли в README и скилл.

### 3.2 EdOverflow/bug-bounty-responses
- **URL:** https://github.com/EdOverflow/bug-bounty-responses · ⭐ 90
- **Что это:** шаблоны **ответов триажа** — как программы формулируют not applicable / duplicate / out of scope. Читать их — лучший способ понять, почему отчёты отклоняют, до того как отправишь свой.

### 3.3 dewcode91/report-templates
- **URL:** https://github.com/dewcode91/report-templates · ⭐ 15
- Примеры реальных оформленных отчётов по классам багов (для калибровки тона).

---

## 4. Скрипты-генераторы и автосабмит

### 4.1 fransr/bountyplz — автосабмит из Markdown
- **URL:** https://github.com/fransr/bountyplz · ⭐ 463 · MIT · Shell
- **Автор:** Frans Rosén (топ-1 исследователь HackerOne многократно).
- **Что делает:** читает Markdown с frontmatter (`severity`, `weakness`, `asset`, `attachments`), логинится на HackerOne/Bugcrowd (поддержка 2FA), создаёт черновик и сабмитит — всё одной командой `bountyplz h1 <program> <file.md>`.
- **Фишки:** `-p` preview, `-d` draft-only, `-f` force; inline-картинки `<img upload src="x.jpg" />` заливаются автоматически; после сабмита в frontmatter пишется `report: URL` — **защита от повторного сабмита дубля**; секция `### impact` на HackerOne автоматически уезжает в отдельное поле Impact.
- **Что взято:** идея frontmatter-атрибутов и защита от дублей.

### 4.2 codingo/bbr — генератор из шаблонов с авто-подстановкой
- **URL:** https://github.com/codingo/bbr · ⭐ 218 · GPL-3.0 · Go
- **Что делает:** берёт шаблон и подставляет контекстные переменные: `_target_`, `_username_`, `_program_`, `_researcher_`, `_sha_` (SHA256 юзернейма — для attribution при subdomain takeover), `_whois_`, `_dig_`, `_nameservers_`, `_wayback_`, `_curl_`, `_dig-txt_`, и даже `_joke_`/`_punchline_` (смягчить настроение триажера 😄).
- **Что взято:** идея авто-подстановки контекста цели в шаблон.

### 4.3 kac89/vulnrepo — онлайн-генератор с шифрованием
- **URL:** https://github.com/kac89/vulnrepo · ⭐ 583 · Apache-2.0 · TypeScript · live: https://vulnrepo.com
- **Что делает:** client-side менеджер отчётов (данные шифруются в браузере AES-256-GCM, PBKDF2 600k итераций, ключ только в памяти). Импорт из Burp/Nmap/Nessus/OpenVAS/ZAP/Semgrep/Trivy/Bugcrowd CSV/SARIF, шаблоны из CVE/CWE/MITRE ATT&CK/PCI DSS, экспорт TXT/JSON/MD/HTML/DOCX (+ AES-шифрованный self-contained HTML), чеклисты OWASP ASVS 4 / PCI DSS 4 / TBHM, интеграция с локальным Ollama для AI-помощи в написании.
- **Кому:** для больших пентест-аудитов и командной работы, не только bug bounty.

### 4.4 pwndoc/pwndoc
- **URL:** https://github.com/pwndoc/pwndoc · ⭐ 2915
- Полноценный генератор пентест-отчётов (findings-библиотека, кастомные шаблоны DOCX/PDF, multi-language). Избыточен для одиночного bug bounty репорта, но лучший выбор для регулярных аудитов.

### 4.5 Marmeus/pentesting-report-generator
- **URL:** https://github.com/Marmeus/pentesting-report-generator · ⭐ 29
- Shell-генератор pentest-отчётов из шаблонов — простой пример «шаблон → sed-подстановка → отчёт».

---

## 5. Учимся на реальных отчётах

### reddelexc/hackerone-reports
- **URL:** https://github.com/reddelexc/hackerone-reports · ⭐ 6642 · live: https://reddelexc.github.io/hackerone-reports
- Топ disclosed-репортов HackerOne: топ-100 по апвоутам и по выплатам, разбивка по 28 классам багов (XSS, XXE, CSRF, IDOR, RCE, SQLi, SSRF, Race Condition, Subdomain Takeover, Open Redirect, Clickjacking, DoS, OAuth, Account Takeover, Business Logic, REST API, GraphQL, Info Disclosure, Web Cache, SSTI, Upload, Request Smuggling, OpenID, Mobile, File Reading, AuthZ/AuthN bypass, MFA) и по ~55 программам (Twitter, Shopify, Uber, GitLab, Coinbase, DoD…).
- **Как использовать:** перед оформлением находки класса X читаешь 3–5 топовых disclosed-репортов этого класса — калибруешь структуру, глубину technical analysis и формулировки impact.

### B3nac/Android-Reports-and-Resources
- **URL:** https://github.com/B3nac/Android-Reports-and-Resources · ⭐ 1718
- Android disclosed-репорты + ресурсы (для мобильного пентеста).

---

## 6. Форматы платформ (из официальной документации)

### 6.1 HackerOne
**Источник:** [docs.hackerone.com — Quality Reports](https://docs.hackerone.com/en/articles/8475116-quality-reports)

Структура:
```
Title → Summary → Impact (ОТДЕЛЬНОЕ ПОЛЕ) → Steps to Reproduce → PoC → Root Cause → Remediation
```
- **Impact — отдельное поле формы**, а не секция текста: если заголовок содержит слово «impact», bountyplz режет отчёт и переносит хвост туда.
- Severity: **CVSS 3.1** (Critical 9.0–10.0 / High 7.0–8.9 / Medium 4.0–6.9 / Low 0.1–3.9).
- Тон: инженерно-точно. Прилагательные «devastating/critical» без обоснования CVSS — минус к доверию триажа.

### 6.2 Bugcrowd
**Источники:** [docs.bugcrowd.com — Reporting a Bug](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/reporting-a-bug), [VRT на GitHub](https://github.com/bugcrowd/vulnerability-rating-taxonomy)

Структура:
```
Summary → Technical Details (Endpoint / Input Vector / Missing Control / Why Exploitable)
→ Steps → PoC → Impact (Attacker capability / Data exposure / Priv escalation / Business risk / Why not low)
→ CWE Classification → Remediation
```
- Severity: **VRT-таксономия P1–P5**, а не CVSS напрямую. VRT — 3-уровневое дерево (Category → Sub-Category → Variant), приоритет может быть `null` («Varies») — например, IDOR варьируется P4→P1 в зависимости от возможностей функции.
- Триаж может переклассифицировать приоритет по контексту программы.
- Обязательна **CWE-классификация** находки.

### 6.3 Intigriti
**Источник:** [kb.intigriti.com — Triage Standards](http://kb.intigriti.com/en/articles/10335710-intigriti-triage-standards)

Структура:
```
Description → Technical Analysis (How it works / Why control fails / Trust boundary violated)
→ Steps → PoC → Impact (preconditions + realistic scenario) → Recommendation
```
- Главный критерий EU-триажа — **точная воспроизводимость**: шаги проверяют буквально. UI/UX-баги отклоняют.
- **Trust boundary** — фирменное требование Intigriti: явно указать, какая граница доверия нарушена (данные → код, юзер → админ, клиент → внутренняя сеть).
- Severity по CVSS назначает триаж по PoC; после accept severity **лочится** (определяет bounty).

### 6.4 YesWeHack
**Источник:** [helpcenter.yeswehack.io — Submit a report](https://helpcenter.yeswehack.io/en/articles/586823-submit-a-vulnerability-report)

Структура:
```
Vulnerability Overview → Affected Endpoint/Component → Technical Details (Root cause / Exploit mechanism / Security assumption broken)
→ Steps → PoC → Security Impact по CIA (Confidentiality / Integrity / Availability + business outcome) → Suggested Fix
```
- Тон: «внутренний security-тикет» — консервативные формулировки, акцент на **business-relevance** (что это значит для бизнеса клиента).
- Impact строго по **CIA-триаде** с отдельными полями C/I/A.

---

## 7. Severity-маппинг (унифицированный)

| Наша оценка | HackerOne (CVSS 3.1) | Bugcrowd (VRT) | Intigriti | YesWeHack |
|---|---|---|---|---|
| Critical | Critical (9.0–10.0) | P1 | Critical | Critical |
| High | High (7.0–8.9) | P2 | High | High |
| Medium | Medium (4.0–6.9) | P3 | Medium | Medium |
| Low | Low (0.1–3.9) | P4 | Low | Low |
| Informational | N/A | P5 | Informational | Informational |

⚠️ Нюансы: Bugcrowd VRT допускает «Varies» (null-приоритет) — для IDOR и прочих контекстных классов; HackerOne считает CVSS сам, твой вектор — аргумент; Intigriti лочит severity после accept.

---

## 8. Что почти всегда отклоняют (консенсус триажа всех 4 платформ)

- Self-XSS (ты сам себе внедрил)
- CSRF на login/logout
- Missing security headers без демонстрируемого impact
- Rate limiting без bypass на чувствительных эндпоинтах
- Version disclosure / verbose errors
- «Теоретические» атаки без PoC
- Social engineering как единственный вектор
- UI/UX-баги (Intigriti — сразу)

---

## 9. Чеклист перед сабмитом (универсальный)

- [ ] Заголовок = тип + место + эффект: «Stored XSS in profile bio allows session theft», а не «XSS in web app»
- [ ] Шаги пронумерованы, с точными URL/параметрами/ролями
- [ ] Raw HTTP request/response на каждом критическом шаге
- [ ] Impact — что **конкретно** получает атакующий (не «XSS is bad»)
- [ ] PoC минимальный — ровно столько, чтобы доказать эксплуатируемость
- [ ] Скриншоты аннотированы, PII замазаны
- [ ] Severity обоснован: CVSS-вектор (H1/Intigriti) или VRT-категория (Bugcrowd)
- [ ] Дубликат проверен по disclosed-репортам
- [ ] Цель в scope программы (scope = юридический контракт; вне scope — стоп)

---

## 10. Архитектура этого проекта

```
bugbounty-report-skill/
├── README.md                        # карта находок + чеклисты + этика
├── research.md                      # ЭТОТ ФАЙЛ — полное описание исследования
├── LICENSE                          # MIT
├── scripts/
│   └── generate_report.py           # генератор: JSON-находка → отчёт под 4 платформы
├── examples/
│   ├── finding-xss-example.json     # вход: Stored XSS (все поля)
│   ├── report-hackerone.md          # выход: HackerOne-формат
│   ├── report-bugcrowd.md           # выход: Bugcrowd-формат (VRT P2 + CWE)
│   ├── report-intigriti.md          # выход: Intigriti-формат (trust boundary)
│   └── report-yeswehack.md          # выход: YesWeHack-формат (CIA-impact)
└── SKILL.md                         # Agent Skill (agentskills.io-совместимый)
```

### Как работает генератор
1. Вход: JSON-находка (`--input finding.json`) или интерактивный опрос (`--interactive`).
2. `--vuln-type` (18 классов) подтягивает метаданные: CWE-номер + дефолтный CIA-impact.
3. `--platform` выбирает шаблон: hackerone / bugcrowd / intigriti / yeswehack.
4. Severity конвертируется в шкалу платформы (CVSS-диапазон / VRT P1–P5 / лейбл).
5. Выход: готовый Markdown (`-o report.md` или stdout).

```bash
# Пример: одна находка → отчёт под HackerOne
python3 scripts/generate_report.py --platform hackerone --vuln-type xss \
  --input examples/finding-xss-example.json -o report-hackerone.md

# Все 4 платформы из одной находки
for p in hackerone bugcrowd intigriti yeswehack; do
  python3 scripts/generate_report.py --platform $p --vuln-type xss \
    --input examples/finding-xss-example.json -o examples/report-$p.md
done
```

Все 4 примера в `examples/` сгенерированы этим скриптом из одного `finding-xss-example.json` — можно сравнить, как одна и та же находка ложится на разные форматы.

### Схема JSON-находки (полный список полей)
| Поле | Обязательное | Для какой платформы критично |
|---|---|---|
| `title`, `endpoint`, `severity`, `summary`, `steps`, `poc`, `root_cause`, `remediation`, `attacker_achieves` | ✅ | все |
| `cvss` | — | HackerOne, Intigriti |
| `input_vector`, `missing_control`, `why_exploitable`, `data_exposure`, `priv_escalation`, `business_risk`, `why_not_low`, `cwe_reason` | — | Bugcrowd |
| `how_it_works`, `why_control_fails`, `trust_boundary`, `prerequisites`, `realistic_scenario` | — | Intigriti |
| `component`, `environment`, `confidentiality`, `integrity`, `availability`, `worst_case`, `affected_scope` | — | YesWeHack, HackerOne |

Скрипт толерантен к пропускам: незаполненные необязательные поля подставляются из смежных (например, `how_it_works` ← `root_cause`) или получают `[Not provided]`.

---

## 11. Этика

Только цели в scope активной программы или с явным письменным разрешением. **Scope — юридический контракт.** Не эксфильтрировать данные реальных пользователей, не деградировать сервис, удалять полученные данные после закрытия репорта, следовать responsible disclosure.

---

## 12. Полный список источников

**Agent Skills:**
- https://github.com/shaniidev/bug-reaper (MIT)
- https://github.com/elementalsouls/Claude-BugHunter (MIT)
- https://github.com/BehiSecc/bugSkills

**Шаблоны:**
- https://github.com/ZephrFish/BugBountyTemplates (Apache-2.0)
- https://github.com/EdOverflow/bug-bounty-responses
- https://github.com/dewcode91/report-templates

**Генераторы / автосабмит:**
- https://github.com/fransr/bountyplz (MIT)
- https://github.com/codingo/bbr (GPL-3.0)
- https://github.com/kac89/vulnrepo (Apache-2.0)
- https://github.com/pwndoc/pwndoc
- https://github.com/Marmeus/pentesting-report-generator

**Учимся на репортах:**
- https://github.com/reddelexc/hackerone-reports
- https://github.com/B3nac/Android-Reports-and-Resources

**Документация платформ:**
- https://docs.hackerone.com/en/articles/8475116-quality-reports
- https://docs.bugcrowd.com/researchers/reporting-managing-submissions/reporting-a-bug
- https://github.com/bugcrowd/vulnerability-rating-taxonomy
- http://kb.intigriti.com/en/articles/10335710-intigriti-triage-standards
- https://helpcenter.yeswehack.io/en/articles/586823-submit-a-vulnerability-report

**Стандарты:**
- https://agentskills.io — открытый формат Agent Skills
- https://www.first.org/cvss/calculator/3.1 — CVSS 3.1 калькулятор
