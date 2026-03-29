"""Tests for recruiter-tool/file_handler.py"""

import os
import sys
import sqlite3

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import file_handler
import database


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    """Override UPLOAD_FOLDER to a temp directory."""
    upload_path = str(tmp_path / 'uploads')
    monkeypatch.setattr(file_handler, 'UPLOAD_FOLDER', upload_path)
    return upload_path


@pytest.fixture
def mock_file(mocker):
    """Create a mock file upload object."""
    def _make_file(filename='resume.pdf', content=b'%PDF-1.4 fake content'):
        mock = mocker.MagicMock()
        mock.filename = filename
        mock.save = mocker.MagicMock()
        return mock
    return _make_file


class TestAllowedFile:
    """Tests for allowed_file()."""

    @pytest.mark.parametrize('filename,expected', [
        ('resume.pdf', True),
        ('document.doc', True),
        ('document.docx', True),
        ('notes.txt', True),
        ('recording.mp3', True),
        ('voice.m4a', True),
        ('audio.wav', True),
        ('photo.png', True),
        ('headshot.jpg', True),
        ('avatar.jpeg', True),
        ('malware.exe', False),
        ('script.py', False),
        ('data.csv', False),
        ('archive.zip', False),
        ('noextension', False),
        ('', False),
        ('.pdf', True),
    ])
    def test_file_extension_validation(self, filename, expected):
        assert file_handler.allowed_file(filename) == expected

    def test_case_insensitive_extension(self):
        assert file_handler.allowed_file('resume.PDF')
        assert file_handler.allowed_file('document.DocX')

    def test_double_extension_uses_last(self):
        assert file_handler.allowed_file('file.exe.pdf')
        assert not file_handler.allowed_file('file.pdf.exe')


class TestInitUploadFolder:
    """Tests for init_upload_folder()."""

    def test_creates_folder_if_missing(self, upload_dir):
        assert not os.path.exists(upload_dir)
        file_handler.init_upload_folder()
        assert os.path.isdir(upload_dir)

    def test_idempotent_when_exists(self, upload_dir):
        os.makedirs(upload_dir)
        file_handler.init_upload_folder()
        assert os.path.isdir(upload_dir)


class TestSaveAttachment:
    """Tests for save_attachment()."""

    def test_saves_file_and_returns_id(self, tmp_db, upload_dir, mock_file):
        cid = database.save_candidate({'name': 'Test'})
        f = mock_file('resume.pdf')
        aid = file_handler.save_attachment(cid, f, 'CV upload')
        assert isinstance(aid, int)
        assert aid > 0
        f.save.assert_called_once()

    def test_creates_candidate_subfolder(self, tmp_db, upload_dir, mock_file):
        cid = database.save_candidate({'name': 'Test'})
        f = mock_file('resume.pdf')
        file_handler.save_attachment(cid, f)
        expected_folder = os.path.join(upload_dir, str(cid))
        assert os.path.isdir(expected_folder)

    def test_returns_none_for_empty_file(self, tmp_db, upload_dir, mock_file):
        f = mock_file('')
        result = file_handler.save_attachment(1, f)
        assert result is None

    def test_returns_none_for_none_file(self, tmp_db, upload_dir):
        result = file_handler.save_attachment(1, None)
        assert result is None

    def test_rejects_disallowed_file_type(self, tmp_db, upload_dir, mock_file):
        cid = database.save_candidate({'name': 'Test'})
        f = mock_file('malware.exe')
        with pytest.raises(ValueError, match='File type not allowed'):
            file_handler.save_attachment(cid, f)

    def test_stores_record_in_database(self, tmp_db, upload_dir, mock_file):
        cid = database.save_candidate({'name': 'Test'})
        f = mock_file('cv.docx')
        file_handler.save_attachment(cid, f, 'Main CV')

        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM attachments WHERE candidate_id = ?', (cid,))
        row = dict(cursor.fetchone())
        conn.close()

        assert row['file_name'] == 'cv.docx'
        assert row['file_type'] == 'docx'
        assert row['description'] == 'Main CV'


class TestGetAttachments:
    """Tests for get_attachments()."""

    def test_returns_empty_list_for_no_attachments(self, tmp_db, upload_dir):
        cid = database.save_candidate({'name': 'Test'})
        result = file_handler.get_attachments(cid)
        assert result == []

    def test_returns_all_attachments_for_candidate(self, tmp_db, upload_dir, mock_file):
        cid = database.save_candidate({'name': 'Test'})
        file_handler.save_attachment(cid, mock_file('cv.pdf'), 'CV')
        file_handler.save_attachment(cid, mock_file('cover.docx'), 'Cover Letter')
        result = file_handler.get_attachments(cid)
        assert len(result) == 2

    def test_does_not_return_other_candidates_files(self, tmp_db, upload_dir, mock_file):
        cid1 = database.save_candidate({'name': 'Alice'})
        cid2 = database.save_candidate({'name': 'Bob'})
        file_handler.save_attachment(cid1, mock_file('cv1.pdf'))
        file_handler.save_attachment(cid2, mock_file('cv2.pdf'))
        result = file_handler.get_attachments(cid1)
        assert len(result) == 1
        assert result[0]['file_name'] == 'cv1.pdf'


class TestDeleteAttachment:
    """Tests for delete_attachment()."""

    def test_deletes_record_from_database(self, tmp_db, upload_dir, mock_file):
        cid = database.save_candidate({'name': 'Test'})
        aid = file_handler.save_attachment(cid, mock_file('cv.pdf'))
        file_handler.delete_attachment(aid)
        result = file_handler.get_attachments(cid)
        assert len(result) == 0

    def test_deletes_physical_file(self, tmp_db, upload_dir, tmp_path):
        cid = database.save_candidate({'name': 'Test'})

        # Create a real file to test physical deletion
        candidate_folder = os.path.join(upload_dir, str(cid))
        os.makedirs(candidate_folder, exist_ok=True)
        file_path = os.path.join(candidate_folder, 'cv.pdf')
        with open(file_path, 'w') as f:
            f.write('test content')

        # Insert attachment record manually pointing to real file
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO attachments (candidate_id, file_name, file_type, file_path) VALUES (?, ?, ?, ?)',
            (cid, 'cv.pdf', 'pdf', file_path)
        )
        aid = cursor.lastrowid
        conn.commit()
        conn.close()

        assert os.path.exists(file_path)
        file_handler.delete_attachment(aid)
        assert not os.path.exists(file_path)

    def test_handles_nonexistent_attachment_gracefully(self, tmp_db, upload_dir):
        # Should not raise
        file_handler.delete_attachment(9999)
