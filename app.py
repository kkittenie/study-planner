import os
import sqlite3
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, g, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'study-planner-secret-key-super-secure-2026')
DATABASE = os.path.join(app.root_path, 'study_planner.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT '#ff7aa2',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            deadline DATE NOT NULL,
            priority TEXT CHECK(priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
            status TEXT CHECK(status IN ('To Do', 'In Progress', 'Completed')) DEFAULT 'To Do',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE SET NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            day TEXT CHECK(day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')) NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        );
    ''')
    
    # Check if empty to populate demo data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        demo_pass = generate_password_hash("password123")
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ("sofia", "sofia@example.com", demo_pass)
        )
        user_id = cursor.lastrowid
        
        # Sample Subjects
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                       ("alex", "alex@example.com", demo_pass))
        
        # Subjects for Sofia
        cursor.execute("INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)", (user_id, "Mathematics", "#ff6b8b"))
        math_id = cursor.lastrowid
        cursor.execute("INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)", (user_id, "Programming", "#8b5cf6"))
        prog_id = cursor.lastrowid
        cursor.execute("INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)", (user_id, "English", "#06b6d4"))
        eng_id = cursor.lastrowid

        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=5)

        # Sample Tasks for Sofia
        cursor.execute('''
            INSERT INTO tasks (user_id, subject_id, title, description, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, math_id, "Calculus Homework Ch. 4", "Complete exercises 1-15 on derivatives", today.isoformat(), "High", "In Progress"))
        
        cursor.execute('''
            INSERT INTO tasks (user_id, subject_id, title, description, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, prog_id, "Build Flask Study Planner", "Implement multi-user auth and SQLite schema", tomorrow.isoformat(), "High", "To Do"))
        
        cursor.execute('''
            INSERT INTO tasks (user_id, subject_id, title, description, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, eng_id, "Read Essay Sample", "Review essay draft on modern literature", next_week.isoformat(), "Low", "Completed"))

        # Sample Schedule for Sofia
        cursor.execute('''
            INSERT INTO schedules (user_id, subject_id, day, start_time, end_time, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, math_id, "Monday", "09:00", "11:00", "Room 302 - Bring Graphing Calculator"))
        
        cursor.execute('''
            INSERT INTO schedules (user_id, subject_id, day, start_time, end_time, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, prog_id, "Wednesday", "13:00", "15:30", "Lab 2 - Flask web architecture"))

    db.commit()
    db.close()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for header user info
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return dict(current_user=user)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not username:
            errors.append("Nama pengguna wajib diisi.")
        if not email:
            errors.append("Email wajib diisi.")
        if len(password) < 6:
            errors.append("Kata sandi minimal 6 karakter.")
        if password != confirm_password:
            errors.append("Konfirmasi kata sandi tidak cocok.")

        db = get_db()
        if username and db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            errors.append("Nama pengguna sudah digunakan.")
        if email and db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            errors.append("Email sudah terdaftar.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', username=username, email=email)

        password_hash = generate_password_hash(password)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                       (username, email, password_hash))
        db.commit()

        flash("Pendaftaran berhasil. Silakan masuk.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '')

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (login_input, login_input.lower())
        ).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Selamat datang kembali, {user['username']}.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Email/Nama pengguna atau kata sandi salah.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Anda telah keluar dari akun.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    db = get_db()

    today_str = date.today().isoformat()
    tomorrow_str = (date.today() + timedelta(days=1)).isoformat()

    # Tasks stats
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
    completed_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Completed'", (user_id,)).fetchone()[0]
    pending_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status != 'Completed'", (user_id,)).fetchone()[0]
    due_soon_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status != 'Completed' AND deadline BETWEEN ? AND ?", 
                                (user_id, today_str, tomorrow_str)).fetchone()[0]

    overall_progress = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    # Categorized lists
    due_today = db.execute('''
        SELECT t.*, s.name as subject_name, s.color as subject_color
        FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
        WHERE t.user_id = ? AND t.deadline = ? AND t.status != 'Completed'
        ORDER BY t.priority DESC
    ''', (user_id, today_str)).fetchall()

    due_tomorrow = db.execute('''
        SELECT t.*, s.name as subject_name, s.color as subject_color
        FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
        WHERE t.user_id = ? AND t.deadline = ? AND t.status != 'Completed'
        ORDER BY t.priority DESC
    ''', (user_id, tomorrow_str)).fetchall()

    upcoming_tasks = db.execute('''
        SELECT t.*, s.name as subject_name, s.color as subject_color
        FROM tasks t LEFT JOIN subjects s ON t.subject_id = s.id
        WHERE t.user_id = ? AND t.deadline > ? AND t.status != 'Completed'
        ORDER BY t.deadline ASC LIMIT 5
    ''', (user_id, tomorrow_str)).fetchall()

    # Today's schedule
    day_name_en = date.today().strftime('%A')
    day_map_id = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    today_name_id = day_map_id.get(day_name_en, day_name_en)

    todays_schedule = db.execute('''
        SELECT sc.*, s.name as subject_name, s.color as subject_color
        FROM schedules sc JOIN subjects s ON sc.subject_id = s.id
        WHERE sc.user_id = ? AND sc.day = ?
        ORDER BY sc.start_time ASC
    ''', (user_id, day_name_en)).fetchall()

    return render_template('dashboard.html',
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           pending_tasks=pending_tasks,
                           due_soon_tasks=due_soon_tasks,
                           overall_progress=overall_progress,
                           due_today=due_today,
                           due_tomorrow=due_tomorrow,
                           upcoming_tasks=upcoming_tasks,
                           todays_schedule=todays_schedule,
                           today_name=today_name_id)

@app.route('/tasks')
@login_required
def tasks():
    user_id = session['user_id']
    status_filter = request.args.get('status', 'All')
    priority_filter = request.args.get('priority', 'All')
    search_query = request.args.get('q', '').strip()

    db = get_db()
    
    query = '''
        SELECT t.*, s.name as subject_name, s.color as subject_color
        FROM tasks t
        LEFT JOIN subjects s ON t.subject_id = s.id
        WHERE t.user_id = ?
    '''
    params = [user_id]

    if status_filter != 'All':
        query += ' AND t.status = ?'
        params.append(status_filter)

    if priority_filter == 'High Priority':
        query += ' AND t.priority = "High"'
    elif priority_filter != 'All':
        query += ' AND t.priority = ?'
        params.append(priority_filter)

    if search_query:
        query += ' AND (t.title LIKE ? OR s.name LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])

    query += ' ORDER BY t.deadline ASC, t.created_at DESC'
    task_list = db.execute(query, params).fetchall()

    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? ORDER BY name ASC", (user_id,)).fetchall()

    return render_template('tasks.html',
                           tasks=task_list,
                           subjects=subjects,
                           default_date=date.today().isoformat(),
                           status_filter=status_filter,
                           priority_filter=priority_filter,
                           search_query=search_query)

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def task_create():
    user_id = session['user_id']
    db = get_db()
    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? ORDER BY name ASC", (user_id,)).fetchall()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject_id = request.form.get('subject_id') or None
        description = request.form.get('description', '').strip()
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'To Do')

        if not title or not deadline:
            flash("Judul dan tenggat waktu wajib diisi.", "danger")
            return render_template('task_form.html', subjects=subjects, task=request.form, is_edit=False)

        db.execute('''
            INSERT INTO tasks (user_id, subject_id, title, description, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, subject_id, title, description, deadline, priority, status))
        db.commit()

        flash("Tugas berhasil dibuat.", "success")
        return redirect(url_for('tasks'))

    return render_template('task_form.html', subjects=subjects, is_edit=False, default_date=date.today().isoformat())

@app.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def task_edit(id):
    user_id = session['user_id']
    db = get_db()

    task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not task:
        abort(404)

    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? ORDER BY name ASC", (user_id,)).fetchall()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject_id = request.form.get('subject_id') or None
        description = request.form.get('description', '').strip()
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'To Do')

        if not title or not deadline:
            flash("Judul dan tenggat waktu wajib diisi.", "danger")
            return render_template('task_form.html', subjects=subjects, task=request.form, is_edit=True)

        db.execute('''
            UPDATE tasks
            SET subject_id = ?, title = ?, description = ?, deadline = ?, priority = ?, status = ?
            WHERE id = ? AND user_id = ?
        ''', (subject_id, title, description, deadline, priority, status, id, user_id))
        db.commit()

        flash("Tugas berhasil diperbarui.", "success")
        return redirect(url_for('tasks'))

    return render_template('task_form.html', subjects=subjects, task=task, is_edit=True)

@app.route('/tasks/<int:id>/delete', methods=['POST'])
@login_required
def task_delete(id):
    user_id = session['user_id']
    db = get_db()

    task = db.execute("SELECT id FROM tasks WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not task:
        abort(404)

    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (id, user_id))
    db.commit()

    flash("Tugas telah dihapus.", "info")
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:id>/complete', methods=['POST'])
@login_required
def task_complete(id):
    user_id = session['user_id']
    db = get_db()

    task = db.execute("SELECT id, status FROM tasks WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not task:
        abort(404)

    new_status = 'Completed' if task['status'] != 'Completed' else 'To Do'
    db.execute("UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?", (new_status, id, user_id))
    db.commit()

    flash("Status tugas berhasil diperbarui.", "success")
    return redirect(request.referrer or url_for('tasks'))

@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    user_id = session['user_id']
    db = get_db()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        color = request.form.get('color', '#347C7C').strip()

        if not name:
            flash("Nama mata pelajaran tidak boleh kosong.", "danger")
        else:
            db.execute("INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)", (user_id, name, color))
            db.commit()
            flash("Mata pelajaran berhasil ditambahkan.", "success")

        return redirect(url_for('subjects'))

    user_subjects = db.execute('''
        SELECT s.*, COUNT(t.id) as task_count
        FROM subjects s
        LEFT JOIN tasks t ON s.id = t.subject_id AND t.user_id = ?
        WHERE s.user_id = ?
        GROUP BY s.id
        ORDER BY s.name ASC
    ''', (user_id, user_id)).fetchall()

    return render_template('subjects.html', subjects=user_subjects)

@app.route('/subjects/<int:id>/edit', methods=['POST'])
@login_required
def subject_edit(id):
    user_id = session['user_id']
    db = get_db()

    subject = db.execute("SELECT id FROM subjects WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not subject:
        abort(404)

    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#347C7C').strip()

    if name:
        db.execute("UPDATE subjects SET name = ?, color = ? WHERE id = ? AND user_id = ?", (name, color, id, user_id))
        db.commit()
        flash("Mata pelajaran berhasil diperbarui.", "success")
    else:
        flash("Nama mata pelajaran tidak boleh kosong.", "danger")

    return redirect(url_for('subjects'))

@app.route('/subjects/<int:id>/delete', methods=['POST'])
@login_required
def subject_delete(id):
    user_id = session['user_id']
    db = get_db()

    subject = db.execute("SELECT id FROM subjects WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not subject:
        abort(404)

    db.execute("DELETE FROM subjects WHERE id = ? AND user_id = ?", (id, user_id))
    db.commit()

    flash("Mata pelajaran telah dihapus.", "info")
    return redirect(url_for('subjects'))

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    user_id = session['user_id']
    db = get_db()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        day = request.form.get('day')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        notes = request.form.get('notes', '').strip()

        if not subject_id or not day or not start_time or not end_time:
            flash("Mata pelajaran, Hari, Jam Mulai, dan Jam Selesai wajib diisi.", "danger")
        else:
            db.execute('''
                INSERT INTO schedules (user_id, subject_id, day, start_time, end_time, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, subject_id, day, start_time, end_time, notes))
            db.commit()
            flash("Jadwal berhasil ditambahkan.", "success")

        return redirect(url_for('schedule'))

    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? ORDER BY name ASC", (user_id,)).fetchall()
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedules_by_day = {}
    for d in days:
        schedules_by_day[d] = db.execute('''
            SELECT sc.*, s.name as subject_name, s.color as subject_color
            FROM schedules sc
            JOIN subjects s ON sc.subject_id = s.id
            WHERE sc.user_id = ? AND sc.day = ?
            ORDER BY sc.start_time ASC
        ''', (user_id, d)).fetchall()

    return render_template('schedule.html', subjects=subjects, days=days, schedules_by_day=schedules_by_day)

