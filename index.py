from flask import Flask, request, jsonify
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'career_autopilot_secret_key_vercel'

# Mock data
CAREER_PATHS = {
    "Data Scientist": {
        "skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
        "description": "Specialist in data analysis and building ML models"
    },
    "Frontend Developer": {
        "skills": ["JavaScript", "React", "HTML/CSS", "TypeScript", "UI/UX"],
        "description": "User interface developer"
    },
    "Project Manager": {
        "skills": ["Project Management", "Communication", "Agile", "Presentations", "Leadership"],
        "description": "Project and team leader"
    }
}

QUESTS = [
    {"id": 1, "name": "Complete a Python course", "xp": 100, "coins": 50, "skill": "Python", "type": "education"},
    {"id": 2, "name": "Watch an Agile webinar", "xp": 80, "coins": 40, "skill": "Agile", "type": "education"},
    {"id": 3, "name": "Read an article about React", "xp": 60, "coins": 30, "skill": "React", "type": "reading"},
    {"id": 4, "name": "Ask for feedback from a colleague", "xp": 120, "coins": 60, "skill": "Communication",
     "type": "social"},
    {"id": 5, "name": "Solve an algorithms problem", "xp": 150, "coins": 75, "skill": "Python", "type": "practice"},
    {"id": 6, "name": "Prepare a presentation", "xp": 90, "coins": 45, "skill": "Presentations", "type": "practice"}
]

BADGES = {
    "python_beginner": {"name": "Python Beginner", "description": "Completed first Python task", "icon": "🐍"},
    "active_learner": {"name": "Active Learner", "description": "Completed 5 tasks", "icon": "⭐"},
    "team_player": {"name": "Team Player", "description": "Received feedback from a colleague", "icon": "👥"},
    "ml_master": {"name": "ML Master", "description": "Mastered machine learning", "icon": "🤖"},
    "quest_master": {"name": "Quest Master", "description": "Completed 10 tasks", "icon": "🏆"},
    "skill_collector": {"name": "Skill Collector", "description": "Learned 5 different skills", "icon": "📚"}
}

CAREER_GOALS = {
    "short_term": [
        {"id": 1, "name": "Learn basic Python syntax", "category": "Programming", "priority": "high"},
        {"id": 2, "name": "Study SQL fundamentals", "category": "Databases", "priority": "medium"},
        {"id": 3, "name": "Understand OOP principles", "category": "Programming", "priority": "high"},
        {"id": 4, "name": "Learn to work with Git", "category": "Tools", "priority": "medium"},
        {"id": 5, "name": "Master algorithm basics", "category": "Programming", "priority": "medium"}
    ],
    "medium_term": [
        {"id": 6, "name": "Develop your own project", "category": "Practice", "priority": "high"},
        {"id": 7, "name": "Learn Django/Flask framework", "category": "Programming", "priority": "medium"},
        {"id": 8, "name": "Master machine learning basics", "category": "Data Science", "priority": "medium"},
        {"id": 9, "name": "Learn to work with Docker", "category": "Infrastructure", "priority": "low"},
        {"id": 10, "name": "Study web development basics", "category": "Web", "priority": "medium"}
    ],
    "long_term": [
        {"id": 11, "name": "Become a Middle Developer", "category": "Career", "priority": "high"},
        {"id": 12, "name": "Participate in open-source project", "category": "Practice", "priority": "medium"},
        {"id": 13, "name": "Prepare for technical interview", "category": "Career", "priority": "high"},
        {"id": 14, "name": "Master advanced algorithms", "category": "Programming", "priority": "medium"},
        {"id": 15, "name": "Study application architecture", "category": "Architecture", "priority": "medium"}
    ]
}

AI_RESPONSES = {
    "hello": "Hello! I'm your AI career assistant. How can I help with your professional development?",
    "hi": "Hi! I'm your AI career assistant. How can I help with your professional development?",
    "how are you": "Everything is great! Ready to help you with career questions and skill development.",
    "what can you do": "I can help with career path selection, recommend skill development tasks, track progress and set goals.",
    "career": "Analyzing your profile, I see potential in Data Science. I recommend starting with Python basics and statistics.",
    "skills": "Your current skills: Python (65%), SQL (40%). For your chosen path, I recommend learning machine learning and data visualization.",
    "plan": "Your career plan:\n1. Master Python (2 weeks)\n2. Learn SQL (3 weeks)\n3. ML basics (4 weeks)\n4. Real projects (2 months)",
    "quests": "Today available quests: Python, Agile and teamwork. Choose what aligns with your goals!",
    "statistics": "Check the 'Personal Account' section to view your detailed statistics and skill progress.",
    "goals": "In your personal account, you can select and track your career goals. I'll help choose suitable goals for your development.",
    "default": "I'm here to help with your career development. Ask about skills, career plan, available tasks or recommendations."
}

