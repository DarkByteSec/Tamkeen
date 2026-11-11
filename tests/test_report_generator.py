import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import ui
from report_generator import build_report_text, generate_report
from validators import get_governorate_names


class ReportGeneratorTests(unittest.TestCase):
    def test_report_excludes_national_id_and_labels_generic_documents(self):
        national_id = "31234567890123"
        data = {
            "lang": "ar",
            "service": "خدمة اختبار",
            "user_data": {
                "national_id": national_id,
                "birth_date": "2001-02-03",
                "governorate": {"ar": "القاهرة", "en": "Cairo"},
            },
            "docs_have": [],
            "docs_missing": ["مستند عام"],
            "docs_generic": True,
        }

        text = build_report_text(data)

        self.assertNotIn(national_id, text)
        self.assertIn("ليست تأكيدًا رسميًا", text)

    def test_report_filenames_are_unique_for_same_timestamp(self):
        fixed_time = datetime(2026, 1, 2, 3, 4, 5, 6)
        original_directory = os.getcwd()
        with tempfile.TemporaryDirectory() as temporary_directory:
            os.chdir(temporary_directory)
            try:
                with patch("report_generator.datetime") as mocked_datetime:
                    mocked_datetime.now.return_value = fixed_time
                    first_path = generate_report({"lang": "en"})
                    second_path = generate_report({"lang": "en"})
                    first_exists = Path(first_path).exists()
                    second_exists = Path(second_path).exists()
            finally:
                os.chdir(original_directory)

        self.assertNotEqual(first_path, second_path)
        self.assertTrue(first_exists)
        self.assertTrue(second_exists)

    def test_governorate_names_are_localized(self):
        self.assertEqual(
            get_governorate_names("01"),
            {"ar": "القاهرة", "en": "Cairo"},
        )

    def test_ui_report_payload_never_contains_national_id(self):
        national_id = "31234567890123"
        session_state = SimpleNamespace(
            lang="en",
            service={"id": "service-1", "name_en": "Test service", "documents": []},
            docs={},
            include_id=True,
            nid_result={"valid": True},
            nid_data={
                "birth_date": "2001-02-03",
                "governorate": {"ar": "القاهرة", "en": "Cairo"},
                "gender": "female",
            },
            nid=national_id,
        )

        with patch.object(ui.st, "session_state", session_state):
            report_data = ui.build_report_data()

        self.assertNotIn("national_id", report_data["user_data"])
        self.assertEqual(
            set(report_data["user_data"]),
            {"birth_date", "governorate"},
        )

    def test_streamlit_app_starts_without_exceptions(self):
        from streamlit.testing.v1 import AppTest

        app_path = Path(ui.__file__).with_name("app.py")
        app = AppTest.from_file(str(app_path)).run()

        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()