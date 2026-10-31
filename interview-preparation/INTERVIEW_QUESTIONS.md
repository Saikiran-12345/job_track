# JobTrack – 50+ Technical Interview Questions & Answers

A curated question bank covering Python, OOP, Django, ORM, MySQL, SQL, Frontend, REST API, Git, and Project Scenarios.

---

## Category 1: Python Fundamentals & OOP (Q1 – Q10)

### Q1: What are Python's key features?
**Answer:** Python is an interpreted, high-level, dynamically typed language with clean syntax. It supports multiple paradigms (Object-Oriented, Functional, Procedural), has automatic memory management (garbage collection), and a massive standard library.

### Q2: What is the difference between mutable and immutable data types in Python?
**Answer:**
- **Mutable:** Objects whose content can be modified after creation (e.g. `list`, `dict`, `set`).
- **Immutable:** Objects whose content cannot be changed (e.g. `int`, `float`, `str`, `tuple`).
- *Example:* Modifying a string creates a new string object in memory.

### Q3: Explain the 4 core pillars of Object-Oriented Programming (OOP) with examples from JobTrack.
**Answer:**
1. **Encapsulation:** Grouping data and methods together inside a class. In `JobApplication`, data fields and `get_status_badge_class()` are encapsulated together.
2. **Inheritance:** Creating a new class from an existing class. In `api/serializers.py`, `JobApplicationSerializer` inherits from `serializers.ModelSerializer`.
3. **Polymorphism:** The ability of different classes to respond to the same method name. Both `JobApplication` and `Interview` implement `__str__()` returning custom descriptive strings.
4. **Abstraction:** Hiding complex underlying implementation and exposing only necessary details. Django's ORM abstracts complex SQL `JOIN` and `GROUP BY` statements behind simple Python methods like `.filter()` and `.count()`.

### Q4: What is the purpose of `__init__` in Python classes?
**Answer:** `__init__` is a special constructor method automatically called when a new instance of a class is instantiated. In `InterviewForm`, we override `__init__(self, *args, user=None, **kwargs)` to customize the `job_application` dropdown queryset dynamically based on the logged-in user.

### Q5: What is the difference between `args` and `kwargs`?
**Answer:**
- `*args` allows passing a variable number of positional arguments as a tuple.
- `**kwargs` allows passing a variable number of keyword (named) arguments as a dictionary.

### Q6: What are decorators in Python and how did you use them?
**Answer:** A decorator is a higher-order function that takes another function as an argument, extends or modifies its behavior, and returns a new function without altering the original code. In JobTrack, we used `@login_required` to protect views so unauthenticated users cannot view the dashboard or delete applications.

### Q7: How does Python manage memory?
**Answer:** Python uses private heap space managed by the Python memory manager. It uses **reference counting** (destroying objects when reference count drops to zero) alongside a cyclic **garbage collector** to clean up circular references.

### Q8: What is the difference between `is` and `==`?
**Answer:**
- `==` checks for equality of **values** (`[1, 2] == [1, 2]` is `True`).
- `is` checks for **identity** (whether both variables point to the exact same memory address).

### Q9: What are list comprehensions and why use them?
**Answer:** A concise syntax to construct lists based on existing iterables.
- *Example from JobTrack:* `company_names = [app.company_name for app in applications]`

### Q10: How does exception handling work in Python?
**Answer:** Handled via `try`, `except`, `else`, and `finally` blocks.
```python
try:
    application = JobApplication.objects.get(pk=1)
except JobApplication.DoesNotExist:
    # Handle missing record
```

---

## Category 2: Django & Architecture (Q11 – Q20)

### Q11: What is Django's architecture?
**Answer:** Django follows the **MVT (Model-View-Template)** architecture:
- **Model:** Defines database structure and business data rules (`models.py`).
- **View:** Contains business logic, queries the Model, and selects which template to render (`views.py`).
- **Template:** Presentation layer containing HTML and Django Template Language (DTL) tags (`templates/`).

