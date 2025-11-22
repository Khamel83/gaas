"""FastAPI web application"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import json
import os
from pathlib import Path

app = FastAPI(title="GAAS", description="Gami As A Service - Rare Statistical Performances")

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="src/web/templates")

# Results directory
RESULTS_DIR = Path("results")

@app.get("/")
async def index(request: Request):
    """Main page with overview"""
    try:
        index_file = RESULTS_DIR / "index.json"
        if not index_file.exists():
            # Create a basic index if it doesn't exist
            data = {
                'last_updated': 'No data available',
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
        else:
            with open(index_file) as f:
                data = json.load(f)

        return templates.TemplateResponse("index.html", {"request": request, "data": data})
    except Exception as e:
        # Return a basic template if files don't exist
        return templates.TemplateResponse("index.html", {
            "request": request,
            "data": {
                'last_updated': 'Error loading data',
                'sports': {'nfl': {'positions': ['rb']}}
            }
        })

@app.get("/nfl/{position}")
async def nfl_position(request: Request, position: str):
    """NFL position performances page"""
    try:
        latest_file = RESULTS_DIR / "nfl" / f"{position}_latest.json"
        if latest_file.exists():
            with open(latest_file) as f:
                data = json.load(f)
        else:
            # Create sample data if file doesn't exist
            data = {
                'generated_at': 'No data available',
                'sport': 'nfl',
                'position': position,
                'rare_performances': []
            }

        return templates.TemplateResponse("position.html", {"request": request, "data": data})
    except Exception as e:
        return templates.TemplateResponse("position.html", {
            "request": request,
            "data": {
                'generated_at': f'Error: {str(e)}',
                'sport': 'nfl',
                'position': position,
                'rare_performances': []
            }
        })

@app.get("/nfl/rb")
async def nfl_rb(request: Request):
    """NFL RB performances page (backward compatibility)"""
    return await nfl_position(request, "rb")

@app.get("/api/nfl/rb/latest")
async def api_nfl_rb_latest():
    """API endpoint for latest RB performances"""
    try:
        latest_file = RESULTS_DIR / "nfl" / "rb_latest.json"
        if latest_file.exists():
            with open(latest_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/nba")
async def nba(request: Request):
    """NBA overall performances page"""
    try:
        summary_file = RESULTS_DIR / "nba" / "nba_summary.json"
        detailed_file = RESULTS_DIR / "nba" / "nba_detailed.json"

        data = {
            'generated_at': 'No data available',
            'sport': 'nba',
            'total_rare_performances': 0,
            'rare_performances': []
        }

        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
                data.update(summary)

        if detailed_file.exists():
            with open(detailed_file) as f:
                detailed = json.load(f)
                data['rare_performances'] = detailed.get('rare_performances', [])

        return templates.TemplateResponse("position.html", {"request": request, "data": data})
    except Exception as e:
        return templates.TemplateResponse("position.html", {
            "request": request,
            "data": {
                'generated_at': f'Error: {str(e)}',
                'sport': 'nba',
                'total_rare_performances': 0,
                'rare_performances': []
            }
        })

@app.get("/api/nba/summary")
async def api_nba_summary():
    """API endpoint for NBA summary"""
    try:
        summary_file = RESULTS_DIR / "nba" / "nba_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/nba/detailed")
async def api_nba_detailed():
    """API endpoint for detailed NBA performances"""
    try:
        detailed_file = RESULTS_DIR / "nba" / "nba_detailed.json"
        if detailed_file.exists():
            with open(detailed_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/nfl/{position}/latest")
async def api_nfl_position_latest(position: str):
    """API endpoint for latest position performances"""
    try:
        latest_file = RESULTS_DIR / "nfl" / f"{position}_latest.json"
        if latest_file.exists():
            with open(latest_file) as f:
                return json.load(f)
        else:
            return {"error": f"No data available for {position}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/nfl/{position}/all_time")
async def api_nfl_position_all_time(position: str):
    """API endpoint for all-time rarest position performances"""
    try:
        all_time_file = RESULTS_DIR / "nfl" / f"{position}_all_time.json"
        if all_time_file.exists():
            with open(all_time_file) as f:
                return json.load(f)
        else:
            return {"error": f"No data available for {position}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/nfl/rb/latest")
async def api_nfl_rb_latest():
    """API endpoint for latest RB performances (backward compatibility)"""
    return await api_nfl_position_latest("rb")

@app.get("/api/nfl/rb/all_time")
async def api_nfl_rb_all_time():
    """API endpoint for all-time rarest RB performances (backward compatibility)"""
    return await api_nfl_position_all_time("rb")

@app.get("/mlb")
async def mlb(request: Request):
    """MLB overall performances page"""
    try:
        summary_file = RESULTS_DIR / "mlb" / "mlb_summary.json"
        detailed_file = RESULTS_DIR / "mlb" / "mlb_detailed.json"

        data = {
            'generated_at': 'No data available',
            'sport': 'mlb',
            'total_rare_performances': 0,
            'rare_performances': []
        }

        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
                data.update(summary)

        if detailed_file.exists():
            with open(detailed_file) as f:
                detailed = json.load(f)
                data['rare_performances'] = detailed.get('rare_performances', [])

        return templates.TemplateResponse("position.html", {"request": request, "data": data})
    except Exception as e:
        return templates.TemplateResponse("position.html", {
            "request": request,
            "data": {
                'generated_at': f'Error: {str(e)}',
                'sport': 'mlb',
                'total_rare_performances': 0,
                'rare_performances': []
            }
        })

@app.get("/api/mlb/summary")
async def api_mlb_summary():
    """API endpoint for MLB summary"""
    try:
        summary_file = RESULTS_DIR / "mlb" / "mlb_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/mlb/detailed")
async def api_mlb_detailed():
    """API endpoint for detailed MLB performances"""
    try:
        detailed_file = RESULTS_DIR / "mlb" / "mlb_detailed.json"
        if detailed_file.exists():
            with open(detailed_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/f1")
async def f1(request: Request):
    """F1 overall performances page"""
    try:
        summary_file = RESULTS_DIR / "f1" / "f1_summary.json"
        detailed_file = RESULTS_DIR / "f1" / "f1_detailed.json"

        data = {
            'generated_at': 'No data available',
            'sport': 'f1',
            'total_rare_performances': 0,
            'rare_performances': []
        }

        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
                data.update(summary)

        if detailed_file.exists():
            with open(detailed_file) as f:
                detailed = json.load(f)
                data['rare_performances'] = detailed.get('rare_performances', [])

        return templates.TemplateResponse("position.html", {"request": request, "data": data})
    except Exception as e:
        return templates.TemplateResponse("position.html", {
            "request": request,
            "data": {
                'generated_at': f'Error: {str(e)}',
                'sport': 'f1',
                'total_rare_performances': 0,
                'rare_performances': []
            }
        })

@app.get("/api/f1/summary")
async def api_f1_summary():
    """API endpoint for F1 summary"""
    try:
        summary_file = RESULTS_DIR / "f1" / "f1_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/f1/detailed")
async def api_f1_detailed():
    """API endpoint for detailed F1 performances"""
    try:
        detailed_file = RESULTS_DIR / "f1" / "f1_detailed.json"
        if detailed_file.exists():
            with open(detailed_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/champions-league")
async def champions_league(request: Request):
    """Champions League overall performances page"""
    try:
        latest_file = RESULTS_DIR / "champions_league" / "champions_league_latest.json"
        all_time_file = RESULTS_DIR / "champions_league" / "champions_league_all_time.json"

        data = {
            'generated_at': 'No data available',
            'sport': 'champions_league',
            'total_performances': 0,
            'performances': []
        }

        if latest_file.exists():
            with open(latest_file) as f:
                latest = json.load(f)
                data['latest_performances'] = latest.get('performances', [])
                data['latest_count'] = latest.get('total_performances', 0)

        if all_time_file.exists():
            with open(all_time_file) as f:
                all_time = json.load(f)
                data['performances'] = all_time.get('performances', [])
                data['total_performances'] = all_time.get('total_performances', 0)

        return templates.TemplateResponse("position.html", {"request": request, "data": data})
    except Exception as e:
        return templates.TemplateResponse("position.html", {
            "request": request,
            "data": {
                'generated_at': f'Error: {str(e)}',
                'sport': 'champions_league',
                'total_performances': 0,
                'performances': []
            }
        })

@app.get("/api/champions-league/latest")
async def api_champions_league_latest():
    """API endpoint for latest Champions League performances"""
    try:
        latest_file = RESULTS_DIR / "champions_league" / "champions_league_latest.json"
        if latest_file.exists():
            with open(latest_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/champions-league/all_time")
async def api_champions_league_all_time():
    """API endpoint for all-time Champions League performances"""
    try:
        all_time_file = RESULTS_DIR / "champions_league" / "champions_league_all_time.json"
        if all_time_file.exists():
            with open(all_time_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/nhl")
async def nhl(request: Request):
    """NHL overall performances page"""
    try:
        latest_file = RESULTS_DIR / "nhl" / "nhl_latest.json"
        all_time_file = RESULTS_DIR / "nhl" / "nhl_all_time.json"

        data = {
            'generated_at': 'No data available',
            'sport': 'nhl',
            'total_performances': 0,
            'performances': []
        }

        if latest_file.exists():
            with open(latest_file) as f:
                latest = json.load(f)
                data['latest_performances'] = latest.get('performances', [])
                data['latest_count'] = latest.get('total_performances', 0)

        if all_time_file.exists():
            with open(all_time_file) as f:
                all_time = json.load(f)
                data['performances'] = all_time.get('performances', [])
                data['total_performances'] = all_time.get('total_performances', 0)

        return templates.TemplateResponse("position.html", {"request": request, "data": data})
    except Exception as e:
        return templates.TemplateResponse("position.html", {
            "request": request,
            "data": {
                'generated_at': f'Error: {str(e)}',
                'sport': 'nhl',
                'total_performances': 0,
                'performances': []
            }
        })

@app.get("/api/nhl/latest")
async def api_nhl_latest():
    """API endpoint for latest NHL performances"""
    try:
        latest_file = RESULTS_DIR / "nhl" / "nhl_latest.json"
        if latest_file.exists():
            with open(latest_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/nhl/all_time")
async def api_nhl_all_time():
    """API endpoint for all-time NHL performances"""
    try:
        all_time_file = RESULTS_DIR / "nhl" / "nhl_all_time.json"
        if all_time_file.exists():
            with open(all_time_file) as f:
                return json.load(f)
        else:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GAAS Web UI"}

if __name__ == '__main__':
    import uvicorn

    # Get domain from environment or use localhost
    domain = os.getenv('GAAS_DOMAIN', 'localhost')
    port = 8000

    # Check if Tailscale certificates exist
    cert_path = f"/var/lib/tailscale/certs/{domain}.crt"
    key_path = f"/var/lib/tailscale/certs/{domain}.key"

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"Starting with HTTPS on https://{domain}")
        uvicorn.run(app, host="0.0.0.0", port=443, ssl_certfile=cert_path, ssl_keyfile=key_path)
    else:
        print(f"Starting with HTTP on http://localhost:{port}")
        print("To enable HTTPS, run: sudo tailscale cert gaas && sudo tailscale up")
        uvicorn.run(app, host="0.0.0.0", port=port)