import base64
import binascii
import os

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI(title="image-api")


class ImageIn(BaseModel):
    image: str


# plain `def` on purpose - decoding is CPU work, so FastAPI runs it in
# the threadpool instead of blocking the event loop
@app.post("/image")
def upload_image(body: ImageIn, response: Response):
    data = body.image

    # some clients send "data:image/png;base64,...."
    if data.startswith("data:"):
        data = data.split(",", 1)[-1]

    try:
        raw = base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="image is not valid base64")

    if not raw:
        raise HTTPException(status_code=400, detail="image is empty")

    # handy for checking which worker picked up the request
    response.headers["X-Worker-PID"] = str(os.getpid())
    return {"message": "accepted"}
