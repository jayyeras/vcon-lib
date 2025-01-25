from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from typing import Union

import pytest
import json
from datetime import datetime

from vcon.vcon import Attachment

"""
This covers testing the main methods of the Vcon class, including:

Building from JSON
Building a new instance
Adding and retrieving tags
Adding and finding attachments
Adding and finding analysis
Adding parties and dialogs
Serializing to JSON
Generating a UUID8 based on a domain name
"""


test_vcon_string = (
    '{"uuid":"0192aa73-e702-8cef-9dd8-dd37220d739c","vcon":"0.0.1",'
    '"created_at":"2024-10-20T15:02:55.490850+00:00","parties":['
    '{"tel":"+14513886516","mailto":"david.scott@pickrandombusinesstype.com",'
    '"name":"David Scott","meta":{"role":"agent"}},'
    '{"tel":"+16171557264","mailto":"diane.allen@gmail.com","name":"Diane Allen",'
    '"meta":{"role":"customer"}}],"dialog":[{"type":"recording",'
    '"start":"2024-10-20T15:02:54.888840","duration":52.68,"parties":[0,1],'
    '"mimetype":"audio/x-wav","filename":"bb1489ad-0b45-47a0-bca6-de124da39a3a.mp3",'
    '"body":"","encoding":"base64url","alg":"sha256",'
    '"signature":"JBzeZEPDNVm8iPEeout0UK-B2Fp6JzeQxqy70SvM_MU=",'
    '"disposition":"ANSWERED"}],"attachments":[{"type":"generation_info","body":'
    '{"agent_name":"David Scott","customer_name":"Diane Allen",'
    '"business":"Auto Repair Shop","problem":"billing","emotion":"disappointed",'
    '"prompt":"\\nGenerate a fake conversation between a customer and an agent.'
    "\\nThe agent should introduce themselves, their company and give the customer"
    "\\ntheir name. The agent should ask for the customer's name.\\nAs part of the "
    "conversation, have the agent ask for two pieces of\\npersonal information.  "
    "Spell out numbers. For example, 1000 should be\\nsaid as one zero zero zero, "
    "not one thousand. The conversation should be\\nat least 10 lines long and be "
    "complete. At the end\\nof the conversation, the agent should thank the customer "
    "for their time\\nand end the conversation. Return the conversation formatted "
    "\\nlike the following example:\\n\\n{'conversation': \\n    [\\n    {'speaker': "
    "'Agent', 'message': 'xxxxx'}, \\n    {'speaker': 'Customer', 'message': "
    "\\\"xxxxx.\\\"}, \\n    {'speaker': 'Agent', 'message': \\\"xxxxxx\\\"}\\n    ] "
    "\\n}\\n\\n\\nIn this conversation, the agent's name is David Scott and the "
    "customer's name is Diane Allen.  The conversation is about a random business "
    '(a Auto Repair Shop ) and is a conversation about billing.",'
    '"created_on":"2024-10-20T15:02:55.490740","model":"gpt-4o-mini"},'
    '"encoding":"none"}],"analysis":[{"type":"analysis_info","dialog":0,'
    '"vendor":"openai","body":[{"speaker":"Agent","message":"Hello! My name is '
    "David Scott, and I'm with Quick Fix Auto Repair. How can I assist you today?\"},"
    '{"speaker":"Customer","message":"Hi David, I\'m Diane Allen. I have a question '
    'about my recent bill."},{"speaker":"Agent","message":"Of course, Diane! I\'d be '
    'happy to help you with that. Can you please provide me with the invoice number?"},'
    '{"speaker":"Customer","message":"Yes, the invoice number is one two three four '
    'five."},{"speaker":"Agent","message":"Thank you for that information. And could '
    'you also confirm your phone number for me?"},{"speaker":"Customer","message":'
    '"Sure, my phone number is two zero two, five six seven, eight nine zero zero."},'
    '{"speaker":"Agent","message":"Great, thank you, Diane. Let me look up your '
    'invoice for a moment."},{"speaker":"Customer","message":"No problem. I appreciate '
    'your help."},{"speaker":"Agent","message":"I see your invoice now. It looks like '
    'there was an extra charge for parts. Would you like me to explain that?"},'
    '{"speaker":"Customer","message":"Yes, I would appreciate that."},'
    '{"speaker":"Agent","message":"The extra charge was for a new battery that was '
    "installed. Thank you for your patience, and please let me know if you have any "
    'more questions."}],"encoding":"none","vendor_schema":{"model":"gpt-4o-mini",'
    '"prompt":"\\nGenerate a fake conversation between a customer and an agent.'
    "\\nThe agent should introduce themselves, their company and give the customer"
    "\\ntheir name. The agent should ask for the customer's name.\\nAs part of the "
    "conversation, have the agent ask for two pieces of\\npersonal information.  "
    "Spell out numbers. For example, 1000 should be\\nsaid as one zero zero zero, "
    "not one thousand. The conversation should be\\nat least 10 lines long and be "
    "complete. At the end\\nof the conversation, the agent should thank the customer "
    "for their time\\nand end the conversation. Return the conversation formatted "
    "\\nlike the following example:\\n\\n{'conversation': \\n    [\\n    {'speaker': "
    "'Agent', 'message': 'xxxxx'}, \\n    {'speaker': 'Customer', 'message': "
    "\\\"xxxxx.\\\"}, \\n    {'speaker': 'Agent', 'message': \\\"xxxxxx\\\"}\\n    ] "
    "\\n}\\n\\n\\nIn this conversation, the agent's name is David Scott and the "
    "customer's name is Diane Allen.  The conversation is about a random business "
    '(a Auto Repair Shop ) and is a conversation about billing."}}]}'
)

