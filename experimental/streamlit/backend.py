from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# In-memory storage for events
events = []


# {  "time_received": "2024-11-17 12:34:56",  "claim": "This is a test claim", "data": {"Customer": {"Name": "Emily Patel", "Address": "456 Maple Street", "Policy Number": "EV-901234567", "Telephone Number": "(555) 901-2345"}, "Case": {"Accident Location": "Oakdale, CA 95361", "Date": "January 15th, 2024", "Time": "9:45 AM"}} }}


# Event data model
class Event(BaseModel):
    specversion: str
    id: str


@app.post("/push-event/")
async def push_event(event: Event):
    """Endpoint to push events."""
    events.append(event)
    return {"status": "success", "event": event}


@app.get("/get-events/")
async def get_events():
    """Endpoint to get all events."""
    return events


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
