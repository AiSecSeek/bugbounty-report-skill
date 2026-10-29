# Bug Bounty Report Skill — HackerOne / Bugcrowd / Intigriti / YesWeHack

Скилл + инструменты для оформления отчётов по уязвимостям на 4 основных платформах bug bounty.

## 📁 Структура проекта

```
├── README.md                        # этот файл — карта находок + чеклисты
├── research.md                      # ПОЛНОЕ описание исследования: все найденные скиллы/шаблоны/скрипты, форматы платформ
├── SKILL.md                         # Agent Skill (agentskills.io-совместимый)
├── LICENSE                          # MIT
├── scripts/
│   └── generate_report.py           # генератор отчётов под 4 платформы (JSON → Markdown)
├── examples/
│   ├── finding-xss-example.json     # пример входных данных (находка Stored XSS)
│   ├── report-hackerone.md          # пример готового отчёта HackerOne
│   ├── report-bugcrowd.md           # пример Bugcrowd (VRT P2 + CWE)
│   ├── report-intigriti.md          # пример Intigriti (Technical Analysis)
│   └── report-yeswehack.md          # пример YesWeHack (CIA-impact)
└── upload_github.py                 # скрипт публикации проекта на GitHub (GH_TOKEN)
```

> 📖 **Полное описание исследования** (все 15+ найденных репозиториев с разбором, форматы платформ из офиц. документации, severity-нюансы, архитектура генератора) — в [research.md](research.md).

## 🚀 Быстрый старт

```bash
# Из JSON-находки
python3 scripts/generate_report.py --platform hackerone --vuln-type xss --input finding.json -o report.md

# Интерактивно (спросит все поля по очереди)
python3 scripts/generate_report.py --platform bugcrowd --vuln-type idor --interactive
```

Платформы: `hackerone`, `bugcrowd`, `intigriti`, `yeswehack`
Типы уязвимостей (18): `xss`, `sqli`, `nosqli`, `ssrf`, `idor`, `auth`, `biz-logic`, `rce`, `lfi`, `xxe`, `ssti`, `open-redirect`, `cors`, `csrf`, `subdomain-takeover`, `prototype-pollution`, `http-smuggling`, `api-graphql`

## 📋 Форматы платформ (кратко)

