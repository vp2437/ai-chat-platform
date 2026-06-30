# AI Chat Platform

A custom chat interface powered by the Gemini API, with tool-use capabilities provided by local MCP (Model Context Protocol) servers for Excel, PDF, SQL, and DXF file operations.

## Prerequisites

- Python 3.10+
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/))
- A local clone of the [mcp-prototypes](https://github.com/<your-username>/mcp-prototypes) repo — this project does not bundle the MCP servers, it connects to them as external subprocesses

## Setup

### 1. Clone both repos

```bash
git clone https://github.com/<your-username>/ai-chat-platform.git
git clone https://github.com/<your-username>/mcp-prototypes.git
```

They don't need to be in the same parent folder, but it's simplest if they are.

### 2. Set up the mcp-prototypes servers

Follow the setup instructions in the `mcp-prototypes` README to create its virtual environment and install its dependencies (openpyxl, pdfplumber, ezdxf, etc.).

### 3. Set up the backend

**macOS / Linux:**

```bash
cd ai-chat-platform/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
cd ai-chat-platform\backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows
```

Edit `.env`:
GEMINI_API_KEY=your_gemini_api_key_here
MCP_PROTOTYPES_DIR=/absolute/path/to/your/local/mcp-prototypes

`MCP_PROTOTYPES_DIR` must be an absolute path to wherever you cloned `mcp-prototypes` in step 1. On Windows, use either forward slashes or escaped backslashes, e.g. `C:/Users/you/mcp-prototypes`.

### 5. Run the backend

```bash
uvicorn app:app --reload
```

The server starts at `http://127.0.0.1:8000` and connects to all four MCP servers on startup. You should see `Processing request of type ListToolsRequest` four times in the logs, confirming each server connected successfully.

### 6. Open the frontend

Open `frontend/index.html` directly in a browser (or serve it with any static file server). It talks to the backend at `http://127.0.0.1:8000/chat`.

## Project Structure
ai-chat-platform/
├── backend/
│   ├── venv/   
│   ├── app.py                  
│   ├── mcp_client.py       
│   ├── gemini_function_calling.py   
│   ├── requirements.txt
│   ├── .env.example    
│   └── .env                  
└── frontend/
    ├── style.css
    ├── index.html
    └── script.js

## Notes

- The MCP servers' file operations (Excel/PDF/DXF reads/writes, SQL queries) are sandboxed to each server's own directory in `mcp-prototypes`.
- See the `mcp-prototypes` README for the full list of available tools and example prompts.