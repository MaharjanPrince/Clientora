from fastapi import FastAPI


from .database import Base, engine
from .routers import auth, contacts, deals, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(deals.router)
app.include_router(dashboard.router)