GITHUB_WAV_URL = "https://github.com/vcon-dev/vcon-lib/raw/841eca9198397e768f478569a3595a70c6e892cc/tests/sample.mp3"


# Helper function to get the duration of an external audio file. Account for WAV and MP3 files, which have different formats.
# Download the file and calculate the duration.
def get_audio_duration(url: str) -> Union[float, None]:
    """
    Downloads an audio file and calculates its duration.s
    Supports WAV and MP3 formats.

    Args:
        url (str): URL of the audio file

    Returns:
        float: Duration in seconds, or None if file format not supported
    """
    import requests
    import io
    import wave
    from mutagen.mp3 import MP3

    try:
        # Download the file
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to download file from {url}")
            return None

        audio_data = io.BytesIO(response.content)

        # Calculate duration based on file type
        if url.lower().endswith(".wav"):
            with wave.open(audio_data) as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                print(f"Duration: {duration}")
                return duration

        elif url.lower().endswith(".mp3"):
            audio_data.seek(0)
            mp3 = MP3(audio_data)
            print(f"Duration: {mp3.info.length}")
            return mp3.info.length

        return None

    except Exception:
        return None


def test_build_from_json() -> None:
    """
    Test that we can create a Vcon object from a JSON string.

    The JSON string is a sample vCon object that contains a single dialog
    with several turns.

    The test verifies that the resulting Vcon object has the expected UUID,
    vcon version, and created_at timestamp.
    """
    vcon = Vcon.build_from_json(test_vcon_string)
    assert vcon.uuid == "0192aa73-e702-8cef-9dd8-dd37220d739c"
    assert vcon.vcon == "0.0.1"
    assert vcon.created_at == "2024-10-20T15:02:55.490850+00:00"


def test_build_new() -> None:
    vcon = Vcon.build_new()
    assert vcon.uuid is not None
    assert vcon.vcon == "0.0.1"
    assert vcon.created_at is not None


def test_tags() -> None:
    vcon = Vcon.build_new()
    assert vcon.tags is None

    vcon.add_tag("test_tag", "test_value")
    assert vcon.get_tag("test_tag") == "test_value"


def test_add_attachment():
    vcon = Vcon()
    attachment = vcon.add_attachment(type="test_type", body="test_body")

    assert len(vcon.vcon_dict["attachments"]) == 1
    assert vcon.vcon_dict["attachments"][0] == {
        "type": "test_type",
        "body": "test_body",
        "encoding": "none",
    }
    assert isinstance(attachment, Attachment)


