# Plant Intelligence Platform - AI Service

FastAPI-based AI microservice for plant science research.

## Features

- Research Chat - Scientific Q&A with literature retrieval
- Gene Recommendations - Evidence-based candidate gene suggestions
- Experiment Design - Rigorous experimental protocol generation
- Literature Search - PubMed-powered paper discovery
- Paper Summarization - Automated literature synthesis
- Image Analysis - Disease detection, phenotype measurement
- Knowledge Graph - Entity relationships and inference

## Development

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8001
```

## Docker

```bash
docker build -t pip-ai-service .
docker run -p 8001:8001 pip-ai-service
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## License

MIT