# Simple in-memory storage
user_storage = {}


def get_user_data(user_id='default'):
    if user_id not in user_storage:
        user_storage[user_id] = {
            'level': 1,
            'xp': 0,
            'coins': 0,
            'badges': [],
            'completed_quests': [],
            'career_path': None,
            'skills_progress': {
                "Python": 65, "SQL": 40, "Machine Learning": 20, "Statistics": 30, "Data Visualization": 25,
                "JavaScript": 10, "React": 5, "HTML/CSS": 15, "TypeScript": 0, "UI/UX": 10,
                "Project Management": 35, "Communication": 60, "Agile": 45, "Presentations": 50, "Leadership": 40
            },
            'join_date': datetime.now().strftime("%Y-%m-%d"),
            'total_quests_completed': 0,
            'total_xp_earned': 0,
            'total_coins_earned': 0,
            'quests_by_type': {'education': 0, 'reading': 0, 'social': 0, 'practice': 0},
            'last_activity': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'learning_streak': 1,
            'career_goals': {'short_term': [], 'medium_term': [], 'long_term': []}
        }
    return user_storage[user_id]


def get_user_id():
    return request.headers.get('X-User-ID', 'default')


def update_skills_progress(user_data, skill, xp_earned):
    if skill in user_data['skills_progress']:
        progress_increase = min(xp_earned / 10, 10)
        user_data['skills_progress'][skill] = min(user_data['skills_progress'][skill] + progress_increase, 100)
    else:
        user_data['skills_progress'][skill] = min(xp_earned / 5, 20)


def ai_assistant_response(message):
    message_lower = message.lower()
    for key, response in AI_RESPONSES.items():
        if key in message_lower and key != "default":
            return response
    return AI_RESPONSES["default"]


