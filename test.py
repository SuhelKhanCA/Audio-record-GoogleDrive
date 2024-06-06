from flask import Flask, render_template, request, jsonify
import os
import uuid
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import pandas as pd
import random

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
    df = pd.read_excel('text_data.xlsx')
    
    random_row = df.sample().iloc[0]
    text_id = random_row['ID']
    english_text = random_row['English Text']
    hindi_text = random_row['Hindi Text']
    
    return render_template('index.html', text_id=text_id, english_text=english_text, hindi_text=hindi_text)

@app.route('/upload', methods=['POST'])
def upload_file():
    user_name = request.form.get('user_name')
    text_id = request.form.get('text_id')

    if 'audio_data_english' not in request.files or 'audio_data_hindi' not in request.files or not user_name or not text_id:
        return jsonify({"status": "error", "message": "All inputs are required"}), 400


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


    english_file = request.files['audio_data_english']
    english_filename = f"{user_name}_{text_id}_English_{timestamp}.wav"
    english_path = os.path.join(app.config['RECORD_FOLDER'], english_filename)
    english_file.save(english_path)

    hindi_file = request.files['audio_data_hindi']
    hindi_filename = f"{user_name}_{text_id}_Hindi_{timestamp}.wav"
    hindi_path = os.path.join(app.config['RECORD_FOLDER'], hindi_filename)
    hindi_file.save(hindi_path)
    
    try:
        english_file_id = upload_to_drive(english_path, english_filename)
        hindi_file_id = upload_to_drive(hindi_path, hindi_filename)

        os.remove(english_path)
        os.remove(hindi_path)
        
        return jsonify({"status": "success", "message": "Files uploaded and saved to Google Drive!", "english_file_id": english_file_id, "hindi_file_id": hindi_file_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