### Q12: What is the difference between MVC and MVT?
**Answer:** In traditional MVC, the Controller handles routing and request processing. In Django's MVT, the framework itself acts as the Controller (via URL dispatcher and middleware), while the Django **View** acts like the MVC Controller and the **Template** acts like the View.

### Q13: What is the role of `manage.py`?
**Answer:** A command-line utility for executing project-specific tasks, such as `python manage.py runserver`, `makemigrations`, `migrate`, `createsuperuser`, and `test`.

### Q14: Explain the difference between `makemigrations` and `migrate`.
**Answer:**
- `makemigrations`: Inspects changes in `models.py` and creates Python migration files in the `migrations/` folder (acting as blueprints).
- `migrate`: Reads migration files and executes actual `CREATE TABLE` or `ALTER TABLE` SQL commands against the connected database (MySQL).

### Q15: What is Django Middleware?
**Answer:** A framework of hooks into Django’s request/response processing. It is a light, low-level plugin system for globally altering Django’s input or output. Examples: `AuthenticationMiddleware`, `CsrfViewMiddleware`.

### Q16: How does Django handle CSRF protection?
**Answer:** Through `CsrfViewMiddleware` and the `{% csrf_token %}` template tag. When rendering a form, Django generates a cryptographically secure token stored in a cookie. When submitting `POST`, the token in the form must match the cookie, preventing malicious third-party sites from executing forged requests.

### Q17: What are Context Processors in Django?
**Answer:** Python functions that automatically inject variables into the context of every rendered template. For example, `django.contrib.auth.context_processors.auth` makes `{{ user }}` accessible in all templates without passing it manually.

### Q18: What is the difference between `DateField` and `DateTimeField`?
**Answer:**
- `DateField` stores only the date (`YYYY-MM-DD`). Used for `application_date`.
- `DateTimeField` stores both date and exact time (`YYYY-MM-DD HH:MM:SS`). Used for `interview_date` and `created_at`.

### Q19: What is `select_related()` vs `prefetch_related()`?
**Answer:**
- `select_related()`: Performs an SQL `INNER JOIN` in a single query. Best for single-valued relationships (`ForeignKey` and `OneToOne`). Used in JobTrack for fetching interviews with their job application: `Interview.objects.select_related('job_application')`.
- `prefetch_related()`: Executes separate queries and joins data in Python. Best for many-to-many and reverse `ForeignKey` sets.

### Q20: How did you implement user data isolation in JobTrack?
**Answer:**
1. In Views: `JobApplication.objects.filter(user=request.user)`.
2. In Detail/Update/Delete Views: `get_object_or_404(JobApplication, pk=pk, user=request.user)`.
3. In Forms: Restricting dropdown choices to `user=request.user`.
4. In DRF: Overriding `get_queryset()` to filter by `self.request.user`.

---

## Category 3: MySQL & SQL Database (Q21 – Q28)

### Q21: What are Primary Keys and Foreign Keys?
**Answer:**
- **Primary Key (PK):** A column (or set of columns) that uniquely identifies each row in a table. In `JobApplication`, `id` is the auto-increment PK.
- **Foreign Key (FK):** A field in one table that links to the Primary Key of another table, enforcing referential integrity. `job_application_id` in `interviews_interview` references `id` in `jobs_jobapplication`.

### Q22: What is `ON DELETE CASCADE`?
**Answer:** A referential constraint specifying that if a parent record is deleted, all related child records are automatically deleted by the database. In JobTrack, if a job application is deleted, its scheduled interviews are cascaded and deleted.

### Q23: What are database indexes and why are they used?
**Answer:** An index is a data structure (commonly B-Tree) that speeds up data retrieval operations on a table at the cost of slower writes and additional storage. In `JobApplication`, we indexed `['user', 'application_status']` to accelerate dashboard and filter queries.

### Q24: What is database normalization?
**Answer:** The process of structuring a relational database to reduce data redundancy and improve data integrity (1NF, 2NF, 3NF). In JobTrack, interviews are kept in a separate table rather than storing multiple interview columns inside the job application table.

