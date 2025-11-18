# Sample Data Files

This directory contains sample data files for testing the ICP Analysis Dashboard.

## Database Data

### `mock_signups.sql`

SQL script to create and populate a PostgreSQL database with sample user signup data.

**To use:**
```bash
psql -U postgres -d render_data -f data/mock_signups.sql
```

**Contains:**
- `user_signups` table schema
- 15 mock user records
- Various industries: SaaS, Technology, E-commerce, Finance, Healthcare, etc.
- Company sizes from startups to enterprises
- Revenue ranges and use cases
- Metadata in JSONB format

## CSV Data

### `customer_data.csv` (RECOMMENDED)

Comprehensive customer data with social media profiles and marketing campaign information.

**Columns:**
- `Webhook` - Webhook identifier (usually empty)
- `Full Name` - Customer's full name
- `Email` - Email address
- `LinkedIn Profile` - LinkedIn profile URL
- `Company` - Company name
- `Title` - Job title (e.g., VP of Engineering, CTO, Head of Product)
- `City` - Location/city
- `X Username` - Twitter/X handle (e.g., @username)
- `X Followers Count` - Number of Twitter/X followers
- `X Description` - Twitter/X bio description
- `LinkedIn Followers Count` - Number of LinkedIn followers
- `Push to Zapier Marketing Flow` - Yes/No flag for automation
- `Top Social Platform` - Primary social platform (LinkedIn or X)
- `Marketing Campaign` - Campaign name (e.g., Enterprise_2024, AI_Campaign)

**Sample use cases:**
- ICP analysis with social media presence
- Influencer identification (follower counts)
- Marketing campaign effectiveness
- Social platform preference analysis
- Contact enrichment workflows

**Contains:**
- 20 mock customer records
- Mix of senior technical roles (VP, CTO, Director, Head of)
- Tech-focused companies
- Various cities across the US
- Social media metrics and preferences

## Usage in the App

1. **Start the Streamlit app:**
   ```bash
   streamlit run main.py
   ```

2. **Load database data:**
   - Configure database connection in sidebar
   - Select `user_signups` table
   - View preview and metrics

3. **Upload CSV data:**
   - Navigate to "Data Sources" tab
   - Click "Browse files" or drag & drop
   - Use `customer_data.csv` for contact/social analysis

4. **Compare datasets:**
   - Review side-by-side comparison
   - Check for common columns
   - Proceed to analysis

## Creating Your Own Data

### For Database
Follow the schema in `mock_signups.sql`:
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

### For CSV
Either format works. Key recommendations:
- Include email addresses for matching
- Add company names for identification
- Include industry/sector for segmentation
- Add any fields relevant to your ICP criteria

## Notes

- All data in these files is completely fictional
- Names, emails, and companies are mock data
- Social media profiles are not real
- Use this data for testing and development only
- Replace with your actual data when ready for production

