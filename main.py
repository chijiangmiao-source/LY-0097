import os
from dotenv import load_dotenv
from waitress import serve
from app import create_app

load_dotenv()

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', '8000'))
    print(f"Starting server on http://localhost:{port}")
    print(f"Default admin: admin / admin123")
    serve(app, host='0.0.0.0', port=port)
