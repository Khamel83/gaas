# GAAS: Gami As A Service
## Complete Production Requirements Document

**Version**: 5.0 ULTIMATE  
**Status**: Ready for execution  
**Cost**: $0/month forever  
**Timeline**: 50-70 hours  
**GitHub**: Make public after first push

---

## 🎯 EXECUTION INSTRUCTIONS FOR CLAUDE CODE

This is a **self-contained, checkpoint-driven PRD**. Follow this process:

### Execution Loop
```
1. Load ONLY the next unchecked section
2. Implement that section completely  
3. Test it
4. Update checkbox in this file (✅)
5. Git commit with message: "Complete: [section name]"
6. Git push to GitHub
7. CLEAR CONTEXT / START FRESH
8. Repeat from step 1
```

### Context Management Strategy
- **DO NOT** keep entire PRD in memory
- Load ONLY active section (use line numbers below)
- After each section: commit, push, clear context
- Resume by: checking which boxes are unchecked
- This keeps memory usage minimal

### Recovery from Interruption
```bash
# If Claude Code crashes or needs to restart:
cd ~/gaas
git pull  # Get latest checkpoint
grep "\- \[ \]" PRD.md | head -1  # Find next unchecked item
# Load that section and continue
```

---

## 📋 MASTER PROGRESS TRACKER

**Update checkboxes as you go. Commit after each.**

### ⚙️ Phase 0: Environment Setup (Lines 200-500)
- [ ] 0.1: Oracle VM verified
- [ ] 0.2: System deps installed  
- [ ] 0.3: Python venv created
- [ ] 0.4: Tailscale + HTTPS configured
- [ ] 0.5: Git initialized + GitHub remote added
- [ ] 0.6: requirements.txt installed
- [ ] 0.7: Directory structure created

### 🏈 Phase 1: NFL RB Proof of Concept (Lines 500-1500)
- [ ] 1.1: nflfastR data downloaded (~5GB)
- [ ] 1.2: Archive DB loaded (~50K games)
- [ ] 1.3: NFLCollector implemented
- [ ] 1.4: RarityEngine implemented
- [ ] 1.5: Output generators working
- [ ] 1.6: Basic web UI created
- [ ] 1.7: Git auto-push working
- [ ] 1.8: End-to-end test passed

### 🏈 Phase 2: All NFL Positions (Lines 1500-2500)
- [ ] 2.1: QB implemented
- [ ] 2.2: WR implemented  
- [ ] 2.3: TE implemented
- [ ] 2.4: DL implemented
- [ ] 2.5: LB implemented
- [ ] 2.6: DB implemented
- [ ] 2.7: K implemented
- [ ] 2.8: P implemented

### 🏀 Phase 3: NBA (Lines 2500-3500)
- [ ] 3.1: NBA data downloaded
- [ ] 3.2: Archive DB loaded
- [ ] 3.3: NBACollector implemented
- [ ] 3.4: NBA web UI created
- [ ] 3.5: Pipeline tested

### ⚾ Phase 4: MLB (Lines 3500-4500)
- [ ] 4.1: Retrosheet data downloaded
- [ ] 4.2: Archive DB loaded
- [ ] 4.3: MLBCollector implemented
- [ ] 4.4: Batter stats working
- [ ] 4.5: Pitcher stats working
- [ ] 4.6: MLB web UI created
- [ ] 4.7: Pipeline tested

### 🏎️ Phase 5: F1 (Lines 4500-5500)
- [ ] 5.1: F1 data downloaded
- [ ] 5.2: Archive DB loaded
- [ ] 5.3: F1Collector implemented
- [ ] 5.4: F1 web UI created
- [ ] 5.5: Pipeline tested

### ⚽ Phase 6: Champions League (Lines 5500-6500)
- [ ] 6.1: UCL data downloaded
- [ ] 6.2: Archive DB loaded
- [ ] 6.3: UCLCollector implemented
- [ ] 6.4: UCL web UI created
- [ ] 6.5: Pipeline tested

### 🏒 Phase 7: NHL (Lines 6500-7500)
- [ ] 7.1: MoneyPuck data downloaded
- [ ] 7.2: Archive DB loaded
- [ ] 7.3: NHLCollector implemented
- [ ] 7.4: NHL web UI created
- [ ] 7.5: Attribution added
- [ ] 7.6: Pipeline tested

### 🔧 Phase 8: Integration (Lines 7500-8500)
- [ ] 8.1: Main orchestrator (gaas.py) complete
- [ ] 8.2: All sports coordinated
- [ ] 8.3: Smart polling configured
- [ ] 8.4: DB indexes optimized
- [ ] 8.5: Error handling tested
- [ ] 8.6: Memory validated

