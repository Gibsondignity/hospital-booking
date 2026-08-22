# Eye Clinic Management System

The `eye-clinic-management` branch converts the original multi-hospital appointment prototype into a dedicated, single-clinic eye-care management system. The `main` branch remains unchanged.

## Implemented foundation

- Single active clinic configuration with contact details, branding, Ghana cedi currency, Africa/Accra timezone, configurable business-number prefixes, appointment duration and prescription validity defaults.
- One Django user account per staff member, staff profiles, nine role groups and enforced server-side permissions.
- Patient registration, independent patient numbers, Ghana phone normalisation, duplicate warnings, Ghana Card uniqueness, search, pagination and longitudinal patient profiles.
- Separate basic medical histories with clinician-only access.
- Eye-clinic appointments with references, practitioner validation, clash prevention and tracked status.
- Appointment check-in, walk-in encounters, waiting queue and consultation status transitions.
- Dashboard metrics calculated only from real patient, appointment and visit records.
- Privacy-conscious audit events and a configurable SMS service boundary without a scheduler.

## Application structure

- `accounts`: staff authentication, central user roles and staff account management.
- `clinic`: clinic configuration, staff profiles, business-number sequences, audit events, roles and SMS abstraction.
- `patients`: patient identity, medical history, search and patient profiles.
- `appointment`: eye-clinic scheduling and appointment check-in.
- `visits`: actual clinic encounters, walk-ins and waiting queues.
- `dashboard`: responsive clinic dashboard and shared authenticated navigation.

## Staff roles

| Role | Current access |
| --- | --- |
| System Administrator | All configured application permissions |
| Clinic Administrator | All configured application permissions |
| Optometrist | Patients, appointments, visits, medical histories and consultation state |
| Ophthalmologist | Patients, appointments, visits, medical histories and consultation state |
| Nurse | Patients, appointments, visits and read-only sensitive medical history |
| Receptionist | Patient registration, basic patient updates, appointments, check-in and walk-ins |
| Optician | Read-only patient, appointment and visit access |
| Pharmacist / Dispensing Staff | Read-only patient and visit access |
| Accountant / Cashier | Read-only patient, appointment and visit access; finance permissions arrive with billing |

Permissions are assigned through Django groups. Hidden navigation is supplementary; each internal route enforces authentication and permissions on the backend.

## Business identifiers

Patient numbers use the configured patient prefix and an independent sequence, for example `EC-000001`. Appointment numbers use `APT-000001`, visits use `VIS-000001`, and staff profiles use `STF-000001`. These identifiers do not derive from database primary keys.

## Appointment and visit workflow

1. Register or locate a patient.
2. Schedule an eye examination, consultation, refraction, review, follow-up, emergency or another appointment type.
3. Check in a scheduled or confirmed appointment to create exactly one actual visit.
4. Alternatively, create a walk-in visit without an appointment.
5. A clinician starts the consultation and subsequently marks the visit complete.
6. Appointment state follows the corresponding visit state.

## Environment variables

Copy `.env.example` for reference and export the selected values into the application environment before starting Django. At minimum configure:

- `DJANGO_SECRET_KEY`: required whenever `DJANGO_DEBUG=False`.
- `DJANGO_DEBUG`: `True` only for local development.
- `DJANGO_ALLOWED_HOSTS`: comma-separated host names.
- `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`, `DJANGO_SECURE_HSTS_PRELOAD`: deployment HTTPS and HSTS controls; production defaults enable HTTPS redirects and one year of HSTS. Enable subdomain coverage and preloading only after confirming that every applicable hostname supports HTTPS.
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: database settings; SQLite is supported locally and PostgreSQL can be configured for production.
- `ARKESSEL_API_KEY`, `ARKESSEL_SENDER_ID`, `SMS_PROVIDER`: SMS provider settings; credentials are never committed.

The project intentionally does not automatically parse `.env` files. Configure the environment through your shell, Docker Compose, systemd or the deployment platform.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_DEBUG=True
export DJANGO_SECRET_KEY='replace-with-a-long-random-development-secret'
python manage.py migrate
python manage.py setup_clinic_roles
python manage.py createsuperuser
python manage.py runserver
```

After creating a superuser, use `/admin/` to create the clinic configuration. Administrators can then create staff accounts through the application or configure staff profiles through Django administration.

## Verification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test --verbosity 2
```

Development-only database files, uploads, secrets, Python bytecode and virtual environments are ignored by Git.

## Security and migration notes

The branch removes obsolete public self-registration, CSRF-exempt public booking, multi-hospital management, generic doctors, duplicate bookings, blocked slots and old hospital-specific audit models. Existing historical migrations are retained so clean databases can still replay the original migration history before applying the eye-clinic transformation.

Production startup fails when `DJANGO_SECRET_KEY` is absent and debugging is disabled. Medical history is not available to receptionists or cashiers, and audit metadata excludes passwords, tokens, API keys and clinical notes.

## Next phase

**Clinical Consultation & Eye Examination Module**: consultation history, chief complaint, visual acuity, refraction, eye measurements, examination findings, diagnoses, clinical notes, eye prescriptions and follow-up recommendations. Prescription reminders, optical stock, pharmacy inventory, accounting and SMS scheduling remain separate later phases.
