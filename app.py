import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Universal downloader Bot is Running'

if __name__ == "__main__":
    # Get the PORT from environment variables, default to 8080 if not found
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
