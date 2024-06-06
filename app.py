from flask import Flask, render_template, request, jsonify
import os
import uuid
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
RECORD_FOLDER = 'record'
app.config['RECORD_FOLDER'] = RECORD_FOLDER

if not os.path.exists(RECORD_FOLDER):
    os.makedirs(RECORD_FOLDER)

# Google Drive API settings
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = "drivecloud-425512-d71d80cfa1ad.json"
PARENT_FOLDER_ID = "1rj8Hd1ckkhdVeRjwPhlyZ-9IqQnVnT94"

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_to_drive(file_path, filename):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': filename,
        'parents': [PARENT_FOLDER_ID]
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return file.get('id')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_data_english' not in request.files or 'audio_data_hindi' not in request.files:
        return jsonify({"status": "error", "message": "Both English and Hindi audio files are required"}), 400

    # Generate unique ID and timestamp
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Process English audio
    english_file = request.files['audio_data_english']
    english_filename = f"{unique_id}_English_{timestamp}.wav"
    english_path = os.path.join(app.config['RECORD_FOLDER'], english_filename)
    english_file.save(english_path)

    # Process Hindi audio
    hindi_file = request.files['audio_data_hindi']
    hindi_filename = f"{unique_id}_Hindi_{timestamp}.wav"
    hindi_path = os.path.join(app.config['RECORD_FOLDER'], hindi_filename)
    hindi_file.save(hindi_path)
    
    try:
        # Upload both files to Google Drive
        english_file_id = upload_to_drive(english_path, english_filename)
        hindi_file_id = upload_to_drive(hindi_path, hindi_filename)

        # Remove local files after upload
        os.remove(english_path)
        os.remove(hindi_path)
        
        return jsonify({"status": "success", "message": "Files uploaded and saved to Google Drive!", "english_file_id": english_file_id, "hindi_file_id": hindi_file_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
