# Render Data Agent - Project Plan

## Project Overview
A Streamlit web application that analyzes customer data from multiple sources (PostgreSQL database and CSV files) using an LLM to identify Ideal Customer Profile (ICP) matches and provide actionable insights.

## Goals
- Compare mock user signups from a PostgreSQL database with customer data from CSV files
- Use LLM to intelligently parse and analyze data between sources
- Identify which customers match the user's Ideal Customer Profile (ICP)
- Provide clear, actionable analysis and recommendations

## Technology Stack

### Core Technologies
- **Frontend/UI**: Streamlit
- **Database**: PostgreSQL
- **LLM Integration**: OpenAI API / Anthropic Claude / Local LLM
- **Data Processing**: Pandas, NumPy
- **Database Connectivity**: psycopg2 / SQLAlchemy

### Development Tools
- **Python**: >=3.9
- **Package Manager**: uv
- **Environment**: python-dotenv for configuration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web App                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Data       │  │    LLM       │  │   Analysis      │  │
│  │  Ingestion   │→ │  Processing  │→ │   Dashboard     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│         ↓                                      ↓            │
│  ┌──────────────┐                    ┌─────────────────┐  │
│  │  PostgreSQL  │                    │   Export        │  │
│  │  Connection  │                    │   Results       │  │
│  └──────────────┘                    └─────────────────┘  │
│         ↓                                                   │
│  ┌──────────────┐                                          │
│  │  CSV Upload  │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

## Features Breakdown

### Phase 1: Core Infrastructure (MVP) ✅
- [x] Basic Streamlit app structure
- [x] PostgreSQL connection setup
- [x] CSV file upload functionality
- [x] Environment configuration (.env file)
- [x] Basic data preview capabilities

### Phase 2: Data Processing ✅
- [x] PostgreSQL query builder for user signups
- [x] CSV parser and validator
- [x] Data normalization and cleaning
- [x] Schema mapping between different data sources
- [x] Handle missing/incomplete data

### Phase 3: LLM Integration ✅
- [x] LLM client setup (OpenAI/Anthropic/etc.)
- [x] Prompt engineering for ICP analysis
- [x] Data comparison logic
- [x] Pattern recognition for ICP matching
- [x] Generate insights and recommendations

### Phase 4: Advanced Dashboard ✅
- [x] Display matched customers
- [x] ICP scoring/ranking system
- [x] Visual charts and graphs (customer segments, trends)
- [x] Detailed customer profiles
- [x] Confidence scores for matches
- [x] Customer segmentation (by score and confidence)
- [x] Customer comparison tools
- [x] Attribute analysis and heatmaps
- [x] Trend analysis and insights

### Phase 5: Advanced Features
- [ ] Custom ICP criteria definition
- [ ] Historical analysis and trends
- [ ] Export results (CSV, PDF, JSON)
- [ ] Batch processing capabilities
- [ ] Save and load analysis sessions

### Phase 6: Polish & Production
- [ ] Error handling and validation
- [ ] Loading states and progress indicators
- [ ] User authentication (optional)
- [ ] Deployment configuration
- [ ] Documentation and user guide

## Data Schema

### PostgreSQL Schema (User Signups)
```sql
CREATE TABLE user_signups (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    role VARCHAR(100),
    signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    use_case TEXT,
    revenue_range VARCHAR(50),
    location VARCHAR(100),
    metadata JSONB
);
```

### CSV Schema (Customer Data)
Expected columns:
- `company_name`: Company name
- `industry`: Industry/sector
- `size`: Company size (employees or revenue)
- `contact_email`: Primary contact
- `status`: Customer status (active, prospect, churned)
- `value`: Customer lifetime value or deal size
- `additional_data`: Any extra relevant fields

### ICP Definition Schema
```json
{
  "ideal_profile": {
    "industries": ["SaaS", "Technology", "E-commerce"],
    "company_size": ["50-200", "200-1000"],
    "revenue_range": ["$1M-$10M", "$10M-$50M"],
    "key_attributes": ["fast-growing", "technical team"],
    "use_cases": ["automation", "analytics"]
  }
}
```

## LLM Prompting Strategy

