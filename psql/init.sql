-- Creation of databases
CREATE DATABASE IF NOT EXISTS keycloak;
CREATE DATABASE IF NOT EXISTS praxis_db;

-- Creation of users
CREATE USER IF NOT EXISTS keycloak WITH PASSWORD 'keycloak';
CREATE USER IF NOT EXISTS praxis WITH PASSWORD 'praxis';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
GRANT ALL PRIVILEGES ON DATABASE praxis_db TO praxis;