# ICP Analysis Chat Agent 🎯

A modern chat-based application that analyzes customer data using LLM insights to identify Ideal Customer Profile (ICP) matches. Ask natural language questions about your data and get instant insights. Built with FastAPI, Next.js, PostgreSQL, and OpenAI/Anthropic.

## Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Architecture](#-architecture)
- [Data Processing & Parsing](#-data-processing--parsing)
- [Usage Guide](#-usage-guide)
- [API Endpoints](#-api-endpoints)
- [Environment Variables](#-environment-variables)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🚀 Quick Start

### Option 1: Docker Compose (Local Development) 🐳

**Fastest way to get started locally:**

```bash
# 1. Configure environment
cp env.docker.example .env
# Add your API key to .env (OPENAI_API_KEY or ANTHROPIC_API_KEY)

# 2. Start everything
docker-compose up -d

# 3. Open the app
# Visit http://localhost:3000/data-analyst
```

That's it! Backend, frontend, and database all running in containers.

**Docker Commands:**
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart after code changes
docker-compose up -d --build

# Access database
docker-compose exec postgres psql -U postgres -d render_data
```

### Option 2: Local Development (Without Docker)

**Run services directly on your machine:**

**Prerequisites:**
- Python 3.9+
- Node.js 18+
- PostgreSQL (optional)
- OpenAI or Anthropic API key

**Backend:**
```bash
# Install dependencies
pip install -e .
# or with uv: uv sync

# Configure
cp env.docker.example .env
# Add API key to .env

# Start backend
./run_api.sh
# Runs at http://localhost:8000
```

**Frontend:**
```bash
# Install dependencies
cd frontend
npm install

# Configure
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
# Runs at http://localhost:3000
```

**Usage:**
1. Open http://localhost:3000/data-analyst
2. Upload your enrichment CSV file (sidebar)
3. Start asking questions about your data!

> **💡 Production Deployment**: For production, we recommend deploying to [Render](https://render.com). See the [Deployment](#-deployment) section for detailed instructions. Docker Compose is intended for local development only.

## ✨ Features

### Chat-Based Interface 💬
- 🤖 **Natural Language Queries** - Ask questions in plain English
- 💡 **Smart Responses** - Get insights with tables, charts, and explanations
- 🔄 **Conversation History** - Context-aware responses based on previous questions
- 📊 **Dynamic Visualizations** - Automatic chart generation for data insights

### Data Analysis 📊
- 📁 **CSV Upload** - Upload enrichment data directly through the UI
- 🔌 **Database Integration** - Connect to PostgreSQL for signup data
- 🎯 **ICP Scoring** - AI-powered scoring (0-100 scale) with confidence levels
- 📈 **Pattern Recognition** - Identify trends and commonalities
- 💡 **Smart Recommendations** - Actionable insights from your data

### LLM Integration 🤖
- 🔀 **Multi-Provider Support** - OpenAI and Anthropic
- 🎨 **Flexible Models** - Choose GPT-4, Claude, or other models
- 🧠 **Context-Aware** - Understands your data structure automatically
- 📊 **Structured Outputs** - Tables, charts, and SQL queries

### Developer-Friendly 🛠️
- ⚡ **FastAPI Backend** - High-performance, async Python API
- ⚛️ **Next.js Frontend** - Modern React with TypeScript
- 📖 **OpenAPI Docs** - Auto-generated API documentation
- 🔒 **Environment Variables** - Secure configuration management

## 🏗️ Architecture

```
┌──────────────┐        ┌──────────────┐
│   Frontend   │ ─────▶ │   Backend    │
│   (Next.js)  │  HTTP  │  (FastAPI)   │
│              │ ◀───── │              │
│  • Chat UI   │  JSON  │  • REST API  │
│  • Upload    │        │  • LLM Logic │
│  • Display   │        │  • Data Proc │
└──────────────┘        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  PostgreSQL  │
                        │  (Optional)  │
                        └──────────────┘
```

**Backend (FastAPI + Python)**
- REST API with async support
- LLM integration (OpenAI/Anthropic)
- PostgreSQL database connector
- In-memory state management
- Auto-generated OpenAPI docs

**Frontend (Next.js + React)**
- Server-side rendering
- TypeScript for type safety
- Tailwind CSS for styling
- Real-time chat interface
- Recharts for visualizations

**Data Flow**
1. User uploads CSV → Backend stores in memory
2. User asks question → Frontend sends to `/api/chat`
3. Backend processes with LLM → Returns structured response
4. Frontend displays → Tables, charts, explanations

## 📊 Data Processing & Parsing

This section explains how the API combines and parses user data from multiple sources.

### Data Sources

The system works with two primary data sources:

1. **Enrichment Data (CSV)** - Customer enrichment data uploaded via the UI
2. **Signup Data (Database)** - User signup records from PostgreSQL (optional)

### Upload & Storage Process

#### 1. CSV Upload (`/api/upload`)

When a CSV file is uploaded:

```python
# File is read into memory
content = await file.read()

# Saved to temporary file
with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp:
    tmp.write(content)
    tmp_path = tmp.name

# Loaded into pandas DataFrame
df = pd.read_csv(tmp_path)

# Stored in application state
state.enrichment_data = df
```

**Key Steps:**
- File validation (must be `.csv`)
- Temporary file creation for processing
- Pandas DataFrame conversion
- In-memory storage in `AppState.enrichment_data`
- Temporary file cleanup

#### 2. Database Signup Data Loading

When a chat query is made and database is connected:

```python
# Check database connection
db = get_database_connection()
success, _ = db.test_connection()

if success:
    # Get available tables
    tables = db.get_tables()
    if tables:
        # Query signup data (default: first table, limit 1000 rows)
        table_name = tables[0]
        state.signup_data = db.query_signups(table_name, limit=1000)
```

**Key Steps:**
- Database connection test
- Table discovery
- Data querying (with row limit for performance)
- Storage in `AppState.signup_data`

### Data Cleaning & Normalization

Before analysis, data goes through cleaning via `DataCleaner`:

#### Column Standardization
```python
# Standardizes column names to lowercase with underscores
"Company Name" → "company_name"
"Email Address" → "email_address"
"Industry/Sector" → "industry_sector"
```

**Process:**
- Convert to lowercase
- Replace spaces with underscores
- Remove special characters
- Remove consecutive underscores
- Trim leading/trailing underscores

#### Data Cleaning Operations

1. **Duplicate Removal**
   - Removes duplicate rows
   - Handles unhashable types gracefully
   - Removes duplicate columns

2. **String Cleaning**
   - Strips whitespace
   - Normalizes multiple spaces to single space
   - Replaces null indicators (`'nan'`, `'None'`, `'NULL'`, `''`) with `NaN`

3. **Numeric Cleaning**
   - Replaces infinite values (`inf`, `-inf`) with `NaN`
   - Preserves numeric types

4. **Missing Data Handling**
   - Can drop columns with >50% missing values
   - Can fill missing values (mean, median, mode, forward fill)
   - Default: drops rows with any missing values

### Schema Mapping & Alignment

When combining enrichment and signup data, `SchemaMapper` aligns schemas:

#### Column Mapping
```python
# Automatically suggests column mappings based on similarity
mappings = SchemaMapper.suggest_column_mapping(
    source_df=enrichment_data,
    target_df=signup_data,
    threshold=0.6  # Minimum similarity score
)

# Example mappings:
# "company" → "company_name" (similarity: 0.85)
# "email" → "email_address" (similarity: 0.90)
# "industry" → "sector" (similarity: 0.75)
```

**Similarity Calculation:**
- Exact match: 1.0
- Sequence matcher ratio (fuzzy matching)
- Pattern boosts (e.g., `email`/`mail` → 0.9, `company`/`organization` → 0.8)

#### Schema Alignment
```python
# Aligns two DataFrames to have matching columns
df1_aligned, df2_aligned = SchemaMapper.align_schemas(
    df1=enrichment_data,
    df2=signup_data,
    mapping=optional_explicit_mapping
)

# Result: Both DataFrames have the same column names
# Only common columns are kept
```

### Data Combination for Analysis

When processing a chat query, data is combined:

#### Context Building (`process_chat_query`)

```python
# Build context for LLM
context_parts = []

# Add enrichment data summary
context_parts.append("## Available Data\n")
context_parts.append(f"### Enrichment Data")
context_parts.append(f"- Rows: {len(enrichment_data)}")
context_parts.append(f"- Columns: {', '.join(enrichment_data.columns)}")
context_parts.append(f"- Sample:\n```\n{enrichment_data.head(3).to_string()}\n```\n")

# Add signup data summary (if available)
if signup_data is not None:
    context_parts.append(f"### Signup Data")
    context_parts.append(f"- Rows: {len(signup_data)}")
    context_parts.append(f"- Columns: {', '.join(signup_data.columns)}")
    context_parts.append(f"- Sample:\n```\n{signup_data.head(3).to_string()}\n```\n")

# Add conversation history (last 3 exchanges)
if len(conversation_history) > 1:
    context_parts.append("\n## Recent Conversation")
    for msg in conversation_history[-6:]:  # Last 6 messages
        context_parts.append(f"**{msg['role']}**: {msg['content']}")
```

**Key Points:**
- Both datasets are summarized (row count, columns, sample rows)
- Data is presented as text tables for LLM consumption
- Conversation history provides context for follow-up questions
- Limited to first 3 rows per dataset to manage token usage

### ICP Analysis Process

For full ICP analysis (`/api/analyze`), data is processed differently:

#### 1. Data Sampling
```python
# Limit data size for LLM context
signup_sample = signup_data.head(max_customers)  # Default: 50
customer_sample = customer_data.head(max_customers)  # Default: 50
```

#### 2. ICP Derivation
The system derives ICP from signup data:

```python
# Signup data represents the ICP (Ideal Customer Profile)
# The LLM analyzes patterns in signups to understand:
# - Common industries
# - Company size ranges
# - Use cases
# - Behavioral patterns
```

#### 3. Customer Matching
Each customer in enrichment data is scored against the ICP:

```python
# For each customer:
# 1. Compare attributes to ICP patterns
# 2. Calculate match score (0-100)
# 3. Identify matching attributes
# 4. Identify gaps
# 5. Assign confidence level (high/medium/low)
# 6. Generate reasoning
```

#### 4. Pattern Recognition
The LLM identifies patterns across high-scoring customers:

```python
patterns = {
    "common_industries": ["SaaS", "Technology", "Finance"],
    "common_sizes": ["50-200", "200-1000"],
    "common_attributes": ["Has engineering team", "Uses cloud infrastructure"],
    "key_indicators": ["High engagement", "Multiple users"]
}
```

### Data Validation

Before processing, data is validated via `DataValidator`:

```python
validation = DataValidator.validate_dataframe(df)

# Returns:
{
    'is_valid': True/False,
    'errors': ['Column X has all missing values'],
    'warnings': ['Found 5 duplicate rows', 'Missing data: 10%'],
    'stats': {
        'total_rows': 1000,
        'total_columns': 15,
        'numeric_columns': 8,
        'text_columns': 7,
        'missing_values': 150,
        'duplicate_rows': 5
    }
}
```

**Quality Score Calculation:**
```python
score = DataValidator.get_data_quality_score(df)

# Factors:
# - Completeness (40%): No missing values
# - Uniqueness (30%): No duplicates
# - Validity (30%): No all-null columns

# Returns: 0-100 score
```

### Memory Management

**Current Implementation:**
- Data stored in-memory (`AppState` class)
- Resets on server restart
- No persistence between sessions

**Limitations:**
- Single user session (no multi-user support)
- Data lost on restart
- No file persistence

**Future Enhancements:**
- Redis for session storage
- Database persistence for uploaded files
- File system storage for CSVs
- Multi-user support with session management

### Example: Complete Data Flow

```
1. User uploads "customers.csv"
   ↓
2. Backend reads CSV → pandas DataFrame
   ↓
3. DataCleaner.clean_dataframe() standardizes columns
   ↓
4. Stored in state.enrichment_data
   ↓
5. User asks: "Who are my top ICP customers?"
   ↓
6. Backend loads signup_data from database (if connected)
   ↓
7. SchemaMapper aligns schemas (if needed)
   ↓
8. Context built with both datasets + conversation history
   ↓
9. LLM analyzes and generates response
   ↓
10. Response parsed into ChatResponse (tables, charts, text)
   ↓
11. Frontend displays formatted results
```

## 📖 Usage Guide

### 1. Start the Application

**Backend (FastAPI):**
```bash
./run_api.sh
# Starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Frontend (Next.js):**
```bash
cd frontend
npm run dev
# Starts at http://localhost:3000
```

### 2. Upload Enrichment Data

1. Open http://localhost:3000/data-analyst
2. Click the CSV upload area in the sidebar
3. Select your enrichment CSV file
4. Wait for upload confirmation
5. Check the "Connected Data" section shows green status

### 3. Ask Questions

Type natural language questions in the chat box, such as:

- **Basic Analysis**: "Who are our highest ICP fit customers?"
- **Segmentation**: "Show me customers grouped by industry"
- **Patterns**: "What do high-scoring customers have in common?"
- **Comparisons**: "Compare customers by company size"
- **Trends**: "What percentage of customers are in tech?"

### 4. Interpret Results

The agent responds with:
- **Text explanations** - Natural language insights
- **Tables** - Structured data summaries
- **Charts** - Visual representations of trends
- **SQL queries** - The underlying queries (optional)

### 5. Continue the Conversation

Ask follow-up questions to dive deeper:
- "Tell me more about the top 5"
- "What about customers in enterprise segment?"
- "Show me the breakdown by source"

### Example Workflow

```
You: "Upload enrichment CSV" → Click sidebar upload
Agent: "✅ Successfully uploaded! 1,247 rows loaded"

You: "Who are our top ICP customers?"
Agent: [Shows table with top 10, includes scores and reasons]

You: "What patterns do they share?"
Agent: [Analyzes commonalities, shows charts]

You: "Show me customers in the SaaS industry"
Agent: [Filters and displays SaaS customers]
```

### Sample Data

The project includes sample data to help you get started:
- **`data/mock_signups.sql`**: SQL script with mock user records
- **`data/customer_data.csv`**: Mock customer enrichment data

## 🔌 API Endpoints

### GET `/`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "ICP Analysis Agent API",
  "version": "1.0.0"
}
```

### GET `/api/status`
Get current data status.

**Response:**
```json
{
  "enrichment_loaded": true,
  "enrichment_rows": 1247,
  "enrichment_columns": 15,
  "signup_loaded": true,
  "signup_rows": 500,
  "signup_columns": 12,
  "database_connected": true
}
```

### POST `/api/upload`
Upload enrichment CSV file.

**Request:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@customer_data.csv"
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully uploaded customer_data.csv",
  "data": {
    "rows": 1247,
    "columns": 15,
    "column_names": ["company", "industry", "size", ...],
    "sample": [...]
  }
}
```

### POST `/api/chat`
Send chat message for analysis.

**Request:**
```json
{
  "message": "Who are our top ICP customers?",
  "include_sql": true
}
```

**Response:**
```json
{
  "content": "Based on your data, here are the top ICP customers...",
  "table": {
    "title": "Top ICP Customers",
    "columns": ["Company", "Score", "Industry"],
    "rows": [...]
  },
  "charts": [
    {
      "id": "score-distribution",
      "title": "ICP Score Distribution",
      "data": [...],
      "xKey": "score_range",
      "yKey": "count"
    }
  ],
  "sql": "SELECT ..."
}
```

### POST `/api/analyze`
Run full ICP analysis.

**Response:**
```json
{
  "status": "success",
  "summary": "Analysis complete...",
  "statistics": {
    "total_analyzed": 50,
    "avg_score": 72.5,
    "matches_above_80": 12
  },
  "top_matches": [...],
  "patterns": {...},
  "recommendations": [...]
}
```

### DELETE `/api/reset`
Reset all application state.

**Response:**
```json
{
  "status": "success",
  "message": "State reset successfully"
}
```

### GET `/docs`
Interactive API documentation (Swagger UI).

## 🔧 Environment Variables

### Backend (.env in project root)

```env
# LLM API Keys (at least one required)
OPENAI_API_KEY=sk-...        # Get from https://platform.openai.com/api-keys
ANTHROPIC_API_KEY=sk-...     # Get from https://console.anthropic.com/

# Database Configuration (optional - for signup data)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=your_password

# API Configuration
PORT=8000
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
```

### Frontend (frontend/.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Backend won't start
- Check that port 8000 is available: `lsof -i :8000`
- Verify Python version: `python --version` (needs 3.9+)
- Check `.env` file has valid API keys
- Install dependencies: `pip install -e .`

### Frontend won't start
- Check that port 3000 is available: `lsof -i :3000`
- Verify Node version: `node --version` (needs 18+)
- Install dependencies: `cd frontend && npm install`
- Check `.env.local` has correct API URL

### Frontend can't connect to backend
- Ensure backend is running at http://localhost:8000
- Test backend: `curl http://localhost:8000/api/status`
- Check browser console for CORS errors
- Verify `NEXT_PUBLIC_API_URL` in frontend/.env.local

### CSV upload fails
- Check file is valid CSV format
- Ensure CSV has header row
- Verify file size is reasonable (<300MB)
- Check backend logs for detailed error

### LLM API errors
- Verify API key is correct and active
- Check API quotas and billing
- Try switching providers (OpenAI ↔ Anthropic)
- Check backend logs for full error message

### Database connection issues (optional)
- Verify PostgreSQL is running
- Check credentials in `.env`
- Test connection: `psql -h localhost -U user -d dbname`
- Database is optional - agent works with CSV only

### Docker Issues

**Port conflicts:**
```bash
# Find what's using the port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill the process or change ports in docker-compose.yml
```

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Restart services
docker-compose restart
```

**Frontend can't connect to backend:**
```bash
# Check if backend is running
curl http://localhost:8000/api/status

# Check frontend logs
docker-compose logs frontend

# Restart both
docker-compose restart backend frontend
```

**Getting more help:**
1. Check backend logs in terminal where `run_api.sh` is running
2. Check frontend logs in terminal where `npm run dev` is running
3. Check browser console (F12) for frontend errors
4. Review API docs: http://localhost:8000/docs

## 🚀 Deployment

### Production Deployment (Recommended: Render)

**Render** is the recommended production deployment platform for this application.

#### Deploy Backend to Render

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Configure settings:
   - **Build Command**: `pip install -e .` or `uv sync`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
4. Add environment variables:
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
   - `DATABASE_URL` (if using PostgreSQL)
   - `LLM_PROVIDER` (default: `openai`)
   - `LLM_MODEL` (default: `gpt-4-turbo-preview`)
5. Deploy! Render will automatically run migrations on each deploy.

#### Deploy Frontend to Render

1. Create a new **Static Site** or **Web Service** on Render
2. Connect your GitHub repository
3. Set root directory to `frontend`
4. Configure settings:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/.next`
   - **Environment**: Node
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend Render URL (e.g., `https://your-backend.onrender.com`)
6. Deploy!

**Alternative Production Platforms:**
- **Railway**: Auto-detects Python/Node, similar setup
- **Fly.io**: Containerize with Docker
- **Vercel**: Great for Next.js frontend (one-click deploy)

### Local Development (Docker Compose)

For local development, use Docker Compose:

```bash
# Start all services (backend, frontend, database)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Local Development Setup:**
1. Copy `env.docker.example` to `.env`
2. Add your API keys to `.env`
3. Run `docker-compose up -d`
4. Access frontend at http://localhost:3000
5. Access backend API at http://localhost:8000

**Note**: Docker Compose is intended for local development only. For production, use Render or another managed platform.

## 📁 Repository Structure

```
render-data-agent/
├── api.py                      # FastAPI backend application
├── run_api.sh                  # Backend startup script
├── pyproject.toml              # Python dependencies
├── docker-compose.yml          # Docker setup for local development
├── Dockerfile                  # Backend container
├── Dockerfile.frontend         # Frontend container
│
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── page.tsx            # Landing page
│   │   └── data-analyst/
│   │       └── page.tsx        # Main chat interface
│   ├── components/             # React components
│   ├── package.json            # Node dependencies
│   └── tsconfig.json           # TypeScript config
│
├── src/                        # Core Python modules
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── database.py             # PostgreSQL connection
│   ├── data_processing.py      # Data cleaning and transformation
│   ├── icp_analyzer.py         # LLM-powered ICP analysis
│   ├── llm_client.py           # LLM provider abstraction
│   ├── segmentation.py         # Customer segmentation logic
│   └── utils.py                # Helper functions
│
├── data/                       # Sample data
│   ├── customer_data.csv       # Sample customer data
│   ├── mock_signups.sql        # Database setup script
│   └── README.md               # Data documentation
│
└── tests/                      # Test files
    └── __init__.py
```

## 🗄️ Database Setup (Optional)

The agent can work with just CSV files, but connecting a PostgreSQL database allows comparison with signup data.

### Setup Database

1. **Install PostgreSQL** (if not already installed)

2. **Create database:**
```bash
createdb render_data
```

3. **Load sample data:**
```bash
psql -U postgres -d render_data -f data/mock_signups.sql
```

4. **Configure in .env:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/render_data
```

The agent will automatically detect and use the database if configured.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test both backend and frontend

**Backend formatting:**
```bash
black src/ api.py
ruff check src/ api.py
```

**Frontend formatting:**
```bash
cd frontend
npm run lint
```

## 📚 Additional Resources

- **API Documentation**: Interactive docs at http://localhost:8000/docs
- **Sample Data**: See `data/README.md` for data documentation
- **Docker Guide**: See `DOCKER_QUICKSTART.md` for Docker commands

## 🔮 Future Enhancements

- Multi-file comparison and merging
- Historical tracking and trends
- Custom ICP criteria configuration
- Scheduled analysis and reporting
- Export to CRM systems
- Team collaboration features
- Session persistence (Redis)
- WebSocket streaming for real-time responses
- User authentication and multi-user support

---

Built with ❤️ using FastAPI, Next.js, and modern full-stack practices.
