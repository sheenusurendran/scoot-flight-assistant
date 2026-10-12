# Scoot Flight Assistant

An AI-assisted flight-search chatbot built as a learning and QA portfolio project. The application collects a user's trip details, confirms the search request, and then retrieves flight-search information through a configured search provider.

> **Project note:** This is an independent learning project and is not affiliated with any real or endorsed by Scoot. It is a flight-search assistant, not an airline booking or ticketing system. Search results depend on the configured third-party provider and may be incomplete or change.

## Features

- Conversational collection of travel details, including origin, destination, travel date, and passenger counts.
- A confirmation step before submitting a flight search.
- Gemini-powered language understanding and response generation.
- Flight-search integration through SerpApi.
- Structured data models for handling trip details.
- Automated journey tests and evaluation assets.
- HTML evaluation report generation.

## Technology stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- SerpApi
- Pytest
- DeepEval (for LLM/agent evaluation)

## Project structure

```text
scoot-flight-assistant/
├── flight_agent.py                 # Assistant logic
├── flight_api.py                   # Flight-search API integration
├── flight_chatbot_ui.py            # Streamlit user interface
├── flight_models.py                # Structured data models
├── pytest.ini                      # Pytest configuration
├── tests/
│   └── test_flight_journey_deepeval.py
└── evaluation/
    ├── evaluation_results.json     # Saved evaluation results
    ├── flight_test_cases.json      # Evaluation/test cases
    ├── generate_flight_report.py   # HTML report generator
    └── report/
        └── flight_test_report.html # Generated HTML report
```

## Prerequisites

- Python 3 installed on your Mac or computer.
- A Google Gemini API key.
- A SerpApi API key.

## Setup

1. Clone the repository and enter the project folder:

   ```bash
   git clone https://github.com/sheenusurendran/scoot-flight-assistant.git
   cd scoot-flight-assistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the Python packages used by the project. For the current stack, the likely packages are:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install streamlit google-genai google-search-results python-dotenv pydantic pytest deepeval
   ```

   If your source code imports any additional packages, install them too. For repeatable setup, maintain a `requirements.txt` file with the project's verified dependencies and versions.

4. Create a local `.env` file in the project root and add your API keys. For example:

   ```dotenv
   GEMINI_API_KEY=your_gemini_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   ```

   **Important:** The variable names must match the names read by `flight_agent.py` and `flight_api.py`. Adjust the examples if your code uses different names. Never commit `.env`, `.env.local`, API keys, or other credentials to GitHub.

## Run the application

Activate the virtual environment, then launch the Streamlit interface:

```bash
streamlit run flight_chatbot_ui.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

## Run tests and generate the report

Run the automated tests:

```bash
pytest -q
```

Test execution may require configured API keys and access to the external services used by the tests. Review the test file before running any tests that make external requests or incur API usage.

Generate the HTML evaluation report from the saved evaluation results:

```bash
python evaluation/generate_flight_report.py
```

The report generator is configured to write the report under `evaluation/report/flight_test_report.html`.

## Security notes

- Keep API keys in local environment files or a secrets manager.
- `.env` and `.env.local` should be excluded by `.gitignore`.
- Do not paste API keys into source code, README files, screenshots, logs, or public issues.
- Before publishing, review evaluation outputs and HTML reports to ensure they do not contain credentials or private data.

## Current limitations

- Results rely on the configured third-party flight-search provider and its returned data.
- The project does not itself guarantee fare availability, final prices, or successful ticket booking.
- This README's example environment variable names and dependency list should be checked against the actual imports and configuration in the source code before using the setup instructions on a fresh machine.

## License

No license has been specified yet. Unless a license is added, others should not assume they have permission to reuse, modify, or redistribute this code.
