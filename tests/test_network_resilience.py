"""
Tests for Network Resilience, State Checkpoint, and Auto-Resumption.
"""

import pytest
import socket
from core.network_resilience import (
    check_internet_connection,
    is_network_error,
    execute_with_network_resume,
)


def test_check_internet_connection():
    # Verify connectivity probe executes without crashing
    online = check_internet_connection(timeout=2.0)
    assert isinstance(online, bool)


def test_is_network_error_detection():
    # True positives
    assert is_network_error(socket.gaierror(11001, "getaddrinfo failed"))
    assert is_network_error(ConnectionResetError("Connection reset by peer"))
    assert is_network_error(TimeoutError("Operation timed out"))
    assert is_network_error(Exception("503 Service Unavailable: High Demand"))
    assert is_network_error(Exception("Failed to establish a new connection: [Errno 111] Connection refused"))

    # False positives (regular application exceptions)
    assert not is_network_error(ValueError("Invalid argument format"))
    assert not is_network_error(KeyError("missing_key"))
    assert not is_network_error(SyntaxError("invalid syntax"))


def test_execute_with_network_resume_success():
    call_count = 0

    def mock_successful_api():
        nonlocal call_count
        call_count += 1
        return "Success telemetry data"

    result = execute_with_network_resume(mock_successful_api)
    assert result == "Success telemetry data"
    assert call_count == 1


def test_execute_with_network_resume_transient_retry():
    call_count = 0

    def mock_transient_network_failure():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionResetError("Connection reset by peer - transient network drop")
        return "Recovered response after connection restoration"

    result = execute_with_network_resume(mock_transient_network_failure, max_network_retries=5)
    assert result == "Recovered response after connection restoration"
    assert call_count == 3
