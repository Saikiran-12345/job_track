# JobTrack – 5–7 Minute Technical Project Demo Script

> **Instructions for the Candidate:** Speak clearly, maintain a friendly and confident tone, and walk the interviewer through your application step-by-step. Keep your browser open with the application running on `http://127.0.0.1:8000/`.

---

## Part 1: Project Introduction (0:00 – 0:45)

> *"Good morning / afternoon sir/ma'am. Today, I am excited to demonstrate my full-stack web application called **JobTrack**.*
> 
> *As a fresher actively applying for software developer positions across portals like LinkedIn, Naukri, and company career pages, I realized how difficult it is to stay organized. Candidates frequently miss interview deadlines, lose track of recruiter feedback, and struggle to see their job search progress.*
> 
> *To solve this, I designed and developed **JobTrack** using **Python, Django, MySQL, Django REST Framework, and Bootstrap 5**. It provides complete application tracking, multi-round interview scheduling, real-time analytics, and RESTful APIs with strict user data isolation.*
> 
> *Let me demonstrate the live application."*

---

## Part 2: User Authentication & Security (0:45 – 1:30)

> *(Point to the screen at `/login/`)*
> 
> *"Here is the authentication interface. I implemented Django's built-in authentication system with custom Bootstrap forms. Passwords are never stored in plaintext—they are securely hashed using the PBKDF2 algorithm with SHA-256.*
> 
> *All pages are protected with the `@login_required` decorator. If an unauthenticated user tries to type `/` or `/applications/`, Django automatically redirects them to the login screen with a `?next=` parameter.*
> 
> *Now, I will log in with my account."*
> 
> *(Log in and land on the Dashboard)*

---

## Part 3: Live Dashboard & Database Metrics (1:30 – 2:30)

> *(Screen shows Dashboard counters and tables)*
> 
> *"Once logged in, the user lands on this responsive SaaS dashboard.*
> 
> *Notice these 6 metric cards at the top: **Total Applications, Applied, Shortlisted, Interviews Scheduled, Selected, and Rejected**.*
> 
> *These numbers are 100% dynamic and calculated directly from our MySQL database using Django ORM aggregation queries. There is zero hardcoded data.*
> 
> *Right below, we have our **Search Conversion Rates** showing the percentage of applications progressing to interviews and offers.*
> 
> *On the left, we see **Recent Applications**, and on the right, we have an **Upcoming Interviews** widget displaying any interview rounds scheduled in the future with their exact date, time, and meeting link."*

---

## Part 4: Creating a Job Application (CRUD Demonstration) (2:30 – 3:30)

> *(Click 'Add Application' button)*
> 
> *"Now, let's create a new job application.*
> 
> *Here, I will add:
> - **Company Name:** Google Cloud
> - **Job Title:** Python Full Stack Developer
> - **Location:** Hyderabad
> - **Employment Type:** Full Time
> - **Status:** Applied
> - **Salary:** ₹12 LPA
> - **Job URL:** `https://careers.google.com/jobs/results/12345`
> - **Job Description:** 'Looking for a Python Developer proficient in Django, REST APIs, and relational databases.'*
> 
> *(Click 'Save Application')*
> 
> *When I click 'Save Application', Django validates the form, sets the owner to the current logged-in user, and inserts the record into our MySQL `jobs_jobapplication` table.*
> 
> *We are redirected to the **Job Detail Page**, which displays all application details, a status badge, and an empty interview history."*

---

## Part 5: Scheduling an Interview & Automatic Status Progression (3:30 – 4:30)

> *(Click 'Schedule Interview' on the Job Detail page)*
> 
> *"Now, let's simulate receiving an interview invite from the recruiter.*
> 
> *Notice that the application is pre-selected. For security, the dropdown query is strictly filtered so users can only schedule interviews for their own applications.*
> 
> *I will select:
> - **Round Type:** Technical
> - **Date & Time:** Tomorrow at 11:00 AM
> - **Status:** Scheduled
> - **Meeting Link:** `https://meet.google.com/xyz-jobtrack`
> - **Notes:** 'Review Python OOP, Django ORM joins, and MySQL indexing.'*
> 
> *(Click 'Save Interview')*
> 
> *Notice an intelligent feature I built: Because the job was in 'Applied' status, scheduling an interview automatically advanced its status to **'Interview'** in the database! This reflects real-world productivity workflows."*

---

## Part 6: Search, Filtering & Data Isolation (4:30 – 5:15)

> *(Click 'Applications' in top navigation)*
> 
> *"Here on the Applications List page, I implemented:
> 1. Full-text search across company name, job title, and location using Django `Q` objects.
> 2. Dropdown filtering by status and job type.
> 3. Sorting by date and company name.
> 4. Clean pagination with 10 records per page.*
> 
> *Most importantly, **User Data Isolation** is strictly enforced. Even if another registered user logs into JobTrack, they cannot see or modify my applications, and typing my application ID into the URL immediately returns an HTTP 404 error."*

---

## Part 7: Analytics & Chart.js Integration (5:15 – 6:00)

> *(Click 'Analytics' in top navigation)*
> 
> *"On the Analytics page, we visualize the job search progress using **Chart.js**:
> 1. A **Line Chart** displaying monthly application trends over the last 6 months.
> 2. A **Doughnut Chart** breaking down applications by status.
> 3. A **Horizontal Bar Chart** showing distribution across Full Time, Remote, and Internship roles.*
> 
> *The backend aggregates these metrics via Django ORM, formats them as JSON, and passes them safely to the client for responsive rendering."*

---

## Part 8: Django REST Framework APIs & Testing (6:00 – 6:45)

> *(Open browser tab at `/api/` or `/api/applications/`)*
> 
> *"In addition to the server-rendered templates, JobTrack exposes a complete REST API built with **Django REST Framework (DRF)**.*
> 
> *Users can perform full CRUD via standard JSON endpoints:
> - `GET /api/applications/`
> - `POST /api/applications/`
> - `GET /api/interviews/`
> - `GET /api/dashboard/` for live statistics.*
> 
> *Endpoints are secured with `IsAuthenticated` permissions.*
> 
> *To guarantee quality, I built an automated test suite with **31 unit and integration tests** in the `tests/` folder covering authentication, CRUD operations, isolation boundaries, and REST APIs—all running against our MySQL database."*

---

## Part 9: Conclusion (6:45 – 7:00)

> *"In summary, JobTrack demonstrates my understanding of:
> - Core Python and Object-Oriented Programming.
> - Django's MVT architecture, forms, views, and templates.
> - MySQL relational database design with foreign keys and cascade rules.
> - Django ORM queries and data isolation.
> - Django REST Framework for building modern web APIs.
> - Clean Git workflow and automated testing.*
> 
> *Thank you, and I would be delighted to answer any technical questions or walk through the codebase."*
