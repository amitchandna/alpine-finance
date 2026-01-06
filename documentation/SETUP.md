# Alpine Finance - Setup Guide

This guide will help you set up and run the Alpine Finance RAG system.

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher
- PostgreSQL 15+ with pgvector extension
- Ollama (for local LLM inference)
- Git
- Docker and Docker Compose (optional, for containerized deployment)

## Option 1: Local Development Setup

### Step 1: Install System Dependencies

#### macOS
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install pgvector
brew install pgvector

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql-15 postgresql-contrib

# Install pgvector (compile from source)
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Setup Database

```bash
# Create database
createdb alfin_lakes

# Enable pgvector extension
psql alfin_lakes -c "CREATE EXTENSION vector;"

# Verify
psql alfin_lakes -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Step 3: Setup Python Environment

```bash
# Navigate to project
cd alpine-finance/django_project

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp ../.env.example .env

# Edit .env with your settings
nano .env
```

### Step 5: Run Migrations

```bash
# Run Django migrations
python manage.py migrate

# Verify tables
python manage.py dbshell
\dt
\q
```

### Step 6: Start Ollama

```bash
# Start Ollama service (in separate terminal)
ollama serve

# Pull a model
ollama pull tinyllama

# Test it
ollama run tinyllama
```

### Step 7: Process Your Data

**Note**: You need to have your 10-K data in the `raw_ten_k_data` table first.

```bash
# Chunk filings (creates text chunks)
python manage.py chunk_filings --size small_384 --limit 100

# Generate embeddings (creates vector embeddings)
python manage.py generate_embeddings --size small_384 --batch-size 32

# Check progress
python manage.py dbshell
SELECT COUNT(*) FROM rag_chunks_small;
SELECT COUNT(*) FROM rag_chunks_small WHERE embedding_384 IS NOT NULL;
\q
```

### Step 8: Start API

```bash
# Start FastAPI server
uvicorn upper_lake.api.main:app --reload

# Or using Python directly
python -m uvicorn upper_lake.api.main:app --reload
```

### Step 9: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main business risks?",
    "ticker": "AAPL",
    "year": 2023
  }'
```

### Step 10: Interactive Chat (Optional)

```bash
# Start interactive chat
python manage.py chat

# With filters
python manage.py chat --ticker AAPL --year 2023

# With different model
python manage.py chat --model phi3:mini
```

## Option 2: Docker Setup

### Step 1: Start All Services

```bash
cd alpine-finance

# Start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop when done
docker-compose down
```

### Step 2: Run Commands in Container

```bash
# Access API container
docker-compose exec api bash

# Inside container, run commands
python manage.py chunk_filings --size small_384 --limit 100
python manage.py generate_embeddings --size small_384
```

### Step 3: Pull Ollama Model

```bash
# Access Ollama container
docker-compose exec ollama bash

# Pull model
ollama pull tinyllama
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection
psql -h localhost -U amit_chandna -d alfin_lakes -c "SELECT 1"

# Restart PostgreSQL
brew services restart postgresql@15  # macOS
sudo systemctl restart postgresql    # Linux
```

### Ollama Not Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Check models
ollama list
```

### pgvector Extension Missing

```bash
# Check if installed
psql alfin_lakes -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Install if missing
psql alfin_lakes -c "CREATE EXTENSION vector;"
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify Django can be imported
python -c "import django; print(django.get_version())"
```

### Memory Issues with Ollama

```bash
# Use smaller model
ollama pull qwen2.5:1.5b

# Update .env
OLLAMA_MODEL=qwen2.5:1.5b
```

## Next Steps

1. **Load Your Data**: Ensure your 10-K data is in `raw_ten_k_data` table
2. **Chunk and Embed**: Process all your filings
3. **Test Queries**: Try different questions and filters
4. **Deploy**: Consider deploying to cloud (AWS, GCP, etc.)

## Additional Resources

- [Full Documentation](ALPINE_FINANCE_PROJECT_RECONSTRUCTION.md)
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector)
- [Ollama Documentation](https://ollama.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Django Documentation](https://docs.djangoproject.com/)

## Support

For issues or questions:
- Check the full documentation
- Review error logs
- Verify all services are running
- Test individual components

## License

MIT
