# GAAS - Gami As A Service

![GAAS Logo](https://img.shields.io/badge/GAAS-Sports%20Analytics-blue?style=for-the-badge)
![License](https://img.shields.io/github/license/Khamel83/gaas?style=for-the-badge)
![Live Site](https://img.shields.io/badge/Live%20Site-gaas.zoheri.com-green?style=for-the-badge)

**GAAS (Gami As A Service)** is an automated sports analytics system that identifies statistically rare performances across multiple professional sports leagues. Our algorithm continuously monitors games and calculates rarity scores based on historical data.

## 🌐 Live Demo

**[https://gaas.zoheri.com](https://gaas.zoheri.com)**

## 📊 Current Coverage

### ✅ **Live (NFL)**
- **Quarterbacks** - Passing yards, touchdowns, completion rates
- **Running Backs** - Rushing yards, touchdowns, efficiency metrics
- **Wide Receivers** - Receptions, yards, targets, touchdowns
- **Tight Ends** - Receiving statistics and blocking metrics

### 🚧 **In Development**
- **NBA** - Points, rebounds, assists, advanced metrics (data collected)
- **MLB** - Pitching, hitting, fielding statistics (data collected)
- **F1** - Race times, qualifying positions, pit stop performance (data collected)
- **Champions League** - Goals, assists, defensive actions (data collected)
- **NHL** - Goals, assists, plus/minus, goalie stats (data collected)

## 🎯 What Makes GAAS Unique

### Statistical Rigor
- **Historical Context**: Each performance is compared against decades of historical data
- **Rarity Classification**:
  - `never_before`: Occurred exactly once in history
  - `extremely_rare`: 2-5 occurrences
  - `very_rare`: 6-10 occurrences
  - `rare`: 11-25 occurrences
- **Confidence Scores**: Probability-based rarity calculations

### Real-Time Processing
- **Automated Collection**: Data gathered continuously during game windows
- **Instant Analysis**: Rare performances identified within minutes of game completion
- **Historical Comparison**: Cross-referenced with comprehensive archives

### Expert-Driven Bucketing
- **Position-Specific Metrics**: Tailored statistical buckets for each position
- **Context-Aware**: Accounts for era differences, rule changes, and strategic evolution
- **Similarity Algorithms**: Groups performances by statistical patterns, not just raw numbers

## 🏗️ Architecture

### Data Sources
```
📊 Historical Archives (10GB+)
├── NFL: 1999-2024 via nflfastR
├── NBA: 2010-2024 via nba_api
├── MLB: 1871-2024 via Retrosheet
├── F1: 1950-2024 via fastf1
├── Champions League: 2016-2022 via Kaggle
└── NHL: 2008-2024 via MoneyPuck

🔄 Real-Time Feeds
└── Current season data (updated 5-30 min during games)
```

### Processing Pipeline
```
📥 Data Collection → 🔍 Rarity Engine → 📱 Web Interface
     ↓                    ↓                     ↓
API Polling         Historical Query        JSON/HTML Output
Data Validation     Bucket Analysis         GitHub Publishing
Error Handling      Score Calculation       Real-Time Updates
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- SQLite 3
- Git
- GitHub account (for deployment)

### Installation
```bash
# Clone the repository
git clone https://github.com/Khamel83/gaas.git
cd gaas

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize databases
python scripts/init_databases.py

# Run analysis
python src/gaas.py
```

### Configuration
```bash
# Environment variables
export GITHUB_TOKEN="your_github_token"
export ATLAS_DB_PATH="data/atlas.db"
export ATLAS_PROJECT_DIR="/path/to/gaas"
```

## 📱 Web Interface

### Local Development
```bash
# Start web server
python src/web/app.py

# Access at http://localhost:8000
```

### Production Deployment
- **GitHub Pages**: Automatic deployment via GitHub Actions
- **Custom Domain**: Configured with HTTPS enforcement
- **CDN**: Global distribution for fast loading

## 📈 Sample Output

### Recent NFL Rare Performances
```
🏈 Saquon Barkley (PHI) - Week 20
   📊 205 rush yards, 2 TDs
   🎯 Rarity Score: 99.77
   📈 Historical Occurrences: 11/9,742 games
   ⏰ First: Todd Gurley (2018)
```

## 🛠️ Development

### Project Structure
```
gaas/
├── src/
│   ├── collectors/      # Sport-specific data collectors
│   ├── processors/      # Rarity analysis algorithms
│   ├── generators/      # Output format generators
│   ├── web/            # FastAPI web application
│   └── utils/          # Shared utilities
├── data/               # Database files
├── scripts/            # Data loading and maintenance
├── tests/              # Test suite
└── docs/               # Documentation
```

### Adding New Sports
1. **Create Collector**: `src/collectors/sport_collector.py`
2. **Define Buckets**: Position-specific statistical groupings
3. **Write Tests**: `tests/test_sport_collector.py`
4. **Update Web**: Add routes and templates
5. **Deploy**: Automatic via GitHub Actions

### Code Quality
```bash
# Linting and formatting
ruff check src/
black src/

# Testing
pytest tests/ --cov=src/

# Type checking
mypy src/
```

## 📊 Data Validity & Quality

### Validation Process
- **Source Verification**: Multiple data source cross-referencing
- **Outlier Detection**: Statistical anomaly identification
- **Historical Consistency**: Era-adjusted comparisons
- **Manual Review**: Expert validation for edge cases

### Known Limitations
- **Historical Gaps**: Some older data may be incomplete
- **Rule Changes**: Statistical definitions evolve over time
- **Sample Size**: Rare events by definition have limited data points

### Quality Assurance
- Continuous data validation pipeline
- Automated anomaly detection
- Regular historical data audits
- Expert review for significant findings

## 🔧 Operations

### Monitoring
```bash
# Check system status
python scripts/health_check.py

# View logs
tail -f logs/gaas.log

# Monitor data freshness
python scripts/data_freshness.py
```

### Maintenance
```bash
# Update historical archives
python scripts/update_archives.py

# Database optimization
sqlite3 data/*.db "VACUUM;"

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Areas for Contribution
- **New Sports**: Add coverage for additional leagues
- **Algorithm Improvements**: Enhance rarity detection
- **UI/UX**: Improve web interface
- **Documentation**: Expand guides and examples
- **Performance**: Optimize data processing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Sources**: nflfastR, nba_api, Retrosheet, fastf1, Kaggle, MoneyPuck
- **Inspiration**: Statistical analysis pioneers in sports analytics
- **Community**: Open source sports data enthusiasts

## 📞 Contact

- **Website**: [https://gaas.zoheri.com](https://gaas.zoheri.com)
- **GitHub**: [Khamel83/gaas](https://github.com/Khamel83/gaas)
- **Issues**: [Report Bug/Request Feature](https://github.com/Khamel83/gaas/issues)

---

⚡ **Built with passion for sports analytics and data-driven insights**