### 🚀 Phase 9: Deployment (Lines 8500-9500)
- [ ] 9.1: Systemd services created
- [ ] 9.2: Services running
- [ ] 9.3: Web UI accessible
- [ ] 9.4: SSL working
- [ ] 9.5: Auto-restart verified

### ✅ Phase 10: Testing (Lines 9500-10500)
- [ ] 10.1: Unit tests passing
- [ ] 10.2: Integration tests passing
- [ ] 10.3: Known rare perfs validated
- [ ] 10.4: 48hr stability test passed

### 📚 Phase 11: Documentation (Lines 10500-11000)
- [ ] 11.1: README.md complete
- [ ] 11.2: Screenshots added
- [ ] 11.3: License added
- [ ] 11.4: Final push to GitHub

---

## 📊 DATA SOURCES (All Verified & Free)

### NFL (1999-2024)
- **Source**: nflfastR  
- **URL**: https://github.com/nflverse/nflverse-data/releases
- **Size**: ~5GB  
- **Install**: `pip install nfl-data-py`

### NBA (2010-2024)
- **Source**: Kaggle + nba_api  
- **URL**: https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores
- **Size**: ~2GB  
- **Install**: `pip install nba-api`

### MLB (1871-2024)
- **Source**: Retrosheet  
- **URL**: https://www.retrosheet.org/game.htm
- **Size**: 632MB  
- **Install**: `pip install pybaseball` (or manual CSV)

### F1 (1950-2024, focus 2018+)
- **Source**: Kaggle + fastf1  
- **URL**: https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020
- **Size**: ~500MB  
- **Install**: `pip install fastf1`

### Champions League (2016-2022)
- **Source**: Kaggle  
- **URL**: https://www.kaggle.com/datasets/cbxkgl/uefa-champions-league-2016-2022-data
- **Size**: ~100MB  
- **Format**: CSV

### NHL (2008-2024)
- **Source**: MoneyPuck  
- **URL**: https://moneypuck.com/data.htm
- **Size**: ~1GB  
- **License**: Free with attribution

---

## 🏗️ SYSTEM ARCHITECTURE

```
Oracle VM (Free Tier)
├── Historical Data (SQLite, read-only, ~10GB total)
│   ├── nfl_archive.db
│   ├── nba_archive.db
│   ├── mlb_archive.db
│   ├── f1_archive.db
│   ├── ucl_archive.db
│   └── nhl_archive.db
│
├── Current Season (SQLite, read-write, updated every 5-30min)
│   └── [sport]_current.db
│
├── GAAS Service (Python, runs 24/7)
│   ├── Collectors (fetch new games)
│   ├── RarityEngine (compute rarity)
│   └── OutputGenerator (create JSON/MD)
│
└── Web UI (FastAPI, Tailscale HTTPS)
    └── https://gaas.{your-tailnet}.ts.net

Results → GitHub (public repo, auto-pushed)
```

---

## ⚙️ PHASE 0: ENVIRONMENT SETUP (Lines 200-500)

**Goal**: Prepare Oracle VM for development

### 0.1: Verify Oracle VM

```bash
# Check specs
echo "=== System Info ==="
lscpu | grep -E "Architecture|CPU\(s\)"
free -h
df -h /
lsb_release -a
python3 --version
```

**Expected**:
- 4 ARM cores
- 24GB RAM
- 200GB storage
- Ubuntu 22.04 or 24.04
- Python 3.11+

✅ **Checkpoint**: VM meets requirements

### 0.2: Install System Dependencies

```bash
#!/bin/bash
# File: scripts/setup_system.sh

echo "Installing system dependencies..."

sudo apt update
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

echo "✅ System dependencies installed"
```

Run: `bash scripts/setup_system.sh`

✅ **Checkpoint**: System deps installed

### 0.3: Create Python Virtual Environment

```bash
cd ~/gaas
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

✅ **Checkpoint**: Venv created and activated

### 0.4: Install Python Packages

**File**: `requirements.txt`

```
# Data sources
nfl-data-py>=0.3.0
nba-api>=1.4.0
fastf1>=3.3.0
pybaseball>=2.2.7

# Core
pandas>=2.1.0
numpy>=1.26.0

# Web
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
jinja2>=3.1.0

# Utils
httpx>=0.25.0
schedule>=1.2.0
gitpython>=3.1.40
loguru>=0.7.0
pyyaml>=6.0.1
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Quality
ruff>=0.1.0
black>=23.0.0
```

Install: `pip install -r requirements.txt`

✅ **Checkpoint**: Packages installed

### 0.5: Configure Tailscale HTTPS

```bash
#!/bin/bash
# File: scripts/setup_tailscale.sh

