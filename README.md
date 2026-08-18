# Multi-User Study Planner 🎀

A multi-user personal study planner web application built with **Python 3**, **Flask**, **SQLite**, and **Vanilla CSS/JS**.

## 🌟 Key Features

1. **Strict Multi-User Data Isolation**: Every task, subject, and schedule item is bound to the logged-in `user_id`. Users cannot view or modify other users' study data.
2. **Secure Authentication**: Password hashing powered by Werkzeug (`scrypt`/`pbkdf2`), Flask session management, and validation check for unique usernames & emails.
3. **Automated SQLite Database Setup**: Auto-initializes `study_planner.db` with schema and demo data on first startup.
4. **Dashboard & Analytics**: Real-time stats (Total, Completed, Pending, Due Soon), Progress bars, and breakdown per subject.
5. **Full CRUD Modules**:
   - **Tasks**: Priority, Status (To Do, In Progress, Completed), Deadline, Search, and Status/Priority Filters.
   - **Subjects**: Custom color tag assignment and linked task count.
   - **Study Schedule**: Weekly study focus block planner from Monday to Sunday.
6. **Design Aesthetic**: Blend of soft pastel coquette student planner aesthetics with industrial brutalist precision grids.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+ installed on your system.

### 2. Setup Virtual Environment

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python app.py
```

The application will be running locally at:
👉 **http://127.0.0.1:5000**

---

## 🔐 Default Demo Accounts

If starting with a clean database, the system generates sample data for testing multi-user isolation:

- **User 1**:
  - **Email**: `sofia@example.com` (or Username: `sofia`)
  - **Password**: `password123`

- **User 2**:
  - **Email**: `alex@example.com` (or Username: `alex`)
  - **Password**: `password123`

---

## 📁 Project Structure

```
study-planner/
├── app.py                  # Core Flask backend & SQLite ORM routes
├── requirements.txt        # Flask & Werkzeug dependencies
├── study_planner.db        # SQLite database (auto-generated)
├── README.md               # Project documentation & instructions
├── static/
│   ├── css/
│   │   └── style.css       # Soft Pastel & Industrial Brutalist styles
│   └── js/
│       └── app.js          # Interactive UI & helper scripts
└── templates/
    ├── base.html           # Master layout & top navigation
    ├── login.html          # Authentication login page
    ├── register.html       # Authentication registration page
    ├── dashboard.html      # Personal study dashboard & schedule
    ├── tasks.html          # Task list, search & filters
    ├── task_form.html      # Create & edit task form
    ├── subjects.html       # Subject management with color tags
    ├── schedule.html       # Weekly schedule matrix
    ├── progress.html       # Overall & subject progress metrics
    ├── profile.html        # User profile & account overview
    ├── 404.html            # Resource not found error template
    └── 403.html            # Access denied error template
```

---

## 🔒 Security Architecture
- Password stored exclusively as irreversible hashes (`password_hash`).
- All SQL queries use parameterized input bindings to prevent SQL injection (`?` placeholders).
- All resource lookup routes check `WHERE id = ? AND user_id = ?` to prevent ID tampering across accounts.
