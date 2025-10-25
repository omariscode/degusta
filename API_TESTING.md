# Degusta — API Testing Guide

Base URL (dev): http://localhost:8000/

Use this document in Postman / ApiDog. Each request shows method, path, headers and example JSON (or form) payloads. Where JWT is required, include header:

Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

---
## 1) Authentication

### 1.1 Register (customer)
POST /auth/register/

Headers:
- Content-Type: application/json

Body (JSON):
{
  "email": "user@example.com",
  "name": "Fulano",
  "phone": "923000001",
  "password": "secret123"
}

Expected: 201 Created with user data (no token). Then call token endpoint to log in.

---
### 1.2 Login (customer) - obtain JWT
POST /auth/token/

Headers:
- Content-Type: application/json

Body (JSON):
{
  "phone": "923000001",
  "password": "secret123"
}

Response (200):
{
  "refresh": "<REFRESH_TOKEN>",
  "access": "<ACCESS_TOKEN>"
}

Use the `access` token for authenticated requests in the Authorization header.

---
### 1.3 Refresh token
POST /auth/token/refresh/

Body:
{ "refresh": "<REFRESH_TOKEN>" }

Response: new access token.

---
### 1.4 Admin register (creates superuser)
POST /auth/admin/register/

Note: The endpoint is protected by `IsAdminUser` in the current code (only existing admins can create admins). If you have no admin yet, create one with Django's `createsuperuser` or ask to change behaviour.

Headers:
- Content-Type: application/json
- Authorization: Bearer <ADMIN_ACCESS_TOKEN>

Body:
{
  "email": "admin@example.com",
  "name": "Admin",
  "phone": "923000002",
  "password": "adminpass"
}

Created user will have `is_staff` and `is_superuser` = true.

---
### 1.5 Admin login
POST /auth/admin/login/

Body (same shape as /auth/token/):
{
  "phone": "923000002",
  "password": "adminpass"
}

This returns access/refresh tokens but will fail if the user is not `is_superuser`.

---
## 2) Products

### 2.1 List products
GET /products/

Headers: none required (AllowAny)

Response: array of products with fields: id, name, slug, description, price, stock, image

### 2.2 Create product
POST /products/

Headers:
- For JSON: Content-Type: application/json (the view currently allows open creation).

Body (JSON):
{
  "name": "Pizza Margherita",
  "description": "Deliciosa...",
  "price": "8.50",
  "stock": 20
}

If you want to upload an image, send multipart/form-data (key `image`) with Authorization header if your app requires it.

### 2.3 Retrieve / Update / Delete
GET /products/<id>/
PUT /products/<id>/
DELETE /products/<id>/

PUT example body (JSON):
{
  "name": "Pizza Margherita - Large",
  "price": "10.00",
  "stock": 15
}

---
## 3) Checkout & Orders (flow)

### 3.1 Checkout (creates Order, OrderItems, decrements stock and generates Invoice automatically)
POST /checkout/

Headers:
- Authorization: Bearer <ACCESS_TOKEN>
- Content-Type: application/json

Body (JSON):
{
  "delivery_address": "Rua Exemplo 123, Luanda",
  "items": [
    { "product": 1, "qty": 2 },
    { "product": 3, "qty": 1 }
  ]
}

Behavior:
- The API checks product stock (uses select_for_update to lock rows).
- Creates the Order and OrderItem rows.
- Decrements product stock.
- Marks order as `paid` (example implementation) and creates an Invoice record.
- Attempts to generate a PDF using `pdfkit` if available; otherwise saves HTML as invoice file in `tmp/`.

Response: 201 Created with order details (see `OrderDetailSerializer` fields: id, customer, status, total, delivery_address, created_at, items).

Notes:
- Ensure `pdfkit` and `wkhtmltopdf` are installed if you want a true PDF output.
- The invoice file path is stored in `invoice.pdf` model field (may be a local `tmp/` path in dev).

---
### 3.2 Get order detail
GET /orders/<id>/

Headers:
- Authorization: Bearer <ACCESS_TOKEN> (user must be authenticated; no extra restrictions in the current code)

Response: OrderDetail JSON

### 3.3 My orders (list for authenticated user)
GET /my-orders/

Headers:
- Authorization: Bearer <ACCESS_TOKEN>