echo "Configuring Tailscale..."

# Start Tailscale (will prompt for login)
sudo tailscale up

# Get cert for HTTPS
sudo tailscale cert gaas

# Save tailnet domain for later
DOMAIN=$(tailscale status | grep "$(hostname)" | awk '{print $1}')
echo "export GAAS_DOMAIN=$DOMAIN" >> ~/.bashrc

echo "✅ Tailscale configured"
echo "Your site: https://$DOMAIN"
```

Run: `bash scripts/setup_tailscale.sh`

✅ **Checkpoint**: Tailscale HTTPS ready

### 0.6: Initialize Git Repository

```bash
cd ~/gaas
git init
git config user.name "GAAS Bot"
git config user.email "gaas@yourdomain.com"

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
venv/
*.db
*.db-journal
data/downloads/
data/archive/*.db
data/current/*.db
logs/*.log
*.log
.DS_Store
*.crt
*.key
EOF

git add .
git commit -m "Initial commit: GAAS PRD"
```

**Manually create GitHub repo**, then:

```bash
git remote add origin https://github.com/{username}/gaas.git
git push -u origin main
```

✅ **Checkpoint**: Git initialized, GitHub connected

### 0.7: Create Directory Structure

```bash
mkdir -p ~/gaas/{data/{downloads,archive,current},logs,results,src/{collectors,processors,generators,web/{static/{css,js},templates},utils,config},scripts,tests,docs}
```

✅ **Checkpoint**: Directories created

**🎯 COMMIT CHECKPOINT**: 
```bash
git add .
git commit -m "Complete Phase 0: Environment Setup"
git push
```

---

## 🏈 PHASE 1: NFL RB PROOF OF CONCEPT (Lines 500-1500)

**Goal**: Build end-to-end pipeline for one position

### 1.1: Download NFL Historical Data

**File**: `scripts/download_nfl_data.py`

```python
#!/usr/bin/env python3
"""Download NFL historical data (1999-2024)"""
import nfl_data_py as nfl
import pandas as pd
from pathlib import Path
from loguru import logger

def main():
    logger.add("logs/download_nfl.log")
    logger.info("Downloading NFL data...")
    
    Path("data/downloads/nfl").mkdir(parents=True, exist_ok=True)
    
    # Download play-by-play (takes 15-30min)
    pbp = nfl.import_pbp_data(
        years=range(1999, 2025),
        downcast=True,
        cache=True
    )
    
    logger.info(f"Downloaded {len(pbp):,} plays")
    
    # Extract RB stats
    rb_rush = pbp[pbp['play_type'] == 'run'].groupby(
        ['game_id', 'rusher_player_id', 'rusher_player_name', 
         'posteam', 'defteam', 'game_date', 'season', 'week']
    ).agg({
        'rushing_yards': 'sum',
        'rush_touchdown': 'sum',
        'fumble_lost': 'sum'
    }).reset_index()
    
    attempts = pbp[pbp['play_type'] == 'run'].groupby(
        ['game_id', 'rusher_player_id']
    ).size().reset_index(name='rush_attempts')
    
    rb_games = rb_rush.merge(attempts, on=['game_id', 'rusher_player_id'])
    rb_games.columns = ['game_id', 'player_id', 'player_name', 'team', 
                        'opponent', 'game_date', 'season', 'week',
                        'rush_yards', 'rush_td', 'fumbles_lost', 'rush_attempts']
    
    rb_games.to_csv('data/downloads/nfl/rb_games.csv', index=False)
    logger.success(f"Saved {len(rb_games):,} RB games")

if __name__ == '__main__':
    main()
```

Run: `python scripts/download_nfl_data.py`

✅ **Checkpoint**: NFL data downloaded

### 1.2: Load Archive Database

**File**: `scripts/load_nfl_archive.py`

```python
#!/usr/bin/env python3
"""Load NFL RB data into archive database"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger

def bucket_rush_yards(y):
    if y < 50: return '0-49'
    elif y < 100: return '50-99'
    elif y < 150: return '100-149'
    elif y < 200: return '150-199'
    else: return '200+'

def bucket_rush_td(t):
    if t == 0: return '0'
    elif t == 1: return '1'
    elif t == 2: return '2'
    elif t == 3: return '3'
    else: return '4+'

def bucket_fumbles(f):
    if f == 0: return '0'
    elif f == 1: return '1'
    else: return '2+'

def main():
    logger.add("logs/load_nfl.log")
    
    df = pd.read_csv('data/downloads/nfl/rb_games.csv')
    
    # Apply bucketing
    df['rush_yards_bucket'] = df['rush_yards'].apply(bucket_rush_yards)
    df['rush_td_bucket'] = df['rush_td'].apply(bucket_rush_td)
    df['fumbles_bucket'] = df['fumbles_lost'].apply(bucket_fumbles)
    
    # Create database
    Path("data/archive").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('data/archive/nfl_archive.db')
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rb_games (
            game_id TEXT,
            player_id TEXT,
            player_name TEXT,
            team TEXT,
            opponent TEXT,
            game_date DATE,
            season INTEGER,
            week INTEGER,
            rush_attempts INTEGER,
            rush_yards INTEGER,
            rush_td INTEGER,
            fumbles_lost INTEGER,
            rush_yards_bucket TEXT,
            rush_td_bucket TEXT,
            fumbles_bucket TEXT,
            PRIMARY KEY (game_id, player_id)
        )
    """)
    
    df.to_sql('rb_games', conn, if_exists='replace', index=False)
    
    conn.execute("CREATE INDEX idx_rb_buckets ON rb_games(rush_yards_bucket, rush_td_bucket, fumbles_bucket)")
    conn.execute("CREATE INDEX idx_rb_date ON rb_games(game_date)")
    
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM rb_games").fetchone()[0]
    conn.close()
    
    logger.success(f"Loaded {count:,} games")

if __name__ == '__main__':
    main()
```

Run: `python scripts/load_nfl_archive.py`

✅ **Checkpoint**: Archive DB loaded

### 1.3: Implement Core Classes

**File**: `src/processors/rarity_engine.py`

```python
"""Core rarity computation engine"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger

class RarityEngine:
    def __init__(self, sport: str, position: str):
        self.sport = sport
        self.position = position
        self.archive_db = Path(f"data/archive/{sport}_archive.db")
        self.current_db = Path(f"data/current/{sport}_current.db")
    
    def compute_rarity(self, game: pd.Series) -> dict:
        """Compute how rare a performance is"""
        matches = self._find_matches(game)
        
        if matches is None or len(matches) == 0:
            count = 0
            first = None
            last = None
        else:
            count = len(matches)
            first = matches.iloc[0].to_dict()
            last = matches.iloc[-1].to_dict()
        
        total = self._get_total_games()
        score = 100 * (1 - (count / total)) ** 2 if total > 0 else 100
        
        return {
            'occurrence_count': count,
            'first_occurrence': first,
            'last_occurrence': last,
            'rarity_score': round(score, 2),
            'classification': self._classify(count),
            'total_games': total
        }
    
    def _find_matches(self, game):
        """Find matching stat lines in archive + current"""
        query = f"""
            SELECT * FROM {self.position}_games 
            WHERE rush_yards_bucket = '{game['rush_yards_bucket']}'
            AND rush_td_bucket = '{game['rush_td_bucket']}'
            AND fumbles_bucket = '{game['fumbles_bucket']}'
            ORDER BY game_date ASC
        """
        
        dfs = []
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    df = pd.read_sql(query, conn)
                    conn.close()
                    dfs.append(df)
                except:
                    pass
        
        return pd.concat(dfs) if dfs else None
    
    def _get_total_games(self):
        """Count all games in dataset"""
        total = 0
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    res = conn.execute(f"SELECT COUNT(*) FROM {self.position}_games").fetchone()
                    total += res[0]
                    conn.close()
                except:
                    pass
        return total
    
    def _classify(self, count):
        """Classify rarity"""
        if count == 1: return 'never_before'
        elif count <= 5: return 'extremely_rare'
        elif count <= 10: return 'very_rare'
        elif count <= 25: return 'rare'
        else: return 'common'
    
    def is_interesting(self, game):
        """Check if game is worth analyzing"""
        return (
            game['rush_yards'] >= 100 or
            game['rush_td'] >= 2 or
            game['fumbles_lost'] >= 2
        )
```

**File**: `src/collectors/nfl_collector.py`

```python
"""NFL data collector for current season"""
import nfl_data_py as nfl
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from loguru import logger

class NFLCollector:
    def __init__(self, position='rb'):
        self.position = position
        self.current_season = self._get_season()
        self.current_db = Path("data/current/nfl_current.db")
        self._init_db()
    
    def _get_season(self):
        now = datetime.now()
        return now.year if now.month >= 9 else now.year - 1
    
    def _init_db(self):
        self.current_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.current_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rb_games (
                game_id TEXT,
                player_id TEXT,
                player_name TEXT,
                team TEXT,
                opponent TEXT,
                game_date DATE,
                season INTEGER,
                week INTEGER,
                rush_attempts INTEGER,
                rush_yards INTEGER,
                rush_td INTEGER,
                fumbles_lost INTEGER,
                rush_yards_bucket TEXT,
                rush_td_bucket TEXT,
                fumbles_bucket TEXT,
                PRIMARY KEY (game_id, player_id)
            )
        """)
        conn.close()
    
    def fetch_new_games(self):
        """Fetch new games from current season"""
        logger.info(f"Checking for new RB games ({self.current_season})")
        
        try:
            weekly = nfl.import_weekly_data([self.current_season], downcast=True)
            rb_data = weekly[weekly['position'] == 'RB'].copy()
            
            if len(rb_data) == 0:
                return pd.DataFrame()
            
            # Check existing
            conn = sqlite3.connect(self.current_db)
            existing = pd.read_sql("SELECT game_id, player_id FROM rb_games", conn)
            conn.close()
            
            # Find new
            if len(existing) > 0:
                rb_data['key'] = rb_data['game_id'] + '_' + rb_data['player_id']
                existing['key'] = existing['game_id'] + '_' + existing['player_id']
                new_data = rb_data[~rb_data['key'].isin(existing['key'])]
            else:
                new_data = rb_data
            
            if len(new_data) == 0:
                logger.info("No new games")
                return pd.DataFrame()
            
            # Transform
            games = pd.DataFrame({
                'game_id': new_data['game_id'],
                'player_id': new_data['player_id'],
                'player_name': new_data['player_display_name'],
                'team': new_data['recent_team'],
                'opponent': new_data['opponent_team'],
                'game_date': new_data['week'],
                'season': new_data['season'],
                'week': new_data['week'],
                'rush_attempts': new_data['carries'],
                'rush_yards': new_data['rushing_yards'],
                'rush_td': new_data['rushing_tds'],
                'fumbles_lost': new_data['rushing_fumbles_lost']
            })
            
            # Bucket
            games = self._apply_buckets(games)
            
            # Save
            conn = sqlite3.connect(self.current_db)
            games.to_sql('rb_games', conn, if_exists='append', index=False)
            conn.close()
            
            logger.success(f"Found {len(games)} new games")
            return games
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return pd.DataFrame()
    
    def _apply_buckets(self, df):
        def yard_bucket(y):
            if y < 50: return '0-49'
            elif y < 100: return '50-99'
            elif y < 150: return '100-149'
            elif y < 200: return '150-199'
            else: return '200+'
        
        def td_bucket(t):
            if t == 0: return '0'
            elif t == 1: return '1'
            elif t == 2: return '2'
            elif t == 3: return '3'
            else: return '4+'
        
        def fum_bucket(f):
            if f == 0: return '0'
            elif f == 1: return '1'
            else: return '2+'
        
        df['rush_yards_bucket'] = df['rush_yards'].apply(yard_bucket)
        df['rush_td_bucket'] = df['rush_td'].apply(td_bucket)
        df['fumbles_bucket'] = df['fumbles_lost'].apply(fum_bucket)
        return df
    
    def is_game_window(self):
        """Check if it's game time"""
        now = datetime.now()
        day = now.strftime('%A')
        hour = now.hour
        
        return (
            (day == 'Thursday' and 19 <= hour <= 23) or
            (day == 'Sunday' and (12 <= hour or hour <= 1)) or
            (day == 'Monday' and 19 <= hour <= 23)
        )
```

✅ **Checkpoint**: Core classes implemented

### 1.4: Output Generators

**File**: `src/generators/json_generator.py`

```python
"""Generate JSON output files"""
import json
from pathlib import Path
from datetime import datetime

class JSONGenerator:
    def __init__(self, sport, position):
        self.sport = sport
        self.position = position
        self.output_dir = Path(f"results/{sport}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_latest(self, rare_perfs):
        """Generate latest.json (last 7 days)"""
        output = {
            'generated_at': datetime.now().isoformat(),
            'sport': self.sport,
            'position': self.position,
            'time_range': 'last_7_days',
            'rare_performances': rare_perfs
        }
        
        file = self.output_dir / f"{self.position}_latest.json"
        with open(file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        return file
    
    def generate_all_time(self, rare_perfs, top_n=50):
        """Generate all_time.json (top N rarest)"""
        sorted_perfs = sorted(
            rare_perfs,
            key=lambda x: x['rarity']['rarity_score'],
            reverse=True
        )[:top_n]
        
        output = {
            'generated_at': datetime.now().isoformat(),
            'sport': self.sport,
            'position': self.position,
            'time_range': 'all_time',
            'top_rare_performances': sorted_perfs
        }
        
        file = self.output_dir / f"{self.position}_all_time.json"
        with open(file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        return file
    
    def generate_index(self):
        """Generate master index.json"""
        output = {
            'last_updated': datetime.now().isoformat(),
            'sports': {
                'nfl': {
                    'positions': ['rb'],
                    'files': {
                        'rb': {
                            'latest': 'nfl/rb_latest.json',
                            'all_time': 'nfl/rb_all_time.json'
                        }
                    }
                }
            }
        }
        
        file = Path("results/index.json")
        with open(file, 'w') as f:
            json.dump(output, f, indent=2)
        
        return file
```

✅ **Checkpoint**: Output generator working

### 1.5: Git Automation

**File**: `src/utils/git_pusher.py`

```python
"""Automated Git commits and pushes"""
from git import Repo
from datetime import datetime
from loguru import logger

def push_results(files):
    """Commit and push result files"""
    try:
        repo = Repo('.')
        repo.index.add(files)
        
        msg = f"Update results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        repo.index.commit(msg)
        
        repo.remote('origin').push()
        logger.success(f"Pushed: {msg}")
        
    except Exception as e:
        logger.error(f"Git push failed: {e}")
```

✅ **Checkpoint**: Git automation working

### 1.6: Basic Web UI

**File**: `src/web/app.py`

```python
"""FastAPI web application"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI(title="GAAS")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")

@app.get("/")
async def index(request: Request):
    data = json.load(open("results/index.json"))
    return templates.TemplateResponse("index.html", {"request": request, "data": data})

@app.get("/nfl/rb")
async def nfl_rb(request: Request):
    data = json.load(open("results/nfl/rb_latest.json"))
    return templates.TemplateResponse("position.html", {"request": request, "data": data})

if __name__ == '__main__':
    import uvicorn
    import os
    
    domain = os.getenv('GAAS_DOMAIN', 'localhost')
    cert = f"/var/lib/tailscale/certs/{domain}.crt"
    key = f"/var/lib/tailscale/certs/{domain}.key"
    
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_certfile=cert, ssl_keyfile=key)
```

**File**: `src/web/templates/base.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}GAAS{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <h1>GAAS: Gami As A Service</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/nfl/rb">NFL RB</a>
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**File**: `src/web/templates/index.html`

```html
{% extends "base.html" %}
{% block content %}
<h2>Rare Statistical Performances</h2>
<div class="sports">
    {% for sport, info in data.sports.items() %}
    <div class="sport-card">
        <h3>{{ sport|upper }}</h3>
        <ul>
            {% for pos in info.positions %}
            <li><a href="/{{ sport }}/{{ pos }}">{{ pos|upper }}</a></li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

**File**: `src/web/templates/position.html`

```html
{% extends "base.html" %}
{% block content %}
<h2>{{ data.sport|upper }} {{ data.position|upper }}</h2>
<p>Updated: {{ data.generated_at }}</p>

{% for perf in data.rare_performances %}
<div class="perf-card {{ perf.rarity.classification }}">
    <h3>{{ perf.game.player_name }}</h3>
    <p>{{ perf.game.game_date }} - {{ perf.game.team }} vs {{ perf.game.opponent }}</p>
    <p>{{ perf.game.rush_yards }} yards, {{ perf.game.rush_td }} TDs, {{ perf.game.fumbles_lost }} fumbles</p>
    <p class="rarity">
        <strong>{{ perf.rarity.classification|upper }}</strong><br>
        Occurred {{ perf.rarity.occurrence_count }} times
        {% if perf.rarity.last_occurrence %}
        <br>Last: {{ perf.rarity.last_occurrence.player_name }} ({{ perf.rarity.last_occurrence.game_date }})
        {% endif %}
    </p>
</div>
{% endfor %}
{% endblock %}
```

**File**: `src/web/static/css/style.css`

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: sans-serif; background: #f5f5f5; }
header { background: #2c3e50; color: white; padding: 1rem 2rem; }
nav a { color: white; text-decoration: none; margin-right: 1rem; }
main { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.sports { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
.sport-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.perf-card { background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; border-left: 4px solid #95a5a6; }
.perf-card.never_before { border-left-color: #e74c3c; }
.perf-card.extremely_rare { border-left-color: #e67e22; }
.perf-card.very_rare { border-left-color: #f39c12; }
.perf-card.rare { border-left-color: #f1c40f; }
.rarity { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #ecf0f1; color: #7f8c8d; }
```

✅ **Checkpoint**: Basic web UI created

### 1.7: Main Orchestrator

**File**: `src/gaas.py`

```python
"""Main GAAS orchestrator"""
import schedule
import time
from datetime import datetime
from loguru import logger
import sys

from collectors.nfl_collector import NFLCollector
from processors.rarity_engine import RarityEngine
from generators.json_generator import JSONGenerator
from utils.git_pusher import push_results

logger.add(sys.stdout, level="INFO")
logger.add("logs/gaas.log", rotation="100 MB")

def run_nfl_rb_pipeline():
    """Execute NFL RB pipeline"""
    logger.info("=" * 60)
    logger.info("Running NFL RB pipeline")
    
    collector = NFLCollector('rb')
    new_games = collector.fetch_new_games()
    
    if len(new_games) == 0:
        logger.info("No new games")
        return
    
    logger.info(f"Found {len(new_games)} new games")
    
    engine = RarityEngine('nfl', 'rb')
    rare_perfs = []
    
    for idx, game in new_games.iterrows():
        if engine.is_interesting(game):
            logger.info(f"Checking: {game['player_name']}")
            rarity = engine.compute_rarity(game)
            
            if rarity['occurrence_count'] <= 25:
                rare_perfs.append({
                    'game': game.to_dict(),
                    'rarity': rarity
                })
                logger.success(f"RARE: {game['player_name']} - {rarity['classification']}")
    
    if rare_perfs:
        gen = JSONGenerator('nfl', 'rb')
        files = [
            str(gen.generate_latest(rare_perfs)),
            str(gen.generate_index())
        ]
        push_results(files)
        logger.success(f"Pushed {len(files)} files")

def main():
    logger.info("GAAS starting...")
    
    # Initial run
    run_nfl_rb_pipeline()
    
    # Schedule
    collector = NFLCollector()
    
    while True:
        if collector.is_game_window():
            time.sleep(300)  # 5 min
            run_nfl_rb_pipeline()
        else:
            time.sleep(7200)  # 2 hours
            run_nfl_rb_pipeline()

if __name__ == '__main__':
    main()
```

✅ **Checkpoint**: Main orchestrator working

### 1.8: End-to-End Test

**File**: `tests/test_phase1.py`

```python
"""Test Phase 1 end-to-end"""
import pytest
import sqlite3
from pathlib import Path

def test_archive_exists():
    assert Path("data/archive/nfl_archive.db").exists()

def test_archive_has_data():
    conn = sqlite3.connect("data/archive/nfl_archive.db")
    count = conn.execute("SELECT COUNT(*) FROM rb_games").fetchone()[0]
    conn.close()
    assert count > 40000

def test_collector():
    from src.collectors.nfl_collector import NFLCollector
    collector = NFLCollector('rb')
    assert collector.position == 'rb'

def test_rarity_engine():
    from src.processors.rarity_engine import RarityEngine
    engine = RarityEngine('nfl', 'rb')
    assert engine.sport == 'nfl'

# Run: pytest tests/test_phase1.py -v
```

Run tests: `pytest tests/test_phase1.py -v`

✅ **Checkpoint**: All tests passing

**🎯 COMMIT CHECKPOINT**:
```bash
git add .
git commit -m "Complete Phase 1: NFL RB Proof of Concept"
git push
```

---

## 🏈 PHASE 2-7: ALL OTHER SPORTS (Lines 1500-7500)

**PATTERN**: Each sport follows the same structure:
1. Download data
2. Load archive DB
3. Implement Collector
4. Define stat buckets (use expert prompts)
5. Add to web UI
6. Test pipeline

**For each sport, Claude Code should**:
- Load ONLY that sport's section
- Implement completely
- Test
- Commit
- Clear context
- Move to next

### EXPERT PROMPTS TO USE

For each sport/position, ask:

```
As an expert [SPORT] analyst, what are the 5-8 most important 
statistics for [POSITION]? What thresholds are significant?

Examples:
- NFL QB: 300+ pass yards, 4+ TDs
- NBA: 30+ points, triple-double
- MLB Batter: 4+ hits, 3+ HR
- F1: Gained 10+ positions, last-to-podium
```

### Phase 2: All NFL Positions

Implement: QB, WR, TE, DL, LB, DB, K, P

Same pattern as RB. Use expert prompts for each.

✅ **Commit after each position**

### Phase 3: NBA

- Download: Kaggle or nba_api
- Stats: points, rebounds, assists, steals, blocks
- Interesting: 30+ pts OR 10+ reb OR 10+ ast OR triple-double

✅ **Commit after complete**

### Phase 4: MLB

- Download: Retrosheet CSVs
- Batters: hits, HR, RBI, runs
- Pitchers: strikeouts, walks, ER
- Interesting: 4+ hits OR 2+ HR OR 10+ K

✅ **Commit after complete**

### Phase 5: F1

- Download: Kaggle + fastf1
- Stats: finish, grid, positions gained, fastest lap
- Interesting: Gained 10+ OR last-to-podium OR DNF from pole

✅ **Commit after complete**

### Phase 6: Champions League

- Download: Kaggle
- Stats: goals, assists, shots, saves (GK)
- Interesting: 2+ goals OR 2+ assists OR 10+ saves

✅ **Commit after complete**

### Phase 7: NHL

- Download: MoneyPuck
- Stats: goals, assists, points, shots, plus/minus
- Interesting: 3+ goals OR 4+ points OR hat trick

✅ **Commit after complete**

---

## 🔧 PHASE 8: INTEGRATION (Lines 7500-8500)

### 8.1: Update Main Orchestrator

Coordinate all sports in one `gaas.py`:

```python
def main():
    sports_configs = {
        'nfl': {'enabled': True, 'positions': ['rb', 'qb', 'wr', ...]},
        'nba': {'enabled': True},
        'mlb': {'enabled': True},
        'f1': {'enabled': True},
        'ucl': {'enabled': True},
        'nhl': {'enabled': True}
    }
    
    while True:
        for sport, config in sports_configs.items():
            if config['enabled']:
                run_sport_pipeline(sport, config)
        
        time.sleep(determine_sleep_time())
```

✅ **Checkpoint**: All sports coordinated

---

## 🚀 PHASE 9: DEPLOYMENT (Lines 8500-9500)

### Systemd Services

**File**: `/etc/systemd/system/gaas.service`

```ini
[Unit]
Description=GAAS Data Collector
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gaas
ExecStart=/home/ubuntu/gaas/venv/bin/python src/gaas.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**File**: `/etc/systemd/system/gaas-web.service`

```ini
[Unit]
Description=GAAS Web UI
After=network.target tailscaled.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gaas
ExecStart=/home/ubuntu/gaas/venv/bin/python src/web/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable gaas gaas-web
sudo systemctl start gaas gaas-web
```

✅ **Checkpoint**: Services running

---

## ✅ PHASE 10: TESTING (Lines 9500-10500)

### Unit Tests

Test each component individually.

### Integration Tests

Test full pipelines end-to-end.

### 48-Hour Stability Test

Let system run for 48 hours, monitor for crashes.

✅ **Checkpoint**: System stable

---

## 📚 PHASE 11: DOCUMENTATION (Lines 10500-11000)

### README.md

```markdown
# GAAS: Gami As A Service

Automatically detects rare statistical performances across NFL, NBA, MLB, F1, Champions League, and NHL.

## Features
- 6 sports monitored 24/7
- Historical data back to 1871 (MLB) / 1950 (F1) / 1999 (NFL) / etc.
- Web UI with SSL via Tailscale
- Results auto-published to GitHub
- $0/month hosting cost

## Live Site
https://gaas.your-tailnet.ts.net

## Data Sources
- NFL: nflfastR
- NBA: nba_api
- MLB: Retrosheet
- F1: fastf1 + Kaggle
- UCL: Kaggle
- NHL: MoneyPuck (with attribution)

## License
MIT
```

✅ **Checkpoint**: Documentation complete

---

## 🎉 PROJECT COMPLETE

**When all checkboxes are checked:**

1. System runs 24/7 automatically
2. Web UI accessible via Tailscale HTTPS
3. Results published to GitHub
4. All 6 sports monitored
5. Zero monthly costs

**Final push:**

```bash
git add .
git commit -m "🎉 GAAS Complete - All phases finished"
git push
```

---

## 🔧 TROUBLESHOOTING

### Service won't start
```bash
sudo journalctl -u gaas -n 50
# Check logs for errors
```

### Database corruption
```bash
cd ~/gaas
rm data/current/*.db
# Re-initialize current DBs
```

### Git push fails
```bash
git pull --rebase
git push
```

---

## 📝 MAINTENANCE

### Weekly
- Check logs: `tail -100 logs/gaas.log`
- Verify disk space: `df -h`

### Monthly
- Update packages: `pip install -U -r requirements.txt`
- Vacuum DBs: `sqlite3 data/archive/*.db "VACUUM;"`

### Annually
- Merge current → archive
- Download new historical data
- Review stat thresholds

---

## 🎯 EXECUTION SUMMARY

**Total Time**: 50-70 hours  
**Total Cost**: $0/month  
**Lines of Code**: ~5,000  
**Database Size**: ~10GB  
**Sports Covered**: 6  
**Positions Tracked**: 20+  
**Historical Games**: 1M+  

**This is a production-ready, enterprise-grade system built entirely on free tier resources.**

---

**END OF PRD**

This document is complete and self-contained. Execute section by section, updating checkboxes as you go.
