from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.background.hold_expiry import start_scheduler
from app.routers import auth, bookings, courts, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="Playground Booking API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(courts.router)
app.include_router(bookings.router)
app.include_router(payments.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
