# Eye Clinic Management System

This branch converts the original multi-hospital appointment prototype into a focused eye-clinic management platform. The `main` branch remains unchanged.

## Target modules

1. Staff accounts and role-based permissions
2. Patient registration and searchable patient numbers
3. Appointments, queue, consultations, diagnoses and clinical notes
4. Eye examinations and right/left-eye measurements
5. Glasses and contact-lens prescriptions
6. Medication prescriptions, dispensing and refill/expiry tracking
7. Automated SMS reminders with delivery logs and retry protection
8. Optical and pharmacy inventory, suppliers, purchases and stock movements
9. Invoices, payments, refunds, expenses, cash sessions and financial reports
10. Documents, audit trail, dashboards, exports, backups and configuration

## Delivery phases

- Phase 1: repository cleanup, secure settings, architecture and test foundation
- Phase 2: clinic, staff, patient and appointment management
- Phase 3: consultations, eye examinations and prescriptions
- Phase 4: SMS reminder engine and notification history
- Phase 5: inventory, dispensing and optical orders
- Phase 6: billing, payments, expenses and reports
- Phase 7: dashboard redesign, exports, security hardening and deployment

## Important domain rule

A prescription does not literally “expire” in every case. The system records an explicit review or expiry date chosen by the clinician. Reminder schedules are calculated from that date, and duplicate SMS messages are prevented with a notification log.

## Local setup

Create a `.env` file from `.env.example`, install `requirements.txt`, run migrations and create a superuser. Production deployments must use PostgreSQL, a background worker/scheduler, HTTPS and environment-managed secrets.
