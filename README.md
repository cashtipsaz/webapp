# 💰 CashTips - Financial Education Web App

A comprehensive financial education platform built with Flask that helps users learn about budgeting, investing, and financial management through interactive lessons, challenges, and portfolio tracking.

## 🚀 Features

### 📚 Educational Content
- **Interactive Lessons**: Video-based learning on budgeting and investing
- **Progress Tracking**: Monitor your learning journey
- **Points System**: Earn points for completing lessons

### 🎯 Gamification
- **Daily Challenges**: Complete daily financial tasks
- **Weekly Challenges**: Longer-term financial goals
- **Streak System**: Build consistent financial habits
- **Points & Rewards**: Gamified learning experience

### 💼 Financial Management
- **Expense Tracking**: Log income and expenses
- **Portfolio Management**: Track your assets and investments
- **Goal Setting**: Set and monitor financial goals
- **Progress Visualization**: See your financial growth

### 👤 User Experience
- **User Authentication**: Secure login/registration
- **Avatar System**: Customize your profile
- **Responsive Design**: Works on all devices
- **Admin Dashboard**: Manage user data and analytics

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with gradients and modern design
- **Icons**: Font Awesome

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd webapp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the app**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account or login

## 🗄️ Database Structure

### Core Models
- **User**: Authentication, profile, points, streaks
- **FinancialEntry**: Income/expense tracking
- **Lesson**: Educational content
- **LessonProgress**: User learning progress
- **Challenge**: Gamified tasks
- **ChallengeProgress**: User challenge completion
- **PortfolioItem**: Asset tracking

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (change in production)
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: File upload directory

### Admin Access
- Create an account with username `admin`
- Access admin dashboard at `/admin/users`
- View all user data and export to CSV

## 🚀 Deployment

### Railway (Recommended)
1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Railway will automatically deploy your app
4. Add environment variables in Railway dashboard

### Render
1. Create account on render.com
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`

### Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Deploy: `git push heroku main`

## 📊 Admin Features

### Dashboard Access
- URL: `/admin/users`
- Username: `admin`
- Features:
  - View all users
  - Export data to CSV
  - Monitor app statistics
  - Track user engagement

## 🔒 Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- File upload validation
- SQL injection protection via SQLAlchemy
- XSS protection with template escaping

## 📱 Mobile Responsive

The app is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🎨 Design Features

- Modern gradient backgrounds
- Smooth animations
- Intuitive navigation
- Color-coded data visualization
- Professional admin interface

## 📈 Future Enhancements

- [ ] Email notifications
- [ ] Social features
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] API endpoints
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built with ❤️ for financial education.

---

**CashTips** - Making financial literacy accessible to everyone! 💰📚 