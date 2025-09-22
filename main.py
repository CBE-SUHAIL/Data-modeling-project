from fastapi import FastAPI
from routers import farmer, crop, field, activity_log, advisory
from routers import activity_log
from routers import advisory


app = FastAPI(title="Smart Crop API", version="1.0")




# Register routes
app.include_router(farmer.router, prefix="/farmers", tags=["Farmers"])
app.include_router(crop.router, prefix="/crops", tags=["Crops"])
app.include_router(field.router, prefix="/fields", tags=["Fields"])
app.include_router(advisory.router, prefix="/advisories", tags=["Advisories"])

app.include_router(activity_log.router, prefix="/activities", tags=["Activity Logs"])
app.include_router(advisory.router, prefix="/advisories", tags=["Advisories"])