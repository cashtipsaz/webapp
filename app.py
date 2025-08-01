from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cashtips.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Production settings
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(200), default='/static/avatars/default.png')
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    assets = db.Column(db.Float, default=0.0)
    goal = db.Column(db.Float, default=1000.0)
    spending_goal = db.Column(db.Float, default=500.0)
    spending_days = db.Column(db.Integer, default=30)
    spending_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    income_days = db.Column(db.Integer, default=30)
    income_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    month_growth = db.Column(db.Float, default=0.0)
    lessons_done = db.Column(db.Integer, default=0)
    challenges_done = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    financial_entries = db.relationship('FinancialEntry', backref='user', lazy=True)
    lesson_progress = db.relationship('LessonProgress', backref='user', lazy=True)
    portfolio_items = db.relationship('PortfolioItem', backref='user', lazy=True)
    
    def update_streak(self):
        """Update user streak based on recent activity"""
        today = datetime.utcnow().date()
        last_activity = self.last_activity.date() if self.last_activity else None
        
        if last_activity is None:
            self.streak = 1
        elif today - last_activity == timedelta(days=1):
            self.streak += 1
        elif today - last_activity > timedelta(days=1):
            self.streak = 1
        # If same day, keep current streak
        
        self.last_activity = datetime.utcnow()

class FinancialEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(200))
    points_reward = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # Daily, Weekly, Monthly
    description = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=15)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Cash, Checking, Savings, Stocks, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
@login_required
def home():
    # Update streak on home page visit
    current_user.update_streak()
    db.session.commit()
    
    # Get portfolio items for the user
    portfolio_items = PortfolioItem.query.filter_by(user_id=current_user.id).all()
    total_portfolio_value = sum(item.amount for item in portfolio_items)
    
    percent_goal = int((total_portfolio_value / current_user.goal) * 100) if current_user.goal > 0 else 0
    
    return render_template('home.html', user=current_user, percent_goal=percent_goal, 
                         portfolio_items=portfolio_items, total_portfolio_value=total_portfolio_value)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt - Username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}, checking password...")
            if check_password_hash(user.password_hash, password):
                print(f"Password correct, logging in {user.username}")
                login_user(user)
                return redirect(url_for('home'))
            else:
                print(f"Password incorrect for {username}")
                flash('Invalid username or password')
        else:
            print(f"User {username} not found")
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            display_name = request.form['display_name']
            
            print(f"Registration attempt - Username: {username}, Email: {email}")
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                print(f"Username {username} already exists")
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                print(f"Email {email} already registered")
                return render_template('register.html')
            
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                display_name=display_name
            )
            db.session.add(user)
            db.session.commit()
            
            print(f"User {username} registered successfully")
            login_user(user)
            return redirect(url_for('home'))
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/financial-log', methods=['GET', 'POST'])
@login_required
def financial_log():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category = request.form['category']
        description = request.form['description']
        amount = float(request.form['amount'])
        
        # Ensure expenses are negative (for tracking purposes)
        if amount > 0:
            amount = -amount
        
        entry = FinancialEntry(
            user_id=current_user.id,
            date=date,
            category=category,
            description=description,
            amount=amount
        )
        db.session.add(entry)
        
        # Update user assets and streak
        current_user.assets += amount
        current_user.update_streak()
        db.session.commit()
        
        flash('Financial entry added successfully!')
        return redirect(url_for('financial_log'))
    
    entries = FinancialEntry.query.filter_by(user_id=current_user.id).order_by(FinancialEntry.date.desc()).all()
    
    # Calculate expense total
    expense_total = abs(sum(entry.amount for entry in entries if entry.amount < 0))
    
    # Calculate spending progress
    days_elapsed = (datetime.utcnow() - current_user.spending_start_date).days
    days_remaining = max(0, current_user.spending_days - days_elapsed)
    spending_progress = (expense_total / current_user.spending_goal * 100) if current_user.spending_goal > 0 else 0
    
    # Check if spending period is complete and user is under budget
    spending_complete = days_elapsed >= current_user.spending_days
    under_budget = expense_total <= current_user.spending_goal
    
    return render_template('financial_log.html', 
                         entries=entries, 
                         expense_total=expense_total, 
                         spending_goal=current_user.spending_goal,
                         spending_days=current_user.spending_days,
                         days_elapsed=days_elapsed,
                         days_remaining=days_remaining,
                         spending_progress=spending_progress,
                         spending_complete=spending_complete,
                         under_budget=under_budget,
                         today=datetime.now().strftime('%Y-%m-%d'), 
                         user=current_user)

