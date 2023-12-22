#Ce  fichier contient toutes les routes du projet chatAi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Union
app = FastAPI()

origins = [
    "http://localhost",
   "http://localhost:8080",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# Pour le lancement => A tester
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


