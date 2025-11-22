# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GAAS (Gami As A Service) is a sports analytics system designed to automatically detect rare statistical performances across multiple sports leagues. The system is planned to monitor NFL, NBA, MLB, F1, Champions League, and NHL games 24/7, compute rarity scores, and publish results via a web interface and GitHub repository.

**Current Status**: Project planning phase - only the PRD document exists

## Development Commands

This project is currently in planning phase with no implemented code yet. When implementation begins, the following commands will be essential:

### Environment Setup
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database structure
python scripts/init_databases.py
```

### Development
```bash
# Run main application
python src/gaas.py

# Run web server
python src/web/app.py

# Run tests
pytest tests/

# Code formatting and linting
ruff check src/
black src/
```

### Data Management
```bash
# Download historical data
python scripts/download_nfl_data.py
python scripts/download_nba_data.py
# ... etc for other sports

# Load archive databases
python scripts/load_nfl_archive.py
python scripts/load_nba_archive.py
# ... etc

# Database maintenance
sqlite3 data/archive/*.db "VACUUM;"
```

### Deployment
```bash
# SystemD service management
sudo systemctl enable gaas gaas-web
sudo systemctl start gaas gaas-web
sudo systemctl status gaas gaas-web

# View logs
sudo journalctl -u gaas -f
tail -f logs/gaas.log
```

## Architecture Overview

### Core Components

**Data Collection Layer** (`src/collectors/`)
- Sport-specific collectors that fetch current season data
- NFLCollector, NBACollector, MLBCollector, F1Collector, UCLCollector, NHLCollector
- Each collector handles data fetching, transformation, and storage

**Processing Layer** (`src/processors/`)
- `RarityEngine`: Core algorithm that computes how statistically rare a performance is
- Uses historical data + current season data to calculate occurrence counts
- Applies bucketing strategy for different stat categories

**Generation Layer** (`src/generators/`)
- `JSONGenerator`: Creates JSON output files for web consumption
- `MarkdownGenerator`: Creates human-readable reports
- Generates both "latest" (7 days) and "all_time" perspectives

**Web Layer** (`src/web/`)
- FastAPI-based web server with Tailscale HTTPS
- Jinja2 templates for displaying rare performances
- Static CSS/JS for responsive UI

**Utilities** (`src/utils/`)
- `GitPusher`: Automated result publishing to GitHub
- Database helpers and common utilities

### Data Architecture

**Historical Archive Databases** (read-only, ~10GB total)
- SQLite databases for each sport spanning decades
- `nfl_archive.db`: NFL data 1999-2024 via nflfastR
- `nba_archive.db`: NBA data 2010-2024 via nba_api
- `mlb_archive.db`: MLB data 1871-2024 via Retrosheet
- `f1_archive.db`: F1 data 1950-2024 via fastf1
- `ucl_archive.db`: Champions League 2016-2022 via Kaggle
- `nhl_archive.db`: NHL data 2008-2024 via MoneyPuck

**Current Season Databases** (read-write, updated frequently)
- Separate SQLite DBs for each sport's current season
- Updated every 5-30 minutes during game windows
- Merged into archives annually

### Stat Bucketing Strategy

Each sport position uses specific statistical bucketing to determine similarity:

**NFL RB Example:**
- Rush yards: 0-49, 50-99, 100-149, 150-199, 200+
- Rush TDs: 0, 1, 2, 3, 4+
- Fumbles: 0, 1, 2+

**Rarity Classification:**
- `never_before`: Occurred exactly once in history
- `extremely_rare`: 2-5 occurrences
- `very_rare`: 6-10 occurrences
- `rare`: 11-25 occurrences
- `common`: 26+ occurrences

### Scheduling and Automation

**Game Window Detection:**
- Each sport has specific game windows (e.g., NFL: Thu/Mon evenings, Sun all day)
- System polls frequently during active windows (5 min)
- Polls slowly outside windows (2 hours)

**Automated Pipeline:**
1. Collector fetches new games
2. RarityEngine computes rarity for interesting performances
3. Generator creates JSON/MD outputs
4. GitPusher publishes results to GitHub
5. Web UI displays latest results

## Data Sources and Dependencies

### Python Packages
```python
# Data sources
nfl-data-py>=0.3.0      # NFL play-by-play data
nba-api>=1.4.0          # NBA API access
fastf1>=3.3.0           # F1 historical and live data
pybaseball>=2.2.7       # MLB Retrosheet data

# Core processing
pandas>=2.1.0           # Data manipulation
numpy>=1.26.0           # Numerical operations
sqlite3                 # Database (built-in)

# Web framework
fastapi>=0.104.0        # API framework
uvicorn[standard]>=0.24.0 # ASGI server
jinja2>=3.1.0           # Template engine

# Utilities
httpx>=0.25.0           # HTTP client
schedule>=1.2.0         # Task scheduling
gitpython>=3.1.40       # Git automation
loguru>=0.7.0           # Logging
```

### External Data Sources
- **NFL**: nflfastR GitHub releases (~5GB, 1999-2024)
- **NBA**: Kaggle datasets + nba_api (~2GB, 2010-2024)
- **MLB**: Retrosheet game logs (~632MB, 1871-2024)
- **F1**: Kaggle + fastf1 (~500MB, 1950-2024)
- **UCL**: Kaggle (~100MB, 2016-2022)
- **NHL**: MoneyPuck (~1GB, 2008-2024, free with attribution)

## Development Workflow

### Adding New Sports
1. Create sport-specific collector in `src/collectors/`
2. Define appropriate stat buckets using expert knowledge
3. Implement data loading script in `scripts/`
4. Add routes to web UI
5. Update main orchestrator in `src/gaas.py`
6. Add tests in `tests/`

### Testing Strategy
- Unit tests for each component (`tests/test_*.py`)
- Integration tests for end-to-end pipelines
- 48-hour stability tests for deployment validation
- Use pytest with async support for FastAPI testing

### Code Quality
- Use ruff for linting and formatting
- Black for code style consistency
- Type hints where applicable
- Comprehensive logging with loguru
- Error handling for external API failures

## Deployment Architecture

### Production Environment
- **Platform**: Oracle Cloud Free Tier (4 ARM cores, 24GB RAM, 200GB storage)
- **OS**: Ubuntu 22.04/24.04
- **Networking**: Tailscale for HTTPS and private access
- **Process Management**: SystemD services for 24/7 operation

### Services
- `gaas.service`: Main data collection and processing pipeline
- `gaas-web.service`: FastAPI web server
- Both services configured with auto-restart and proper logging

### Monitoring
- Application logs via loguru to `logs/gaas.log`
- SystemD service logs via journalctl
- Git commit history shows all published results
- Web UI provides real-time status

## Important Implementation Notes

### Performance Considerations
- SQLite databases use indexes on bucketed columns for fast queries
- Historical archive databases are read-only for integrity
- Current season databases use efficient append-only operations
- Memory usage optimized through streaming large datasets

### Reliability Features
- Automatic retry for external API failures
- Graceful handling of missing or corrupted data
- Database transaction integrity
- Git operations use rebase to avoid conflicts

### Security Practices
- No API keys or secrets committed to repository
- Tailscale provides secure HTTPS without certificates
- Database access limited to application user
- Input validation for all external data

## Project Status and Next Steps

This project is currently in the planning phase with only the comprehensive PRD document existing. The next steps for implementation would be:

1. **Phase 0**: Environment setup and dependency installation
2. **Phase 1**: NFL RB proof of concept (end-to-end pipeline)
3. **Phase 2-7**: Expand to all sports positions
4. **Phase 8**: Integration and orchestration
5. **Phase 9**: Deployment and automation
6. **Phase 10**: Comprehensive testing
7. **Phase 11**: Documentation and public release

The PRD contains detailed implementation guidance including exact file structures, code patterns, and execution commands for each phase.