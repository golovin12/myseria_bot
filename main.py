from fastapi import FastAPI

import api
from setup.init_bots import init_bots
from setup.startup import startup
from setup.shutdown import shutdown

init_bots()

app = FastAPI()
app.include_router(api.bot_router)
app.add_event_handler('startup', startup)
app.add_event_handler('shutdown', shutdown)