### Q25: Write an SQL query equivalent to `JobApplication.objects.filter(user=request.user, application_status='Shortlisted')`.
**Answer:**
```sql
SELECT * FROM jobs_jobapplication
WHERE user_id = 1 AND application_status = 'Shortlisted'
ORDER BY application_date DESC;
```

### Q26: What is the difference between `CHAR` and `VARCHAR`?
**Answer:**
- `CHAR` is fixed-length (pads with spaces up to length).
- `VARCHAR` is variable-length (stores only actual characters plus prefix byte for length), saving disk space.

### Q27: How does MySQL handle transactions?
**Answer:** MySQL with the InnoDB engine supports ACID transactions via `START TRANSACTION`, `COMMIT`, and `ROLLBACK`. Django wraps requests or `transaction.atomic()` blocks in transactions.

### Q28: How do you connect Django to MySQL 8.0 on Windows?
**Answer:** By installing `pymysql` and `cryptography` (for MySQL 8's `caching_sha2_password` authentication), and adding `pymysql.install_as_MySQLdb()` in `config/__init__.py`.

---

## Category 4: REST APIs & Django REST Framework (Q29 – Q36)

### Q29: What is a REST API?
**Answer:** **Representational State Transfer** is an architectural style for web services using stateless HTTP requests, standard HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), and resource-oriented URIs with JSON payloads.

### Q30: What is the difference between PUT and PATCH?
**Answer:**
- `PUT`: Replaces the entire resource. All required fields must be supplied.
- `PATCH`: Partially updates specific fields without modifying untouched fields.

### Q31: What are standard HTTP Status Codes?
**Answer:**
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `204 No Content`: Resource successfully deleted.
- `400 Bad Request`: Validation failure or invalid data.
- `401 Unauthorized`: Authentication credentials missing or invalid.
- `403 Forbidden`: Authenticated, but not authorized to perform this action.
- `404 Not Found`: Resource does not exist.
- `500 Internal Server Error`: Unhandled server-side exception.

### Q32: What is a DRF Serializer?
**Answer:** A class that converts complex Django model instances into Python native datatypes (which easily render into JSON) and validates incoming JSON payloads to save them back into models.

### Q33: What is the difference between `APIView` and `ModelViewSet` in DRF?
**Answer:**
- `APIView`: Low-level view providing explicit HTTP method handlers (`get()`, `post()`, `put()`, `delete()`). Used for `/api/dashboard/`.
- `ModelViewSet`: High-level class providing standard CRUD operations (`list`, `create`, `retrieve`, `update`, `destroy`) automatically bound to a model. Used for `/api/applications/`.

### Q34: What is `read_only_fields` in a ModelSerializer?
**Answer:** Fields that the serializer includes in outgoing JSON responses but ignores during incoming `POST` or `PUT` payloads (e.g. `id`, `created_at`, `user`).

### Q35: How do you protect DRF endpoints?
**Answer:** By configuring `permission_classes = [permissions.IsAuthenticated]`. Unauthenticated requests receive HTTP 403 Forbidden.

### Q36: How does DRF handle pagination?
**Answer:** Through `PageNumberPagination` configured in `settings.py` (`PAGE_SIZE = 10`), returning paginated JSON with `count`, `next`, `previous`, and `results`.

---

## Category 5: Frontend, Bootstrap & JavaScript (Q37 – Q42)

### Q37: What is Bootstrap 5 and why use it?
**Answer:** A modern, mobile-first CSS framework providing a responsive 12-column grid system, pre-styled components (cards, badges, modals, navbars), and utility classes without requiring jQuery.

### Q38: How does the Bootstrap grid system work?
**Answer:** It divides each row into 12 virtual columns. Using classes like `col-12 col-md-6 col-lg-4`, layout adapts across mobile, tablet, and desktop viewports.

