# Quick Start Guide 🚀

Get the ICP Analysis Dashboard running in under 5 minutes with Docker!

## 🐳 Docker Setup (Recommended)

**Why Docker?**
- ✅ No dependencies to install (Python, PostgreSQL, etc.)
- ✅ Works on macOS, Linux, and Windows
- ✅ Production-ready setup
- ✅ Isolated environment
- ✅ Easy cleanup

### Prerequisites

- [ ] Docker and Docker Compose installed
- [ ] OpenAI API key (optional for Phase 1)

**Don't have Docker?** [Install Docker Desktop](https://www.docker.com/products/docker-desktop)

## Four Simple Steps

### 1. Copy Environment File

```bash
cp env.docker.example .env
```

### 2. Add Your OpenAI API Key (Optional)

Edit the `.env` file:
```bash
nano .env  # or use your preferred editor
```

Update this line:
```env
OPENAI_API_KEY=sk-your-key-here
```

**Note:** You can skip this for Phase 1 testing with database data only.

### 3. Start Everything!

```bash
docker-compose up -d
```

That's it! 🎉

The app will be running at: **http://localhost:8501**

### 4. Run Database Migrations

```bash
# Wait a few seconds for PostgreSQL to start, then:
docker-compose exec app uv run python migrate.py
```

This will automatically:
- ✅ Create the `render_data` database schema
- ✅ Set up the `user_signups` table
- ✅ Load 20 sample records with test data
- ✅ Create performance indexes

## Using the App

### Step 1: Check Database Connection

Look at the sidebar:
- ✅ Green = Connected
- ❌ Red = Connection failed (check your .env)

### Step 2: Select Your Data Source

In the sidebar:
1. Choose a table from the dropdown (e.g., `user_signups`)
2. View the row count
3. Optionally limit records for testing

### Step 3: Load Database Data

In the "Data Sources" tab:
- Preview your database table (`user_signups`)
- Check the schema
- View sample records (20 mock signups included)

### Step 4: Upload Customer CSV (Optional)

Still in "Data Sources" tab:
1. Click "Browse files" or drag & drop
2. Choose the sample file: `data/customer_data.csv`
3. Review data quality metrics
4. Check the preview

### Step 5: Compare Datasets

Once both are loaded:
- See side-by-side comparison
- Check for common columns
- Click "Proceed to Analysis" button

### Step 6: Analysis (Coming in Phase 3)

Switch to the "Analysis" tab to run ICP analysis (Phase 3 feature)

## Docker Management

### View Logs

```bash
# All services
docker-compose logs -f

# Just the app
docker-compose logs -f app

# Just the database
docker-compose logs -f postgres
```

### Stop the App

```bash
docker-compose down
```

### Restart After Changes

```bash
docker-compose up -d --build
```

### Access the Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d render_data

# View tables
docker-compose exec postgres psql -U postgres -d render_data -c "\dt"

# Check data
docker-compose exec postgres psql -U postgres -d render_data -c "SELECT COUNT(*) FROM user_signups;"
```

### Check Container Status

```bash
docker-compose ps
```

### Complete Cleanup

Remove everything (containers, volumes, networks):
```bash
docker-compose down -v
```

## Troubleshooting

### "Cannot connect to the Docker daemon"

Make sure Docker Desktop is running:
- **macOS/Windows**: Open Docker Desktop app
- **Linux**: Start Docker service: `sudo systemctl start docker`

### "Port 8501 already in use"

Another service is using the port:
```bash
# Stop existing containers
docker-compose down

