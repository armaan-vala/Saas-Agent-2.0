from flask import render_template
from app.main import main
from app.models import Agent

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/create')
def create_agent_page():
    return render_template('create_agent.html')

@main.route('/chat/<int:agent_id>')
def chat_page(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    return render_template('chat.html', agent=agent)