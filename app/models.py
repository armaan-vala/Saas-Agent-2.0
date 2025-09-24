from app.extensions import db 
from datetime import datetime, timezone 

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_name = db.Column(db.String(128), index=True, unique=True)
    system_prompt = db.Column(db.Text)
    status = db.Column(db.String(64), default='Ready', index=True)
    
    # relationship for tracking conversation agent
    conversations = db.relationship('Conversation', backref='agent', lazy='dynamic')
    # relationship for tracking doc of each agent.
    documents = db.relationship('Document', backref='agent', lazy='dynamic') # Existing documents relationship

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


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    title = db.Column(db.String(255), default="New Chat") 
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc)) 
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)) 

    # relationship for tracking all messeges of single conversation
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade="all, delete-orphan") 

    def __repr__(self):
        return f'<Conversation {self.id} - {self.title}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    
    # Image data ko base64 string ke roop mein store karne ke liye
    # Yeh field sirf tab populate hoga jab user ne image upload ki ho.
    # Hum isse database mein store karenge taaki follow-up questions ke liye image context available rahe.
    image_data = db.Column(db.Text, nullable=True) 
    
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc)) 

    def __repr__(self):
        return f'<Message {self.id} from {self.sender}>'