# vCon Python Library

## IETF vCon Working Group

The vCon (Virtual Conversation) format is being developed as an open standard through the Internet Engineering Task Force (IETF). The vCon Working Group is focused on creating a standardized format for representing digital conversations across various platforms and use cases.

### Participating in the Working Group

1. **Join the Mailing List**: Subscribe to the vCon working group mailing list at [vcon@ietf.org](mailto:vcon@ietf.org)

2. **Review Documents**: 
   - Working group documents and drafts can be found at: https://datatracker.ietf.org/wg/vcon/documents/
   - The current Internet-Draft can be found at: https://datatracker.ietf.org/doc/draft-howe-vcon/

3. **Attend Meetings**:
   - The working group meets virtually during IETF meetings
   - Meeting schedules and connection details are announced on the mailing list
   - Past meeting materials and recordings are available on the IETF datatracker

4. **Contribute**:
   - Submit comments and suggestions on the mailing list
   - Propose changes through GitHub pull requests
   - Participate in working group discussions
   - Help with implementations and interoperability testing

For more information about the IETF standardization process and how to participate, visit: https://www.ietf.org/about/participate/

## About the Library

The vCon (Virtual Conversation) library is a powerful Python tool designed to capture, structure, and manage conversation data in a standardized format. It provides a robust set of features for creating, manipulating, and analyzing digital representations of conversations, making it particularly useful for applications in customer service, call centers, chat systems, and any scenario where structured conversation data is valuable.

At its core, the vCon library allows you to create vCon objects, which serve as containers for all elements of a conversation. These objects can include multiple parties (participants in the conversation), a series of dialogs (individual messages or utterances), metadata (such as tags for easy categorization), attachments (like transcripts or other related files), and even analysis data (such as sentiment analysis results).

Key capabilities of the vCon library include:

1. Creating and managing vCon objects with a flexible, extensible structure.
2. Adding and retrieving conversation participants (parties) with various attributes.
3. Recording and organizing dialog entries with timestamps, content, and sender information.
4. Attaching metadata and tags for easy categorization and searching.
5. Including file attachments related to the conversation.
6. Incorporating analysis data from various sources (e.g., sentiment analysis, topic classification).
7. Signing and verifying vCon objects for data integrity and authenticity.
8. Serializing vCon objects to and from JSON for easy storage and transmission.

The library is designed with extensibility in mind, allowing for easy integration with various analysis tools and systems. It also includes built-in support for handling different types of conversation data, including text, audio, and video.

By providing a standardized way to structure and manage conversation data, the vCon library enables powerful applications in areas such as conversation analytics, quality assurance, compliance monitoring, and machine learning model training for natural language processing tasks.

Whether you're building a customer service platform, a conversation analysis tool, or any application that deals with structured dialog data, the vCon library offers a comprehensive solution for capturing, storing, and working with conversation information in a consistent and powerful way.

## Features

- Create and manipulate vCon objects
- Add parties, dialogs, attachments, and analysis to vCons
- Sign and verify vCons using JWS (JSON Web Signature)
- Generate UUID8 identifiers
- Pack and unpack dialogs
- Add and retrieve tags


## Usage
# vCon API Tutorial

This tutorial will guide you through creating a vCon (Virtual Conversation) object using the vCon API. We'll cover creating a new vCon, adding parties and dialogs, attaching metadata and analysis, and finally signing and verifying the vCon.

## Prerequisites

Before you begin, make sure you have the vCon library installed in your Python environment.

```bash
pip install vcon  # Replace with the actual package name if different
```

## Step 1: Import Required Modules

First, let's import the necessary modules:

```python
import datetime
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from vcon.party import PartyHistory
```

## Step 2: Create a New vCon Object

To start, we'll create a new vCon object:

```python
vcon = Vcon.build_new()
```

## Step 3: Add Parties

Next, we'll add two parties to our vCon: a caller and an agent.

