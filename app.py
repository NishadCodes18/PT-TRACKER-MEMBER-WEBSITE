import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for shared backend models
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Load environment from parent directory
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

from member_app import create_member_app

app = create_member_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
