from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import mysql.connector
import bcrypt
import re
import os

# created by: bsit 2d - finals project
# portfoliohub - portfolio builder

app = Flask(__name__, static_folder='.')
app.secret_key = 'portfoliohub2024'
CORS(app, supports_credentials=True)

# connect to database
# uses environment variables when deployed on Railway
# locally it falls back to XAMPP defaults
def get_db():
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQLHOST', 'localhost'),
        user=os.environ.get('MYSQLUSER', 'root'),
        password=os.environ.get('MYSQLPASSWORD', ''),
        database=os.environ.get('MYSQLDATABASE', 'portfoliohub'),
        port=int(os.environ.get('MYSQLPORT', 3306))
    )
    return conn

# serve the html pages
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


# ======================
#   SIGN UP / LOGIN
# ======================

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name', '').strip()
    username = data.get('username', '').strip().lower()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # check if all fields are filled
    if not name or not username or not email or not password:
        return jsonify({'error': 'Please fill in all fields.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    # username should only have letters, numbers, underscore
    if not re.match(r'^[a-z0-9_]+$', username):
        return jsonify({'error': 'Username can only have letters, numbers and underscore.'}), 400

    # hash the password before saving
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)

        # check if username or email already exists
        cur.execute('SELECT id FROM users WHERE username=%s OR email=%s', (username, email))
        existing = cur.fetchone()
        if existing:
            return jsonify({'error': 'Username or email is already taken.'}), 400

        cur.execute(
            'INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)',
            (name, username, email, hashed)
        )
        db.commit()

        new_id = cur.lastrowid
        session['user_id'] = new_id

        return jsonify({'success': True, 'username': username})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute('SELECT * FROM users WHERE email=%s', (email,))
        user = cur.fetchone()

        # check if user exists and password is correct
        if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
            return jsonify({'error': 'Wrong email or password.'}), 401

        session['user_id'] = user['id']
        return jsonify({'success': True, 'username': user['username']})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/me')
def me():
    # check if logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            'SELECT id, name, username, email, bio, photo_url, github, linkedin, twitter, facebook, instagram FROM users WHERE id=%s',
            (session['user_id'],)
        )
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


# ======================
#   PROFILE UPDATE
# ======================

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cur = db.cursor()

        cur.execute(
            '''UPDATE users SET name=%s, bio=%s, photo_url=%s,
               github=%s, linkedin=%s, twitter=%s, facebook=%s, instagram=%s
               WHERE id=%s''',
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
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


# ======================
#   PROJECTS CRUD
# ======================

@app.route('/api/projects')
def get_projects():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT * FROM projects WHERE user_id=%s ORDER BY id DESC', (session['user_id'],))
        projects = cur.fetchall()
        return jsonify(projects)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/projects', methods=['POST'])
def add_project():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'INSERT INTO projects (user_id, title, description, status, link, tags) VALUES (%s, %s, %s, %s, %s, %s)',
            (
                session['user_id'],
                data.get('title'),
                data.get('desc', ''),
                data.get('status', 'Planned'),
                data.get('link', ''),
                data.get('tags', '')
            )
        )
        db.commit()
        return jsonify({'success': True, 'id': cur.lastrowid})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/projects/<int:pid>', methods=['PUT'])
def update_project(pid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'UPDATE projects SET title=%s, description=%s, status=%s, link=%s, tags=%s WHERE id=%s AND user_id=%s',
            (
                data.get('title'),
                data.get('desc', ''),
                data.get('status', 'Planned'),
                data.get('link', ''),
                data.get('tags', ''),
                pid,
                session['user_id']
            )
        )
        db.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/projects/<int:pid>', methods=['DELETE'])
def delete_project(pid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('DELETE FROM projects WHERE id=%s AND user_id=%s', (pid, session['user_id']))
        db.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


# ======================
#   SKILLS CRUD
# ======================

@app.route('/api/skills')
def get_skills():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT * FROM skills WHERE user_id=%s ORDER BY id DESC', (session['user_id'],))
        skills = cur.fetchall()
        return jsonify(skills)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/skills', methods=['POST'])
def add_skill():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'INSERT INTO skills (user_id, title, level, percent) VALUES (%s, %s, %s, %s)',
            (session['user_id'], data.get('title'), data.get('level', 'Beginner'), data.get('percent', 0))
        )
        db.commit()
        return jsonify({'success': True, 'id': cur.lastrowid})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/skills/<int:sid>', methods=['PUT'])
def update_skill(sid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'UPDATE skills SET title=%s, level=%s, percent=%s WHERE id=%s AND user_id=%s',
            (data.get('title'), data.get('level', 'Beginner'), data.get('percent', 0), sid, session['user_id'])
        )
        db.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


@app.route('/api/skills/<int:sid>', methods=['DELETE'])
def delete_skill(sid):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('DELETE FROM skills WHERE id=%s AND user_id=%s', (sid, session['user_id']))
        db.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


# ======================
#   PUBLIC PORTFOLIO
#   (no login needed)
# ======================

@app.route('/api/portfolio/<username>')
def public_portfolio(username):
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute(
            'SELECT id, name, username, bio, photo_url, github, linkedin, twitter, facebook, instagram FROM users WHERE username=%s',
            (username,)
        )
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        uid = user['id']

        cur.execute('SELECT * FROM projects WHERE user_id=%s ORDER BY id DESC', (uid,))
        user['projects'] = cur.fetchall()

        cur.execute('SELECT * FROM skills WHERE user_id=%s ORDER BY id DESC', (uid,))
        user['skills'] = cur.fetchall()

        return jsonify(user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