# Or change the port in docker-compose.yml
# Edit the ports line: "8502:8501"
```

### "Database connection failed"

Check if containers are running:
```bash
docker-compose ps
```

Restart the services:
```bash
docker-compose restart
```

### "No tables found in database"

The database initialization might have failed. Rebuild:
```bash
docker-compose down -v
docker-compose up -d
```

### Container Won't Start

View the logs to see the error:
```bash
docker-compose logs app
# or
docker-compose logs postgres
```

### "CSV upload failed"

**Check:**
1. File is valid CSV format
2. File has header row
3. File size < 50MB
4. No special characters in column names

## Sample Data

The Docker setup automatically loads sample data:

**Database Data** (`data/mock_signups.sql`):
- ✅ 20 mock user signups
- ✅ Various industries (Technology, AI, Finance, SaaS)
- ✅ Company sizes from startups (10-50) to enterprise (1000+)
- ✅ Revenue ranges from $0-$1M to $50M+
- ✅ Realistic use cases and metadata

**CSV Data** (`data/customer_data.csv`):
- 20 mock customer records
- Full Name, Email, LinkedIn Profile, Company, Title
- City, X (Twitter) Username, Follower counts
- Social platform preferences and marketing campaigns

## Common Docker Commands

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View live logs
docker-compose logs -f

# Restart everything
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Check status
docker-compose ps

# Access database shell
docker-compose exec postgres psql -U postgres -d render_data

# Clean everything (including data)
docker-compose down -v
```

## What You Should See

### Sidebar
- ⚙️ Configuration section
- Database connection status
- Table selection dropdown
- Data options (record limits)
- Analysis mode selector

### Data Sources Tab
- 📊 Database preview with metrics
- 📤 CSV upload area
- 🔄 Side-by-side comparison
- 🚀 Proceed button

### UI Style
- Purple gradient header (#A855F7)
- Black primary buttons
- Clean white cards
- Professional metrics
- Render.com-inspired design

## Next Steps

Once you're up and running:

1. ✅ **Verify the connection**: Check the green status in sidebar
2. 📊 **Explore the data**: View the 20 sample signups in the database
3. 📤 **Upload CSV**: Try the `data/customer_data.csv` file
4. 🔍 **Compare datasets**: Use the side-by-side comparison
5. 🚀 **Wait for Phase 2 & 3**: Data processing and LLM-powered analysis coming soon!

## Pro Tips

1. **Use the sample data first** to verify everything works
2. **Check the logs** with `docker-compose logs -f` for errors
3. **Restart containers** if something seems stuck: `docker-compose restart`
4. **Clear browser cache** if UI acts strange: `Ctrl+Shift+R`
5. **Clean restart**: `docker-compose down -v && docker-compose up -d`

---

**Need more help?** Check the [DOCKER.md](DOCKER.md) or [README.md](README.md)!

Happy analyzing! 🎯

---

## Alternative: Local Development Setup

Prefer to run directly on your machine without Docker? Here's how:

### Prerequisites

- [ ] Python 3.9+ installed
- [ ] PostgreSQL installed and running
- [ ] OpenAI API key (optional for Phase 1)

### Steps

**1. Install Dependencies**

```bash
# Using uv (recommended)
uv sync

# Or with pip
pip install streamlit pandas numpy psycopg2-binary sqlalchemy python-dotenv openai plotly altair
```

**2. Configure Environment**

```bash
# Copy template
cp .env.example .env

# Edit with your local settings
nano .env
```

Required settings:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=render_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
OPENAI_API_KEY=sk-your-key-here
```

**3. Set Up Database**

```bash
# Create database
createdb render_data

# Run migrations (recommended)
uv run python migrate.py
# Or use the helper script:
./migrate.sh

# Or load manually:
# psql -U postgres -d render_data -f data/mock_signups.sql
```

**4. Run the App**

```bash
# With uv
uv run streamlit run main.py

# Or directly
streamlit run main.py

# Or use the quick-start script
./run.sh
```

### Local Development Commands

```bash
# Run on different port
uv run streamlit run main.py --server.port 8502

# Run in development mode (auto-reload)
uv run streamlit run main.py --server.runOnSave=true

# Check database connection
psql -U postgres -d render_data -c "SELECT COUNT(*) FROM user_signups;"

# View database tables
psql -U postgres -d render_data -c "\dt"

# Add new dependency
uv add package-name

# Run tests
uv run pytest tests/
```

### Local Troubleshooting

**PostgreSQL not running:**
```bash
# macOS (Homebrew)
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

**Port 8501 already in use:**
```bash
# Find and kill process
kill -9 $(lsof -ti:8501)
```

---

## Additional Resources

- 📖 [README.md](README.md) - Full documentation
- 🐳 [DOCKER.md](DOCKER.md) - Production deployment guide
- 📋 [plan.md](plan.md) - Development roadmap
- 🚀 [RENDER_DEPLOY.md](RENDER_DEPLOY.md) - Deploy to Render.com

