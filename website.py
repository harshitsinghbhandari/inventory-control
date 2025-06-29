from fastapi import FastAPI, Request, HTTPException,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse,RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# import psycopg2
from dotenv import load_dotenv
import logging
import uuid
from simulate_inventory import run_simulation, log_normal_lead_time_generator, lumpy_ar1_demand_generator,ar1_demand_generator,positive_normal_lead_time_generator
templates = Jinja2Templates(directory="templates")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler("website.log",mode="w"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
load_dotenv()
app = FastAPI()
result_store = {}
def my_function(threshold, final, sim_time, seed,demand_func, lead_time_func,avgLeadTime, varLeadTime, lumpiness):
    kpis,data = run_simulation(s=threshold, S=final, sim_time=sim_time, seed=seed,demand_func=demand_func,lead_time_func=lead_time_func,muLeadTime=avgLeadTime,sigmaLeadTime=varLeadTime,pOccurence=lumpiness)
    # print("Simulation with parameters: s={}, S={}, sim_time={}, seed={}, demand_func={}, lead_time_func={}, avgLeadTime={}, varLeadTime={}, lumpiness={}".format())
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
    seed: int = Form(...),
    lead_time_generator: str = Form(...),
    demand_time_generator: str = Form(...),
    avgLeadTime: int = Form(...),
    varLeadTime: float = Form(...),
    lumpiness: float = Form(...),
):
    result = my_function(threshold_inventory, final_inventory, simulation_time, seed,demand_func=demand_time_generator, lead_time_func=lead_time_generator,avgLeadTime=avgLeadTime,varLeadTime=varLeadTime,lumpiness=lumpiness)

    # Generate unique ID and store result
    result_id = str(uuid.uuid4())
    result_store[result_id] = result

    # Redirect to results page
    return RedirectResponse(url=f"/results?rid={result_id}", status_code=303)
@app.get("/results")
async def show_results(request: Request, rid: str):
    result = result_store.get(rid)
    if not result:
        return templates.TemplateResponse("results.html", {"request": request, "error": "Result not found."},404)

    return templates.TemplateResponse("results.html", {"request": request, "result": result},200)