import logging
import os
import random
import time
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI, Response


EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)
TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")
TARGET_TWO_HOST = os.environ.get("TARGET_TWO_HOST", "app-c")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = FastAPI()


@app.get("/")
async def read_root():
  logging.info("Hello World")
  return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
  logging.info("items")
  return {"item_id": item_id, "q": q}


@app.get("/io_task")
async def io_task():
  time.sleep(1)
  logging.info("io task")
  return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
  for i in range(1000):
    n = i*i*i

  time.sleep(1)
  logging.info("cpu task result %s", n)
  return "CPU bound task finish!"


@app.get("/random_status")
async def random_status(response: Response):
  response.status_code = random.choice([200, 200, 300, 400, 500])
  logging.info("random status")
  return {"path": "/random_status"}


@app.get("/random_sleep")
async def random_sleep(response: Response):
  time.sleep(random.randint(0, 5))
  logging.info("random sleep")
  return {"path": "/random_sleep"}


@app.get("/error_test")
async def error_test(response: Response):
  logging.error("got error!!!!")
  raise ValueError("value error")


@app.get("/chain")
async def chain(response: Response):

  headers = {}
  logging.info(headers)

  async with httpx.AsyncClient() as client:
    await client.get("http://localhost:8000/", headers=headers,)
  async with httpx.AsyncClient() as client:
    await client.get(f"http://{TARGET_ONE_HOST}:8000/io_task", headers=headers,)
  async with httpx.AsyncClient() as client:
    await client.get(f"http://{TARGET_TWO_HOST}:8000/cpu_task", headers=headers,)
  logging.info("Chain Finished")
  return {"path": "/chain"}


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT)