Response: list of orders for the authenticated user (reverse chronological)

---
## 4) Invoice PDF endpoint (explicit)
GET /invoice/pdf/

Headers:
- Authorization: Bearer <ACCESS_TOKEN>

This endpoint in the repo currently renders a demo invoice using the logged-in user. It attempts to return a PDF (requires pdfkit + wkhtmltopdf) or HTML fallback.

Notes: checkout already generates and saves an invoice (one-to-one). You can fetch the saved invoice file path from the Order -> `invoice.pdf` field in the Order detail response and download if you want.

---
## 5) Admin endpoints (require admin JWT)
All admin endpoints require the Authorization header with an admin access token (user.is_superuser == True).

### 5.1 Stats
GET /admin/stats/

Headers:
- Authorization: Bearer <ADMIN_ACCESS_TOKEN>

Response JSON example:
{
  "cards": {
    "total_sales": {
      "value": 1200.5,
      "trend": 15.2,
      "trend_type": "up",
      "period": "30 dias"
    },
    "customers": {
      "value": 42,
      "trend": 5.0,
      "trend_type": "up",
      "period": "30 dias"
    },
    "todays_orders": {
      "value": 8,
      "trend": -12.5,
      "trend_type": "down",
      "period": "24h"
    },
    "completion_rate": {
      "value": 95.2,
      "period": "30 dias"
    }
  },
  "daily_sales": [
    {
      "day": "01",
      "total": 350.0,
      "count": 5
    },
    // ... mais 14 dias
  ]
}

### 5.2 List users
GET /admin/users/

Returns list of users (UserSerializer: id, email, name, phone, is_active).

### 5.3 User detail
GET /admin/users/<id>/
PUT /admin/users/<id>/
DELETE /admin/users/<id>/

PUT example to deactivate a user:
{
  "is_active": false
}

---
## 6) Realtime notifications (optional)

WebSocket endpoint (if Channels installed and running):

ws://localhost:8000/ws/notifications/

Behavior:
- When a Product or Order is saved the repo's `signals` broadcasts a message to group `notifications`.
- Messages are JSON objects like:
  { "event": "order_created", "id": 12, "total": "30.00" }

Client example (JS):
```js
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');
ws.onmessage = e => console.log('notif', JSON.parse(e.data));
```

Note: Channels and a channel layer (Redis for production) are recommended.

---
## 7) SMS (placeholder)

The project includes `api/utils/sms.py` with `send_sms(phone, text)` which currently logs and returns True. To send real SMS, implement provider integration (Tello or other) and store API key in environment variables.

---
## 8) Headers & auth summary
- For protected endpoints include: `Authorization: Bearer <ACCESS_TOKEN>`
- Always set `Content-Type: application/json` for JSON bodies.
- For file uploads use `multipart/form-data` and include `Authorization` header.

---
## 9) Test sequence (recommended)
1. Create a normal user: POST /auth/register/
2. Login: POST /auth/token/ -> get access token
3. Create a product (or prepare existing): POST /products/ (or via admin panel)
4. Checkout (POST /checkout/) with items
5. GET /my-orders/ to confirm order exists
6. Login as admin (or create admin with createsuperuser): POST /auth/admin/login/ -> get admin token
7. GET /admin/stats/ and GET /admin/users/
8. Connect to websocket ws://localhost:8000/ws/notifications/ (if channels running) and create/update a product/order to see messages

---
## 10) Troubleshooting
- If you receive import errors for `rest_framework` or `channels`, install dependencies in your venv:
  - `pip install djangorestframework djangorestframework-simplejwt django-cors-headers` (mandatory)
  - `pip install channels pdfkit Pillow` (optional; pdfkit requires wkhtmltopdf on OS)
- If `AUTH_USER_MODEL refers to model 'api.User' that has not been installed` occurs, ensure migrations exist and run `python manage.py makemigrations` then `python manage.py migrate`.
- Invoice PDF generation requires `wkhtmltopdf` installed system-wide when using `pdfkit`.

---
If quiser, eu posso também:
- Gerar uma coleção Postman/ApiDog (JSON export) para importar automaticamente.
- Adicionar exemplos de respostas mais detalhados.

Bom teste — diga se quer que eu gere a colecção Postman agora.