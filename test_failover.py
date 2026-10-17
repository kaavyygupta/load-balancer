import subprocess
import sys
import time

import httpx
import pytest

BALANCER = "http://127.0.0.1:8000"


@pytest.fixture
def system():
    procs = {
        "A": subprocess.Popen([sys.executable, "server.py", "A", "8001"]),
        "B": subprocess.Popen([sys.executable, "server.py", "B", "8002"]),
        "C": subprocess.Popen([sys.executable, "server.py", "C", "8003"]),
        "balancer": subprocess.Popen([sys.executable, "balancer.py"]),
    }
    time.sleep(3)
    yield procs
    for p in procs.values():
        p.terminate()
    for p in procs.values():
        p.wait()
    time.sleep(1)          

def test_everything_up(system):
    for _ in range(10):
        response = httpx.get(BALANCER)
        assert response.status_code == 200


def test_failover_when_one_server_dies(system):
    system["B"].terminate()
    system["B"].wait()
    time.sleep(4)          

    answers = []
    for _ in range(10):
        response = httpx.get(BALANCER)
        assert response.status_code == 200
        answers.append(response.json())

    assert "hello from server B" not in answers


def test_all_servers_down_returns_503(system):
    for name in ["A", "B", "C"]:
        system[name].terminate()
        system[name].wait()
    time.sleep(4)

    response = httpx.get(BALANCER)
    assert response.status_code == 503