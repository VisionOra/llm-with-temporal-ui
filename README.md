# Temporal LLM Web App

A comprehensive web application that integrates **Temporal** for workflow orchestration and **LLM providers** (OpenAI) for text processing. This application demonstrates backend orchestration, frontend integration, and infrastructure management in a single, production-ready solution.

## 🚀 Features

- **Temporal Workflow Integration**: String reversal via distributed workflows
- **LLM Processing**: Text summarization, rephrasing, and analysis using OpenAI GPT-4
- **Modern Web UI**: Responsive, intuitive interface with real-time status updates
- **Health Monitoring**: Live system status indicators and error handling
- **Docker Deployment**: Complete containerized setup with Docker Compose
- **Production Ready**: Proper logging, error handling, and security practices

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Temporal      │
│   (HTML/CSS/JS) │◄──►│   Backend       │◄──►│   Workflows     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI        │
                       │   LLM Service   │
                       └─────────────────┘
```

### Components

- **Frontend**: Modern HTML/CSS/JavaScript with responsive design
- **Backend**: FastAPI async web framework
- **Temporal Server**: Workflow orchestration and state management
- **Temporal Worker**: Background workflow and activity execution
- **LLM Service**: OpenAI integration for text processing
- **Database**: PostgreSQL for Temporal persistence
- **Search**: Elasticsearch for Temporal visibility

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- OpenAI API key
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd temporal-llm-web-app
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your OpenAI API key
nano .env
```

**Required**: Set your OpenAI API key in the `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Web Application**: http://localhost:8001
- **Temporal Web UI**: http://localhost:8080
- **API Documentation**: http://localhost:8001/docs

## 🛠️ Local Development

### Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Start Temporal Server (Local)

Option 1: Using Docker
```bash
docker-compose up temporal postgresql elasticsearch -d
```

Option 2: Using Temporal CLI
```bash
temporal server start-dev
```

### Run Application Services

```bash
# Terminal 1: Start the worker
cd backend
python worker.py

# Terminal 2: Start the web app
cd backend
python main.py
```

### Frontend Development

The frontend files are in the `frontend/` directory. For local development:
- Modify HTML, CSS, or JavaScript files
- The FastAPI app serves static files automatically
- Refresh browser to see changes

## 📊 Usage Examples

### 1. String Reversal (Temporal Workflow)

1. Enter text in the input field
2. Click "Reverse String (Temporal)"
3. View the workflow execution results

### 2. LLM Text Processing

1. Enter text in the input field
2. Choose an operation:
   - **Summarize**: Get a concise summary
   - **Rephrase**: Rewrite in different words
   - **Analyze**: Sentiment and theme analysis
3. View the LLM processing results

## 🧪 Testing

### Run Tests

```bash
cd backend
pytest
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
```

### API Testing

```bash
# Health check
curl http://localhost:8001/api/health

# Test string reversal
curl -X POST http://localhost:8001/api/reverse \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'

# Test LLM operation
curl -X POST http://localhost:8001/api/llm \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test", "operation": "summarize"}'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TEMPORAL_HOST` | Temporal server address | `localhost:7233` |
| `TEMPORAL_NAMESPACE` | Temporal namespace | `default` |
| `TEMPORAL_TASK_QUEUE` | Task queue name | `reverse-string-task-queue` |
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4-turbo-preview` |

### Temporal Configuration

The application uses these Temporal settings:
- **Namespace**: `default`
- **Task Queue**: `reverse-string-task-queue`
- **Workflow ID**: Auto-generated with prefix `reverse-string-`
- **Retry Policy**: 3 attempts with exponential backoff

### LLM Configuration

Supported operations:
- `summarize`: Generate concise summaries
- `rephrase`: Rewrite maintaining meaning
- `analyze`: Sentiment and theme analysis
- `questions`: Generate insightful questions
- `expand`: Add relevant details

## 🚧 Production Deployment

### Docker Production Setup

1. **Update Environment Variables**:
   ```bash
   cp env.example .env.prod
   # Edit .env.prod with production values
   ```

2. **Build and Deploy**:
   ```bash
   # Build images
   docker-compose build

   # Deploy with production config
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Configure Reverse Proxy** (Nginx/Traefik):
   ```nginx
   location / {
       proxy_pass http://localhost:8001;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

### Scaling Workers

```bash
# Scale worker replicas
docker-compose up -d --scale worker=4
```

### Monitoring

- **Health Endpoints**: `/api/health`
- **Temporal Web UI**: Monitor workflows and activities
- **Application Logs**: `docker-compose logs -f`

## 🔒 Security Considerations

- API keys stored as environment variables
- CORS configured for specific origins
- Input validation and sanitization
- Non-root containers
- Health checks for service monitoring

## 🐛 Troubleshooting

### Common Issues

1. **Temporal Connection Failed**
   ```bash
   # Check Temporal server status
   docker-compose logs temporal
   
   # Restart Temporal services
   docker-compose restart temporal postgresql elasticsearch
   ```

2. **OpenAI API Errors**
   - Verify API key is correct
   - Check API quota and billing
   - Review rate limiting

3. **Worker Not Processing**
   ```bash
   # Check worker logs
   docker-compose logs worker
   
   # Restart worker
   docker-compose restart worker
   ```

### Debug Mode

```bash
# Enable debug logging
export APP_DEBUG=true
export APP_LOG_LEVEL=debug

# Run with detailed logs
python main.py
```

## 📚 API Documentation

### Endpoints

- `GET /` - Main application page
- `POST /api/reverse` - Trigger string reversal workflow
- `POST /api/llm` - Process text with LLM
- `GET /api/health` - System health check
- `GET /docs` - Interactive API documentation

### WebSocket Support (Future Enhancement)

Real-time workflow status updates via WebSocket connections.

## 🧪 Testing Strategy

### Unit Tests
- Workflow logic testing
- Activity testing
- LLM service testing
- API endpoint testing

### Integration Tests
- End-to-end workflow execution
- LLM integration testing
- Health check validation

### Load Tests
- Workflow throughput testing
- Concurrent request handling
- System resource monitoring

## 🔄 Development Workflow

1. **Feature Development**
   - Create feature branch
   - Implement changes
   - Add tests
   - Update documentation

2. **Testing**
   - Run unit tests
   - Test locally with Docker
   - Validate integration

3. **Deployment**
   - Push to repository
   - CI/CD pipeline
   - Production deployment

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Review existing documentation
- Check Temporal and OpenAI documentation

---

**Built with**: FastAPI, Temporal, OpenAI, Docker, HTML/CSS/JavaScript 