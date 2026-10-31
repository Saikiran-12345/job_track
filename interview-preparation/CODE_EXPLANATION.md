# JobTrack – File-by-File Code Explanation Guide

This guide walks through every critical code file in JobTrack, explaining **What it is**, **Why it is required**, **How functions work**, and **What happens during runtime user actions**.

---

## 1. `config/settings.py`

### What is this file?
The central configuration hub for the entire Django project.

### Why is it required?
Django reads `settings.py` during startup to know which apps are installed, which database to connect to, where templates and static files live, and which middleware to execute.

### Important Code Sections & Functions:
```python
# 1. Environment Variable Loading
load_dotenv(BASE_DIR / '.env')
SECRET_KEY = os.getenv('SECRET_KEY', 'default-key')

# 2. MySQL Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'jobtrack_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', '...'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```
- **What it does:** Uses `python-dotenv` to keep sensitive credentials outside source code. Connects Django to MySQL 8.0 on port 3306 with UTF-8 support.
- **Communication:** Every app (`accounts`, `jobs`, `interviews`, `api`) relies on `settings.py` for database connectivity and authentication rules.

---

## 2. `config/__init__.py`

### What is this file?
Package initialization script for the project root.

### Why is it required?
```python
import pymysql

pymysql.install_as_MySQLdb()
```
- **What it does:** Django looks for `MySQLdb` (the C-extension driver). PyMySQL is a pure-Python driver. `install_as_MySQLdb()` monkey-patches Python's module registry so Django uses PyMySQL seamlessly without needing C++ compilers.

---

## 3. `accounts/forms.py`

### What is this file?
Defines HTML form structures and Python validation logic for user authentication.

### Important Classes:
1. **`UserRegisterForm(forms.ModelForm)`**:
   - Fields: `first_name`, `last_name`, `username`, `email`, `password`, `confirm_password`.
   - `clean_email()`: Enforces case-insensitive email uniqueness.
   - `clean()`: Compares `password` and `confirm_password` and checks minimum 8 characters.
   - `save()`: Calls `user.set_password()` to generate a secure PBKDF2 hash before database insert.
2. **`UserProfileForm(forms.ModelForm)`**:
   - Lets users edit first name, last name, and email while ensuring email does not conflict with another account (`exclude(pk=self.user.pk)`).

---

## 4. `accounts/views.py`

### What is this file?
Controls authentication flow between templates and Django's user model.

### Key Functions:
- **`register_view(request)`**:
  - *Runtime Action:* When a user visits `/register/`, returns blank form. When user submits form (`POST`), validates fields. If valid, saves hashed user, attaches a success message, and redirects to `/login/`.
- **`login_view(request)`**:
  - *Runtime Action:* Validates credentials using Django's `AuthenticationForm`. On success, calls `login(request, user)` to write session cookies, then redirects to `/` (dashboard) or `next` URL.
- **`logout_view(request)`**:
  - *Runtime Action:* Calls `logout(request)` to delete session data and flush browser cookie. Redirects to `/login/`.
- **`profile_view(request)`**:
  - Decorated with `@login_required`. Calculates `request.user.job_applications.count()` and renders profile stats.

---

## 5. `jobs/models.py`

### What is this file?
The database entity definition for job applications.

### Important Fields & Methods:
```python
class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    company_name = models.CharField(max_length=150)
    job_title = models.CharField(max_length=150)
    job_location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    application_status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    application_date = models.DateField(default=timezone.now)
    salary = models.CharField(max_length=50, blank=True)
    ...
```
- **`user = models.ForeignKey(User, on_delete=models.CASCADE)`**: Ties every application to a User. If user is deleted, their applications are also deleted.
- **`get_status_badge_class()`**: Model helper returning the CSS class (`badge-status-applied`, `badge-status-shortlisted`, etc.) so templates stay clean and logic stays in the model.

---

## 6. `jobs/views.py`

### What is this file?
Executes business logic for listing, searching, filtering, creating, updating, and deleting job applications.

### Key Functions:
1. **`job_list_view(request)`**:
   ```python
   applications = JobApplication.objects.filter(user=request.user)
   if search_query:
       applications = applications.filter(
           Q(company_name__icontains=search_query) |
           Q(job_title__icontains=search_query) |
           Q(job_location__icontains=search_query)
       )
   ```
   - *Why `Q` objects?* `Q` enables complex SQL `OR` queries in Django ORM.
   - *Pagination:* Uses `Paginator(applications, 10)` so large application lists load smoothly.
2. **`job_detail_view(request, pk)`**:
   - Uses `get_object_or_404(JobApplication, pk=pk, user=request.user)`.
   - *Security:* If `user=request.user` does not match the record, Django immediately returns an HTTP 404 error, preventing unauthorized data snooping.
3. **`job_create_view(request)`**:
   - `application = form.save(commit=False)` &rarr; `application.user = request.user` &rarr; `application.save()`.
4. **`job_delete_view(request, pk)`**:
   - Verifies user ownership and calls `application.delete()`.

---

## 7. `jobs/views_dashboard.py`

### What is this file?
Dedicated module for computing dynamic dashboard metrics and Chart.js analytics.

### Key Logic:
- Counts applications by status:
  ```python
  applied_count = user_apps.filter(application_status='Applied').count()
  shortlisted_count = user_apps.filter(application_status='Shortlisted').count()
  ```
- Computes interview conversion rate and selection rate.
- Aggregates applications over the last 6 months into an `OrderedDict`.
- Uses `json.dumps()` to pass clean JSON arrays (`status_labels_json`, `trend_values_json`) to the template for seamless Chart.js rendering.

---

## 8. `interviews/models.py`

### What is this file?
Defines the `Interview` model for multi-round interview tracking.

### Key Fields & Properties:
```python
class Interview(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interview_round = models.CharField(max_length=30, choices=ROUND_CHOICES)
    interview_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    location_or_link = models.CharField(max_length=255, blank=True)
    notes_or_feedback = models.TextField(blank=True)
```
- **`is_upcoming` Property:** Checks `interview_date >= timezone.now() and status == 'Scheduled'`.

---

## 9. `interviews/views.py`

### Key Highlights:
1. **`interview_create_view(request)`**:
   - When a user schedules an interview, the system inspects `job_application.application_status`.
   - If it was `Applied`, it automatically upgrades the application status to `Interview`:
     ```python
     if interview.job_application.application_status == JobApplication.STATUS_APPLIED:
         interview.job_application.application_status = JobApplication.STATUS_INTERVIEW
         interview.job_application.save(update_fields=['application_status'])
     ```
2. **`interview_create_for_job_view(request, job_pk)`**:
   - Direct shortcut from the Job Detail page pre-filling the target application.

---

## 10. `api/serializers.py` & `api/views.py`

### What are these files?
The REST API layer powered by Django REST Framework (DRF).

### Key Components:
- **`JobApplicationSerializer`**: Converts model instances into JSON format and validates API payloads. Includes nested `interviews` array.
- **`JobApplicationViewSet` & `InterviewViewSet`**:
  - `permission_classes = [permissions.IsAuthenticated]`
  - `get_queryset()`: Enforces `filter(user=self.request.user)` and `filter(job_application__user=self.request.user)`.
- **`DashboardStatsAPIView`**: Returns live JSON statistics for single-page apps or mobile clients.
