# AI-Based Natural Language Database Interaction System

A full-stack application that enables users to interact with a PostgreSQL database using natural-language questions.

The system converts user questions into SQL queries using an AI model, validates the generated queries, executes approved read-only queries, and presents the results through a React interface.

## Key Features

- Natural-language database querying
- AI-assisted PostgreSQL query generation
- SQL validation before execution
- Read-only query execution
- Automatic result limits
- Structured query results with execution time
- Schema-aware query generation

## Technology Stack

**Frontend**
- React
- Vite
- JavaScript
- CSS

**Backend**
- FastAPI
- Python
- SQLAlchemy
- asyncpg
- SQLGlot

**Database and Infrastructure**
- PostgreSQL
- Docker Compose

## How It Works

1. The user enters a question in natural language.
2. The backend retrieves relevant database schema information.
3. The AI model generates a SQL query.
4. The SQL validator checks whether the query is permitted.
5. Approved queries are executed against PostgreSQL.
6. The frontend displays the SQL query and its results.

## Security Considerations

AI-generated SQL must be validated before execution. Read-only database permissions, query timeouts, result limits, and appropriate secret management are important safeguards.

This project is intended for development and demonstration. Production deployment requires additional security testing and access controls.

## Project Status

Development and testing in progress.

## Author

**Afreen**

## Project Overview

AI-Based Natural Language Database Interaction System — a full-stack application for querying PostgreSQL databases using natural language.