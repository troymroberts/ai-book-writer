# Development and Publishing Guide

## Prerequisites
- Node.js 18+
- npm 9+
- Docker 20.10+
- Docker Compose 2.0+

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/context-optimizer.git
cd context-optimizer
```

2. Install dependencies:
```bash
npm install
```

## Configuration
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration values

## Running the Monitoring Stack
1. Start the monitoring services:
```bash
cd monitoring
docker-compose up -d
```

2. Verify services are running:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Testing Pipeline

The project includes a comprehensive testing pipeline that runs:

1. Unit tests
2. Integration tests
3. Monitoring tests

### Key Features:
- Parallel test execution
- Code coverage reporting
- Test result artifacts
- Codecov integration

### Running Tests Locally

1. Install test dependencies:
```bash
pip install -r requirements.txt
pip install pytest-cov pytest-xdist
```

2. Run all tests with coverage:
```bash
pytest tests/ --cov=./ --cov-report=html
```

3. View coverage report:
```bash
open htmlcov/index.html
```

4. Run specific test types:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Monitoring tests
pytest tests/monitoring/
```

### CI/CD Integration
- Tests run automatically on push/pull requests
- Coverage reports uploaded to Codecov
- Test results stored as artifacts

## CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically:

1. Runs tests on push/pull requests to main branch
2. Builds the package
3. Publishes to npm when a version tag is pushed (v*)

To use the pipeline:

1. Push your code to GitHub
2. Create a pull request to trigger tests
3. To publish:
   - Update package.json version
   - Create a version tag:
     ```bash
     git tag v1.0.0
     git push origin v1.0.0
     ```
   - The workflow will automatically publish to npm

## Publishing to npm (Manual)
1. Update package.json with your package details
2. Build the project:
```bash
npm run build
```

3. Publish to npm:
```bash
npm publish
```

## Maintenance
- To stop the monitoring stack:
```bash
docker-compose down
```

- To update dependencies:
```bash
npm update
```

## Troubleshooting
- If tests fail, ensure the monitoring stack is running
- Check logs with:
```bash
docker-compose logs -f
```
