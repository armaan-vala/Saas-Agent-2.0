import os
import shutil
from flask import request, jsonify
from app.extensions import db
from app.models import Agent, Document
from . import agents_bp

VECTOR_STORE_DIR = "vector_stores"



@agents_bp.route('/agents', methods=['GET', 'POST']) 

def handle_agents():
    if request.method == 'POST':
        
        data = request.get_json()
        if not data or 'agent_name' not in data or 'system_prompt' not in data:
            return jsonify({'error': 'Missing data'}), 400

        new_agent = Agent(
            agent_name=data['agent_name'],
            system_prompt=data['system_prompt']
        )
        db.session.add(new_agent)
        db.session.commit()

        return jsonify({
            'message': f"Agent {new_agent.agent_name} created successfully!",
            'agent_id': new_agent.id
        }), 201

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


@agents_bp.route('/agents/<int:agent_id>', methods=['DELETE'])

def delete_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)

    try:
        # Delete the vector store
        agent_vector_store_path = os.path.join(VECTOR_STORE_DIR, f"agent_{agent.id}")
        if os.path.exists(agent_vector_store_path):
            shutil.rmtree(agent_vector_store_path)

        # Delete associated document records
        Document.query.filter_by(agent_id=agent.id).delete()

        # Delete the agent
        db.session.delete(agent)
        db.session.commit()

        return jsonify({'message': f'Agent {agent.agent_name} deleted successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete agent.'}), 500