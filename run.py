from app import create_app
from dotenv import load_dotenv  # <-- ADD THIS LINE

load_dotenv()  # <-- AND ADD THIS LINE

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)