def test_add_analysis() -> None:
    vcon = Vcon.build_new()
    vcon.add_analysis(
        type="test_type", dialog=[1, 2], vendor="test_vendor", body={"key": "value"}
    )
    analysis = vcon.find_analysis_by_type("test_type")
    assert analysis["body"] == {"key": "value"}
    assert analysis["dialog"] == [1, 2]
    assert analysis["vendor"] == "test_vendor"


def test_add_dialog() -> None:
    # Given
    vcon = Vcon.build_new()
    dialog = Dialog(
        start="2023-06-01T10:00:00Z", parties=[0], type="text", body="Hello, world!"
    )
    vcon.add_dialog(dialog)

    # When
    found_dialog = vcon.find_dialog("type", "text")

    # Then these dialogs should be the same values. Check
    assert found_dialog.to_dict() == dialog.to_dict()


def test_to_json() -> None:
    vcon = Vcon.build_new()
    json_string = vcon.to_json()
    assert json.loads(json_string) == vcon.to_dict()


def test_uuid8_domain_name() -> None:
    uuid8 = Vcon.uuid8_domain_name("test.com")
    assert uuid8[14] == "8"  # check version is 8


def test_get_tag() -> None:
    vcon = Vcon.build_new()
    vcon.add_tag("test_tag", "test_value")
    assert vcon.get_tag("test_tag") == "test_value"
    assert vcon.get_tag("nonexistent_tag") is None


def test_find_attachment_by_type() -> None:
    vcon = Vcon.build_new()
    vcon.add_attachment(body={"key": "value"}, type="test_type")
    assert vcon.find_attachment_by_type("test_type") == {
        "type": "test_type",
        "body": {"key": "value"},
        "encoding": "none",
    }
    assert vcon.find_attachment_by_type("nonexistent_type") is None


def test_find_analysis_by_type() -> None:
    vcon = Vcon.build_new()
    vcon.add_analysis(
        type="test_type", dialog=[1, 2], vendor="test_vendor", body={"key": "value"}
    )
    assert vcon.find_analysis_by_type("test_type") == {
        "type": "test_type",
        "dialog": [1, 2],
        "vendor": "test_vendor",
        "body": {"key": "value"},
        "encoding": "none",
    }
    assert vcon.find_analysis_by_type("nonexistent_type") is None


def test_find_party_index() -> None:
    vcon = Vcon.build_new()
    p = Party(name="Alice")
    vcon.add_party(p)
    assert vcon.find_party_index("name", "Alice") == 0
    assert vcon.find_party_index("name", "Bob") is None
    assert vcon.find_party_index("nonexistent_field", "Alice") is None
    assert vcon.find_party_index("name", "nonexistent_party") is None

    vcon.add_party(Party(name="Bob"))
    assert vcon.find_party_index("name", "Bob") == 1
    assert vcon.find_party_index("name", "Alice") == 0

    assert vcon.find_party_index("nonexistent_field", "Alice") is None

    vcon.add_party(Party(name="Charlie"))
    assert vcon.find_party_index("name", "Charlie") == 2
    assert vcon.find_party_index("nonexistent_field", "Alice") is None


