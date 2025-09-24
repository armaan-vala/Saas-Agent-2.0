import logging
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db, celery 
from app.models import Agent, Document, Conversation, Message 

# Langchain aur Groq  imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

from celery.result import AsyncResult
import google.generativeai as genai
import base64
import mimetypes
from datetime import datetime, timezone


from . import chat_bp    

print("app/chat/routes.py is being loaded and using blueprint:", chat_bp.name)


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_vision_model = genai.GenerativeModel('models/gemini-1.5-pro-latest')


VECTOR_STORE_DIR = "vector_stores"

# --- Helper Functions ---

def get_rag_response(agent, user_message, chat_history_messages=None):
   
    # Initialize the LLM
    llm = ChatGroq(temperature=0, groq_api_key=os.environ.get("GROQ_API_KEY"), model_name="gemma2-9b-it")
    
    agent_vector_store_path = os.path.join(VECTOR_STORE_DIR, f"agent_{agent.id}")
    
    if os.path.exists(agent_vector_store_path):
        print(f"Vector store found for Agent {agent.id}. Using RAG.")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") # Ensure embeddings are loaded when needed
        vector_store = FAISS.load_local(agent_vector_store_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()

        # Contextual prompt for RAG
       
        context_prompt = ""
        if chat_history_messages:
            context_prompt = "Here is the previous conversation history:\n"
            for msg in chat_history_messages:
                context_prompt += f"{msg.sender.capitalize()}: {msg.content}\n"
            context_prompt += "\n"
        # logic if out of the context of document question is ask 
        prompt = ChatPromptTemplate.from_template(f"""
        You are a helpful assistant acting with the personality defined by this system prompt: "{agent.system_prompt}"

        {context_prompt}
        First, review the following context from the user's documents to see if it's relevant to the user's question.
        
        Context:
        {{context}}

        Based on the user's question and the context, formulate a response.
        - If the context is relevant and helpful, use it to ground your answer.
        - If the context is not relevant to the question, answer the question using your general knowledge and abilities.

        Question: {{input}}
        """)
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        response = retrieval_chain.invoke({
            "input": user_message,
            "system_prompt": agent.system_prompt 
        })
        return response['answer']

    else:
        print(f"No vector store found for Agent {agent.id}. Using base intelligence.")
        # Contextual prompt for non-RAG
        context_prompt = ""
        if chat_history_messages:
            for msg in chat_history_messages:
                context_prompt += f"{msg.sender.capitalize()}: {msg.content}\n"
            context_prompt += "\n"

        prompt = ChatPromptTemplate.from_messages([
            ("system", agent.system_prompt),
            ("user", f"{context_prompt}{user_message}")
        ])
        chain = prompt | llm
        response = chain.invoke({"input": user_message})
        return response.content

def generate_conversation_title(first_message_content):
   
    if len(first_message_content) > 50:
        return first_message_content[:47] + "..."
    return first_message_content


@chat_bp.route('/agents/<int:agent_id>/conversations', methods=['GET'])
# --- CHANGE END ---
def get_agent_conversations(agent_id):
    
    agent = Agent.query.get_or_404(agent_id)
    conversations = agent.conversations.order_by(Conversation.updated_at.desc()).all()
    
    conv_data = []
    for conv in conversations:
        conv_data.append({
            'id': conv.id,
            'title': conv.title,
            'updated_at': conv.updated_at.isoformat() # Frontend ke liye format karna
        })
    return jsonify(conv_data)


@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])

def get_conversation_messages(conversation_id):
    """
    Ek specific conversation ke saare messages ko return karta hai.
    """
    conversation = Conversation.query.get_or_404(conversation_id)
    messages = conversation.messages.order_by(Message.timestamp.asc()).all() # sorting msg with time
    
    msg_data = []
    for msg in messages:
        image_src = None
        if msg.image_data:
            # image_data is sended directly, assuming it's already in data:image/mime;base64 format
            image_src = msg.image_data 
        
        msg_data.append({
            'id': msg.id,
            'sender': msg.sender,
            'content': msg.content,
            'image_src': image_src, # Frontend image display
            'timestamp': msg.timestamp.isoformat()
        })
    return jsonify(msg_data)


@chat_bp.route('/conversations/<int:conversation_id>/rename', methods=['POST'])

def rename_conversation(conversation_id):
    """
    Conversation ka title rename karta hai.
    """
    data = request.get_json()
    new_title = data.get('title')
    
    if not new_title:
        return jsonify({'error': 'New title is required'}), 400
    
    conversation = Conversation.query.get_or_404(conversation_id)
    conversation.title = new_title
    db.session.commit()
    return jsonify({'message': 'Conversation renamed successfully', 'new_title': new_title})



@chat_bp.route('/chat', methods=['POST'])

