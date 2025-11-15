# AI Feature Validation Tests

This directory contains tests specifically for validating the AI-powered features in the Campus Resource Hub, particularly the **AI Concierge** assistant.

## Purpose

These tests fulfill the optional AI validation requirement from the **AiDD 2025 Capstone Project Brief, Appendix C**:

> "Projects that include AI features should provide at least one automated or manual test verifying that AI-generated outputs behave predictably and align with factual project data."

## Test Objectives

The AI validation tests ensure:

1. **Factual Grounding**: AI responses reference actual resources in the database, not hallucinated data
2. **Graceful Degradation**: System functions correctly when OpenAI API is unavailable
3. **No Hallucinations**: AI does not fabricate resources or information that doesn't exist
4. **Appropriate Responses**: AI outputs are helpful, non-biased, and appropriate
5. **Context Awareness**: AI leverages project context from `/docs/context/` materials
6. **Safety**: AI responses are properly formatted and protected against injection attacks

## Test Coverage

### `test_ai_concierge.py` (6 tests)

- **`test_ai_concierge_grounds_in_actual_data`**: Verifies AI references real resources
- **`test_ai_concierge_graceful_degradation`**: Tests fallback when API fails
- **`test_ai_concierge_no_hallucinations`**: Ensures no fabricated data in responses
- **`test_ai_concierge_appropriate_responses`**: Validates helpful, ethical outputs
- **`test_ai_concierge_context_awareness`**: Checks AI uses project context
- **`test_ai_response_format_and_safety`**: Prevents XSS and injection attacks

## Running the Tests

### Run all AI validation tests:
```bash
# Windows PowerShell
$env:PYTHONPATH="C:\Users\Dewang Sethi\Downloads\FinalProject-main\FinalProject-main"
pytest tests/ai_eval/ -v

# Linux/Mac
export PYTHONPATH=/path/to/FinalProject-main
pytest tests/ai_eval/ -v
```

### Run specific test:
```bash
pytest tests/ai_eval/test_ai_concierge.py::test_ai_concierge_grounds_in_actual_data -v
```

### Run with coverage:
```bash
pytest tests/ai_eval/ --cov=src.services.ai_concierge --cov=src.services.ai_client
```

## Ethical Considerations

These tests reflect the ethical responsibilities outlined in the project brief:

- **Transparency**: All AI usage is documented and tested
- **Verification**: AI outputs are validated against actual data
- **Safety**: Responses are checked for bias and inappropriate content
- **Reliability**: System degrades gracefully when AI is unavailable

## Integration with Main Test Suite

These AI validation tests complement the main test suite (`tests/unit/` and `tests/integration/`) and can be run together:

```bash
pytest tests/ -v  # Runs all 37 tests (31 core + 6 AI validation)
```

## Notes

- **OpenAI API Key**: Some tests may require a valid API key in `.env` for full validation
- **Mock Responses**: Tests use mocking to simulate API failures and validate fallback behavior
- **Test Isolation**: Each test creates its own test database with known resources

## References

- **Project Brief**: AiDD 2025 Capstone - Appendix C (AI-First Development)
- **AI Concierge Implementation**: `src/services/ai_concierge.py`
- **AI Client Wrapper**: `src/services/ai_client.py`