def test_properties() -> None:
    vcon = Vcon.build_from_json(test_vcon_string)

    assert vcon.uuid == "0192aa73-e702-8cef-9dd8-dd37220d739c"
    assert vcon.created_at == "2024-10-20T15:02:55.490850+00:00"
    assert len(vcon.parties) == 2

    assert vcon.parties[0].to_dict() == {
        "tel": "+14513886516",
        "mailto": "david.scott@pickrandombusinesstype.com",
        "name": "David Scott",
        "meta": {"role": "agent"},
    }
    assert vcon.parties[1].to_dict() == {
        "tel": "+16171557264",
        "mailto": "diane.allen@gmail.com",
        "name": "Diane Allen",
        "meta": {"role": "customer"},
    }

    assert len(vcon.dialog) == 1
    assert vcon.dialog[0] == {
        "type": "recording",
        "start": "2024-10-20T15:02:54.888840",
        "duration": 52.68,
        "parties": [0, 1],
        "mimetype": "audio/x-wav",
        "filename": "bb1489ad-0b45-47a0-bca6-de124da39a3a.mp3",
        "body": "",
        "encoding": "base64url",
        "alg": "sha256",
        "signature": "JBzeZEPDNVm8iPEeout0UK-B2Fp6JzeQxqy70SvM_MU=",
        "disposition": "ANSWERED",
    }

    assert len(vcon.attachments) == 1
    assert vcon.attachments[0]["type"] == "generation_info"
    assert vcon.attachments[0]["encoding"] == "none"
    assert "body" in vcon.attachments[0]

    assert len(vcon.analysis) == 1
    assert vcon.analysis[0]["type"] == "analysis_info"
    assert vcon.analysis[0]["dialog"] == 0
    assert vcon.analysis[0]["vendor"] == "openai"
    assert vcon.analysis[0]["encoding"] == "none"
    assert len(vcon.analysis[0]["body"]) == 11  # 11 conversation turns
    assert vcon.analysis[0]["vendor_schema"]["model"] == "gpt-4o-mini"

    print("All assertions passed!")


def test_to_dict() -> None:
    vcon = Vcon.build_new()
    vcon_dict = vcon.to_dict()
    assert isinstance(vcon_dict, dict)
    assert vcon_dict == json.loads(vcon.to_json())


def test_dumps() -> None:
    vcon = Vcon.build_new()
    json_string = vcon.dumps()
    assert isinstance(json_string, str)
    assert json_string == vcon.to_json()


def test_error_handling() -> None:
    with pytest.raises(json.JSONDecodeError):
        Vcon.build_from_json("invalid_json")


def test_add_and_find_party_index() -> None:
    # Given
    vcon = Vcon.build_new()
    party = Party(mailto="R0Hl4@example.com")

    # When
    vcon.add_party(party)

    # Then
    assert vcon.find_party_index("mailto", "R0Hl4@example.com") == 0
    assert vcon.find_party_index("mailto", "nonexistent_party") is None


def test_find_dialog() -> None:
    # Given
    vcon = Vcon.build_new()
    dialog = Dialog(
        start="2023-06-01T10:00:00Z", parties=[0], type="text", body="Hello, world!"
    )
    vcon.add_dialog(dialog)

    # When
    found_dialog = vcon.find_dialog("type", "text")

    # Then these dialogs should be the same values. Check
    # that the dialog we found is the same as the dialog we added.
    assert found_dialog.to_dict() == dialog.to_dict()


def test_add_special_character_tag() -> None:
    # Given
    vcon = Vcon.build_new()

    # When
    vcon.add_tag("special_tag!@#", "special_value")

    # Then
    assert vcon.get_tag("special_tag!@#") == "special_value"


def test_add_and_find_party_index_by_name() -> None:
    # Given
    vcon = Vcon.build_new()
    party = Party(name="Alice")

    # When
    vcon.add_party(party)

    # Then
    assert vcon.find_party_index("name", "Alice") == 0
    assert vcon.find_party_index("name", "Bob") is None


def test_initializes_with_empty_dict() -> None:
    from src.vcon.vcon import Vcon

    vcon = Vcon()
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict


def test_initializes_with_datetime_created_at() -> None:
    from src.vcon.vcon import Vcon
    from datetime import datetime

    vcon_dict = {"created_at": datetime.now()}
    vcon = Vcon(vcon_dict)
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict


def test_initializes_with_created_at_string() -> None:
    from src.vcon.vcon import Vcon
    import datetime

    vcon_dict = {"created_at": "2022-01-01T12:00:00Z"}
    vcon = Vcon(vcon_dict)
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)


def test_initializes_without_created_at() -> None:
    from src.vcon.vcon import Vcon

    vcon = Vcon({})
    assert isinstance(vcon.vcon_dict, dict)
    assert "created_at" in vcon.vcon_dict


def test_converts_created_at_to_iso_format_when_datetime_provided() -> None:
    from src.vcon.vcon import Vcon
    from datetime import datetime

    test_datetime = datetime(2022, 9, 15, 8, 30, 0)
    vcon = Vcon({"created_at": test_datetime})
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)
    assert len(vcon.vcon_dict["created_at"]) == 19


