from app import db

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_name = db.Column(db.String(128), index=True, unique=True)
    system_prompt = db.Column(db.Text)
    status = db.Column(db.String(64), default='Ready', index=True)

    def __repr__(self):
        return f'<Agent {self.agent_name}>'