```python
caller = Party(tel="+1234567890", name="Alice", role="caller")
agent = Party(tel="+1987654321", name="Bob", role="agent")
vcon.add_party(caller)
vcon.add_party(agent)
```

## Step 4: Add Dialogs

Now, let's add some dialog to our vCon. 

```python
start_time = datetime.datetime.now(datetime.timezone.utc)
dialog = Dialog(
    type="text",
    start=start_time.isoformat(),
    parties=[0, 1],  # Indices of the parties in the vCon
    originator=0,  # The caller (Alice) is the originator
    mimetype="text/plain",
    body="Hello, I need help with my account."
)
vcon.add_dialog(dialog)
```

Note that we're using ISO format strings for the datetime values and including UTC timezone information.

## Step 5: Add Metadata

We can add metadata to our vCon using tags:

```python
vcon.add_tag("customer_id", "12345")
vcon.add_tag("interaction_id", "INT-001")
```

## Step 6: Add an Attachment

Let's add a transcript as an attachment:

```python
transcript = "Alice: Hello, I need help with my account.\nBob: Certainly! I'd be happy to help. Can you please provide your account number?"
vcon.add_attachment(body=transcript, type="transcript", encoding="none")
```

## Step 7: Add Analysis

We can also add analysis data to our vCon. Here's an example of adding sentiment analysis:

```python
sentiment_analysis = {
    "overall_sentiment": "positive",
    "customer_sentiment": "neutral",
    "agent_sentiment": "positive"
}
vcon.add_analysis(
    type="sentiment",
    dialog=[0, 1],  # Indices of the dialogs analyzed
    vendor="SentimentAnalyzer",
    body=sentiment_analysis,
    encoding="none"
)
```

## Step 8: Sign and Verify the vCon

Finally, let's generate a key pair, sign the vCon, and verify the signature:

```python
# Generate a key pair for signing
private_key, public_key = Vcon.generate_key_pair()

# Sign the vCon
vcon.sign(private_key)

# Verify the signature
is_valid = vcon.verify(public_key)
print(f"Signature is valid: {is_valid}")
```

## Step 9: Serialize to JSON

To see the final result, we can serialize our vCon to JSON:

```python
print(vcon.to_json())
```

## Complete Example

Here's the complete example putting all these steps together:

```python
import datetime
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from vcon.party import PartyHistory

def main():
    # Create a new vCon object
    vcon = Vcon.build_new()

    # Add parties
    caller = Party(tel="+1234567890", name="Alice", role="caller")
    agent = Party(tel="+1987654321", name="Bob", role="agent")
    vcon.add_party(caller)
    vcon.add_party(agent)

    # Add a dialog
    start_time = datetime.datetime.now(datetime.timezone.utc)
    dialog = Dialog(
        type="text",
        start=start_time.isoformat(),
        parties=[0, 1],  # Indices of the parties in the vCon
        originator=0,  # The caller (Alice) is the originator
        mimetype="text/plain",
        body="Hello, I need help with my account."
    )
    vcon.add_dialog(dialog)

    # Add a response from the agent
    response_time = start_time + datetime.timedelta(minutes=1)
    response = Dialog(
        type="text",
        start=response_time.isoformat(),
        parties=[0, 1],
        originator=1,  # The agent (Bob) is the originator
        mimetype="text/plain",
        body="Certainly! I'd be happy to help. Can you please provide your account number?"
    )
    vcon.add_dialog(response)

    # Add some metadata
    vcon.add_tag("customer_id", "12345")
    vcon.add_tag("interaction_id", "INT-001")

    # Add an attachment (e.g., a transcript)
    transcript = "Alice: Hello, I need help with my account.\nBob: Certainly! I'd be happy to help. Can you please provide your account number?"
    vcon.add_attachment(body=transcript, type="transcript", encoding="none")

    # Add some analysis (e.g., sentiment analysis)
    sentiment_analysis = {
        "overall_sentiment": "positive",
        "customer_sentiment": "neutral",
        "agent_sentiment": "positive"
    }
    vcon.add_analysis(
        type="sentiment",
        dialog=[0, 1],  # Indices of the dialogs analyzed
        vendor="SentimentAnalyzer",
        body=sentiment_analysis,
        encoding="none"
    )

    # Generate a key pair for signing
    private_key, public_key = Vcon.generate_key_pair()

    # Sign the vCon
    vcon.sign(private_key)

    # Verify the signature
    is_valid = vcon.verify(public_key)
    print(f"Signature is valid: {is_valid}")

    # Print the vCon as JSON
    print(vcon.to_json())

if __name__ == "__main__":
    main()
```

