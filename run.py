import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    print("\n=======================================================")
    print("  Smart Expense Tracker - Starting Flask Server")
    print(f"  URL: http://{host}:{port}/")
    print("=======================================================\n")
    
    app.run(host=host, port=port, debug=debug)
