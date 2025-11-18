-- Sample SQL script to create user_signups table and populate with mock data
-- Run this script to set up your test database

-- Create the user_signups table
CREATE TABLE IF NOT EXISTS user_signups (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    role VARCHAR(100),
    signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    use_case TEXT,
    revenue_range VARCHAR(50),
    location VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data (skip if already exists based on email)
INSERT INTO user_signups (full_name, email, company_name, industry, company_size, role, use_case, revenue_range, location, metadata) VALUES
('Sarah Mitchell', 'sarah.mitchell@techcorp.io', 'TechFlow Solutions', 'Technology', '200-1000', 'VP of Engineering', 'Building scalable cloud infrastructure for our growing platform', '$10M-$50M', 'San Francisco Bay Area', '{"trial_plan": "enterprise", "signup_source": "website"}'),
('Michael Chen', 'michael.chen@datastream.com', 'DataStream Analytics', 'Technology', '200-1000', 'CTO', 'Need a data platform for customer analytics and insights', '$10M-$50M', 'New York City', '{"trial_plan": "enterprise", "signup_source": "website"}'),
('Emily Rodriguez', 'emily.r@innovateai.co', 'InnovateAI Labs', 'Artificial Intelligence', '50-200', 'Head of Product', 'Looking for tools to help manage our AI/ML product development', '$10M-$50M', 'Austin', '{"trial_plan": "professional", "signup_source": "product_hunt"}'),
('James Wilson', 'jwilson@cloudscale.io', 'CloudScale Systems', 'Technology', '200-1000', 'VP Engineering', 'Cloud infrastructure automation and optimization', '$10M-$50M', 'Seattle', '{"trial_plan": "enterprise", "signup_source": "referral"}'),
('Alexandra Kim', 'alex.kim@fintech.ventures', 'FinTech Ventures', 'Finance', '200-1000', 'Chief Technology Officer', 'Building the future of financial services technology', '$50M+', 'Boston', '{"trial_plan": "enterprise", "signup_source": "conference"}'),
('David Park', 'dpark@saasbuilder.com', 'SaaS Builder Co', 'SaaS', '50-200', 'Director of Engineering', 'Need better workflow automation for our SaaS product', '$1M-$10M', 'Denver', '{"trial_plan": "professional", "signup_source": "linkedin"}'),
('Rachel Thompson', 'rachel.t@platformio.com', 'Platform.io', 'Technology', '50-200', 'VP of Product', 'Platform engineering and developer experience improvements', '$10M-$50M', 'Remote - Portland', '{"trial_plan": "professional", "signup_source": "website"}'),
('Christopher Lee', 'chris.lee@devtools.dev', 'DevTools Inc', 'Technology', '200-1000', 'Head of Engineering', 'Improving developer experience for our tooling platform', '$10M-$50M', 'San Francisco', '{"trial_plan": "enterprise", "signup_source": "product_hunt"}'),
('Jessica Martinez', 'jmartinez@analytica.ai', 'Analytica AI', 'Artificial Intelligence', '200-1000', 'Chief Data Officer', 'Turning data into actionable business insights', '$10M-$50M', 'Chicago', '{"trial_plan": "professional", "signup_source": "referral"}'),
('Robert Taylor', 'rtaylor@infrastructure.cloud', 'Infrastructure Cloud', 'Technology', '200-1000', 'VP Engineering', 'Infrastructure at scale - need automation and monitoring', '$10M-$50M', 'Remote - Austin', '{"trial_plan": "enterprise", "signup_source": "website"}'),
('Amanda Foster', 'amanda.f@securetech.io', 'SecureTech Solutions', 'Technology', '200-1000', 'Head of Security Engineering', 'Security-first development and compliance automation', '$10M-$50M', 'New York', '{"trial_plan": "professional", "signup_source": "website"}'),
('Daniel Garcia', 'daniel.garcia@apibuilder.com', 'API Builder Labs', 'Technology', '50-200', 'CTO', 'API design, architecture, and developer tools', '$10M-$50M', 'Los Angeles', '{"trial_plan": "professional", "signup_source": "linkedin"}'),
('Nicole Adams', 'nadams@mlplatform.ai', 'ML Platform Inc', 'Artificial Intelligence', '200-1000', 'VP of Engineering', 'MLOps and AI infrastructure automation', '$10M-$50M', 'Seattle', '{"trial_plan": "enterprise", "signup_source": "product_hunt"}'),
('Kevin Zhang', 'kzhang@microservices.tech', 'Microservices Tech', 'Technology', '50-200', 'Director of Architecture', 'Microservices architecture and orchestration', '$1M-$10M', 'San Diego', '{"trial_plan": "professional", "signup_source": "website"}'),
('Laura Bennett', 'laura.b@automationco.io', 'Automation Co', 'Technology', '50-200', 'Head of Engineering', 'Business process automation and efficiency tools', '$10M-$50M', 'Remote - Miami', '{"trial_plan": "professional", "signup_source": "linkedin"}'),
('Thomas Wright', 'twright@realtimedata.com', 'RealTime Data Systems', 'Technology', '200-1000', 'VP Engineering', 'Real-time data processing and streaming analytics', '$10M-$50M', 'Boston', '{"trial_plan": "professional", "signup_source": "referral"}'),
('Sophia Johnson', 'sophia.j@observability.io', 'Observability.io', 'Technology', '200-1000', 'Chief Product Officer', 'Making distributed systems more observable and debuggable', '$50M+', 'San Francisco', '{"trial_plan": "enterprise", "signup_source": "website"}'),
('Andrew Miller', 'amiller@containertech.com', 'Container Tech', 'Technology', '200-1000', 'VP of Engineering', 'Kubernetes orchestration and container management', '$10M-$50M', 'Remote - Denver', '{"trial_plan": "enterprise", "signup_source": "website"}'),
('Olivia Davis', 'olivia.davis@eventstream.io', 'EventStream Systems', 'Technology', '50-200', 'Director of Engineering', 'Event-driven architecture and messaging systems', '$10M-$50M', 'Seattle', '{"trial_plan": "professional", "signup_source": "website"}'),
('Marcus Robinson', 'mrobinson@performanceai.com', 'Performance AI', 'Artificial Intelligence', '200-1000', 'Head of Infrastructure', 'Performance optimization for AI/ML workloads', '$10M-$50M', 'Austin', '{"trial_plan": "professional", "signup_source": "referral"}')
ON CONFLICT (email) DO NOTHING;

-- Create indexes for better query performance (skip if already exist)
CREATE INDEX IF NOT EXISTS idx_user_signups_industry ON user_signups(industry);
CREATE INDEX IF NOT EXISTS idx_user_signups_company_size ON user_signups(company_size);
CREATE INDEX IF NOT EXISTS idx_user_signups_signup_date ON user_signups(signup_date);
CREATE INDEX IF NOT EXISTS idx_user_signups_revenue_range ON user_signups(revenue_range);
CREATE INDEX IF NOT EXISTS idx_user_signups_role ON user_signups(role);

-- Verify the data
SELECT COUNT(*) as total_signups FROM user_signups;
SELECT industry, COUNT(*) as count FROM user_signups GROUP BY industry ORDER BY count DESC;
SELECT company_size, COUNT(*) as count FROM user_signups GROUP BY company_size ORDER BY count DESC;
SELECT revenue_range, COUNT(*) as count FROM user_signups GROUP BY revenue_range ORDER BY count DESC;

