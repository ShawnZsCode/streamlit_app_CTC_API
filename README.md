# Revit Project Assistant

A modern, AI-powered chat interface for interacting with Revit projects. This application uses OpenAI's GPT models to understand user queries and execute Revit API commands through CTC's API endpoints.

## Features

- 🤖 AI-powered chat interface for natural language interaction
- 📊 Real-time project context visualization
- 🏗️ Dynamic view creation and management
- 💾 Session-based memory for contextual awareness
- 🔄 Automatic action suggestions based on conversation
- 📋 Interactive forms for bulk operations

## Quick Start

### Prerequisites

- Python 3.8+
- Revit with CTC API enabled
- OpenAI API key
- CTC API key

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key
CTC_API_KEY=your_ctc_api_key
```

### Running the App

1. Ensure Revit is running with the CTC API enabled
2. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```
3. Open your browser at `http://localhost:8501`

## Project Structure

- `streamlit_app.py`: Main UI application
- `ctc_chat_functions.py`: Business logic and API interactions
- `.env`: Environment variables

## Usage

1. Start a conversation by typing in the chat input
2. View project context in the sidebar
3. Use suggested actions when they appear
4. Execute bulk operations through dynamic forms

## Contributing

[Add contribution guidelines if applicable]

## License

[Add license information]