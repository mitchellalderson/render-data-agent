# ICP Analysis Dashboard 🎯

A modern Streamlit web application that analyzes customer data from PostgreSQL databases and CSV files using LLM insights to identify Ideal Customer Profile (ICP) matches. Built with Streamlit, PostgreSQL, OpenAI, and modern Python practices.

- [Deploy to Render](#-deploy-to-render)
- [Features](#-features)
- [Repository Structure](#-repository-structure)
- [Quick Start with Docker](#-quick-start-with-docker)
- [Local Development Setup](#-local-development-setup)
- [Docker Commands](#-docker-commands)
- [Usage Guide](#-usage-guide)
- [Environment Variables](#-environment-variables)
- [Troubleshooting](#-troubleshooting)
- [Additional Documentation](#-additional-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Deploy to Render

This project is pre-configured for easy deployment to [Render](https://render.com/) with a complete Blueprint configuration.

**What you get:**
- ✅ Streamlit web application with modern UI
- ✅ Managed PostgreSQL database with automatic backups
- ✅ Auto-scaling and health checks
- ✅ Environment variable management
- ✅ One-click Blueprint deployment
- ✅ Automatic deployments on Git push

### Quick Deploy to Render

1. **Push to GitHub** and connect your repository to Render
2. **Create a New Blueprint** in Render Dashboard
3. **Provide your API keys** (OPENAI_API_KEY required)
4. **Click Deploy** - Render handles the rest!

📖 **[Complete Deployment Guide →](./RENDER_DEPLOY.md)**

### Local Development with Docker

For local development and testing:

1. **Set up environment variables:**
   ```bash
   cp env.docker.example .env
   # Edit .env with your API keys
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access your application:**
   - Web App: `http://localhost:8501`
   - Database: PostgreSQL on port 5432

**Cost Estimate:**
- Render Web Service: $7/month (or Free tier)
- PostgreSQL Database: $7/month (or Free tier)
- OpenAI API: Pay-per-use (~$0.01-0.10 per analysis)
- Total: ~$0-20/month depending on tier and usage

## ✨ Features

### Phase 1 - Core Infrastructure ✅
- 📊 **PostgreSQL Integration** - Live database connection with data preview
- 📁 **CSV Upload** - File upload with validation and quality checks
- 🎨 **Modern UI** - Clean interface styled after Render.com
- 🔒 **Secure Configuration** - Environment-based credential management
- 📈 **Real-time Previews** - Interactive data exploration tools

### Phase 2 - Data Processing ✅
- 🧹 **Data Cleaning** - Standardize columns, remove duplicates, handle missing data
- 🗺️ **Schema Mapping** - AI-powered column matching with fuzzy similarity
- ✅ **Data Validation** - Quality scores (0-100), comprehensive reports
- 🔄 **Transformation** - Normalize numeric columns with preview
- 📋 **Pattern Recognition** - Auto-detect email, company, and other fields

### Phase 3 - LLM Integration ✅
- 🤖 **AI-Powered Analysis** - OpenAI and Anthropic LLM support
- 🎯 **ICP Scoring** - Intelligent scoring (0-100 scale) with confidence levels
- 💡 **Smart Insights** - Pattern recognition and automated recommendations
- 📊 **Rich Visualizations** - Histograms, pie charts, and interactive filters
- 💾 **Export Options** - CSV, JSON, and Excel formats

### Phase 4 - Advanced Dashboard ✅
- 👥 **Customer Segmentation** - Automatic grouping by score and confidence
- 🔍 **Comparison Tools** - Side-by-side comparison (2-5 customers)
- 📊 **Advanced Analytics** - Heatmaps, radar charts, funnel analysis
- 🎯 **Customer Profiles** - Detailed profiles with percentiles and recommendations
- 📈 **Pipeline Health** - Segment trends and actionable insights

### Future Enhancements 📋
- Historical tracking and trends over time
- Batch processing capabilities
- Custom scoring weights
- CRM integrations (Salesforce, HubSpot)
- Scheduled automated analysis
- Team collaboration features

## 📁 Repository Structure

```
render-data-agent/
├── main.py                     # Main Streamlit application
├── pyproject.toml              # Python dependencies (uv)
├── docker-compose.yml          # Production Docker configuration
├── docker-compose.dev.yml      # Development Docker configuration
├── Dockerfile                  # Container definition
├── env.docker.example          # Environment template
├── README.md                   # This file
├── DOCKER.md                   # Docker deployment guide
├── QUICKSTART.md              # Quick start guide
│
├── src/                        # Core application modules
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── database.py             # PostgreSQL connection
│   ├── data_processing.py      # Data cleaning and transformation
│   ├── icp_analyzer.py         # LLM-powered ICP analysis
│   ├── llm_client.py           # LLM provider abstraction
│   ├── segmentation.py         # Customer segmentation logic
│   ├── styles.py               # Custom CSS (Render.com style)
│   └── utils.py                # Helper functions
│
├── components/                 # UI components
│   ├── __init__.py
│   ├── data_upload.py          # CSV upload component
│   ├── data_processing_ui.py   # Data processing interface
│   ├── analysis_ui.py          # LLM analysis interface
│   └── advanced_visualizations.py # Charts and visualizations
│
├── data/                       # Sample data
│   ├── customer_data.csv       # Sample customer data
│   ├── mock_signups.sql        # Database setup script
│   └── README.md               # Data documentation
│
└── tests/                      # Test files
    └── __init__.py
```

## 🚀 Quick Start with Docker

**Requirements:**
- Docker & Docker Compose
- Python 3.9 or higher (for local development without Docker)
- PostgreSQL database (or use Docker Compose)
- OpenAI API key

**Setup:**

1. **Clone and install dependencies:**

```bash
git clone <your-repo-url>
cd render-data-agent
```

2. **Set up environment variables:**

```bash
# Copy the Docker environment template
cp env.docker.example .env

# Edit with your credentials
nano .env
```

Add your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
POSTGRES_PASSWORD=your-secure-password
```

3. **Start all services with Docker:**

```bash
docker-compose up -d
```

This starts:
- Streamlit app (port 8501)
- PostgreSQL database (port 5432)

4. **Load sample data:**

```bash
# Wait for PostgreSQL to be ready
sleep 10

# Load sample data
docker-compose exec db psql -U postgres -d render_data -f /docker-entrypoint-initdb.d/mock_signups.sql
```

5. **Access the application:**

Open http://localhost:8501 in your browser and start analyzing!

## 💻 Local Development Setup

**Prerequisites:**
- Python 3.9 or higher
- PostgreSQL database
- OpenAI API key

**Installation:**

1. **Clone the repository:**
```bash
git clone <repository-url>
cd render-data-agent
```

2. **Install dependencies:**

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install streamlit pandas numpy psycopg2-binary sqlalchemy python-dotenv openai anthropic plotly altair
```

3. **Set up environment variables:**

```bash
cp .env.template .env
```

Edit `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/render_data
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=render_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# LLM API Configuration
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4-turbo-preview

# App Configuration
APP_TITLE=ICP Analysis Dashboard
MAX_UPLOAD_SIZE_MB=50
DEBUG_MODE=false
```

4. **Set up the database:**

```bash
psql -U postgres -d render_data -f data/mock_signups.sql
```

5. **Run the application:**

```bash
uv run streamlit run main.py
# Or use: ./run.sh
```

The application will open at `http://localhost:8501`

## 📦 Docker Commands

**Start all services:**
```bash
docker-compose up -d
```

**Start in development mode:**
```bash
docker-compose -f docker-compose.dev.yml up
```

**Stop all services:**
```bash
docker-compose down
```

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Access database:**
```bash
docker-compose exec db psql -U postgres -d render_data
```

**Run without Docker (development):**
```bash
uv run streamlit run main.py
```

## 📖 Usage Guide

### 1. Configure Database Connection

- The sidebar shows your database connection status
- Select the table containing user signup data
- View row counts and table schema
- Test connection with real-time feedback

### 2. Upload Customer Data

- Navigate to the "Data Sources" tab
- Upload a CSV file with your customer data
- Review data quality metrics and preview
- System validates format and content

### 3. Process and Clean Data

- Navigate to "Data Processing" tab
- Clean data: remove duplicates, handle missing values
- Map columns with AI-powered suggestions
- Transform and normalize numeric fields

### 4. Run ICP Analysis

- Navigate to "LLM Analysis" tab
- Configure your ICP criteria
- Click "Analyze All Customers"
- View results with scores and confidence levels

### 5. Explore Advanced Analytics

- Navigate to "Advanced Dashboard" tab
- View customer segmentation
- Compare customers side-by-side
- Generate detailed profiles and insights

### Sample Data

The project includes sample data to help you get started:

- **`data/mock_signups.sql`**: SQL script with 15 mock user records
- **`data/customer_data.csv`**: 20 mock customers with social media and campaign data

## 🔧 Environment Variables

Required environment variables (`.env`):

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/render_data
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=render_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...

# LLM API Keys
OPENAI_API_KEY=...           # Get from https://platform.openai.com/api-keys
ANTHROPIC_API_KEY=...        # Optional, get from https://console.anthropic.com/

# LLM Configuration
LLM_MODEL=gpt-4-turbo-preview
LLM_PROVIDER=openai          # Options: openai, anthropic

# App Configuration
APP_TITLE=ICP Analysis Dashboard
MAX_UPLOAD_SIZE_MB=50
DEBUG_MODE=false
```

## 🐛 Troubleshooting

**1. Database connection fails:**
```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check connection string format
echo $DATABASE_URL

# Ensure database exists
psql -U postgres -l
```

**2. Docker container won't start:**
```bash
# Check if ports are available
lsof -i :8501
lsof -i :5432

# View container logs
docker-compose logs app
docker-compose logs db

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

**3. CSV upload issues:**
- Ensure file is valid CSV format
- Check file size (default max: 50MB)
- Verify CSV has header row
- Check for special characters in column names

**4. LLM API errors:**
- Verify API key is valid and active
- Check API key permissions and quotas
- Ensure correct model name in configuration
- Monitor API usage and rate limits

**5. Data processing errors:**
- Check data types in uploaded CSV
- Verify column names don't have special characters
- Ensure numeric columns contain valid numbers
- Review data quality report for issues

**Getting more help:**
1. Check application logs: `docker-compose logs app`
2. Verify all environment variables are set correctly
3. Ensure Docker containers are healthy: `docker-compose ps`
4. Review detailed troubleshooting in `DOCKER.md`
5. Check `QUICKSTART.md` for step-by-step guide

## 📚 Additional Documentation

- `RENDER_DEPLOY.md` - **Complete Render deployment guide**
- `QUICKSTART.md` - Comprehensive getting started guide
- `DOCKER.md` - Docker deployment guide
- `plan.md` - Detailed project roadmap
- `data/README.md` - Sample data documentation

**Design Philosophy:**

The UI is inspired by Render.com's clean, modern aesthetic:
- **Typography**: Inter font family
- **Colors**: Primary Purple (#A855F7), Neutral grays, Light background (#FAFAFA)
- **Components**: Minimalist, spacious, professional
- **Interaction**: Smooth transitions, clear feedback

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests with clear descriptions

**Code Formatting:**
```bash
black src/ components/ main.py
ruff check src/ components/ main.py
```

**Running Tests:**
```bash
pytest tests/
```

## 📄 License

[Add your license here]

---

Built with ❤️ using Streamlit, PostgreSQL, and modern Python practices.