# vCon Python Library API Documentation

## Table of Contents

1. [Vcon Class](#vcon-class)
2. [Dialog Class](#dialog-class)
3. [Party Class](#party-class)
4. [PartyHistory Class](#partyhistory-class)
5. [Constants](#constants)

## Vcon Class

The `Vcon` class is the root class representing a vCon (Virtual Conversation) object.

### Constructor

```python
Vcon(vcon_dict: Optional[dict] = None)  # Optional: initialize from dictionary
```

Note: If no dictionary is provided, an empty vCon object will be created. Use `build_new()` for a properly initialized vCon object.

### Class Methods

- `build_from_json(json_string: str) -> Vcon`: Initialize a Vcon object from a JSON string.
- `build_new() -> Vcon`: Initialize a Vcon object with default values.
- `generate_key_pair() -> tuple`: Generate a new RSA key pair for signing vCons.

### Instance Methods

- `to_json() -> str`: Serialize the vCon to a JSON string.
- `to_dict() -> dict`: Serialize the vCon to a dictionary.
- `dumps() -> str`: Alias for `to_json()`.
- `get_tag(tag_name: str) -> Optional[str]`: Returns the value of a tag by name.
- `add_tag(tag_name: str, tag_value: str) -> None`: Adds a tag to the vCon.
- `find_attachment_by_type(type: str) -> Optional[dict]`: Finds an attachment by type.
- `add_attachment(body: Union[dict, list, str], type: str, encoding: str = "none") -> None`: Adds an attachment to the vCon.
- `find_analysis_by_type(type: str) -> Optional[dict]`: Finds an analysis by type.
- `add_analysis(type: str, dialog: Union[list, int], vendor: str, body: Union[dict, list, str], encoding: str = "none", extra: Optional[dict] = None) -> None`: Adds analysis data to the vCon.
- `add_party(party: Party) -> None`: Adds a party to the vCon.
- `find_party_index(by: str, val: str) -> Optional[int]`: Find the index of a party in the vCon given a key-value pair.
- `find_dialog(by: str, val: str) -> Optional[Dialog]`: Find a dialog in the vCon given a key-value pair.
- `add_dialog(dialog: Dialog) -> None`: Add a dialog to the vCon.
- `sign(private_key: Union[rsa.RSAPrivateKey, bytes]) -> None`: Sign the vCon using JWS.
- `verify(public_key: Union[rsa.RSAPublicKey, bytes]) -> bool`: Verify the JWS signature of the vCon.

### Properties

Note: Properties that are not set will not be present in the vCon object. Use `hasattr()` to check for their presence.

- `tags: Optional[dict]`: The tags attachment.
- `parties: list[Party]`: The list of parties.
- `dialog: list[Dialog]`: The list of dialogs.
- `attachments: list`: The list of attachments.
- `analysis: list`: The list of analyses.
- `uuid: str`: The UUID of the vCon.
- `vcon: str`: The vCon version.
- `subject: Optional[str]`: The subject of the vCon.
- `created_at: str`: The creation timestamp of the vCon.
- `updated_at: str`: The last update timestamp of the vCon.
- `redacted: Optional[dict]`: The redacted information of the vCon.
- `appended: Optional[dict]`: The appended information of the vCon.
- `group: Optional[dict]`: The group information of the vCon.
- `meta: Optional[dict]`: The metadata of the vCon.

### Example Usage

```python
# Create a new vCon
vcon = Vcon.build_new()

# Add a party
party = Party(tel="+1234567890", name="Alice", role="caller")
vcon.add_party(party)

# Add a dialog
dialog = Dialog(
    type="text",
    start=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    parties=[0],
    body="Hello, I need help."
)
vcon.add_dialog(dialog)

# Add metadata
vcon.add_tag("customer_id", "12345")

# Check for optional properties
if hasattr(vcon, "subject"):
    print(f"vCon subject: {vcon.subject}")

# Sign the vCon
private_key, public_key = Vcon.generate_key_pair()
vcon.sign(private_key)

# Serialize to JSON
json_str = vcon.to_json()
```

## Dialog Class

The `Dialog` class represents a dialog in the system.

### Constructor

```python
Dialog(type: str,            # Required: type of dialog (e.g., "text", "audio")
       start: datetime,      # Required: start time of the dialog
       parties: List[int],   # Required: list of party indices
       originator: Optional[int] = None,    # Optional: index of originating party
       mimetype: Optional[str] = None,      # Optional: MIME type of content
       filename: Optional[str] = None,      # Optional: name of associated file
       body: Optional[str] = None,          # Optional: content of the dialog
       encoding: Optional[str] = None,      # Optional: encoding of the content
       url: Optional[str] = None,           # Optional: URL to external content
       alg: Optional[str] = None,           # Optional: algorithm used for signatures
       signature: Optional[str] = None,      # Optional: signature for verification
       disposition: Optional[str] = None,    # Optional: handling instructions
       party_history: Optional[List[PartyHistory]] = None,  # Optional: party state changes
       transferee: Optional[int] = None,     # Optional: party being transferred
       transferor: Optional[int] = None,     # Optional: party initiating transfer
       transfer_target: Optional[int] = None, # Optional: transfer destination party
       original: Optional[int] = None,       # Optional: original dialog reference
       consultation: Optional[int] = None,    # Optional: consultation dialog reference
       target_dialog: Optional[int] = None,   # Optional: target dialog reference
       campaign: Optional[str] = None,       # Optional: campaign identifier
       interaction: Optional[str] = None,    # Optional: interaction identifier
       skill: Optional[str] = None,          # Optional: skill identifier
       duration: Optional[float] = None,     # Optional: duration in seconds
       meta: Optional[dict] = None)         # Optional: additional metadata
```

Note: Optional parameters that are set to None will not create attributes on the Dialog instance. Use `hasattr()` to check for the presence of optional attributes.

### Methods

- `to_dict()`: Returns a dictionary representation of the Dialog object.
- `add_external_data(url: str, filename: str, mimetype: str) -> None`: Adds external data to the dialog.
- `add_inline_data(body: str, filename: str, mimetype: str) -> None`: Adds inline data to the dialog.
- `is_external_data() -> bool`: Checks if the dialog is an external data dialog.
- `is_inline_data() -> bool`: Checks if the dialog is an inline data dialog.
- `is_text() -> bool`: Checks if the dialog is a text dialog.
- `is_audio() -> bool`: Checks if the dialog is an audio dialog.
- `is_video() -> bool`: Checks if the dialog is a video dialog.
- `is_email() -> bool`: Checks if the dialog is an email dialog.
- `is_external_data_changed() -> bool`: Checks if the external data dialog's contents have changed.
- `to_inline_data() -> None`: Converts the dialog from an external data dialog to an inline data dialog.

### Example Usage

```python
# Create a text dialog
dialog = Dialog(
    type="text",
    start=datetime.datetime.now(datetime.timezone.utc),
    parties=[0, 1],
    originator=0,
    mimetype="text/plain",
    body="Hello, I need help with my account."
)

# Check for optional attributes
if hasattr(dialog, "duration"):
    print(f"Dialog duration: {dialog.duration}")

# Create an audio dialog with external data
audio_dialog = Dialog(
    type="audio",
    start=datetime.datetime.now(datetime.timezone.utc),
    parties=[0, 1]
)
audio_dialog.add_external_data(
    url="https://example.com/audio.mp3",
    filename="conversation.mp3",
    mimetype="audio/mp3"
)
```

## Party Class

The `Party` class represents a participant in a conversation.

### Constructor

```python
Party(tel: Optional[str] = None,          # Optional: telephone number
      stir: Optional[str] = None,         # Optional: STIR/SHAKEN verification info
      mailto: Optional[str] = None,       # Optional: email address
      name: Optional[str] = None,         # Optional: display name
      validation: Optional[str] = None,    # Optional: validation status
      gmlpos: Optional[str] = None,       # Optional: geographic position
      civicaddress: Optional[CivicAddress] = None,  # Optional: structured address
      uuid: Optional[str] = None,         # Optional: unique identifier
      role: Optional[str] = None,         # Optional: party's role
      contact_list: Optional[str] = None,  # Optional: contact list reference
      meta: Optional[dict] = None)        # Optional: additional metadata
```

Note: Optional parameters that are set to None will not create attributes on the Party instance. Use `hasattr()` to check for the presence of optional attributes.

### Methods

- `to_dict() -> dict`: Returns a dictionary representation of the Party object.

### Example Usage

```python
# Create a party with basic information
party = Party(
    tel="+1234567890",
    name="Alice Smith",
    role="caller"
)

# Create a party with address information
address = CivicAddress(
    a1="US",
    a2="California",
    a3="San Francisco"
)
party_with_address = Party(
    tel="+1987654321",
    name="Bob Jones",
    role="agent",
    civicaddress=address
)

# Check for optional attributes
if hasattr(party, "mailto"):
    print(f"Party email: {party.mailto}")

# Add custom metadata
party = Party(
    tel="+1234567890",
    name="Charlie Brown",
    meta={
        "department": "Sales",
        "employee_id": "12345"
    }
)
```

## PartyHistory Class

The `PartyHistory` class represents a change in a party's state during a conversation.

### Constructor

```python
PartyHistory(party: int,           # Required: index of the party
            event: str,           # Required: type of event
            time: datetime)       # Required: time of the event
```

### Methods

- `to_dict() -> dict`: Returns a dictionary representation of the PartyHistory object.

### Example Usage

```python
# Create a party history entry
history = PartyHistory(
    party=0,
    event="connected",
    time=datetime.datetime.now(datetime.timezone.utc)
)

# Add to a dialog
dialog = Dialog(
    type="text",
    start=datetime.datetime.now(datetime.timezone.utc),
    parties=[0, 1],
    party_history=[history]
)
```

## Constants

- `MIME_TYPES`: A list of supported MIME types for dialogs.

```python
MIME_TYPES = [
    "text/plain",
    "audio/x-wav",
    "audio/x-mp3",
    "audio/x-mp4",
    "audio/ogg",
    "video/x-mp4",
    "video/ogg",
    "multipart/mixed",
    "message/external-body",
]
```

## Attachments and Analysis

### Attachments

Attachments in vCon objects are used to store additional data related to the conversation. Common use cases include transcripts, metadata, and supplementary files.

#### Adding Attachments

```python
vcon.add_attachment(
    body: Union[dict, list, str],  # Required: content of the attachment
    type: str,                     # Required: type identifier for the attachment
    encoding: str = "none"         # Optional: encoding of the content
)
```

Note: The `body` parameter can accept different types of data:
- Strings for text content
- Dictionaries for structured data
- Lists for collections of data

#### Example Usage

```python
# Add a transcript attachment
transcript = "Customer: Hello\nAgent: How can I help you today?"
vcon.add_attachment(
    body=transcript,
    type="transcript",
    encoding="none"
)

# Add structured metadata
metadata = {
    "queue_time": 45,
    "handling_time": 180,
    "satisfaction_score": 9
}
vcon.add_attachment(
    body=metadata,
    type="call_metrics",
    encoding="none"
)

# Find an attachment
transcript = vcon.find_attachment_by_type("transcript")
if transcript:
    print(transcript["body"])
```

### Analysis

Analysis objects store the results of various types of analysis performed on the conversation, such as sentiment analysis, topic classification, or compliance checking.

#### Adding Analysis

```python
vcon.add_analysis(
    type: str,                                # Required: type of analysis
    dialog: Union[list, int],                 # Required: dialog indices analyzed
    vendor: str,                              # Required: analysis provider
    body: Union[dict, list, str],             # Required: analysis results
    encoding: str = "none",                   # Optional: encoding of the content
    extra: Optional[dict] = None              # Optional: additional metadata
)
```

#### Example Usage

```python
# Add sentiment analysis
sentiment_results = {
    "overall_sentiment": "positive",
    "segments": [
        {
            "text": "Hello, I need help with my account",
            "sentiment": "neutral",
            "confidence": 0.85
        },
        {
            "text": "I'm happy to help you with that!",
            "sentiment": "positive",
            "confidence": 0.92
        }
    ]
}
vcon.add_analysis(
    type="sentiment",
    dialog=[0, 1],  # Analyzing first two dialogs
    vendor="SentimentAnalyzer",
    body=sentiment_results
)

# Add topic classification
topic_results = {
    "primary_topic": "account_access",
    "confidence": 0.88,
    "secondary_topics": ["authentication", "password_reset"]
}
vcon.add_analysis(
    type="topic_classification",
    dialog=[0],  # Analyzing first dialog only
    vendor="TopicClassifier",
    body=topic_results,
    extra={"model_version": "2.1.0"}
)

# Find analysis results
sentiment = vcon.find_analysis_by_type("sentiment")
if sentiment:
    print(f"Overall sentiment: {sentiment['body']['overall_sentiment']}")
```

### Common Use Cases

1. **Quality Monitoring**
```python
# Add QA scoring
qa_results = {
    "overall_score": 92,
    "categories": {
        "greeting": 100,
        "problem_solving": 85,
        "closing": 90
    },
    "notes": "Excellent customer service, could improve problem resolution time"
}
vcon.add_analysis(
    type="quality_score",
    dialog=list(range(len(vcon.dialog))),  # Analyze all dialogs
    vendor="QATeam",
    body=qa_results
)
```

2. **Compliance Checking**
```python
# Add compliance analysis
compliance_results = {
    "compliant": True,
    "checks": [
        {"type": "pci_detection", "passed": True},
        {"type": "pii_detection", "passed": True},
        {"type": "disclaimer_present", "passed": True}
    ]
}
vcon.add_analysis(
    type="compliance_check",
    dialog=list(range(len(vcon.dialog))),
    vendor="ComplianceChecker",
    body=compliance_results,
    extra={"regulation": "GDPR"}
)
```

3. **Conversation Analytics**
```python
# Add interaction metrics
metrics = {
    "talk_time_ratio": {
        "agent": 0.45,
        "customer": 0.55
    },
    "interruptions": 2,
    "silence_periods": [
        {"start": 45, "duration": 3.5},
        {"start": 120, "duration": 2.1}
    ]
}
vcon.add_analysis(
    type="conversation_metrics",
    dialog=list(range(len(vcon.dialog))),
    vendor="InteractionAnalyzer",
    body=metrics
)
```

## Contributing

Contributions to the vCon library are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the MIT License:

MIT License

Copyright (c) 2023 Thomas McCarthy-Howe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contact

For questions or support, please contact:

Thomas McCarthy-Howe
Email: ghostofbasho@gmail.com