### Analysis Prompt Template
```
You are an expert data analyst specializing in customer profiling.

TASK: Analyze the following datasets to identify which customers match the Ideal Customer Profile (ICP).

USER SIGNUPS DATA:
{signups_data}

CUSTOMER DATA:
{customer_data}

ICP CRITERIA:
{icp_criteria}

Please:
1. Compare and match records between the two datasets
2. Score each customer on ICP fit (0-100)
3. Identify key patterns in high-scoring customers
4. Provide specific recommendations for targeting similar profiles
5. Highlight any data quality issues or gaps

Format your response as structured JSON with:
- matched_customers: list of matches with scores
- patterns: key insights about ICP characteristics
- recommendations: actionable next steps
- data_quality_notes: any issues found
```

## File Structure

```
render-data-agent/
├── main.py                     # Main Streamlit app entry point
├── pyproject.toml              # Python dependencies
├── README.md                   # Project documentation
├── plan.md                     # This file
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── database.py             # PostgreSQL connection handling
│   ├── data_processing.py      # Data cleaning and normalization
│   ├── llm_client.py           # LLM API integration
│   ├── icp_analyzer.py         # Core ICP matching logic
│   └── utils.py                # Helper functions
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py              # Streamlit sidebar components
│   ├── data_upload.py          # File upload UI
│   ├── results_display.py      # Results visualization
│   └── charts.py               # Chart components
│
├── data/
│   ├── customer_data.csv        # Sample CSV for testing
│   └── mock_signups.sql        # SQL script for test data
│
└── tests/
    ├── __init__.py
    ├── test_database.py
    ├── test_data_processing.py
    └── test_icp_analyzer.py
```

## Configuration Requirements

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=render_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# LLM API
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai  # or 'anthropic', 'local'
LLM_MODEL=gpt-4-turbo-preview

# App Configuration
APP_TITLE="ICP Analysis Dashboard"
MAX_UPLOAD_SIZE_MB=50
DEBUG_MODE=true
```

## Dependencies to Add

```toml
[project]
dependencies = [
    "streamlit>=1.50.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "psycopg2-binary>=2.9.9",
    "sqlalchemy>=2.0.0",
    "python-dotenv>=1.0.0",
    "openai>=1.0.0",
    "anthropic>=0.18.0",
    "plotly>=5.18.0",
    "altair>=5.2.0",
    "openpyxl>=3.1.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.12.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
]
```

## Development Workflow

### 1. Setup Development Environment
```bash
# Install dependencies
uv pip install -e ".[dev]"

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Setup PostgreSQL database
psql -U postgres -f data/mock_signups.sql
```

### 2. Development Process
- Build features incrementally following phases
- Write tests for core functionality
- Use git branches for features
- Regular commits with clear messages

### 3. Testing Strategy
- Unit tests for data processing functions
- Integration tests for database connections
- Manual testing with sample data
- LLM response validation

## Deployment Considerations

### Streamlit Cloud
- Add `requirements.txt` or use `pyproject.toml`
- Configure secrets in Streamlit Cloud dashboard
- Ensure PostgreSQL is accessible from cloud

### Docker (Alternative)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv pip install -e .
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

## Success Metrics

### Technical
- App loads in < 3 seconds
- Database queries complete in < 1 second
- LLM analysis completes in < 30 seconds
- Handle datasets up to 10,000 rows

### User Experience
- Intuitive UI requiring no documentation
- Clear error messages and guidance
- Export functionality works reliably
- Results are actionable and clear

## Timeline Estimate

- **Week 1**: Phase 1 & 2 - Infrastructure and Data Processing
- **Week 2**: Phase 3 - LLM Integration and Basic Analysis
- **Week 3**: Phase 4 - Dashboard and Visualization
- **Week 4**: Phase 5 & 6 - Advanced Features and Polish

## Open Questions

1. What LLM provider should we prioritize? (OpenAI, Anthropic, local models)
2. What defines an "ICP match"? (specific criteria from user)
3. Should we support multiple CSV formats or enforce a standard?
4. Do we need user authentication/multi-tenancy?
5. What's the expected data volume? (hundreds, thousands, millions of records)
6. Should the PostgreSQL schema be created by the app or pre-existing?
7. What export formats are needed? (CSV, JSON, PDF reports)

## Next Steps

1. ✅ Create this plan document
2. Update `pyproject.toml` with all required dependencies
3. Create project structure (src/, components/, data/, tests/)
4. Setup `.env.example` file
5. Create basic Streamlit app layout
6. Implement PostgreSQL connection module
7. Build CSV upload component
8. Integrate LLM client
9. Develop ICP matching algorithm
10. Create visualization dashboard

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [PostgreSQL Python Tutorial](https://www.psycopg.org/docs/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