@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Career Autopilot | Holding T1</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-blue: #4a90e2; --light-blue: #87ceeb; --soft-blue: #b0e0e6; 
                --very-light-blue: #e6f3ff; --dark-blue: #2c5aa0; --text-dark: #2c3e50; 
                --text-light: #7f8c8d; --white: #ffffff; --success: #27ae60; 
                --warning: #f39c12; --danger: #e74c3c;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
            body { background: linear-gradient(135deg, var(--very-light-blue) 0%, var(--soft-blue) 100%); color: var(--text-dark); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: var(--dark-blue); margin-bottom: 10px; }
            .card { background: white; border-radius: 10px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .btn { background: var(--primary-blue); color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:disabled { background: #ccc; cursor: not-allowed; }
            .nav { display: flex; justify-content: center; margin: 20px 0; flex-wrap: wrap; }
            .nav-btn { padding: 10px 20px; margin: 5px; background: var(--light-blue); border: none; border-radius: 5px; cursor: pointer; }
            .nav-btn.active { background: var(--primary-blue); color: white; }
            .section { display: none; }
            .section.active { display: block; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-item { background: var(--very-light-blue); padding: 15px; border-radius: 8px; text-align: center; }
            .quest-item { border-left: 4px solid var(--primary-blue); padding: 15px; margin: 10px 0; background: white; }
            .skill-bar { background: #eee; height: 10px; border-radius: 5px; margin: 5px 0; }
            .skill-progress { background: var(--primary-blue); height: 100%; border-radius: 5px; }
            .chat-container { max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin: 15px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 10px; max-width: 80%; }
            .user-message { background: var(--primary-blue); color: white; margin-left: auto; }
            .ai-message { background: var(--very-light-blue); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-rocket"></i> Career Autopilot</h1>
                <p>Holding T1 Internal Growth Platform</p>
            </div>

            <div class="nav">
                <button class="nav-btn active" data-section="dashboard">Dashboard</button>
                <button class="nav-btn" data-section="career">Career Map</button>
                <button class="nav-btn" data-section="quests">Quests</button>
                <button class="nav-btn" data-section="ai">AI Assistant</button>
                <button class="nav-btn" data-section="profile">Profile</button>
            </div>

            <!-- Dashboard -->
            <div id="dashboard" class="section active">
                <div class="card">
                    <h2><i class="fas fa-tachometer-alt"></i> Dashboard</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value" id="level">1</div>
                            <div>Level</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="xp">0</div>
                            <div>XP</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="coins">0</div>
                            <div>Coins</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="quests-completed">0</div>
                            <div>Quests Completed</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>Current Career Path</h3>
                    <div id="current-career">Not selected</div>
                </div>

                <div class="card">
                    <h3>Recent Activity</h3>
                    <div id="recent-activity">No recent activity</div>
                </div>
            </div>

            <!-- Career Map -->
            <div id="career" class="section">
                <div class="card">
                    <h2><i class="fas fa-map"></i> Career Paths</h2>
                    <div id="career-paths"></div>
                </div>
            </div>

            <!-- Quests -->
            <div id="quests" class="section">
                <div class="card">
                    <h2><i class="fas fa-tasks"></i> Available Quests</h2>
                    <div id="quests-list"></div>
                </div>
            </div>

            <!-- AI Assistant -->
            <div id="ai" class="section">
                <div class="card">
                    <h2><i class="fas fa-robot"></i> AI Career Assistant</h2>
                    <div class="chat-container" id="chat-messages">
                        <div class="message ai-message">Hello! I'm your AI career assistant. How can I help you today?</div>
                    </div>
                    <div style="display: flex; margin-top: 15px;">
                        <input type="text" id="chat-input" placeholder="Ask me anything..." style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <button class="btn" id="send-btn"><i class="fas fa-paper-plane"></i></button>
                    </div>
                </div>
            </div>

            <!-- Profile -->
            <div id="profile" class="section">
                <div class="card">
                    <h2><i class="fas fa-user"></i> Personal Profile</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <div>Join Date</div>
                            <div id="join-date">-</div>
                        </div>
                        <div class="stat-item">
                            <div>Last Activity</div>
                            <div id="last-activity">-</div>
                        </div>
                        <div class="stat-item">
                            <div>Learning Streak</div>
                            <div id="streak">1 day</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>Skills Progress</h3>
                    <div id="skills-list"></div>
                </div>

                <div class="card">
                    <h3>Badges Earned</h3>
                    <div id="badges-list"></div>
                </div>
            </div>
        </div>

        <script>
            let userData = {};
            let userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('userId', userId);

            // Navigation
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                    btn.classList.add('active');
                    document.getElementById(btn.dataset.section).classList.add('active');
                });
            });

            // Load user data
            async function loadUserData() {
                try {
                    const response = await fetch('/api/user', {
                        headers: { 'X-User-ID': userId }
                    });
                    userData = await response.json();
                    updateUI();
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }

            function updateUI() {
                // Update dashboard
                document.getElementById('level').textContent = userData.level;
                document.getElementById('xp').textContent = userData.xp;
                document.getElementById('coins').textContent = userData.coins;
                document.getElementById('quests-completed').textContent = userData.completed_quests.length;
                document.getElementById('current-career').textContent = userData.career_path || 'Not selected';
                document.getElementById('join-date').textContent = userData.join_date;
                document.getElementById('last-activity').textContent = userData.last_activity;
                document.getElementById('streak').textContent = userData.learning_streak + ' days';

                // Update career paths
                updateCareerPaths();

                // Update quests
                updateQuests();

                // Update skills
                updateSkills();

                // Update badges
                updateBadges();
            }

            async function updateCareerPaths() {
                const response = await fetch('/api/career_paths');
                const paths = await response.json();
                let html = '';
                for (const [name, data] of Object.entries(paths)) {
                    const isSelected = userData.career_path === name;
                    html += `<div class="quest-item" style="cursor: pointer; background: ${isSelected ? '#e6f3ff' : 'white'}" onclick="selectCareer('${name}')">
                        <h3>${name}</h3>
                        <p>${data.description}</p>
                        <div>Skills: ${data.skills.join(', ')}</div>
                        ${isSelected ? '<div><strong>✓ Selected</strong></div>' : ''}
                    </div>`;
                }
                document.getElementById('career-paths').innerHTML = html;
            }

            async function updateQuests() {
                const response = await fetch('/api/quests');
                const quests = await response.json();
                let html = '';
                quests.forEach(quest => {
                    const isCompleted = userData.completed_quests.includes(quest.id);
                    html += `<div class="quest-item">
                        <h3>${quest.name}</h3>
                        <p>Skill: ${quest.skill} | Type: ${quest.type}</p>
                        <p>Reward: ${quest.xp} XP + ${quest.coins} coins</p>
                        <button class="btn" onclick="completeQuest(${quest.id})" ${isCompleted ? 'disabled' : ''}>
                            ${isCompleted ? 'Completed' : 'Complete Quest'}
                        </button>
                    </div>`;
                });
                document.getElementById('quests-list').innerHTML = html;
            }

            function updateSkills() {
                let html = '';
                for (const [skill, progress] of Object.entries(userData.skills_progress)) {
                    html += `<div style="margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>${skill}</span>
                            <span>${Math.round(progress)}%</span>
                        </div>
                        <div class="skill-bar">
                            <div class="skill-progress" style="width: ${progress}%"></div>
                        </div>
                    </div>`;
                }
                document.getElementById('skills-list').innerHTML = html;
            }

            function updateBadges() {
                let html = '';
                for (const [badgeId, badge] of Object.entries({
                    "python_beginner": {"name": "Python Beginner", "description": "Completed first Python task", "icon": "🐍"},
                    "active_learner": {"name": "Active Learner", "description": "Completed 5 tasks", "icon": "⭐"},
                    "team_player": {"name": "Team Player", "description": "Received feedback from a colleague", "icon": "👥"},
                    "quest_master": {"name": "Quest Master", "description": "Completed 10 tasks", "icon": "🏆"}
                })) {
                    const hasBadge = userData.badges.includes(badgeId);
                    html += `<div style="padding: 10px; margin: 5px; background: ${hasBadge ? '#e8f5e8' : '#f5f5f5'}; border-radius: 5px;">
                        <span style="font-size: 24px;">${badge.icon}</span>
                        <strong>${badge.name}</strong>
                        <div>${badge.description}</div>
                        <div style="color: ${hasBadge ? 'green' : '#999'}">${hasBadge ? '✓ Earned' : 'Not earned'}</div>
                    </div>`;
                }
                document.getElementById('badges-list').innerHTML = html;
            }

            async function selectCareer(careerPath) {
                const response = await fetch('/api/select_career', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-User-ID': userId
                    },
                    body: JSON.stringify({ career_path: careerPath })
                });
                if (response.ok) {
                    loadUserData();
                }
            }

            async function completeQuest(questId) {
                const response = await fetch(`/api/complete_quest/${questId}`, {
                    method: 'POST',
                    headers: { 'X-User-ID': userId }
                });
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        userData = result.user_data;
                        updateUI();
                        alert('Quest completed! Rewards received.');
                    }
                }
            }

            // Chat functionality
            document.getElementById('send-btn').addEventListener('click', sendMessage);
            document.getElementById('chat-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });

            async function sendMessage() {
                const input = document.getElementById('chat-input');
                const message = input.value.trim();
                if (!message) return;

                // Add user message
                addMessage(message, 'user');
                input.value = '';

                // Get AI response
                const response = await fetch('/api/ai_chat', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-User-ID': userId
                    },
                    body: JSON.stringify({ message })
                });

                if (response.ok) {
                    const data = await response.json();
                    addMessage(data.response, 'ai');
                }
            }

            function addMessage(text, sender) {
                const chat = document.getElementById('chat-messages');
                const msg = document.createElement('div');
                msg.className = `message ${sender}-message`;
                msg.textContent = text;
                chat.appendChild(msg);
                chat.scrollTop = chat.scrollHeight;
            }

            // Initialize
            loadUserData();
        </script>
    </body>
    </html>
    '''


# API routes
@app.route('/api/user')
def api_user():
    user_id = get_user_id()
    return jsonify(get_user_data(user_id))


@app.route('/api/career_paths')
def api_career_paths():
    return jsonify(CAREER_PATHS)


@app.route('/api/quests')
def api_quests():
    return jsonify(QUESTS)


@app.route('/api/complete_quest/<int:quest_id>', methods=['POST'])
def api_complete_quest(quest_id):
    user_id = get_user_id()
    user_data = get_user_data(user_id)
    quest = next((q for q in QUESTS if q['id'] == quest_id), None)

    if quest and quest_id not in user_data['completed_quests']:
        user_data['xp'] += quest['xp']
        user_data['coins'] += quest['coins']
        user_data['completed_quests'].append(quest_id)
        user_data['total_quests_completed'] = len(user_data['completed_quests'])
        user_data['quests_by_type'][quest['type']] += 1
        user_data['last_activity'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        user_data['learning_streak'] += 1

        update_skills_progress(user_data, quest['skill'], quest['xp'])

        # Check level up
        xp_needed = user_data['level'] * 100
        if user_data['xp'] >= xp_needed:
            user_data['level'] += 1
            user_data['xp'] = 0

        # Check badges
        if quest['skill'] == 'Python' and 'python_beginner' not in user_data['badges']:
            user_data['badges'].append('python_beginner')
        if len(user_data['completed_quests']) >= 3 and 'active_learner' not in user_data['badges']:
            user_data['badges'].append('active_learner')

        return jsonify({'success': True, 'user_data': user_data})
    return jsonify({'success': False})


@app.route('/api/ai_chat', methods=['POST'])
def api_ai_chat():
    data = request.get_json()
    message = data.get('message', '')
    response = ai_assistant_response(message)
    return jsonify({'response': response})


@app.route('/api/select_career', methods=['POST'])
def api_select_career():
    data = request.get_json()
    career_path = data.get('career_path')
    user_id = get_user_id()
    user_data = get_user_data(user_id)
    user_data['career_path'] = career_path
    return jsonify({'success': True})


# Vercel handler
if __name__ == '__index.py__':

    app.run()