def chat():
    data = request.get_json()
    user_message = data.get('message')
    agent_id = int(data.get('agent_id')) 
    raw_conversation_id = data.get('conversation_id')
    effective_conversation_id = int(raw_conversation_id) if raw_conversation_id is not None else None

    image_data = data.get('image')

    # Error handling for missing agent_id
    if not agent_id: 
        return jsonify({'error': 'Agent ID is required'}), 400

    if not user_message and not image_data:
        return jsonify({'error': 'Message or image is required'}), 400
    if not agent_id:
        return jsonify({'error': 'Agent ID is required'}), 400

    agent = Agent.query.get_or_404(agent_id)

    # --- Conversation Handling ---
    conversation = None
    if effective_conversation_id: 
        conversation = Conversation.query.get_or_404(effective_conversation_id) 
        print(f"DEBUG BACKEND (Pre-Comparison): Request Agent ID: {agent_id}, Type: {type(agent_id)}")
        print(f"DEBUG BACKEND (Pre-Comparison): Conversation Agent ID from DB: {conversation.agent_id}, Type: {type(conversation.agent_id)}")
        print(f"DEBUG BACKEND (Pre-Comparison): Conversation ID from request: {effective_conversation_id}, Type: {type(effective_conversation_id)}")
        print(f"DEBUG BACKEND (Pre-Comparison): Fetched Conversation object: {conversation.id} - {conversation.title}")
        if conversation.agent_id != agent_id: 
            return jsonify({'error': 'Conversation does not belong to this agent'}), 403
    else:
        # new conversation started
        conversation = Conversation(agent_id=agent.id, title=generate_conversation_title(user_message or "New Chat"))
        db.session.add(conversation)
        db.session.commit()

    # User messegd getting saved in db
    user_msg_db = Message(
        conversation_id=conversation.id,
        sender='user',
        content=user_message or "Image uploaded", 
        image_data=image_data, # Base64 image data 
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(user_msg_db)
    db.session.commit() 

    # Smart Router Logic (Image vs Text) 
    agent_response_content = ""
    
    
    chat_history_messages = Message.query.filter_by(conversation_id=conversation.id)\
                                   .order_by(Message.timestamp.asc())\
                                   .filter(Message.id != user_msg_db.id).all() # Current message excluding
    
    if image_data:
        # Image Processing for this using gemini api
        try:
            mime_type = "image/jpeg" 
            if image_data.startswith('data:'):
                parts = image_data.split(';', 1)
                if len(parts) > 0:
                    mime_type = parts[0].split(':')[1]
                    # Actual base64 data extraction, considering potential multiple commas in data
                    data_prefix, b64_content = image_data.split(',', 1)
                    image_data_decoded = base64.b64decode(b64_content)
                else:
                    # Fallback if format is not exactly 'data:mime;base64,content'
                    b64_content = image_data.split(',', 1)[1] if ',' in image_data else image_data
                    image_data_decoded = base64.b64decode(b64_content)
            else:
                image_data_decoded = base64.b64decode(image_data)


            # prepare prompts part, image will always be frist part
            prompt_parts = []
            
            # if previous history,adding them in prompt too
            if chat_history_messages:
                for msg in chat_history_messages:
                    if msg.image_data:
                        # if in previous chat then list of image will be given again to gemini so he wont fumble                      
                        prev_mime_type = "image/jpeg"
                        prev_b64_content = msg.image_data.split(',', 1)[1] if ',' in msg.image_data else msg.image_data
                        prompt_parts.append({
                            "mime_type": prev_mime_type, # Assuming all prev images are jpeg for simplicity, or extract from stored data
                            "data": base64.b64decode(prev_b64_content)
                        })
                    prompt_parts.append(f"{msg.sender.capitalize()}: {msg.content}")
            
            
            prompt_parts.append({
                "mime_type": mime_type,
                "data": image_data_decoded
            })
            prompt_parts.append(user_message or "Describe this image.")

            response = gemini_vision_model.generate_content(prompt_parts)
            agent_response_content = response.text

        except Exception as e:
            current_app.logger.error(f"Error with Gemini Vision Model: {e}", exc_info=True)  # MODIFYING THIS 
            agent_response_content = "Sorry, I had trouble processing the image. Please try again or with a text-only query."
    else:
        # Text-only query use existing RAG pipeline 
        try:
            # pass chat_history_messages function to get_rag_response function
            agent_response_content = get_rag_response(agent, user_message, chat_history_messages)
        except Exception as e:
            current_app.logger.error(f"Error with RAG Pipeline: {e}")
            agent_response_content = "Sorry, I encountered an error while processing your text query. Please try again."

    # Agent response saved in db
    agent_msg_db = Message(
        conversation_id=conversation.id,
        sender='agent',
        content=agent_response_content,
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(agent_msg_db)
    
    # Conversation  updated_at timestamp 
    conversation.updated_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        'response': agent_response_content,
        'conversation_id': conversation.id,
        'conversation_title': conversation.title 
    })


@chat_bp.route('/agents/<int:agent_id>/documents', methods=['POST'])

def upload_document(agent_id):
    agent = Agent.query.get_or_404(agent_id)

    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected file'}), 400

    uploaded_count = 0
    processing_tasks = []

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(agent.id))
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Database entry for the document
            document = Document(filename=filename, filepath=filepath, agent_id=agent.id, status='Pending')
            db.session.add(document)
            db.session.commit() # Commit to get document.id

            # Send to Celery for processing
            task = celery.send_task('app.tasks.process_document', args=[document.id, agent.id]) # <--- celery.send_task
            processing_tasks.append(task.id)
            uploaded_count += 1
    
    if uploaded_count > 0:
        return jsonify({
            'message': f'{uploaded_count} documents uploaded and sent for processing.',
            'task_ids': processing_tasks
        }), 202
    else:
        return jsonify({'error': 'No valid files uploaded.'}), 400


@chat_bp.route('/tasks/<task_id>', methods=['GET'])

def get_task_status(task_id):
    task = AsyncResult(task_id, app=celery) # <--- app=celery
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': task.info.get('status', 'Processing...'), 'result': task.info.get('result', '')}
    else:
        response = {'state': task.state, 'status': str(task.info), 'error': 'Task failed'}
    return jsonify(response)