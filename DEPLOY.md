# Deployment Guide

This is a Flask app (gunicorn + MySQL + email OTP). Below is how to deploy it to a
free host and, importantly, how the **registration / email problem is fixed**.

## Why registration failed on Render (and the fix)

Registration sends an OTP email. The old code only used **SMTP** (Gmail on port 587).
On free hosts like Render, outbound SMTP is commonly **blocked or slow**, so the request
hung until gunicorn's 30s worker timeout killed it → register appeared to "fail".

This is now fixed two ways:

1. **HTTP email API (recommended).** When `BREVO_API_KEY` is set, all mail is sent through
   Brevo's HTTPS API (port 443, never blocked). See `deliver_email()` in `app.py`.
2. **Resilience.** SMTP now has a timeout, gunicorn runs with `--timeout 120`, and SMTP is
   only a fallback. If Brevo fails, it falls back to SMTP automatically.

## 1. Set up email (5 minutes, free)

1. Create a free account at <https://www.brevo.com> (300 emails/day free).
2. **Senders & IPs → Senders**: add and verify the email you want to send *from*.
3. **SMTP & API → API Keys**: create a key.
4. You'll set these env vars on your host:
   - `BREVO_API_KEY` = the key
   - `MAIL_SENDER` = your verified sender email
   - `MAIL_SENDER_NAME` = `University Transport System`

> No Brevo? Leave `BREVO_API_KEY` empty and configure SMTP instead — but use a Gmail
> **App Password**, and pick a host that allows SMTP.

## 2. Set up a free MySQL database

Render has no free MySQL, so use an external one (free tiers):
[Railway](https://railway.app), [Aiven](https://aiven.io), or
[Clever Cloud](https://www.clever-cloud.com). Create a MySQL instance, import your schema
(see `db/`), and note host/port/user/password/db name.

## 3. Deploy on Render

**Option A — Blueprint (uses `render.yaml`):**
1. Push this repo to GitHub.
2. Render Dashboard → **New + → Blueprint** → select the repo.
3. Fill in the `sync: false` env vars (DB + Brevo) when prompted. Deploy.

**Option B — Manual web service:**
1. New + → **Web Service** → connect repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2`
4. Add the env vars from `.env.example` (DB + email + `SECRET_KEY`).

## 4. Other free hosts

The `Procfile` works on any Procfile-based host (Railway, Heroku-likes). Just set the same
env vars. `runtime.txt` pins Python 3.12.

## Local development

```bash
cp .env.example .env   # fill in values
pip install -r requirements.txt
python app.py
```

## Troubleshooting

- **Register still fails:** check logs. If you see Brevo errors, the sender isn't verified
  or the key is wrong. If you see SMTP timeouts, set `BREVO_API_KEY`.
- **`mysqlclient` build error:** ensure the host provides MySQL client headers; on Render's
  native Python runtime this is included. If not, switch the driver to `PyMySQL`.
