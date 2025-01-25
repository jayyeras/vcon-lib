import pytest
from src.vcon.dialog import Dialog
import hashlib
import base64
import requests
from unittest.mock import Mock, patch
from datetime import datetime


class TestDialog:
    # Initialization of Dialog object with all parameters
    def test_initialization_with_all_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        # Given
        party_history = [PartyHistory(1, "join", datetime.now())]
        dialog = Dialog(
            type="text",
            start=datetime.now(),
            duration=120.0,
            parties=[1, 2],
            originator=1,
            mimetype="text/plain",
            filename="example.txt",
            body="Hello, World!",
            encoding="utf-8",
            url="http://example.com",
            alg="sha256",
            signature="signature",
            disposition="inline",
            party_history=party_history,
            transferee=2,
            transferor=1,
            transfer_target=3,
            original=1,
            consultation=2,
            target_dialog=3,
            campaign="campaign1",
            interaction="interaction1",
            skill="skill1",
        )

        # When & Then
        assert dialog.type == "text"
        assert dialog.duration == 120.0
        assert dialog.parties == [1, 2]
        assert dialog.party_history == party_history

    # Initialization with missing optional parameters
    def test_initialization_with_missing_optional_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog

        # Given
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            duration=None,
            parties=[1, 2],
            originator=None,
            mimetype=None,
            filename=None,
            body=None,
            encoding=None,
            url=None,
            alg=None,
            signature=None,
            disposition=None,
            party_history=None,
            transferee=None,
            transferor=None,
            transfer_target=None,
            original=None,
            consultation=None,
            target_dialog=None,
            campaign=None,
            interaction=None,
            skill=None,
        )

        # When & Then
        assert dialog.type == "audio"
        assert not hasattr(dialog, "duration")
        assert not hasattr(dialog, "originator")
        assert not hasattr(dialog, "mimetype")

    def test_initialization_with_default_optional_parameters(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(
            type="video", start=datetime.now(), duration=0.0, parties=[1], originator=1
        )

        # When & Then
        assert dialog.duration == 0.0
        assert dialog.parties == [1]
        assert dialog.originator == 1

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            duration=0.0,
            parties=[1],
            originator=None,
        )

        assert not hasattr(dialog, "originator")
        assert not hasattr(dialog, "body")

        dialog = Dialog(
            type="video",
            start=datetime.now(),
            duration=0.0,
            parties=[1],
            originator=1,
            mimetype="video/mp4",
        )

        # When & Then
        assert dialog.mimetype == "video/mp4"

    # Conversion of Dialog object to dictionary
    def test_conversion_to_dict(self):
        # Given
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from src.vcon.party import PartyHistory

        party_time = datetime.now().isoformat()
        party_history = [PartyHistory(1, "join", party_time)]
        dialog = Dialog(
            type="text",
            start=datetime.now(),
            duration=120.0,
            parties=[1, 2],
            originator=1,
            mimetype="text/plain",
            filename="example.txt",
            body="Hello, World!",
            encoding="utf-8",
            url="http://example.com",
            alg="sha256",
            signature="signature",
            disposition="inline",
            party_history=party_history,
            transferee=2,
            transferor=1,
            transfer_target=3,
            original=1,
            consultation=2,
            target_dialog=3,
            campaign="campaign1",
            interaction="interaction1",
            skill="skill1",
        )

        # When
        dialog_dict = dialog.to_dict()

        # Then
        assert dialog_dict["type"] == "text"
        assert dialog_dict["duration"] == 120.0
        assert dialog_dict["parties"] == [1, 2]
        assert dialog_dict["party_history"] == [
            {"party": 1, "event": "join", "time": party_time}
        ]
        assert dialog_dict["party_history"] == [
            {"party": 1, "event": "join", "time": party_time}
        ]

    # Test the meta variable in the dialog
    def test_meta_variable_in_dialog(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog

        type = "audio"
        start = datetime.now().isoformat()
        parties = [1, 2]
        meta = {"key": "value"}

        dialog = Dialog(type=type, start=start, parties=parties, meta=meta)

        assert dialog.type == type
        assert dialog.start == start
        assert dialog.parties == parties
        assert dialog.meta == meta

    # Successfully fetches external data from a valid URL
    def test_fetch_external_data_success(self, mocker):
        # Arrange
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.headers = {"Content-Type": "text/plain"}
        response_mock.text = "sample data"
        mocker.patch("requests.get", return_value=response_mock)

        # Act
        dialog.add_external_data(url, filename, mimetype)

        # Assert
        assert dialog.mimetype == "text/plain"
        assert dialog.filename == filename
        assert dialog.alg == "sha256"
        assert dialog.encoding == "base64url"
        expected_signature = base64.urlsafe_b64encode(
            hashlib.sha256("sample data".encode()).digest()
        ).decode()
        assert dialog.signature == expected_signature
        assert not hasattr(dialog, "body")

    # URL returns a non-200 status code
    def test_fetch_external_data_failure(self, mocker):
        # Arrange
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 404
        mocker.patch("requests.get", return_value=response_mock)

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            dialog.add_external_data(url, filename, mimetype)

        assert str(excinfo.value) == "Failed to fetch external data: 404"

    # Correctly sets the mimetype from the response headers
    def test_correctly_sets_mimetype(self, mocker):
        # Setup
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "example_data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.headers = {"Content-Type": mimetype}
        response_mock.text = "dummy data"
        mocker.patch("requests.get", return_value=response_mock)

        # Invoke
        dialog.add_external_data(url, filename, None)

        # Assert
        assert dialog.mimetype == mimetype

    # Overrides the filename if provided
    def test_overrides_filename_if_provided(self, mocker):
        # Setup
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        url = "http://example.com/data"
        filename = "example_data.txt"
        new_filename = "new_data.txt"
        mimetype = "text/plain"
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.headers = {"Content-Type": mimetype}
        response_mock.text = "dummy data"
        mocker.patch("requests.get", return_value=response_mock)

        # Invoke
        dialog.add_external_data(url, filename, None)
        dialog.add_external_data(url, new_filename, None)

        # Assert
        assert dialog.filename == new_filename

    # Correctly sets body, filename, and mimetype attributes
    def test_correctly_sets_attributes(self):
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        body = "sample body"
        filename = "sample.txt"
        mimetype = "text/plain"

        dialog.add_inline_data(body, filename, mimetype)

        assert dialog.body == body
        assert dialog.filename == filename
        assert dialog.mimetype == mimetype

    # Handles empty string for body
    def test_handles_empty_body(self):
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])
        body = ""
        filename = "empty.txt"
        mimetype = "text/plain"

        dialog.add_inline_data(body, filename, mimetype)

        assert dialog.body == body
        assert dialog.filename == filename
        assert dialog.mimetype == mimetype
        assert (
            dialog.signature
            == base64.urlsafe_b64encode(hashlib.sha256(body.encode()).digest()).decode()
        )

    # Generates a valid SHA-256 hash signature for the body
    def test_valid_sha256_signature(self):
        # Initialize the dialog object
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])

        # Add inline data
        dialog.add_inline_data("example_body", "example_filename", "text/plain")

        # Check if the SHA-256 hash signature is valid
        expected_signature = base64.urlsafe_b64encode(
            hashlib.sha256("example_body".encode()).digest()
        ).decode()
        assert dialog.signature == expected_signature

    # Sets the encoding to "base64url"
    def test_encoding_base64url(self):
        # Initialize the dialog object
        dialog = Dialog(type="text", start="2023-06-01T10:00:00Z", parties=[0])

        # Add inline data
        dialog.add_inline_data("example_body", "example_filename", "text/plain")

        # Check if the encoding is set to "base64url"
        assert dialog.encoding == "base64url"

    # Initializes Dialog object with all required parameters
    def test_initializes_with_required_parameters(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog

        dialog = Dialog(type="text", start=datetime.now(), parties=[1, 2, 3])

        assert dialog.type == "text"
        assert isinstance(dialog.start, str)
        assert dialog.parties == [1, 2, 3]

    # Handles invalid datetime string for start parameter
    def test_handles_invalid_datetime_string(self):
        from src.vcon.dialog import Dialog
        from dateutil.parser import ParserError
        import pytest

        with pytest.raises(ParserError):
            Dialog(type="text", start="invalid-datetime", parties=[1, 2, 3])

    # Converts start time to ISO 8601 string if provided as datetime
    def test_convert_datetime_to_iso_string(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from unittest.mock import patch

        # Define a datetime object for the start time
        start_time = datetime(2022, 9, 15, 10, 30, 0)

        # Create a Dialog object with a datetime start time
        with patch("src.vcon.dialog.parser") as mock_parser:
            mock_parser.parse.return_value.isoformat.return_value = (
                "2022-09-15T10:30:00"
            )
            dialog = Dialog(type="audio", start=start_time, parties=[1, 2])

        # Check if the start time is converted to ISO 8601 string
        assert dialog.start == "2022-09-15T10:30:00"

    # Converts start time to ISO 8601 string if provided as string
    def test_convert_string_to_iso_string(self):
        from datetime import datetime
        from src.vcon.dialog import Dialog
        from unittest.mock import patch

        start_time = "2022-01-01T12:00:00"
        expected_iso_time = "2022-01-01T12:00:00"

        with patch("src.vcon.dialog.parser") as mock_parser:
            mock_parser.parse.return_value.isoformat.return_value = expected_iso_time

            dialog = Dialog(type="text", start=start_time, parties=[1, 2, 3])

            assert dialog.start == expected_iso_time

    def test_to_inline_data_binary(self):
        # Create some fake binary audio data
        fake_binary_data = (
            b"\x52\x49\x46\x46\x24\x08\x00\x00\x57\x41\x56\x45"  # WAV header snippet
        )

        # Mock the requests.get response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = fake_binary_data
        mock_response.headers = {"Content-Type": "audio/x-wav"}

        # Create a dialog with external data
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            parties=[1, 2],
            url="http://example.com/audio.wav",
        )

        # Mock the requests.get call
        with patch("requests.get", return_value=mock_response):
            dialog.to_inline_data()

        # Verify the conversion was successful
        assert not hasattr(dialog, "url")  # URL should be removed
        assert dialog.mimetype == "audio/x-wav"
        assert dialog.filename == "audio.wav"
        assert dialog.encoding == "base64url"
        assert dialog.alg == "sha256"

        # Decode the base64url body and verify it matches original content
        decoded_body = base64.urlsafe_b64decode(dialog.body.encode())
        assert decoded_body == fake_binary_data

        # Verify the signature matches the content
        expected_signature = base64.urlsafe_b64encode(
            hashlib.sha256(fake_binary_data).digest()
        ).decode()
        assert dialog.signature == expected_signature

    def test_to_inline_data_failed_request(self):
        # Create a dialog with external data
        dialog = Dialog(
            type="audio",
            start=datetime.now(),
            parties=[1, 2],
            url="http://example.com/audio.wav",
        )

        # Mock a failed request
        mock_response = Mock()
        mock_response.status_code = 404

        # Verify that the conversion raises an exception
        with patch("requests.get", return_value=mock_response):
            with pytest.raises(Exception) as exc_info:
                dialog.to_inline_data()
            assert "Failed to fetch external data: 404" in str(exc_info.value)
