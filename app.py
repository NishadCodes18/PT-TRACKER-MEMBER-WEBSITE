import os
import sys
from dotenv import load_dotenv

# Add current directory to path for backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment from current directory
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path)

from member_app import create_member_app

app = create_member_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
