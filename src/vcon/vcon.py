from __future__ import annotations

import copy
from dateutil import parser
import json
from typing import Optional, Union, Any
import hashlib
import time
import uuid6
from datetime import datetime
from datetime import timezone
from pydash import get as _get
import base64
from authlib.jose import JsonWebSignature
from authlib.jose.errors import BadSignatureError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from .party import Party
from .dialog import Dialog

_LAST_V8_TIMESTAMP = None


class Attachment:
    VALID_ENCODINGS = ["base64", "base64url", "none"]

    def __init__(self, type, body, encoding="none"):
        if encoding not in self.VALID_ENCODINGS:
            raise ValueError(f"Invalid encoding: {encoding}")
        self.type = type
        self.body = body
        self.encoding = encoding

    def to_dict(self):
        return {"type": self.type, "body": self.body, "encoding": self.encoding}


class Vcon:
    def __init__(self, vcon_dict={}) -> None:
        # deep copy
        """
        Initialize a Vcon object from a dictionary.

        :param vcon_dict: a dictionary representing a vCon
        :type vcon_dict: dict
        """
        # If the vcon_dict contains a created_at in datetime or in string, format it like a ISO 8601
        if vcon_dict.get("created_at"):
            if isinstance(vcon_dict["created_at"], datetime):
                vcon_dict["created_at"] = vcon_dict["created_at"].isoformat()
            elif isinstance(vcon_dict["created_at"], str):
                vcon_dict["created_at"] = parser.parse(
                    vcon_dict["created_at"]
                ).isoformat()
        else:
            vcon_dict["created_at"] = datetime.now(timezone.utc).isoformat()

        # Ensure attachments array exists
        if "attachments" not in vcon_dict:
            vcon_dict["attachments"] = []

        self.vcon_dict = json.loads(json.dumps(vcon_dict))

    @classmethod
    def build_from_json(cls, json_string: str) -> Vcon:
        """
        Initialize a Vcon object from a JSON string.

        :param json_string: a JSON string representing a vCon
        :type json_string: str
        :return: a Vcon object
        :rtype: Vcon
        """
        return cls(json.loads(json_string))

    @classmethod
    def build_new(cls) -> Vcon:
        """
        Initialize a Vcon object with default values.

        :return: a Vcon object
        :rtype: Vcon
        """
        vcon_dict = {
            "uuid": cls.uuid8_domain_name("strolid.com"),
            "vcon": "0.0.1",
            # the created_at timestamp is set to the current time in ISO 8601
            # format with the timezone set to UTC. The last three characters
            # of the ISO 8601 format string are the millisecond part of the
            # timestamp, which is not used in vCon.
            "created_at": datetime.now(timezone.utc).isoformat(),
            "redacted": {},
            "group": [],
            "parties": [],
            "dialog": [],
            "attachments": [],
            "analysis": [],
        }
        return cls(vcon_dict)

    @property
    def tags(self) -> Optional[dict]:
        """
        Returns the tags attachment.

        :return: the tags attachment
        :rtype: dict or None
        """
        return self.find_attachment_by_type("tags")

    def get_tag(self, tag_name) -> Optional[dict]:
        """
        Returns the value of a tag by name.

        :param tag_name: the name of the tag
        :type tag_name: str
        :return: the value of the tag or None if not found
        :rtype: str or None
        """
        tags_attachment = self.find_attachment_by_type("tags")
        if not tags_attachment:
            return None
        tag = next(
            (t for t in tags_attachment["body"] if t.startswith(f"{tag_name}:")), None
        )
        if not tag:
            return None
        tag_value = tag.split(":")[1]
        return tag_value

    def add_tag(self, tag_name, tag_value) -> None:
        """
        Adds a tag to the vCon.

        :param tag_name: the name of the tag
        :type tag_name: str
        :param tag_value: the value of the tag
        :type tag_value: str
        :return: None
        :rtype: None
        """
        tags_attachment = self.find_attachment_by_type("tags")
        if not tags_attachment:
            tags_attachment = {
                "type": "tags",
                "body": [],
                "encoding": "json",
            }
            self.vcon_dict["attachments"].append(tags_attachment)
        tags_attachment["body"].append(f"{tag_name}:{tag_value}")

    def find_attachment_by_type(self, type: str) -> Optional[dict]:
        """
        Finds an attachment by type.

        :param type: the type of the attachment
        :type type: str
        :return: the attachment or None if not found
        :rtype: dict or None
        """
        return next(
            (a for a in self.vcon_dict["attachments"] if a["type"] == type), None
        )

    def add_attachment(self, type, body, encoding="none"):
        VALID_ENCODINGS = ["base64", "base64url", "none"]

        if encoding not in VALID_ENCODINGS:
            raise ValueError(f"Invalid encoding: {encoding}")

        attachment = Attachment(type, body, encoding)

        self.vcon_dict["attachments"].append(attachment.to_dict())
        return attachment

    def find_analysis_by_type(self, type) -> Any | None:
        """
        Finds an analysis by type.

        :param type: the type of the analysis
        :type type: str
        :return: the analysis or None if not found
        :rtype: dict or None
        """
        return next((a for a in self.vcon_dict["analysis"] if a["type"] == type), None)

    def add_analysis(
        self,
        *,
        type: str,
        dialog: Union[list, int],
        vendor: str,
        body: Union[dict, list, str],
        encoding="none",
        extra={},
    ) -> None:
        """
        Adds analysis data to the vCon.

        :param type: the type of the analysis
        :type type: str
        :param dialog: the dialog(s) associated with the analysis
        :type dialog: Union[list, int]
        :param vendor: the vendor of the analysis
        :type vendor: str
        :param body: the body of the analysis
        :type body: Union[dict, list, str]
        :param encoding: the encoding of the body
        :type encoding: str
        :param extra: extra key-value pairs to include in the analysis
        :type extra: dict
        :return: None
        :rtype: None
        """
        if encoding not in ["json", "none", "base64url"]:
            raise Exception("Invalid encoding")

        if encoding == "json":
            try:
                json.loads(body)
            except Exception as e:
                raise Exception("Invalid JSON body: ", e)

        if encoding == "base64url":
            try:
                base64.urlsafe_b64decode(body)
            except Exception as e:
                raise Exception("Invalid base64url body: ", e)

        analysis = {
            "type": type,
            "dialog": dialog,
            "vendor": vendor,
            "body": body,
            "encoding": encoding,
            **extra,
        }
        self.vcon_dict["analysis"].append(analysis)

    def add_party(self, party: Party) -> None:
        """
        Adds a party to the vCon.

        :param party: the party to add
        :type party: Party
        :return: None
        :rtype: None
        """
        self.vcon_dict["parties"].append(party.to_dict())

    def find_party_index(self, by: str, val: str) -> Optional[int]:
        """
        Find the index of a party in the vCon given a key-value pair.

        :param by: the key to look for
        :type by: str
        :param val: the value to look for
        :type val: str
        :return: The index of the party if found, None otherwise
        :rtype: Optional[int]
        """
        return next(
            (
                ind
                for ind, party in enumerate(self.vcon_dict["parties"])
                if _get(party, by) == val
            ),
            None,
        )

    def find_dialog(self, by: str, val: str) -> Optional[Dialog]:
        """
        Find a dialog in the vCon given a key-value pair. Convert the dialog to a Dialog object.

        :param by: the key to look for
        :type by: str
        :param val: the value to look for
        :type val: str
        :return: The dialog if found, None otherwise
        :rtype: Optional[dict]
        """
        dialog = next(
            (dialog for dialog in self.vcon_dict["dialog"] if _get(dialog, by) == val),
            None,
        )
        if dialog:
            return Dialog(**dialog)
        return None

    def add_dialog(self, dialog: Dialog) -> None:
        """
        Add a dialog to the vCon.

        :param dialog: the dialog to add
        :type dialog: dict
        :return: None
        :rtype: None
        """
        self.vcon_dict["dialog"].append(dialog.to_dict())

    def to_json(self) -> str:
        """
        Serialize the vCon to a JSON string.

        :return: a JSON string representation of the vCon
        :rtype: str
        """
        tmp_vcon_dict = copy.copy(self.vcon_dict)
        return json.dumps(tmp_vcon_dict)

    def to_dict(self) -> dict:
        """
        Serialize the vCon to a dictionary.

        :return: a dictionary representation of the vCon
        :rtype: dict
        """
        return json.loads(self.to_json())

    def dumps(self) -> str:
        """
        Alias for `to_json()`.

        :return: a JSON string representation of the vCon
        :rtype: str
        """
        return self.to_json()

    @property
    def parties(self) -> list[Party]:
        """
        Returns the list of parties.

        :return: a list of parties
        :rtype: list[Party]
        """
        return [Party(**party) for party in self.vcon_dict.get("parties", [])]

    @property
    def dialog(self) -> list:
        return self.vcon_dict.get("dialog", [])

    @property
    def attachments(self) -> list:
        return self.vcon_dict.get("attachments", [])

    @property
    def analysis(self):
        return self.vcon_dict.get("analysis", [])

    @property
    def uuid(self) -> str:
        return self.vcon_dict["uuid"]

    @property
    def vcon(self) -> str:
        return self.vcon_dict["vcon"]

    @property
    def subject(self) -> Optional[str]:
        return self.vcon_dict.get("subject")

    @property
    def created_at(self):
        return self.vcon_dict.get("created_at")

    @property
    def updated_at(self):
        return self.vcon_dict.get("updated_at")

    @property
    def redacted(self):
        return self.vcon_dict.get("redacted")

    @property
    def appended(self):
        return self.vcon_dict.get("appended")

    @property
    def group(self):
        return self.vcon_dict.get("group", [])

    @property
    def meta(self):
        return self.vcon_dict.get("meta", {})

    @staticmethod
    def uuid8_domain_name(domain_name: str) -> str:
        sha1_hasher = hashlib.sha1()
        sha1_hasher.update(bytes(domain_name, "utf-8"))
        dn_sha1 = sha1_hasher.digest()

        hash_upper_64 = dn_sha1[0:8]
        int64 = int.from_bytes(hash_upper_64, byteorder="big")

        uuid8_domain = Vcon.uuid8_time(int64)

        return uuid8_domain

    @staticmethod
    def uuid8_time(custom_c_62_bits: int) -> str:
        global _LAST_V8_TIMESTAMP

        ns = time.time_ns()
        if _LAST_V8_TIMESTAMP is not None and ns <= _LAST_V8_TIMESTAMP:
            ns = _LAST_V8_TIMESTAMP + 1
        timestamp_ms, timestamp_ns = divmod(ns, 10**6)
        subsec = uuid6._subsec_encode(timestamp_ns)

        subsec_a = subsec >> 8
        uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
        uuid_int |= subsec_a << 64
        uuid_int |= custom_c_62_bits

        uuid_str = str(uuid6.UUID(int=uuid_int, version=7))
        assert uuid_str[14] == "7"
        uuid_str = uuid_str[:14] + "8" + uuid_str[15:]

        return uuid_str

    def sign(self, private_key) -> None:
        """
        Sign the vCon using JWS.

        :param private_key: the private key used for signing
        :type private_key: Union[rsa.RSAPrivateKey, bytes]
        :return: None
        :rtype: None
        """
        """Sign the vCon using JWS."""
        payload = self.to_json()
        jws = JsonWebSignature()
        protected = {"alg": "RS256", "typ": "JWS"}

        # Convert private key to PEM format if it's not already
        if isinstance(private_key, rsa.RSAPrivateKey):
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        else:
            pem = private_key

        signed = jws.serialize_compact(protected, payload, pem)
        signed_str = signed.decode("utf-8")
        header, payload, signature = signed_str.split(".")

        self.vcon_dict["signatures"] = [{"protected": header, "signature": signature}]
        self.vcon_dict["payload"] = payload

    def verify(self, public_key) -> bool:
        """Verify the JWS signature of the vCon.

        :param public_key: the public key used for verification
        :type public_key: Union[rsa.RSAPublicKey, bytes]
        :return: True if the signature is valid, False otherwise
        :rtype: bool
        """
        """Verify the JWS signature of the vCon."""
        if "signatures" not in self.vcon_dict or "payload" not in self.vcon_dict:
            raise ValueError("vCon is not signed")

        jws = JsonWebSignature()
        signed_data = f"{self.vcon_dict['signatures'][0]['protected']}.{self.vcon_dict['payload']}.{self.vcon_dict['signatures'][0]['signature']}"

        # Convert public key to PEM format if it's not already
        if isinstance(public_key, rsa.RSAPublicKey):
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        else:
            pem = public_key

        try:
            jws.deserialize_compact(signed_data, pem)
            return True
        except BadSignatureError:
            return False

    @classmethod
    def generate_key_pair(cls) -> tuple:
        """
        Generate a new RSA key pair for signing vCons.

        :return: a tuple containing the private key and public key
        :rtype: tuple[rSA.RSAPrivateKey, rsa.RSAPublicKey]
        """
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        return private_key, public_key

    def is_valid(self) -> tuple[bool, list[str]]:
        """
        Validate the vCon syntax according to the standard.

        :return: A tuple containing (is_valid, list_of_errors)
        :rtype: tuple[bool, list[str]]
        """
        errors = []

        # Required fields
        required_fields = ["uuid", "vcon", "created_at"]
        for field in required_fields:
            if field not in self.vcon_dict:
                errors.append(f"Missing required field: {field}")

        # Validate created_at format
        if "created_at" in self.vcon_dict:
            try:
                parser.parse(self.vcon_dict["created_at"])
            except Exception:
                errors.append(
                    "Invalid created_at format. Must be ISO 8601 datetime string"
                )

        # Validate parties
        if "parties" in self.vcon_dict:
            if not isinstance(self.vcon_dict["parties"], list):
                errors.append("parties must be a list")
            else:
                for i, party in enumerate(self.vcon_dict["parties"]):
                    if not isinstance(party, dict):
                        errors.append(f"Party at index {i} must be a dictionary")

        # Validate dialogs
        if "dialog" in self.vcon_dict:
            if not isinstance(self.vcon_dict["dialog"], list):
                errors.append("dialog must be a list")
            else:
                for i, dialog in enumerate(self.vcon_dict["dialog"]):
                    if not isinstance(dialog, dict):
                        errors.append(f"Dialog at index {i} must be a dictionary")
                    else:
                        # Required dialog fields
                        dialog_required = ["type", "start", "parties"]
                        for field in dialog_required:
                            if field not in dialog:
                                errors.append(
                                    f"Dialog at index {i} missing required field: {field}"
                                )

                        # Validate dialog parties reference valid party indices
                        if "parties" in dialog and isinstance(dialog["parties"], list):
                            party_count = len(self.vcon_dict.get("parties", []))
                            for party_idx in dialog["parties"]:
                                if (
                                    not isinstance(party_idx, int)
                                    or party_idx < 0
                                    or party_idx >= party_count
                                ):
                                    errors.append(
                                        f"Dialog at index {i} references invalid party index: {party_idx}"
                                    )

                        # Validate start time format
                        if "start" in dialog:
                            try:
                                parser.parse(dialog["start"])
                            except Exception:
                                errors.append(
                                    f"Dialog at index {i} has invalid start format. Must be ISO 8601 datetime string"
                                )

                        # Validate mimetype if present
                        if (
                            "mimetype" not in dialog
                            or not isinstance(dialog["mimetype"], str)
                            or dialog["mimetype"] not in Dialog.MIME_TYPES
                        ):
                            errors.append(
                                f"Dialog {i} has invalid mimetype: {dialog.get('mimetype', 'missing')}"
                            )
                            valid = False

        # Validate attachments
        if "attachments" in self.vcon_dict:
            if not isinstance(self.vcon_dict["attachments"], list):
                errors.append("attachments must be a list")
            else:
                for i, attachment in enumerate(self.vcon_dict["attachments"]):
                    if not isinstance(attachment, dict):
                        errors.append(f"Attachment at index {i} must be a dictionary")
                    else:
                        # Required attachment fields
                        attachment_required = ["type", "body", "encoding"]
                        for field in attachment_required:
                            if field not in attachment:
                                errors.append(
                                    f"Attachment at index {i} missing required field: {field}"
                                )

                        # Validate encoding
                        if "encoding" in attachment and attachment["encoding"] not in [
                            "json",
                            "none",
                            "base64url",
                        ]:
                            errors.append(
                                f"Attachment at index {i} has invalid encoding: {attachment['encoding']}"
                            )

        # Validate analysis
        if "analysis" in self.vcon_dict:
            if not isinstance(self.vcon_dict["analysis"], list):
                errors.append("analysis must be a list")
            else:
                for i, analysis in enumerate(self.vcon_dict["analysis"]):
                    if not isinstance(analysis, dict):
                        errors.append(f"Analysis at index {i} must be a dictionary")
                    else:
                        # Required analysis fields
                        analysis_required = [
                            "type",
                            "dialog",
                            "vendor",
                            "body",
                            "encoding",
                        ]
                        for field in analysis_required:
                            if field not in analysis:
                                errors.append(
                                    f"Analysis at index {i} missing required field: {field}"
                                )

                        # Validate encoding
                        if "encoding" in analysis and analysis["encoding"] not in [
                            "json",
                            "none",
                            "base64url",
                        ]:
                            errors.append(
                                f"Analysis at index {i} has invalid encoding: {analysis['encoding']}"
                            )

                        # Validate dialog references
                        if "dialog" in analysis:
                            dialog_count = len(self.vcon_dict.get("dialog", []))
                            if isinstance(analysis["dialog"], list):
                                for dialog_idx in analysis["dialog"]:
                                    if (
                                        not isinstance(dialog_idx, int)
                                        or dialog_idx < 0
                                        or dialog_idx >= dialog_count
                                    ):
                                        errors.append(
                                            f"Analysis at index {i} references invalid dialog index: {dialog_idx}"
                                        )
                            elif isinstance(analysis["dialog"], int):
                                if (
                                    analysis["dialog"] < 0
                                    or analysis["dialog"] >= dialog_count
                                ):
                                    errors.append(
                                        f"Analysis at index {i} references invalid dialog index: {analysis['dialog']}"
                                    )
                            else:
                                errors.append(
                                    f"Analysis at index {i} has invalid dialog reference type"
                                )

        return len(errors) == 0, errors

    @staticmethod
    def validate_file(file_path: str) -> tuple[bool, list[str]]:
        """
        Validate a vCon file at the given path.

        :param file_path: Path to the vCon JSON file
        :type file_path: str
        :return: A tuple containing (is_valid, list_of_errors)
        :rtype: tuple[bool, list[str]]
        """
        try:
            with open(file_path, "r") as f:
                json_str = f.read()
            return Vcon.validate_json(json_str)
        except FileNotFoundError:
            return False, ["File not found"]
        except json.JSONDecodeError:
            return False, ["Invalid JSON format"]
        except Exception as e:
            return False, [f"Error reading file: {str(e)}"]

    @staticmethod
    def validate_json(json_str: str) -> tuple[bool, list[str]]:
        """
        Validate a vCon from a JSON string.

        :param json_str: JSON string representing a vCon
        :type json_str: str
        :return: A tuple containing (is_valid, list_of_errors)
        :rtype: tuple[bool, list[str]]
        """
        try:
            vcon = Vcon.build_from_json(json_str)
            return vcon.is_valid()
        except json.JSONDecodeError:
            return False, ["Invalid JSON format"]
        except Exception as e:
            return False, [f"Error parsing vCon: {str(e)}"]
