import os
from flask import request, jsonify
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from app.chat import chat_bp
from app.models import Agent

VECTOR_STORE_DIR = "vector_stores"

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data or 'agent_id' not in data:
        return jsonify({'error': 'Missing message or agent_id'}), 400

    agent = Agent.query.get_or_404(data['agent_id'])
    user_message = data['message']
    
    try:
        # Initialize the LLM
        llm = ChatGroq(temperature=0, groq_api_key=os.environ.get("GROQ_API_KEY"), model_name="gemma2-9b-it")
        
        # Check if a vector store exists for this agent
        agent_vector_store_path = os.path.join(VECTOR_STORE_DIR, f"agent_{agent.id}")
        
        if os.path.exists(agent_vector_store_path):
            # --- RAG PATH: The agent has expert knowledge ---
            print(f"Vector store found for Agent {agent.id}. Using RAG.")
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = FAISS.load_local(agent_vector_store_path, embeddings, allow_dangerous_deserialization=True)
            retriever = vector_store.as_retriever()

            # === YEH HAI NAYA, SMART PROMPT ===
            # Humne agent ke niyam badal diye hain.
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant acting with the personality defined by this system prompt: "{system_prompt}"

            First, review the following context from the user's documents to see if it's relevant to the user's question.
            
            Context:
            {context}

            Based on the user's question and the context, formulate a response.
            - If the context is relevant and helpful, use it to ground your answer.
            - If the context is not relevant to the question, answer the question using your general knowledge and abilities.

            Question: {input}
            """)
            # === PROMPT KA BADLAAV KHATAM ===
            
            document_chain = create_stuff_documents_chain(llm, prompt)
            retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            response = retrieval_chain.invoke({
                "input": user_message,
                "system_prompt": agent.system_prompt
            })
            response_content = response['answer']

        else:
            # --- NON-RAG PATH: The agent uses its base intelligence ---
            print(f"No vector store found for Agent {agent.id}. Using base intelligence.")
            prompt = ChatPromptTemplate.from_messages([
                ("system", agent.system_prompt),
                ("user", "{input}")
            ])
            chain = prompt | llm
            response = chain.invoke({"input": user_message})
            response_content = response.content

        return jsonify({'response': response_content})

    except Exception as e:
        print(f"Chat API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500