# JobTrack – Troubleshooting & Common Errors Guide

A practical troubleshooting manual documenting common development and deployment errors encountered in Python, Django, and MySQL, explaining their root causes and verified solutions.

---

## 1. MySQL Connection Error: `1045 (28000): Access denied for user 'root'@'localhost'`

### Symptom:
Running `python manage.py migrate` or starting the app raises:
```text
django.db.utils.OperationalError: (1045, "Access denied for user 'root'@'localhost' (using password: YES)")
```

### Cause:
The password specified in `.env` (`DB_PASSWORD`) does not match the actual root password of the local MySQL instance, or the root user is configured for Windows socket/plugin authentication.

### Solution:
1. Verify the password by opening PowerShell and testing a direct login:
   ```powershell
   mysql -u root -p
   ```
2. Enter your MySQL password. Once verified, update the `.env` file:
   ```ini
   DB_PASSWORD=YourVerifiedPassword
   ```
3. If you forgot the root password on Windows, reset it through MySQL Installer or start the MySQL service with `--skip-grant-tables`.

---

## 2. MySQL Windows Build Failure: `error: Microsoft Visual C++ 14.0 or greater is required`

### Symptom:
Attempting `pip install mysqlclient` fails with a C++ compilation error on Windows.

### Cause:
`mysqlclient` contains C-extensions that need Microsoft Visual Studio C++ build tools installed on Windows.

### Solution:
JobTrack uses `pymysql` (a pure Python driver).
1. Install `pymysql` and `cryptography`:
   ```powershell
   pip install pymysql cryptography
   ```
2. Verify `config/__init__.py` contains:
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```
This instructs Django to use PyMySQL as its drop-in MySQLdb replacement without needing any C++ compilation!

---

## 3. HTTP 403 Forbidden: `CSRF verification failed. Request aborted.`

### Symptom:
Submitting an application, login, or registration form displays a 403 Forbidden error page stating "CSRF verification failed".

### Cause:
The HTML form does not include Django's CSRF token, or browser cookies were blocked/cleared during submission.

### Solution:
Ensure every `<form method="POST">` in templates contains the CSRF token tag right below the opening form tag:
```html
<form method="POST">
    {% csrf_token %}
    ...
</form>
```
For API calls via Postman or cURL, pass the `X-CSRFToken` header or use Session/Token authentication.

---

## 4. URL Reverse Error: `NoReverseMatch: Reverse for 'xyz' not found`

### Symptom:
```text
django.urls.exceptions.NoReverseMatch: Reverse for 'job_detail' with arguments '()' not found. 1 pattern(s) tried: ['applications/(?P<pk>[0-9]+)/$']
```

### Cause:
A template or view called `{% url 'job_detail' %}` without providing the required positional or keyword argument (e.g. `pk`).

### Solution:
Supply the required primary key in the template:
```html
<!-- Correct -->
<a href="{% url 'job_detail' job.pk %}">View Details</a>

<!-- Incorrect -->
<a href="{% url 'job_detail' %}">View Details</a>
```

---

## 5. Port Conflict: `Error: That port is already in use.`

### Symptom:
Running `python manage.py runserver` fails with:
```text
Error: That port is already in use.
```

### Cause:
Another instance of Django or another application is already listening on `127.0.0.1:8000`.

### Solution:
1. Run server on another port:
   ```powershell
   python manage.py runserver 8080
   ```
2. Or kill the existing process on Windows:
   ```powershell
   Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
   ```

---

## 6. Static Files 404: CSS or JS styles not rendering

### Symptom:
Pages load unstyled with browser console reporting `GET /static/css/custom.css 404 (Not Found)`.

### Cause:
`STATICFILES_DIRS` is missing in `settings.py`, or `{% load static %}` was omitted in the template.

### Solution:
1. In `config/settings.py`:
   ```python
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   ```
2. In `templates/base.html`:
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/custom.css' %}">
   ```

---

## 7. User Data Leaking Across Sessions (Horizontal Privilege Escalation)

### Symptom:
User A logs in and can see or edit User B's job application records.

### Cause:
View queries use `.all()` instead of filtering by the authenticated user (`.filter(user=request.user)`).

### Solution:
Always scope queries to `request.user`:
```python
# Unsafe
applications = JobApplication.objects.all()

# Safe & Isolated
applications = JobApplication.objects.filter(user=request.user)
```
For detail and delete views:
```python
application = get_object_or_404(JobApplication, pk=pk, user=request.user)
```

---

## 8. Migration Drift: `django.db.utils.OperationalError: (1050, "Table '...' already exists")`

### Symptom:
Applying migrations raises error 1050 because tables already exist in MySQL.

### Cause:
Database was manually created or migrations were applied out of sync.

### Solution:
Fake the migration so Django records it in `django_migrations` without re-creating existing tables:
```powershell
python manage.py migrate --fake-initial
```
Or reset the local development database cleanly:
```sql
DROP DATABASE jobtrack_db;
CREATE DATABASE jobtrack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then run:
```powershell
python manage.py migrate
```