### Q39: How did you integrate Chart.js into JobTrack?
**Answer:**
1. Loaded Chart.js via CDN (`chart.umd.min.js`).
2. Prepared JSON arrays server-side in `jobs/views_dashboard.py` using `json.dumps()`.
3. Injected data into template via `{{ trend_labels_json|safe }}`.
4. Instantiated `new Chart(ctx, { type: 'line', data: {...} })`.

### Q40: What is the DOM (Document Object Model)?
**Answer:** An object-oriented tree representation of the structured HTML document created by the browser, allowing JavaScript to dynamically inspect and manipulate styles, attributes, and elements.

### Q41: Why use `document.addEventListener('DOMContentLoaded', ...)`?
**Answer:** Ensures that JavaScript executes only after the entire HTML document has been parsed and loaded into the DOM, preventing errors when querying elements.

### Q42: What is the difference between `null` and `undefined` in JavaScript?
**Answer:**
- `undefined`: A variable that has been declared but has not yet been assigned a value.
- `null`: An intentional assignment value representing "no value" or an empty object.

---

## Category 6: Git & Version Control (Q43 – Q46)

### Q43: What is the difference between `git add` and `git commit`?
**Answer:**
- `git add`: Stages changed files in the index, preparing them to be committed.
- `git commit`: Captures a snapshot of the staged changes with a descriptive message in local repository history.

### Q44: What is the purpose of `.gitignore`?
**Answer:** Tells Git which files and directories should never be tracked or committed (e.g. `.env`, `__pycache__/`, `db.sqlite3`, `venv/`).

### Q45: What is a Git remote?
**Answer:** A common repository hosted on the internet or network (e.g. `https://github.com/Saikiran-12345/job_track.git`) that collaborators push to and pull from.

### Q46: How do you resolve a Git merge conflict?
**Answer:** Open conflicting files, inspect conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), choose the correct code, remove markers, stage the file with `git add`, and finalize with `git commit`.

---

## Category 7: Project-Specific Scenarios (Q47 – Q52)

### Q47: What happens when a user registers with an existing email?
**Answer:** In `accounts/forms.py`, `clean_email()` checks `User.objects.filter(email__iexact=email).exists()`. If true, it raises a `forms.ValidationError("An account with this email address already exists.")` and re-renders the registration page with inline error feedback.

### Q48: What happens when User A tries to view User B's job application by typing `/applications/45/` in the URL?
**Answer:** `job_detail_view` calls `get_object_or_404(JobApplication, pk=45, user=request.user)`. Because `user` does not match, the query returns no matching row, and Django immediately raises an `Http404` exception rendering `templates/404.html`.

### Q49: How does the application status automatically change when scheduling an interview?
**Answer:** In `interviews/views.py`:
```python
if interview.job_application.application_status == JobApplication.STATUS_APPLIED:
    interview.job_application.application_status = JobApplication.STATUS_INTERVIEW
    interview.job_application.save(update_fields=['application_status'])
```
When an interview is created for a job marked "Applied", it automatically moves to "Interview".

### Q50: How do you prevent SQL injection in Django?
**Answer:** By using Django's ORM. The ORM automatically parameterizes SQL queries, separating query commands from user input values so input is treated purely as data, not executable code.

### Q51: How did you write automated tests for JobTrack?
**Answer:** Using Django's `TestCase` class and DRF's `APIClient`. Wrote 31 automated tests in `tests/` testing user registration, password hashing, CRUD operations, unauthorized access restrictions, form validation, and REST API endpoints.

### Q52: If this application experiences high traffic, what are 3 things you would optimize?
**Answer:**
1. **Database Query Caching:** Cache dashboard metrics and counts using Redis and Django's caching framework (`django.core.cache`).
2. **Database Connection Pooling:** Use a connection pooler like ProxySQL or persistent database connections (`CONN_MAX_AGE = 600`).
3. **Static File Offloading:** Serve static CSS/JS through a CDN (AWS CloudFront / Cloudflare) using Whitenoise or AWS S3.