def test_sets_created_at_to_current_time() -> None:
    from src.vcon.vcon import Vcon

    vcon = Vcon()
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)
    assert datetime.fromisoformat(vcon.vcon_dict["created_at"])


def test_converts_created_at_to_iso_format_with_timezone() -> None:
    from src.vcon.vcon import Vcon
    from datetime import datetime, timezone

    created_at = datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    vcon_dict = {"created_at": created_at}
    vcon = Vcon(vcon_dict)
    assert "created_at" in vcon.vcon_dict
    assert isinstance(vcon.vcon_dict["created_at"], str)
    assert vcon.vcon_dict["created_at"] == created_at.isoformat()


def test_deep_copy_into_vcon_dict() -> None:
    from src.vcon.vcon import Vcon

    vcon_dict = {"created_at": "2022-01-01T12:00:00Z", "data": {"key": "value"}}
    vcon = Vcon(vcon_dict)
    assert vcon.vcon_dict is not vcon_dict, "vcon_dict should be a deep copy"


def test_add_dialog_external_audio() -> None:
    """Test adding a dialog with an external audio file reference"""
    # Given
    vcon = Vcon.build_new()

    external_dialog = Dialog(
        start="2023-06-01T10:00:00Z",
        parties=[0],
        type="recording",
        url=GITHUB_WAV_URL,
        mimetype="audio/wav",
        duration=get_audio_duration(GITHUB_WAV_URL),
        meta={"direction": "in"},
    )

    # When
    vcon.add_dialog(external_dialog)

    # Then
    found_dialog = vcon.find_dialog("type", "recording")
    assert found_dialog.to_dict() == external_dialog.to_dict()
    assert found_dialog.url == GITHUB_WAV_URL
    assert found_dialog.mimetype == "audio/wav"


def test_add_dialog_inline_audio():
    """Test adding a dialog with inline base64 audio data"""
    # Given
    vcon = Vcon.build_new()

    inline_dialog = Dialog(
        start="2023-06-01T10:00:00Z",
        parties=[0],
        type="recording",
        url=GITHUB_WAV_URL,
        mimetype="audio/mp3",
        duration=get_audio_duration(GITHUB_WAV_URL),
        meta={"direction": "out"},
    )

    # When
    vcon.add_dialog(inline_dialog)

    # Then
    found_dialog = vcon.find_dialog("type", "recording")
    assert found_dialog.to_dict() == inline_dialog.to_dict()
    assert found_dialog.url == GITHUB_WAV_URL
    assert found_dialog.mimetype == "audio/mp3"


def test_add_multiple_dialogs():
    """Test adding and finding multiple dialogs"""
    # Given
    vcon = Vcon.build_new()

    text_dialog = Dialog(
        start="2023-06-01T10:00:00Z", parties=[0], type="text", body="Hello, world!"
    )

    audio_dialog = Dialog(
        start="2023-06-01T10:01:00Z",
        parties=[0, 1],
        type="recording",
        url=GITHUB_WAV_URL,
        mimetype="audio/mp3",
        duration=get_audio_duration(GITHUB_WAV_URL),
    )

    # When
    vcon.add_dialog(text_dialog)
    vcon.add_dialog(audio_dialog)

    # Then
    found_text = vcon.find_dialog("type", "text")
    found_audio = vcon.find_dialog("type", "recording")

    assert found_text.to_dict() == text_dialog.to_dict()
    assert found_audio.to_dict() == audio_dialog.to_dict()
    assert len(vcon.dialog) == 2


def test_is_valid_with_valid_vcon():
    """Test that a valid vCon passes validation"""
    vcon = Vcon.build_from_json(test_vcon_string)
    print(vcon.to_json())
    is_valid, errors = vcon.is_valid()
    print(errors)
    assert is_valid
    assert len(errors) == 0


def test_is_valid_with_missing_required_fields():
    """Test validation fails with missing required fields"""
    vcon = Vcon()
    vcon.vcon_dict = {}  # Empty vCon
    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert len(errors) == 3  # uuid, vcon, created_at
    assert "Missing required field: uuid" in errors
    assert "Missing required field: vcon" in errors
    assert "Missing required field: created_at" in errors


