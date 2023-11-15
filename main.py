from fastapi import FastAPI

import api
from setup import init_bots, startup, shutdown, configure_logging

configure_logging()
init_bots()

app = FastAPI()
app.include_router(api.bot_router)
app.add_event_handler('startup', startup)
app.add_event_handler('shutdown', shutdown)
