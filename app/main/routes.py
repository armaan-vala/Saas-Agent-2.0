from flask import render_template
from app.models import Agent
from app.main import main

@main.route('/')
def index():
    return render_template('index.html')

# Give this function a unique name
@main.route('/create')
def create_agent_page():
    return render_template('create_agent.html')

@main.route('/chat/<int:agent_id>')
def chat_page(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    return render_template('chat.html', agent=agent)