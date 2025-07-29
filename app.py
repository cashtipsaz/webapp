from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# In-memory data for a single user (replace with DB later)
user = {
    'display_name': 'John Doe',
    'avatar_url': '/static/avatars/default.png',
    'points': 250,
    'streak': 3,
    'assets': 1200,
    'goal': 1800,
    'portfolio': {
        'Cash': 400,
        'Checking': 300,
        'Savings': 300,
        'Stocks': 200
    },
    'month_growth': 12,
    'lessons_done': 5,
    'challenges_done': 2
}

financial_entries = [
    {'date': '2024-06-01', 'category': 'Food', 'description': 'Grocery shopping', 'amount': -50},
    {'date': '2024-06-02', 'category': 'Salary', 'description': 'Paycheck', 'amount': 1000},
]

lessons = [
    {'id': 1, 'title': 'Budgeting & Savings', 'video_url': 'https://www.youtube.com/embed/VIDEO_ID_1'},
    {'id': 2, 'title': 'Investing', 'video_url': 'https://www.youtube.com/embed/VIDEO_ID_2'},
]

lesson_progress = {1: True, 2: True}

challenges = [
    {'id': 1, 'type': 'Daily', 'description': 'Track an Expense', 'points': 15, 'completed': False},
    {'id': 2, 'type': 'Daily', 'description': 'No Spend Day!', 'points': 15, 'completed': False},
    {'id': 3, 'type': 'Daily', 'description': 'Short Quiz', 'points': 20, 'completed': False},
]

@app.route('/')
def home():
    percent_goal = int((user['assets'] / user['goal']) * 100)
    return render_template('home.html', user=user, percent_goal=percent_goal)

@app.route('/financial-log', methods=['GET', 'POST'])
def financial_log():
    global financial_entries
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        description = request.form['description']
        amount = float(request.form['amount'])
        financial_entries.append({'date': date, 'category': category, 'description': description, 'amount': amount})
        return redirect(url_for('financial_log'))
    return render_template('financial_log.html', entries=financial_entries)

@app.route('/lessons')
def lessons_page():
    return render_template('lessons.html', lessons=lessons)

@app.route('/lessons/<int:lesson_id>')
def lesson_detail(lesson_id):
    lesson = next((l for l in lessons if l['id'] == lesson_id), None)
    completed = lesson_progress.get(lesson_id, False)
    return render_template('lesson_detail.html', lesson=lesson, completed=completed)

@app.route('/challenges', methods=['GET', 'POST'])
def challenges_page():
    global challenges, user
    if request.method == 'POST':
        challenge_id = int(request.form['challenge_id'])
        for c in challenges:
            if c['id'] == challenge_id and not c['completed']:
                c['completed'] = True
                user['points'] += c['points']
                user['challenges_done'] += 1
    return render_template('challenges.html', challenges=challenges, user=user)

@app.route('/avatar', methods=['GET', 'POST'])
def avatar():
    global user
    if request.method == 'POST':
        display_name = request.form['display_name']
        user['display_name'] = display_name
        # Avatar upload not implemented yet
    return render_template('avatar.html', user=user)

if __name__ == '__main__':
    app.run(debug=True) 