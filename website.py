from fastapi import FastAPI, Request, HTTPException,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse,RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# import psycopg2
from dotenv import load_dotenv
import logging
import uuid
from simulate_inventory import run_simulation
templates = Jinja2Templates(directory="templates")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler("website.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
load_dotenv()
app = FastAPI()
result_store = {}
def my_function(threshold, final, sim_time, seed):
    kpis = run_simulation(s=threshold, S=final, sim_time=sim_time, seed=seed)
    return {
        "status": "Success",
        "fill_rate": kpis["Fill Rate"],
        "average_inventory_level": kpis["Average Inventory Level"],
        "stockouts": kpis["Stockouts"],
        "total_ordering_cost": kpis["Total Ordering Cost"],
        "total_holding_cost": kpis["Total Holding Cost"],
        "total_cost": kpis["Total Cost"]
    }
@app.get("/", response_class=HTMLResponse)
def read_root():
    logger.info("Root endpoint accessed.")
    return FileResponse("templates/index.html")
@app.post("/submit-data")
async def submit_data(
    threshold_inventory: int = Form(...),
    final_inventory: int = Form(...),
    simulation_time: int = Form(...),
    seed: int = Form(...)
):
    result = my_function(threshold_inventory, final_inventory, simulation_time, seed)

    # Generate unique ID and store result
    result_id = str(uuid.uuid4())
    result_store[result_id] = result

    # Redirect to results page
    return RedirectResponse(url=f"/results?rid={result_id}", status_code=303)
@app.get("/results")
async def show_results(request: Request, rid: str):
    result = result_store.get(rid)
    if not result:
        return templates.TemplateResponse("results.html", {"request": request, "error": "Result not found."})

    return templates.TemplateResponse("results.html", {"request": request, "result": result})