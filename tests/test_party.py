import pytest
from datetime import datetime
from vcon.party import Party, PartyHistory
from vcon.civic_address import CivicAddress


def test_party_named_parameters():
    party = Party(tel="123-456-7890", name="Test User", mailto="test@example.com")

    assert party.tel == "123-456-7890"
    assert party.name == "Test User"
    assert party.mailto == "test@example.com"


def test_party_none_parameters_not_set():
    party = Party(tel="123-456-7890", name=None)

    assert party.tel == "123-456-7890"
    assert not hasattr(party, "name")


def test_party_additional_parameters():
    party = Party(
        tel="123-456-7890",
        custom_field="value",
        another_field=42,
        nested_dict={"key": "value"},
    )

    assert party.tel == "123-456-7890"
    assert party.custom_field == "value"
    assert party.another_field == 42
    assert party.nested_dict == {"key": "value"}


def test_party_to_dict():
    party = Party(tel="123-456-7890", name="Test User", custom_field="value")

    expected_dict = {
        "tel": "123-456-7890",
        "name": "Test User",
        "custom_field": "value",
    }

    assert party.to_dict() == expected_dict


def test_party_with_civic_address():
    address = CivicAddress(a1="US", a2="RI", a3="Newport")

    party = Party(tel="401-456-7890", civicaddress=address)

    assert party.tel == "401-456-7890"
    assert party.civicaddress == address


def test_party_history():
    now = datetime.now()
    history = PartyHistory(party=1, event="join", time=now)

    assert history.party == 1
    assert history.event == "join"
    assert history.time == now

    expected_dict = {"party": 1, "event": "join", "time": now}
    assert history.to_dict() == expected_dict
