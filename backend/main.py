from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, contacts, deals, dashboard, conversations

# Tables are managed by Alembic migrations now (see migrations/), not created
# automatically here. Run `alembic upgrade head` after deploying.
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://venerable-kitsune-52fb64.netlify.app",
        "https://clientora.netlify.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(conversations.router)
app.include_router(deals.router)
app.include_router(dashboard.router)