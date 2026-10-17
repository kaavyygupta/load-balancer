# Load Balancer

A small load balancer I built in Python with FastAPI and HTTPX. It sits in front of three servers, sends requests to them one after another, and keeps working when one of them dies.

I made this to understand how websites stay up when a server crashes. It's a learning project, so don't expect nginx-level stuff.

## What it does

- Takes requests on port 8000 and passes them to one of three backend servers (ports 8001, 8002, 8003).
- Goes in order: A, then B, then C, then back to A (round-robin).
- If a server doesn't answer, it marks it as down and tries the next one, so the person making the request doesn't see an error.
- Every 3 seconds it checks `/health` on every server. If a dead server comes back, it starts getting requests again by itself.
- If all three servers are down it returns a 503 error.
- Has a `/metrics` page that shows how many requests were handled, how many failed, how many each server handled, and which servers are up.

```
Client -> Balancer (8000) -> Server A (8001)
                          -> Server B (8002)
                          -> Server C (8003)
```

## Files

- `server.py` is the backend. You run it with a name and a port, like `python server.py A 8001`. It has `/` (says which server it is) and `/health`.
- `balancer.py` is the load balancer.
- `test_failover.py` has the tests.

## How to run it

You need Python 3.9 or newer.

```
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn httpx pytest
```

Then open four terminals (activate the venv in each one) and run:

```
python server.py A 8001
python server.py B 8002
python server.py C 8003
python balancer.py
```

Go to `http://127.0.0.1:8000` and keep refreshing. The message changes between server A, B and C. Go to `http://127.0.0.1:8000/metrics` to see the numbers.

## Try breaking it

1. Refresh the page a few times and watch it go A, B, C.
2. Press Ctrl+C in server B's terminal.
3. Keep refreshing. Now it's only A and C, with no errors.
4. Start server B again. Within a few seconds it's back in the rotation.
5. Stop all three servers. You get a 503.

## Tests

```
pytest -v
```

The tests start the servers and the balancer themselves, then check three things:
1. Everything works when all servers are up.
2. After killing a server, requests still work and none of them come from the dead one.
3. When all servers are down, the balancer gives a 503.

Close any servers you started by hand before running the tests, or the ports will clash.

## Some choices I made

- Each request to a backend times out after 5 seconds, so one stuck server can't freeze everything.
- A request tries each server at most once, so it can never loop forever.
- I use two ways of finding dead servers. The 3 second health check catches them in the background, but a server can die right after a check. So when a real request fails, the balancer also marks that server as down right away and retries on another one.
- The counter that picks the next server moves forward even when a server is skipped. Without this, one server would get double the traffic when another one was down.

## What it doesn't do

- Everything is stored in memory, so the status and counters reset when the balancer restarts.
- It only forwards `GET /`. Other paths and POST requests aren't handled (retrying a POST could do the same thing twice, so that needs more care).
- One failed health check is enough to mark a server as down. A real system would wait for a few failures in a row.
- No circuit breaker or dashboard. Maybe later.