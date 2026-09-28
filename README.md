# image-api

Small FastAPI service with a single endpoint that takes a base64 image.

```
POST /image
{"image": "<base64>"}

-> 200 {"message": "accepted"}
-> 400 if the string isn't valid base64
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running with multiple workers

Uvicorn on its own runs a single process. To handle requests in parallel I'm
using gunicorn as a process manager with uvicorn workers. Gunicorn forks N
worker processes that all listen on the same port, and the OS spreads the
incoming connections between them.

```bash
gunicorn -c gunicorn.conf.py main:app
```

The worker count defaults to `2 * cpu + 1` and can be changed with `WORKERS=4`.

Uvicorn can also do this on its own (`uvicorn main:app --workers 4`), but
gunicorn restarts workers that crash or hang, so it's the better choice for
production.

Quick check:

```bash
python load_test.py                                 # 200 requests at once
python load_test.py http://localhost:8000/image 1000
```

It prints which worker PIDs handled the requests (each response has an
`X-Worker-PID` header), so you can see the load being split up.

## Running multiple instances of the server

Workers scale on a single machine. To run several copies of the whole server,
put a load balancer in front of them.

**Docker Compose (what's in this repo):** 3 containers of the API, each with 2
workers, behind nginx on port 8000.

```bash
docker compose up --build
docker compose up --build --scale api=5   # change the number of instances
```

**Without Docker:** start the app on different ports and point nginx at them.

```bash
BIND=0.0.0.0:8001 gunicorn -c gunicorn.conf.py main:app &
BIND=0.0.0.0:8002 gunicorn -c gunicorn.conf.py main:app &
BIND=0.0.0.0:8003 gunicorn -c gunicorn.conf.py main:app &
```

```nginx
upstream api_servers {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

On Kubernetes this would be a Deployment with `replicas: N` behind a
Service. Same idea, it just handles the load balancing and restarts for you.
