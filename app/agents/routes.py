from flask import request, jsonify
from app import db
from app.models import Agent
from app.agents import agents_bp

@agents_bp.route('/api/agents', methods=['GET', 'POST'])
def handle_agents():
    if request.method == 'POST':
        # This is the "Create Agent" logic
        data = request.get_json()
        if not data or not 'agent_name' in data or not 'system_prompt' in data:
            return jsonify({'error': 'Missing data'}), 400

        new_agent = Agent(
            agent_name=data['agent_name'],
            system_prompt=data['system_prompt']
        )
        db.session.add(new_agent)
        db.session.commit()

        return jsonify({'message': f"Agent {new_agent.agent_name} created successfully!"}), 201

    if request.method == 'GET':
        # This is the "Get Agents" logic
        agents = Agent.query.all()
        agents_list = []
        for agent in agents:
            agents_list.append({
                'id': agent.id,
                'agent_name': agent.agent_name,
                'system_prompt': agent.system_prompt,
                'status': agent.status
            })
        return jsonify(agents_list)