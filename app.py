from flask import Flask, request, jsonify, send_from_directory, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'portfoliohub123'

# Connect to MySQL database
def get_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='portfoliohub'
    )
    return connection

# Serve the main pages
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/portfolio.html')
def portfolio():
    return send_from_directory('.', 'portfolio.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# Sign up a new user
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name', '').strip()
    username = data.get('username', '').strip().lower()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not name or not username or not email or not password:
        return jsonify({'error': 'Please fill in all fields.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check if username or email already exists
        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        existing = cursor.fetchone()
        if existing:
            return jsonify({'error': 'Username or email already taken.'}), 400

        # Insert new user into database
        cursor.execute(
            'INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)',
            (name, username, email, password)
        )
        db.commit()

        # Save user id in session so they stay logged in
        session['user_id'] = cursor.lastrowid

        db.close()
        return jsonify({'success': True, 'username': username})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Log in an existing user
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Find user by email and password
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Invalid email or password.'}), 401

        # Save user id in session
        session['user_id'] = user['id']

        db.close()
        return jsonify({'success': True, 'username': user['username']})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Log out
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# Get current logged in user info
@app.route('/api/me')
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT id, name, username, email, bio, photo_url, github, linkedin, twitter, facebook, instagram FROM users WHERE id = %s',
            (session['user_id'],)
        )
        user = cursor.fetchone()
        db.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update profile info
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE users SET name=%s, bio=%s, photo_url=%s, github=%s, linkedin=%s, twitter=%s, facebook=%s, instagram=%s WHERE id=%s',
            (
                data.get('name', ''),
                data.get('bio', ''),
                data.get('photo_url', ''),
                data.get('github', ''),
                data.get('linkedin', ''),
                data.get('twitter', ''),
                data.get('facebook', ''),
                data.get('instagram', ''),
                session['user_id']
            )
        )
        db.commit()
        db.close()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all projects of logged in user
@app.route('/api/projects')
def get_projects():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM projects WHERE user_id = %s ORDER BY id DESC', (session['user_id'],))
        projects = cursor.fetchall()
        db.close()
        return jsonify(projects)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a new project
@app.route('/api/projects', methods=['POST'])
def add_project():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO projects (user_id, title, description, status, link, tags) VALUES (%s, %s, %s, %s, %s, %s)',
            (session['user_id'], data.get('title'), data.get('desc', ''), data.get('status', 'Planned'), data.get('link', ''), data.get('tags', ''))
        )
        db.commit()
        new_id = cursor.lastrowid
        db.close()
        return jsonify({'success': True, 'id': new_id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update an existing project
@app.route('/api/projects/<int:pid>', methods=['PUT'])
def update_project(pid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE projects SET title=%s, description=%s, status=%s, link=%s, tags=%s WHERE id=%s AND user_id=%s',
            (data.get('title'), data.get('desc', ''), data.get('status', 'Planned'), data.get('link', ''), data.get('tags', ''), pid, session['user_id'])
        )
        db.commit()
        db.close()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a project
@app.route('/api/projects/<int:pid>', methods=['DELETE'])
def delete_project(pid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM projects WHERE id = %s AND user_id = %s', (pid, session['user_id']))
        db.commit()
        db.close()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all skills of logged in user
@app.route('/api/skills')
def get_skills():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM skills WHERE user_id = %s ORDER BY id DESC', (session['user_id'],))
        skills = cursor.fetchall()
        db.close()
        return jsonify(skills)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a new skill
@app.route('/api/skills', methods=['POST'])
def add_skill():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO skills (user_id, title, level, percent) VALUES (%s, %s, %s, %s)',
            (session['user_id'], data.get('title'), data.get('level', 'Beginner'), data.get('percent', 0))
        )
        db.commit()
        new_id = cursor.lastrowid
        db.close()
        return jsonify({'success': True, 'id': new_id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update an existing skill
@app.route('/api/skills/<int:sid>', methods=['PUT'])
def update_skill(sid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE skills SET title=%s, level=%s, percent=%s WHERE id=%s AND user_id=%s',
            (data.get('title'), data.get('level', 'Beginner'), data.get('percent', 0), sid, session['user_id'])
        )
        db.commit()
        db.close()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a skill
@app.route('/api/skills/<int:sid>', methods=['DELETE'])
def delete_skill(sid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM skills WHERE id = %s AND user_id = %s', (sid, session['user_id']))
        db.commit()
        db.close()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Public portfolio page - no login needed
@app.route('/api/portfolio/<username>')
def public_portfolio(username):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Get user info
        cursor.execute(
            'SELECT id, name, username, bio, photo_url, github, linkedin, twitter, facebook, instagram FROM users WHERE username = %s',
            (username,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get their projects
        cursor.execute('SELECT * FROM projects WHERE user_id = %s ORDER BY id DESC', (user['id'],))
        user['projects'] = cursor.fetchall()

        # Get their skills
        cursor.execute('SELECT * FROM skills WHERE user_id = %s ORDER BY id DESC', (user['id'],))
        user['skills'] = cursor.fetchall()

        db.close()
        return jsonify(user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