@app.route('/schedule/<int:id>/edit', methods=['POST'])
@login_required
def schedule_edit(id):
    user_id = session['user_id']
    db = get_db()

    sched = db.execute("SELECT id FROM schedules WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not sched:
        abort(404)

    subject_id = request.form.get('subject_id')
    day = request.form.get('day')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    notes = request.form.get('notes', '').strip()

    if subject_id and day and start_time and end_time:
        db.execute('''
            UPDATE schedules
            SET subject_id = ?, day = ?, start_time = ?, end_time = ?, notes = ?
            WHERE id = ? AND user_id = ?
        ''', (subject_id, day, start_time, end_time, notes, id, user_id))
        db.commit()
        flash("Schedule entry updated.", "success")

    return redirect(url_for('schedule'))

@app.route('/schedule/<int:id>/delete', methods=['POST'])
@login_required
def schedule_delete(id):
    user_id = session['user_id']
    db = get_db()

    sched = db.execute("SELECT id FROM schedules WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()
    if not sched:
        abort(404)

    db.execute("DELETE FROM schedules WHERE id = ? AND user_id = ?", (id, user_id))
    db.commit()

    flash("Schedule entry removed.", "info")
    return redirect(url_for('schedule'))

@app.route('/progress')
@login_required
def progress():
    user_id = session['user_id']
    db = get_db()

    total_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
    completed_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Completed'", (user_id,)).fetchone()[0]
    remaining_tasks = total_tasks - completed_tasks
    completion_percentage = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    # Progress per subject
    subjects_progress = db.execute('''
        SELECT 
            s.id,
            s.name,
            s.color,
            COUNT(t.id) as total,
            SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed
        FROM subjects s
        LEFT JOIN tasks t ON s.id = t.subject_id AND t.user_id = ?
        WHERE s.user_id = ?
        GROUP BY s.id
        ORDER BY s.name ASC
    ''', (user_id, user_id)).fetchall()

    subject_data = []
    for sp in subjects_progress:
        tot = sp['total'] or 0
        comp = sp['completed'] or 0
        pct = round((comp / tot * 100)) if tot > 0 else 0
        subject_data.append({
            'id': sp['id'],
            'name': sp['name'],
            'color': sp['color'],
            'total': tot,
            'completed': comp,
            'percentage': pct
        })

    return render_template('progress.html',
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           remaining_tasks=remaining_tasks,
                           completion_percentage=completion_percentage,
                           subject_data=subject_data)

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    db = get_db()

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    total_subjects = db.execute("SELECT COUNT(*) FROM subjects WHERE user_id = ?", (user_id,)).fetchone()[0]
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
    total_schedules = db.execute("SELECT COUNT(*) FROM schedules WHERE user_id = ?", (user_id,)).fetchone()[0]

    return render_template('profile.html',
                           user=user,
                           total_subjects=total_subjects,
                           total_tasks=total_tasks,
                           total_schedules=total_schedules)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
