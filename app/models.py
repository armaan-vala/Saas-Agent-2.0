from .extensions import db
from datetime import datetime 

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_name = db.Column(db.String(128), index=True, unique=True)
    system_prompt = db.Column(db.Text)
    status = db.Column(db.String(64), default='Ready', index=True)

    def __repr__(self):
        return f'<Agent {self.agent_name}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    filepath = db.Column(db.String(512))
    status = db.Column(db.String(64), default='Pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))

    def __repr__(self):
        return f'<Document {self.filename}>'