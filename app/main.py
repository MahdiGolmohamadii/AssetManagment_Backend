from fastapi import FastAPI


app = FastAPI()


@app.get("/root")
async def get_root():
    return {"we are alive!": "from Root"}