@app.route('/financial-log/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_financial_entry(entry_id):
    entry = FinancialEntry.query.get_or_404(entry_id)
    
    # Ensure user can only delete their own entries
    if entry.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('financial_log'))
    
    # Update user assets (subtract the amount)
    current_user.assets -= entry.amount
    db.session.delete(entry)
    db.session.commit()
    
    flash('Financial entry deleted successfully!')
    return redirect(url_for('financial_log'))

@app.route('/lessons')
@login_required
def lessons_page():
    lessons = Lesson.query.all()
    return render_template('lessons.html', lessons=lessons)

@app.route('/lessons/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id, 
        lesson_id=lesson_id
    ).first()
    completed = progress.completed if progress else False
    return render_template('lesson_detail.html', lesson=lesson, completed=completed)

@app.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        # Complete the lesson
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)
        current_user.points += lesson.points_reward
        current_user.lessons_done += 1
        flash(f'Lesson completed! You earned {lesson.points_reward} points!')
    elif progress.completed:
        # Uncomplete the lesson
        progress.completed = False
        progress.completed_at = None
        current_user.points -= lesson.points_reward
        current_user.lessons_done -= 1
        flash(f'Lesson uncompleted! You lost {lesson.points_reward} points!')
    else:
        # Complete the lesson
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        current_user.points += lesson.points_reward
        current_user.lessons_done += 1
        flash(f'Lesson completed! You earned {lesson.points_reward} points!')
    
    current_user.update_streak()
    db.session.commit()
    
    return redirect(url_for('lesson_detail', lesson_id=lesson_id))

@app.route('/challenges', methods=['GET', 'POST'])
@login_required
def challenges_page():
    if request.method == 'POST':
        challenge_id = int(request.form['challenge_id'])
        challenge = Challenge.query.get_or_404(challenge_id)
        progress = ChallengeProgress.query.filter_by(
            user_id=current_user.id,
            challenge_id=challenge_id
        ).first()
        
        if not progress:
            # Complete the challenge
            progress = ChallengeProgress(
                user_id=current_user.id,
                challenge_id=challenge_id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
            current_user.points += challenge.points
            current_user.challenges_done += 1
            flash(f'Challenge completed! You earned {challenge.points} points!')
        elif progress.completed:
            # Uncomplete the challenge
            progress.completed = False
            progress.completed_at = None
            current_user.points -= challenge.points
            current_user.challenges_done -= 1
            flash(f'Challenge uncompleted! You lost {challenge.points} points!')
        else:
            # Complete the challenge
            progress.completed = True
            progress.completed_at = datetime.utcnow()
            current_user.points += challenge.points
            current_user.challenges_done += 1
            flash(f'Challenge completed! You earned {challenge.points} points!')
        
        current_user.update_streak()
        db.session.commit()
        return redirect(url_for('challenges_page'))
    
    challenges = Challenge.query.filter_by(active=True).all()
    user_progress = {p.challenge_id: p.completed for p in ChallengeProgress.query.filter_by(user_id=current_user.id).all()}
    
    return render_template('challenges.html', challenges=challenges, user=current_user, user_progress=user_progress)

@app.route('/avatar', methods=['GET', 'POST'])
@login_required
def avatar():
    if request.method == 'POST':
        display_name = request.form['display_name']
        current_user.display_name = display_name
        
        # Handle file upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.avatar_url = f'/static/avatars/{filename}'
        
        current_user.update_streak()
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('avatar'))
    
    return render_template('avatar.html', user=current_user)

