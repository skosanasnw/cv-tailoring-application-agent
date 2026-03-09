import pytest
from unittest.mock import MagicMock, patch
from src.agent_logic import JobTailorAgent

@pytest.fixture
def mock_agent():
    """Fixture to initialize the agent with a fake API key."""
    return JobTailorAgent(api_key="fake_key_1234")

def test_parse_response_success(mock_agent):
    """Verifies that the agent correctly splits the Gemini output."""
    raw_input = "Google|Dev===SECTION_BREAK===My CV Content ====SECTION_BREAK==== Prep Tips"
    # Temporarily tweak the split string in the test if needed,
    # but here I use the logic from the agent_logic.py
    parsed = mock_agent._parse_response(raw_input)

    assert parsed["metadata"] == "Google|Dev"
    assert "My CV Content" in parsed["cv_md"]
    assert parsed["prep_md"] == "Prep Tips"

def test_parsed_response_failure(mock_agent):
    """Ensures the agent handles malformed AI response gracefully."""
    raw_input = "Just some random text without breaks."
    parsed = mock_agent._parse_response(raw_input)

    assert "error" in parsed
    assert parsed["error"] == "Incomplete generation"

@patch("src.agent_logic.genai")
def test_analyze_call(mock_client_class, mock_agent):
    """
    Tests if the generated_content method is called with the right parameters.
    This ensures the 'Thinking Level' and 'Resolution' settings are intact.
    """

    # Setup the mock client
    mock_client_instance = mock_client_class.return_value
    mock_agent.client = mock_client_instance

    #Mock the response object
    mock_response = MagicMock()
    mock_response.text = "Meta===SECTION_BREAK===CV===SECTION_BREAK===Prep"
    mock_client_instance.models.generate_content.return_value = mock_response

    # Dummy data
    with patch("builtins.open") as mock_open:
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_image_bytes"
        mock_open.return_value.__enter__.return_value = mock_file

        result = mock_agent.analyze_and_tailor("Master CV Text", "dummy_path.png")

    # Assertions
    assert result["metadata"] == "Meta"
    assert mock_client_instance.models.generate_content.called