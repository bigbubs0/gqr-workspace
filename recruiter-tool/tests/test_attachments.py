from __future__ import annotations

import importlib
import os
import sqlite3
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def purge_modules() -> None:
    for module_name in ["database", "file_handler"]:
        sys.modules.pop(module_name, None)


class AttachmentStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="attachment-tests-")
        temp_path = Path(self.temp_dir.name)

        purge_modules()
        self.database = importlib.import_module("database")
        self.database.DB_PATH = str(temp_path / "candidates.db")

        self.file_handler = importlib.import_module("file_handler")
        self.file_handler.DB_PATH = self.database.DB_PATH
        self.file_handler.UPLOAD_FOLDER = str(temp_path / "uploads")

        self.database.init_db()

    def tearDown(self):
        purge_modules()
        self.temp_dir.cleanup()

    def _upload(self, name: str, content: bytes) -> int:
        storage = FileStorage(stream=BytesIO(content), filename=name)
        return self.file_handler.save_attachment(1, storage)

    def _attachment_path(self, attachment_id: int) -> str:
        conn = sqlite3.connect(self.database.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        return row[0]

    def test_duplicate_attachment_names_get_distinct_files(self):
        first_id = self._upload("cv.pdf", b"first version")
        second_id = self._upload("cv.pdf", b"second version")

        first_path = self._attachment_path(first_id)
        second_path = self._attachment_path(second_id)

        self.assertNotEqual(first_path, second_path)
        self.assertEqual(Path(first_path).read_bytes(), b"first version")
        self.assertEqual(Path(second_path).read_bytes(), b"second version")

        self.file_handler.delete_attachment(first_id)

        self.assertFalse(os.path.exists(first_path))
        self.assertTrue(os.path.exists(second_path))
        self.assertEqual(Path(second_path).read_bytes(), b"second version")

    def test_delete_preserves_file_while_other_rows_reference_it(self):
        shared_path = Path(self.file_handler.UPLOAD_FOLDER) / "1" / "shared.pdf"
        shared_path.parent.mkdir(parents=True)
        shared_path.write_bytes(b"shared content")

        conn = sqlite3.connect(self.database.DB_PATH)
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO attachments (candidate_id, file_name, file_type, file_path, description)
            VALUES (1, 'shared.pdf', 'pdf', ?, '')
            """,
            [(str(shared_path),), (str(shared_path),)],
        )
        first_id, second_id = [row[0] for row in cursor.execute("SELECT id FROM attachments ORDER BY id")]
        conn.commit()
        conn.close()

        self.file_handler.delete_attachment(first_id)

        self.assertTrue(shared_path.exists())
        self.file_handler.delete_attachment(second_id)
        self.assertFalse(shared_path.exists())


if __name__ == "__main__":
    unittest.main()
