# SL Insight Dashboard

A real-time analytics + control dashboard connecting Second Life (LSL) with a web-based system.

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env  # Edit with your settings
python manage.py migrate
python manage.py createsuperuser  # Use any SL avatar name
python manage.py runserver
```

For WebSocket support (instead of `runserver`):

```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Redis (required for WebSockets & OTP queue)

```bash
# macOS
brew install redis && redis-server

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis

# Windows — use WSL or Memurai
```

## API Docs

| Method | Endpoint                  | Auth    | Source |
|--------|---------------------------|---------|--------|
| POST   | /api/auth/send-otp/       | Public  | Web    |
| POST   | /api/auth/verify-otp/     | Public  | Web    |
| POST   | /api/auth/refresh/        | Public  | Web    |
| GET    | /api/auth/profile/        | JWT     | Web    |
| PATCH  | /api/auth/profile/update/ | JWT     | Web    |
| GET    | /api/auth/pending-otps/   | API Key | LSL    |
| POST   | /api/scan/region/         | API Key | LSL    |
| POST   | /api/scan/avatars/        | API Key | LSL    |
| POST   | /api/scan/parcels/        | API Key | LSL    |
| GET    | /api/scan/regions/        | JWT     | Web    |
| GET    | /api/scan/sessions/       | JWT     | Web    |
| POST   | /api/message/send/        | JWT     | Web    |
| GET    | /api/message/history/     | JWT     | Web    |
| GET    | /api/message/pending/     | API Key | LSL    |
| POST   | /api/message/confirm/     | API Key | LSL    |
| POST   | /api/discord/configure/   | JWT     | Web    |
| GET    | /api/discord/config/      | JWT     | Web    |
| GET    | /api/analytics/visitors/  | JWT     | Web    |
| GET    | /api/analytics/peak-hours/| JWT     | Web    |
| GET    | /api/analytics/overview/  | JWT     | Web    |

## LSL Scripts

Place in your Second Life objects:
- `backend/lsl_scripts/scanner_object.lsl` — Avatar/region/parcel scanner
- `backend/lsl_scripts/messaging_relay.lsl` — IM relay + OTP delivery
```