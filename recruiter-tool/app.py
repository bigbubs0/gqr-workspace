from flask import Flask, render_template, request, jsonify, send_file
import os
from database import init_db, save_candidate, search_candidates, get_candidate
from ai_processor import extract_candidate_info, generate_candidate_brief
from file_handler import save_attachment, get_attachments, delete_attachment, init_upload_folder

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize database and upload folder
init_db()
init_upload_folder()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_transcript():
    """Process a candidate transcript and extract information"""
    try:
        data = request.get_json()
        transcript = data.get('transcript', '')
        search_tags = data.get('search_tags', [])

        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400

        # Extract candidate information using AI
        candidate_data = extract_candidate_info(transcript)

        # Add transcript and search tags
        candidate_data['transcript'] = transcript
        candidate_data['search_tags'] = search_tags

        # Generate formatted brief
        brief = generate_candidate_brief(candidate_data)

        # Save to database
        candidate_id = save_candidate(candidate_data)

        return jsonify({
            'success': True,
            'candidate_id': candidate_id,
            'brief': brief,
            'data': candidate_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    """Search candidates with filters"""
    try:
        filters = {
            'therapeutic_area': request.args.get('therapeutic_area'),
            'phase': request.args.get('phase'),
            'company': request.args.get('company'),
            'search_tag': request.args.get('search_tag'),
            'days_back': request.args.get('days_back')
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v}

        candidates = search_candidates(filters)

        return jsonify({
            'success': True,
            'count': len(candidates),
            'candidates': candidates
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidate/<int:candidate_id>', methods=['GET'])
def get_candidate_detail(candidate_id):
    """Get detailed information for a specific candidate"""
    try:
        candidate = get_candidate(candidate_id)

        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404

        brief = generate_candidate_brief(candidate)

        return jsonify({
            'success': True,
            'candidate': candidate,
            'brief': brief
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_candidates():
    """Export multiple candidates based on filter criteria"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})

        candidates = search_candidates(filters)

        # Generate briefs for all candidates
        export_text = ""
        for i, candidate in enumerate(candidates, 1):
            brief = generate_candidate_brief(candidate)
            export_text += f"\n{'='*80}\n"
            export_text += f"CANDIDATE #{i}\n"
            export_text += f"{'='*80}\n\n"
            export_text += brief
            export_text += "\n"

        return jsonify({
            'success': True,
            'count': len(candidates),
            'export_text': export_text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidate/<int:candidate_id>/upload', methods=['POST'])
def upload_attachment(candidate_id):
    """Upload a file attachment for a candidate"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        description = request.form.get('description', '')

        attachment_id = save_attachment(candidate_id, file, description)

        return jsonify({
            'success': True,
            'attachment_id': attachment_id,
            'message': 'File uploaded successfully'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidate/<int:candidate_id>/attachments', methods=['GET'])
def get_candidate_attachments(candidate_id):
    """Get all attachments for a candidate"""
    try:
        attachments = get_attachments(candidate_id)

        return jsonify({
            'success': True,
            'attachments': attachments
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attachment/<int:attachment_id>/download', methods=['GET'])
def download_attachment(attachment_id):
    """Download a specific attachment"""
    try:
        import sqlite3
        from database import DB_PATH

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT file_path, file_name FROM attachments WHERE id = ?', (attachment_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'Attachment not found'}), 404

        file_path, file_name = row

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404

        return send_file(file_path, as_attachment=True, download_name=file_name)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attachment/<int:attachment_id>', methods=['DELETE'])
def remove_attachment(attachment_id):
    """Delete an attachment"""
    try:
        delete_attachment(attachment_id)

        return jsonify({
            'success': True,
            'message': 'Attachment deleted successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
