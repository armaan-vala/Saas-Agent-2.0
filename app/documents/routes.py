import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from config import Config, basedir
from app.extensions import db, celery
from app.models import Agent, Document
from app.tasks import process_document 
from . import documents_bp

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@documents_bp.route('/agents/<int:agent_id>/documents', methods=['POST'])

def upload_documents(agent_id):
    agent = Agent.query.get_or_404(agent_id)

    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    files = request.files.getlist('files[]')

    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected files'}), 400

    document_ids = []
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            new_doc = Document(
                filename=filename,
                filepath=filepath,
                agent_id=agent.id,
                status='Pending'
            )
            db.session.add(new_doc)
            db.session.commit()

           
            process_document.delay(new_doc.id, agent.id) 
           
            document_ids.append(new_doc.id)
            print(f"Sent document {new_doc.id} for agent {agent_id} to background worker.")

    return jsonify({
        'message': f'{len(document_ids)} documents uploaded and sent for processing.',
        'document_ids': document_ids
    }), 202