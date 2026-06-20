-- 1. admin_users table
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. chat_history table
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    content TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. faculty_schedule table
CREATE TABLE faculty_schedule (
    id SERIAL PRIMARY KEY,
    faculty_name VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    day_of_week VARCHAR(50),
    start_time TIME,
    end_time TIME,
    room_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. session_memory table
CREATE TABLE session_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    memory_key VARCHAR(255),
    memory_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE documents
ADD COLUMN document_name TEXT;
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,

    title TEXT,
    category TEXT,
    summary TEXT,

    start_date TEXT,
    last_date TEXT,

    eligibility TEXT,

    required_documents TEXT[],

    source_url TEXT UNIQUE,

    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE processed_documents (
    id SERIAL PRIMARY KEY,

    source_url TEXT UNIQUE,

    processed_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE admission_tables
(
    id SERIAL PRIMARY KEY,

    title TEXT,

    table_data JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE admission_updates (
    id SERIAL PRIMARY KEY,
    title TEXT,
    published_date TIMESTAMP,
    pdf_url TEXT UNIQUE,
    summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    title TEXT,
    pdf_url TEXT UNIQUE,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE scholarships (
    id SERIAL PRIMARY KEY,
    title TEXT,
    pdf_url TEXT UNIQUE,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE notices (
    id SERIAL PRIMARY KEY,
    title TEXT,
    pdf_url TEXT UNIQUE,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title TEXT,
    event_date TEXT,
    pdf_url TEXT UNIQUE,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);