# University Transport System

A Flask-based web application for managing a university's bus transport service. It lets
**students** book bus seats online, **faculty/staff** request dedicated vehicles, and
**administrators** manage routes, schedules, off-days, payments, and feedback — all backed
by MySQL with email‑OTP verification at every sensitive step.

---

## Features

### 👤 Student
- **Account registration with email OTP** — sign up, receive a one‑time code by email, and
  verify before the account is created. Passwords are hashed with bcrypt.
- **Profile management** — full name, 8‑digit student ID, department, gender, address,
  mobile number, blood group, and a profile photo upload.
- **Seat booking flow:**
  - Pick a **route → stop → shift** and see a live seat map.
  - Seats are colour‑coded and **gender‑aware** (male‑reserved / female‑reserved seats).
  - Already‑booked seats are shown as unavailable in real time.
  - A **5‑minute hold timer** protects the seat while you complete booking.
  - **Booking rules enforced:** no booking on weekends or admin‑scheduled off‑days, and a
    user may hold at most one pickup and one drop‑off journey per day.
- **OTP‑confirmed booking** — a code is emailed to confirm the seat before payment.
- **Mock payment** — pay via bKash / Nagad / card with a mobile‑number → OTP → password
  popup flow; a payment record is stored against the booking.
- **Downloadable PDF ticket** — generates a branded ticket (passenger details, route, stop,
  date, shift, seat, ticket number) via fpdf2.
- **Ticket cancellation & refund** — cancel an upcoming ticket and run an OTP‑verified
  refund back to the original payment method.
- **Dashboard** — upcoming tickets, past travel history, submitted feedback, and a badge
  for unread admin replies.
- **Feedback** — rate a journey (1–5), leave comments tied to a bus/route/date, and see the
  admin's reply on your dashboard.

### 👨‍🏫 Faculty / Staff
- **Separate staff registration & login** with email OTP and bcrypt‑hashed passwords.
- **Staff profile** with a 5‑digit PIN, department, and contact details.
- **Vehicle requests** — request a dedicated vehicle (journey date, pickup time & location,
  destination, required capacity) for trips and events.
- **Request tracking** — see request status (Pending / Approved / Rejected), the admin's
  reply, and get an unread‑reply badge on the staff dashboard.

### 🛠️ Administrator
- **Admin dashboard with analytics** — total users, pending vehicle requests, pending
  feedback, total bookings, most‑used route, highest‑booking day, and peak travel hour.
- **Route management** — add bus routes (route name, bus number, driver, capacity).
- **Stop management** — add stops per route with stop type (pickup/drop‑off), fare, seat
  layout, and per‑gender reserved seats; supports multiple trip times (shifts) per stop.
- **Schedule management** — view and edit pickup/drop‑off times per route and shift; editing
  a time **emails affected users** about the change.
- **Off‑day management** — add or remove non‑service dates that block booking.
- **User & staff management** — searchable lists of students and staff, with the ability to
  remove accounts.
- **Vehicle request handling** — approve or reject staff requests with a reply; the staff
  member is **notified by email**.
- **Feedback moderation** — read all feedback, see the average rating, and reply to users.
- **Add additional admins.**

### ✉️ Platform / Infrastructure
- **Resilient email delivery** — uses the **Brevo HTTP API** (works over HTTPS, ideal for
  free hosts that block SMTP) when `BREVO_API_KEY` is set, and falls back to **SMTP**
  (Flask‑Mail) otherwise. See `deliver_email()` in [app.py](app.py).
- **OTP everywhere** — registration, seat confirmation, payment, and refunds are all
  OTP‑gated.
- **Background scheduler** (APScheduler) for releasing expired seat holds.
- **Deployment‑ready** — `Procfile`, `render.yaml`, `runtime.txt` (Python 3.12), and gunicorn
  config for Render and other Procfile hosts. See [DEPLOY.md](DEPLOY.md).

---

## Tech Stack

| Layer        | Technology                                              |
|--------------|---------------------------------------------------------|
| Backend      | Python, Flask, Flask‑WTF, WTForms                       |
| Database     | MySQL (via Flask‑MySQLdb / mysqlclient)                 |
| Auth         | bcrypt password hashing, session‑based auth, email OTP  |
| Email        | Brevo HTTP API (primary) with Flask‑Mail SMTP fallback  |
| PDF tickets  | fpdf2                                                    |
| Scheduling   | APScheduler                                             |
| Server       | gunicorn                                                 |
| Frontend     | Jinja2 templates, static CSS/JS                         |

---

## Getting Started (local)

```bash
# 1. Configure environment
cp .env.example .env        # fill in MySQL + email + SECRET_KEY values

# 2. Create the database and import the schema
#    (see db/mydatabase.sql)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py               # serves on http://localhost:5000
```

### Key environment variables
See [.env.example](.env.example) for the full list. The essentials:

- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
- `SECRET_KEY` — Flask session secret
- `BREVO_API_KEY`, `MAIL_SENDER`, `MAIL_SENDER_NAME` — recommended email path
- `MAIL_USERNAME`, `MAIL_PASSWORD` (Gmail App Password) — SMTP fallback

---

## Project Structure

```
app.py                 # All routes, forms, email, PDF, and scheduling logic
templates/             # Jinja2 templates (user, staff, admin, booking, payment)
static/                # CSS, images, uploads (profile photos, generated tickets)
db/mydatabase.sql      # MySQL schema (users, staffs, admins, bus_routes,
                       #   route_stops, trip_times, seat_bookings, payment_records,
                       #   feedback, vehicle_requests, bus_offdays, ...)
requirements.txt       # Python dependencies
DEPLOY.md              # Deployment guide (Render / Procfile hosts, email setup)
Procfile, render.yaml, runtime.txt   # Deployment config
```

## Deployment

See [DEPLOY.md](DEPLOY.md) for step‑by‑step instructions on hosting (Render blueprint or
manual service), setting up a free MySQL database, and configuring email so registration
OTPs deliver reliably.
