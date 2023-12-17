import logging
import os
import random
import time
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI, Response

from utils import PrometheusMiddleware, metrics
from opentelemetry.propagate import inject
from opentelemetry import trace
tracer = trace.get_tracer("fastapi.tracer")

APP_NAME = os.environ.get("APP_NAME", "app")
EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)

TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")
TARGET_TWO_HOST = os.environ.get("TARGET_TWO_HOST", "app-c")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = FastAPI()

# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
app.add_route("/metrics", metrics)


class EndpointFilter(logging.Filter):
  # Uvicorn endpoint access log filter
  def filter(self, record: logging.LogRecord) -> bool:
    return record.getMessage().find("GET /metrics") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@app.get("/")
async def read_root():
  logging.info("Hello World")
  return {"Hello": "World v6"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
  logging.info("items")
  return {"item_id": item_id, "q": q}


@app.get("/io_task")
async def io_task():
  with tracer.start_as_current_span("mysql") as mysql_span:
    mysql_span.add_event("Start MySQL Query", {
      "log.severity": "info",
      "log.message": "query io",
      "io_task.id": "123",
    })
    mysql_span.set_attribute("query", "SELECT * FROM io_task")
    time.sleep(1)
    mysql_span.add_event("Query Finished!", {
      "log.severity": "info",
      "log.message": "query io",
      "io_task.id": "123",
    })
    logging.info("io task")
    return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
  with tracer.start_as_current_span("cpu_task") as cputask_span:
    for i in range(1000):
      n = i*i*i
    cputask_span.set_attribute("cpu_task.result", n)

    with tracer.start_as_current_span("cpu_rest") as cpu_rest:
      time.sleep(1)
      cpu_rest.set_attribute("description", "we just pause cpu to rest for 1 second")
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
  # inject trace info to header
  inject(headers)
  logging.info(headers)

  async with httpx.AsyncClient() as client:
    await client.get("http://localhost:8000/", headers=headers,)
  async with httpx.AsyncClient() as client:
    await client.get(f"http://{TARGET_ONE_HOST}:8000/io_task", headers=headers,)
  async with httpx.AsyncClient() as client:
    await client.get(f"http://{TARGET_TWO_HOST}:8000/cpu_task", headers=headers,)
  logging.info("Chain Finished")
  return {"path": "/chain"}


# Function to plus number by get endpoint /plus/i/j to plus i and j number together
@app.get("/plus/{i}/{j}")
async def plus(i: int, j: int):
  return {"result": i + j}


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT)