@app.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        item_type = request.form['type']
        
        item = PortfolioItem(
            user_id=current_user.id,
            name=name,
            amount=amount,
            type=item_type
        )
        db.session.add(item)
        current_user.update_streak()
        db.session.commit()
        
        flash('Portfolio item added successfully!')
        return redirect(url_for('portfolio'))
    
    portfolio_items = PortfolioItem.query.filter_by(user_id=current_user.id).all()
    total_portfolio_value = sum(item.amount for item in portfolio_items)
    
    # Calculate income day tracker values
    income_days_elapsed = (datetime.utcnow() - current_user.income_start_date).days
    income_days_remaining = max(0, current_user.income_days - income_days_elapsed)
    
    # Update user assets to match portfolio value for consistency
    current_user.assets = total_portfolio_value
    db.session.commit()
    
    return render_template('portfolio.html', 
                         portfolio_items=portfolio_items, 
                         total_portfolio_value=total_portfolio_value, 
                         user=current_user,
                         income_days_elapsed=income_days_elapsed,
                         income_days_remaining=income_days_remaining)

@app.route('/update-income-goal', methods=['POST'])
@login_required
def update_income_goal():
    income_goal = float(request.form['income_goal'])
    income_days = int(request.form['income_days'])
    current_user.goal = income_goal
    current_user.income_days = income_days
    current_user.income_start_date = datetime.utcnow()  # Reset start date on goal update
    db.session.commit()
    flash('Income goal updated successfully!')
    return redirect(url_for('portfolio'))

@app.route('/update-spending-goal', methods=['POST'])
@login_required
def update_spending_goal():
    spending_goal = float(request.form['spending_goal'])
    spending_days = int(request.form['spending_days'])
    current_user.spending_goal = spending_goal
    current_user.spending_days = spending_days
    current_user.spending_start_date = datetime.utcnow()
    db.session.commit()
    flash('Spending goal updated successfully!')
    return redirect(url_for('financial_log'))

@app.route('/delete-portfolio-item/<int:item_id>', methods=['POST'])
@login_required
def delete_portfolio_item(item_id):
    item = PortfolioItem.query.get_or_404(item_id)
    
    # Ensure user can only delete their own items
    if item.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('portfolio'))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Portfolio item deleted successfully!')
    return redirect(url_for('portfolio'))

@app.route('/admin/users')
@login_required
def admin_users():
    # Simple admin check - you can make this more secure
    if current_user.username != 'admin':  # Change this to your admin username
        flash('Access denied')
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

# Initialize database and create sample data
def init_db():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create lessons - only if they don't exist
        if not Lesson.query.first():
            lessons = [
                Lesson(title='Budgeting & Savings', description='Learn the basics of budgeting and saving money', 
                       video_url='https://www.youtube.com/embed/2M5ExwnN2s4', points_reward=15),
                Lesson(title='Investing Basics', description='Introduction to investing and building wealth', 
                       video_url='https://www.youtube.com/embed/tJd2Shdzh4s', points_reward=20),
            ]
            db.session.add_all(lessons)
            db.session.commit()
            
        # Create sample challenges - only if they don't exist
        if not Challenge.query.first():
            challenges = [
                Challenge(type='Daily', description='Track an Expense', points=15),
                Challenge(type='Daily', description='No Spend Day!', points=15),
                Challenge(type='Daily', description='Short Quiz', points=20),
                Challenge(type='Weekly', description='Review Your Budget', points=25),
                Challenge(type='Weekly', description='Learn Something New', points=30),
            ]
            db.session.add_all(challenges)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 