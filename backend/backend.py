from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def root():
    return {"message": "Welcome to your FastAPI Dockerized backend!"}


#   
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#