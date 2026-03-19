import os
import sqlite3
import shutil
from werkzeug.utils import secure_filename
from database import DB_PATH

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'mp3', 'm4a', 'wav', 'png', 'jpg', 'jpeg'}

def init_upload_folder():
    """Create upload folder if it doesn't exist"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_attachment(candidate_id, file, description=''):
    """Save a file attachment for a candidate"""
    init_upload_folder()

    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    # Create candidate-specific folder
    candidate_folder = os.path.join(UPLOAD_FOLDER, str(candidate_id))
    os.makedirs(candidate_folder, exist_ok=True)

    # Secure the filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(candidate_folder, filename)

    # Save the file
    file.save(file_path)

    # Get file type
    file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    # Store in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO attachments (candidate_id, file_name, file_type, file_path, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (candidate_id, filename, file_type, file_path, description))

    attachment_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return attachment_id

def get_attachments(candidate_id):
    """Get all attachments for a candidate"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM attachments
        WHERE candidate_id = ?
        ORDER BY uploaded_at DESC
    ''', (candidate_id,))

    rows = cursor.fetchall()
    attachments = [dict(row) for row in rows]

    conn.close()
    return attachments

def delete_attachment(attachment_id):
    """Delete an attachment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get file path before deleting
    cursor.execute('SELECT file_path FROM attachments WHERE id = ?', (attachment_id,))
    row = cursor.fetchone()

    if row:
        file_path = row[0]
        # Delete from database
        cursor.execute('DELETE FROM attachments WHERE id = ?', (attachment_id,))
        conn.commit()

        # Delete physical file
        if os.path.exists(file_path):
            os.remove(file_path)

    conn.close()