def test_is_valid_with_invalid_created_at():
    """Test validation fails with invalid created_at format"""
    vcon = Vcon.build_new()
    vcon.vcon_dict["created_at"] = "invalid-date"
    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert "Invalid created_at format" in errors[0]


def test_is_valid_with_invalid_dialog_party_reference():
    """Test validation fails with invalid party reference in dialog"""
    vcon = Vcon.build_new()
    vcon.add_party(Party(name="Test Party"))  # Add one party (index 0)

    # Add dialog referencing non-existent party (index 1)
    dialog = Dialog(
        type="text",
        start="2023-06-01T10:00:00Z",
        parties=[0, 1],  # Party index 1 doesn't exist
        body="Test message",
    )
    vcon.add_dialog(dialog)

    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert any("invalid party index: 1" in error for error in errors)


def test_is_valid_with_invalid_analysis_dialog_reference():
    """Test validation fails with invalid dialog reference in analysis"""
    vcon = Vcon.build_new()

    # Add analysis referencing non-existent dialog
    vcon.add_analysis(
        type="test_type",
        dialog=0,  # Dialog index 0 doesn't exist
        vendor="test_vendor",
        body={"key": "value"},
    )

    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert any("invalid dialog index: 0" in error for error in errors)


def test_is_valid_with_invalid_mimetype():
    """Test validation fails with invalid mimetype in dialog"""
    vcon = Vcon.build_new()

    # Add dialog with invalid mimetype
    dialog = Dialog(
        type="text", start="2023-06-01T10:00:00Z", parties=[], mimetype="invalid/type"
    )
    vcon.add_dialog(dialog)

    is_valid, errors = vcon.is_valid()
    assert not is_valid
    assert any("invalid mimetype: invalid/type" in error for error in errors)


def test_validate_json_with_valid_vcon():
    """Test validation of valid vCon JSON string"""
    is_valid, errors = Vcon.validate_json(test_vcon_string)
    assert is_valid
    assert len(errors) == 0


def test_validate_json_with_invalid_json():
    """Test validation fails with invalid JSON"""
    is_valid, errors = Vcon.validate_json("invalid json")
    assert not is_valid
    assert len(errors) == 1
    assert "Invalid JSON format" in errors[0]


def test_validate_json_with_invalid_vcon():
    """Test validation fails with valid JSON but invalid vCon"""
    invalid_vcon = '{"some": "json"}'
    is_valid, errors = Vcon.validate_json(invalid_vcon)
    assert not is_valid
    assert len(errors) > 0
    assert "Missing required field" in errors[0]


def test_validate_file_with_valid_vcon(tmp_path):
    """Test validation of valid vCon file"""
    # Create a temporary file with valid vCon
    file_path = tmp_path / "valid_vcon.json"
    with open(file_path, "w") as f:
        f.write(test_vcon_string)

    is_valid, errors = Vcon.validate_file(str(file_path))
    assert is_valid
    assert len(errors) == 0


def test_validate_file_with_nonexistent_file():
    """Test validation fails with nonexistent file"""
    is_valid, errors = Vcon.validate_file("nonexistent.json")
    assert not is_valid
    assert len(errors) == 1
    assert "File not found" in errors[0]


def test_validate_file_with_invalid_json(tmp_path):
    """Test validation fails with invalid JSON file"""
    # Create a temporary file with invalid JSON
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w") as f:
        f.write("invalid json")

    is_valid, errors = Vcon.validate_file(str(file_path))
    assert not is_valid
    assert len(errors) == 1
    assert "Invalid JSON format" in errors[0]


def test_validate_file_with_invalid_vcon(tmp_path):
    """Test validation fails with valid JSON but invalid vCon"""
    # Create a temporary file with invalid vCon
    file_path = tmp_path / "invalid_vcon.json"
    with open(file_path, "w") as f:
        f.write('{"some": "json"}')

    is_valid, errors = Vcon.validate_file(str(file_path))
    assert not is_valid
    assert len(errors) > 0
    assert "Missing required field" in errors[0]