### HackerOne
- Поля: Title → Summary → **Impact** (отдельное поле!) → Steps to Reproduce → PoC → Root Cause → Remediation
- Severity: CVSS 3.1 (Critical 9.0–10.0 / High 7.0–8.9 / Medium 4.0–6.9 / Low 0.1–3.9)
- Тон: инженерно-точно, без прилагательных «devastating/critical» без обоснования CVSS
- Источник: [docs.hackerone.com — Quality Reports](https://docs.hackerone.com/en/articles/8475116-quality-reports)

### Bugcrowd
- Поля: Summary → Technical Details (Endpoint/Input Vector/Missing Control) → Steps → PoC → Impact → **CWE Classification** → Remediation
- Severity: **VRT-таксономия P1–P5** (не CVSS напрямую; триаж может переклассифицировать)
- Источник: [docs.bugcrowd.com — Reporting a Bug](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/reporting-a-bug), [VRT на GitHub](https://github.com/bugcrowd/vulnerability-rating-taxonomy)

### Intigriti
- Поля: Description → **Technical Analysis** (How it works / Why control fails / Trust boundary) → Steps → PoC → Impact (preconditions + realistic scenario) → Recommendation
- Severity: CVSS от триажа по PoC; после accept severity лочится (определяет bounty)
- Главное: **воспроизводимость** — EU-триаж строго проверяет шаги; UI/UX-баги отклоняют
- Источник: [kb.intigriti.com — Triage Standards](http://kb.intigriti.com/en/articles/10335710-intigriti-triage-standards)

### YesWeHack
- Поля: Vulnerability Overview → Affected Endpoint/Component → Technical Details (Root cause / Exploit mechanism / Security assumption broken) → Steps → PoC → **Security Impact по CIA** (Confidentiality/Integrity/Availability) → Suggested Fix
- Тон: «внутренний security-тикет», консервативные формулировки, акцент на business-relevance
- Источник: [helpcenter.yeswehack.io — Submit a report](https://helpcenter.yeswehack.io/en/articles/586823-submit-a-vulnerability-report)

## 🗺️ Маппинг severity

| Наша оценка | HackerOne | Bugcrowd | Intigriti | YesWeHack |
|---|---|---|---|---|
| Critical | Critical (9.0–10.0) | P1 | Critical | Critical |
| High | High (7.0–8.9) | P2 | High | High |
| Medium | Medium (4.0–6.9) | P3 | Medium | Medium |
| Low | Low (0.1–3.9) | P4 | Low | Low |
| Informational | N/A | P5 | Informational | Informational |

## 🔧 Готовые инструменты на GitHub

### Шаблоны отчётов
| Репо | ⭐ | Что даёт |
|---|---|---|
| [ZephrFish/BugBountyTemplates](https://github.com/ZephrFish/BugBountyTemplates) | 514 | Blank/Short/HeadersOnly/SSRF/API шаблоны + гайд по CVSS и чеклист evidence |
| [EdOverflow/bug-bounty-responses](https://github.com/EdOverflow/bug-bounty-responses) | 90 | Шаблоны ответов триажа (почему отчёты отклоняют) |
| [dewcode91/report-templates](https://github.com/dewcode91/report-templates) | 15 | Примеры реальных отчётов по классам багов |

### Скрипты-генераторы и автосабмит
| Репо | ⭐ | Что даёт |
|---|---|---|
| [fransr/bountyplz](https://github.com/fransr/bountyplz) | 463 | Автосабмит в HackerOne/Bugcrowd из Markdown + frontmatter (severity/asset/weakness), 2FA, inline-картинки, защита от дублей |
| [codingo/bbr](https://github.com/codingo/bbr) | 218 | Генератор отчётов из шаблонов с авто-подстановкой (`_target_`, `_whois_`, `_dig_`, `_sha_` и т.д.) |
| [kac89/vulnrepo](https://github.com/kac89/vulnrepo) | 583 | Онлайн-генератор отчётов: CWE/CVE/MITRE ATT&CK, импорт Burp/Nessus/Nmap/Bugcrowd, экспорт MD/HTML/DOCX |
| [pwndoc/pwndoc](https://github.com/pwndoc/pwndoc) | 2915 | Полноценный pentest-report генератор (для больших аудитов) |
| [Marmeus/pentesting-report-generator](https://github.com/Marmeus/pentesting-report-generator) | 29 | Shell-генератор pentest-отчётов из шаблонов |

### Готовые Agent Skills (AI)
| Репо | ⭐ | Что даёт |
|---|---|---|
| [shaniidev/bug-reaper](https://github.com/shaniidev/bug-reaper) | 75 | **Web2 bug bounty skill**: 18 классов уязвимостей, форматы отчётов всех 4 платформ, severity-guide, triager-режимы — основа этого проекта |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 5339 | 82 скилла, 681 паттерн из disclosed-репортов HackerOne |
| [BehiSecc/bugSkills](https://github.com/BehiSecc/bugSkills) | 112 | Конвертация твоих H1-репортов в AI-скиллы |

### Учимся на реальных отчётах
| Репо | ⭐ | Что даёт |
|---|---|---|
| [reddelexc/hackerone-reports](https://github.com/reddelexc/hackerone-reports) | 6642 | Топ disclosed-репортов HackerOne (сортировка по баунти) |
| [B3nac/Android-Reports-and-Resources](https://github.com/B3nac/Android-Reports-and-Resources) | 1718 | Android disclosed-репорты |

## ✅ Чеклист перед сабмитом (универсальный)

- [ ] Заголовок: тип + место + эффект («Stored XSS in profile bio allows session theft»), не «XSS in web app»
- [ ] Шаги воспроизведения пронумерованы, с точными URL/параметрами/ролями
- [ ] Есть raw HTTP request/response на каждом критическом шаге
- [ ] Impact — что конкретно получает атакующий (не «XSS is bad»)
- [ ] PoC минимальный — ровно столько, чтобы доказать эксплуатируемость
- [ ] Скриншоты аннотированы, чувствительные данные замазаны
- [ ] Severity обоснован (CVSS-вектор для H1/Intigriti, VRT-категория для Bugcrowd)
- [ ] Проверил disclosed-репорты на дубликат
- [ ] Цель в scope программы (иначе стоп — см. политику)

## ❌ Что почти всегда отклоняют

Self-XSS, CSRF на login/logout, missing headers без PoC, rate limiting без bypass, version disclosure, «теоретические» атаки без демонстрации, social engineering как единственный вектор.

## ⚖️ Этика

Только цели в scope активной программы или с явным письменным разрешением. Scope — юридический контракт. Не эксфильтрировать данные, не деградировать сервис, удалять полученные данные после закрытия репорта.
