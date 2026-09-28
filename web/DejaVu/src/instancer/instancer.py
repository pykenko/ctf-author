#!/usr/bin/env python3
import argparse
import hmac
import json
import os
import random
import re
import socket
import subprocess
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin
from urllib.request import Request, urlopen

try:
    import fcntl
except ImportError:  # pragma: no cover - this instancer is intended for Linux.
    fcntl = None


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE_DIR = ROOT_DIR if (ROOT_DIR / "docker-compose.yml").exists() else ROOT_DIR / "src"
DEFAULT_STATE_DIR = Path(os.environ.get("DEJAVU_STATE_DIR", "/var/lib/dejavu-instancer"))
TEAM_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")


class InstancerError(Exception):
    pass


def now() -> int:
    return int(time.time())


def config() -> dict:
    return {
        "compose_dir": Path(os.environ.get("DEJAVU_COMPOSE_DIR", DEFAULT_COMPOSE_DIR)),
        "state_dir": Path(os.environ.get("DEJAVU_STATE_DIR", DEFAULT_STATE_DIR)),
        "ctfd_base_url": os.environ.get("CTFD_BASE_URL", "http://103.185.52.173/").rstrip("/") + "/",
        "instance_host": os.environ.get("INSTANCE_HOST", "103.152.242.110"),
        "public_scheme": os.environ.get("PUBLIC_SCHEME", "http"),
        "port_min": int(os.environ.get("PORT_MIN", "20000")),
        "port_max": int(os.environ.get("PORT_MAX", "30000")),
        "default_ttl": int(os.environ.get("INSTANCE_TTL_SECONDS", "1200")),
        "max_ttl": int(os.environ.get("MAX_INSTANCE_TTL_SECONDS", "1200")),
        "compose_build": os.environ.get("COMPOSE_BUILD", "1") != "0",
        "require_team": os.environ.get("REQUIRE_TEAM", "1") != "0",
        "challenge_id": os.environ.get("CTFD_CHALLENGE_ID", ""),
        "cleanup_interval": int(os.environ.get("CLEANUP_INTERVAL_SECONDS", "60")),
    }


def validate_team_id(team_id: str) -> str:
    if not team_id or not TEAM_RE.fullmatch(team_id):
        raise InstancerError("team_id must be 1-80 chars: letters, numbers, dot, underscore, colon, or dash")
    return team_id


def project_name(team_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]", "_", team_id).lower()
    return f"dejavu_{safe}"


def ensure_state(cfg: dict) -> tuple[Path, Path]:
    state_dir = cfg["state_dir"]
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "instances.json"
    lock_file = state_dir / "instances.lock"
    if not state_file.exists():
        state_file.write_text("{}\n")
    return state_file, lock_file


@contextmanager
def locked_state(cfg: dict):
    state_file, lock_file = ensure_state(cfg)
    with lock_file.open("w") as lock:
        if fcntl is not None:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            try:
                state = json.loads(state_file.read_text())
            except json.JSONDecodeError:
                state = {}
            yield state
            tmp = state_file.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
            tmp.replace(state_file)
        finally:
            if fcntl is not None:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def compose_cmd() -> list[str]:
    return ["docker", "compose"]


def run_compose(cfg: dict, project: str, port: int | None, args: list[str]) -> None:
    env = os.environ.copy()
    env["COMPOSE_PROJECT_NAME"] = project
    if port is None and "up" in args:
        raise InstancerError("PUBLIC_PORT is required for docker compose up")
    env["PUBLIC_PORT"] = str(port if port is not None else cfg["port_min"])
    result = subprocess.run(
        compose_cmd() + args,
        cwd=cfg["compose_dir"],
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise InstancerError(detail or f"docker compose {' '.join(args)} failed")


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
        except OSError:
            return False
    return True


def choose_port(cfg: dict, state: dict) -> int:
    used = {int(item["port"]) for item in state.values() if "port" in item}
    candidates = list(range(cfg["port_min"], cfg["port_max"] + 1))
    random.shuffle(candidates)
    for port in candidates:
        if port not in used and port_is_free(port):
            return port
    raise InstancerError("no free port available in configured range")


def instance_url(cfg: dict, port: int) -> str:
    return f"{cfg['public_scheme']}://{cfg['instance_host']}:{port}"


def bounded_ttl(cfg: dict, ttl_seconds: int | None = None) -> int:
    requested = ttl_seconds or cfg["default_ttl"]
    return max(1, min(int(requested), cfg["max_ttl"]))


def spawn(team_id: str, ttl_seconds: int | None = None, owner: dict | None = None) -> dict:
    cfg = config()
    validate_team_id(team_id)
    ttl = bounded_ttl(cfg, ttl_seconds)
    with locked_state(cfg) as state:
        existing = state.get(team_id)
        if existing and int(existing.get("expires_at", 0)) > now():
            response = dict(existing)
            response["reused"] = True
            if "port" in response:
                response["url"] = instance_url(cfg, int(response["port"]))
                existing["url"] = response["url"]
            if owner:
                existing["last_requested_by"] = owner
                log_spawn(response, owner, reused=True)
            return response

        if existing:
            destroy(team_id, missing_ok=True, write_state=False)
            state.pop(team_id, None)

        port = choose_port(cfg, state)
        project = project_name(team_id)
        args = ["up", "-d"]
        if cfg["compose_build"]:
            args.append("--build")
        run_compose(cfg, project, port, args)

        record = {
            "team_id": team_id,
            "project": project,
            "port": port,
            "url": instance_url(cfg, port),
            "created_at": now(),
            "expires_at": now() + ttl,
            "ttl_seconds": ttl,
            "reused": False,
        }
        if owner:
            record["created_by"] = owner
            record["last_requested_by"] = owner
        state[team_id] = record
        log_spawn(record, owner, reused=False)
        return record


def access_token(header: str | None) -> str:
    if not header:
        return ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() not in {"bearer", "token"} or not token.strip():
        return ""
    return token.strip()


def ctfd_get(cfg: dict, path: str, token: str) -> dict:
    url = urljoin(cfg["ctfd_base_url"], path.lstrip("/"))
    req = Request(
        url,
        headers={
            "Authorization": f"Token {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=8) as res:
            content_type = res.headers.get("Content-Type", "")
            body = res.read().decode()
            if "application/json" not in content_type.lower():
                raise InstancerError("invalid CTFd token")
            return json.loads(body)
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise InstancerError("invalid CTFd token") from exc
        raise InstancerError(f"CTFd API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise InstancerError(f"could not reach CTFd API: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise InstancerError("invalid CTFd token") from exc


def verify_ctfd_token(token: str) -> dict:
    if not token:
        raise InstancerError("missing CTFd bearer token")

    cfg = config()
    payload = ctfd_get(cfg, "/api/v1/users/me", token)
    if payload.get("success") is False:
        raise InstancerError("invalid CTFd token")

    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    user_id = data.get("id") or data.get("user_id")
    user_name = data.get("name") or data.get("username")
    team = data.get("team") if isinstance(data.get("team"), dict) else {}
    team_id = data.get("team_id") or team.get("id")
    team_name = data.get("team_name") or team.get("name")

    if cfg["require_team"] and not team_id:
        raise InstancerError("your CTFd account is not on a team")
    if not user_id:
        raise InstancerError("CTFd token did not return a user profile")

    scope_id = f"team:{team_id}" if team_id else f"user:{user_id}"
    owner = {
        "user_id": user_id,
        "user_name": user_name,
        "team_id": team_id,
        "team_name": team_name,
        "scope_id": scope_id,
    }
    if cfg["challenge_id"]:
        owner["challenge_id"] = cfg["challenge_id"]
    return owner


def spawn_for_player(token: str) -> dict:
    owner = verify_ctfd_token(token)
    record = spawn(owner["scope_id"], owner=owner)
    record["user_id"] = owner["user_id"]
    record["user_name"] = owner["user_name"]
    record["ctfd_team_id"] = owner["team_id"]
    record["ctfd_team_name"] = owner["team_name"]
    return record


def log_spawn(record: dict, owner: dict | None, reused: bool) -> None:
    if not owner:
        return
    status = "reused" if reused else "spawned"
    print(
        json.dumps(
            {
                "event": "instance_request",
                "status": status,
                "team_key": record.get("team_id"),
                "url": record.get("url"),
                "expires_at": record.get("expires_at"),
                "user_id": owner.get("user_id"),
                "user_name": owner.get("user_name"),
                "ctfd_team_id": owner.get("team_id"),
                "ctfd_team_name": owner.get("team_name"),
            },
            sort_keys=True,
        ),
        flush=True,
    )


def destroy(team_id: str, missing_ok: bool = False, write_state: bool = True) -> dict:
    cfg = config()
    validate_team_id(team_id)

    def remove_from_state(state: dict) -> dict:
        record = state.pop(team_id, None)
        project = record["project"] if record else project_name(team_id)
        port = int(record["port"]) if record and "port" in record else None
        run_compose(cfg, project, port, ["down", "-v", "--remove-orphans"])
        return record or {"team_id": team_id, "project": project}

    if write_state:
        with locked_state(cfg) as state:
            if team_id not in state and not missing_ok:
                raise InstancerError("instance not found")
            return remove_from_state(state)

    state_file, _ = ensure_state(cfg)
    try:
        state = json.loads(state_file.read_text())
    except json.JSONDecodeError:
        state = {}
    if team_id not in state and not missing_ok:
        raise InstancerError("instance not found")
    return remove_from_state(state)


def list_instances() -> dict:
    cfg = config()
    with locked_state(cfg) as state:
        return dict(state)


def cleanup() -> dict:
    cfg = config()
    removed = []
    failed = []
    with locked_state(cfg) as state:
        expired = [team_id for team_id, item in state.items() if int(item.get("expires_at", 0)) <= now()]
        for team_id in expired:
            record = dict(state[team_id])
            try:
                port = int(record["port"]) if "port" in record else None
                run_compose(cfg, record["project"], port, ["down", "-v", "--remove-orphans"])
                record.pop("cleanup_error", None)
                record.pop("last_cleanup_attempt_at", None)
                removed.append(record)
            except InstancerError as exc:
                state[team_id]["cleanup_error"] = str(exc)
                state[team_id]["last_cleanup_attempt_at"] = now()
                failed_record = dict(state[team_id])
                failed.append(failed_record)
            else:
                state.pop(team_id, None)
    return {"removed": removed, "failed": failed}


def cleanup_loop(interval_seconds: int) -> None:
    while True:
        try:
            result = cleanup()
            if result["removed"] or result["failed"]:
                print(
                    json.dumps(
                        {
                            "event": "cleanup",
                            "removed": len(result["removed"]),
                            "failed": len(result["failed"]),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
        except Exception as exc:
            print(
                json.dumps({"event": "cleanup_error", "error": str(exc)}, sort_keys=True),
                flush=True,
            )
        time.sleep(interval_seconds)


class Handler(BaseHTTPRequestHandler):
    server_version = "DejaVuInstancer/1.0"

    INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DejaVu Instancer</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 48px auto; padding: 0 18px; line-height: 1.5; }
    input, button { font: inherit; padding: 10px; }
    input { width: min(100%, 520px); }
    button { cursor: pointer; }
    pre { background: #f4f4f4; padding: 14px; overflow: auto; }
  </style>
</head>
<body>
  <h1>DejaVu Instancer</h1>
  <form id="spawn">
    <p><label>CTFd access token<br><input name="token" type="password" autocomplete="off" required></label></p>
    <button type="submit">Start or Get Instance</button>
  </form>
  <pre id="out"></pre>
  <script>
    document.getElementById('spawn').addEventListener('submit', async (event) => {
      event.preventDefault();
      const token = new FormData(event.target).get('token');
      const out = document.getElementById('out');
      out.textContent = 'Requesting instance...';
      const res = await fetch('/spawn', {method: 'POST', headers: {Authorization: 'Bearer ' + token}});
      const data = await res.json();
      if (!res.ok) {
        out.textContent = data.error || 'Request failed';
        return;
      }
      out.innerHTML = 'URL: <a href="' + data.url + '" target="_blank" rel="noreferrer">' + data.url + '</a>\\nExpires: ' + new Date(data.expires_at * 1000).toLocaleString() + '\\nReused: ' + data.reused;
    });
  </script>
</body>
</html>
"""

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode())

    def write_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def write_html(self, status: int, body: str) -> None:
        payload = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def authorize_admin(self) -> bool:
        token = os.environ.get("INSTANCER_ADMIN_TOKEN", "").strip()
        if not token:
            self.write_json(503, {"error": "INSTANCER_ADMIN_TOKEN is not configured"})
            return False
        expected = f"Bearer {token}"
        if hmac.compare_digest(self.headers.get("Authorization", ""), expected):
            return True
        self.write_json(401, {"error": "unauthorized"})
        return False

    def do_GET(self) -> None:
        try:
            if self.path == "/":
                self.write_html(200, self.INDEX_HTML)
            elif self.path == "/health":
                self.write_json(200, {"ok": True})
            elif self.path == "/instances":
                if not self.authorize_admin():
                    return
                self.write_json(200, {"instances": list_instances()})
            elif self.path.startswith("/instances/"):
                if not self.authorize_admin():
                    return
                team_id = unquote(self.path.removeprefix("/instances/"))
                instances = list_instances()
                if team_id not in instances:
                    self.write_json(404, {"error": "instance not found"})
                else:
                    self.write_json(200, instances[team_id])
            else:
                self.write_json(404, {"error": "not found"})
        except Exception as exc:
            self.write_json(500, {"error": str(exc)})

    def do_POST(self) -> None:
        try:
            if self.path == "/spawn":
                token = access_token(self.headers.get("Authorization"))
                if not token:
                    body = self.read_json()
                    token = body.get("token", "")
                self.write_json(201, spawn_for_player(token))
            elif self.path == "/instances":
                if not self.authorize_admin():
                    return
                body = self.read_json()
                item = spawn(body.get("team_id", ""), body.get("ttl_seconds"))
                self.write_json(201, item)
            elif self.path == "/cleanup":
                if not self.authorize_admin():
                    return
                self.write_json(200, cleanup())
            else:
                self.write_json(404, {"error": "not found"})
        except InstancerError as exc:
            status = 401 if "token" in str(exc).lower() else 400
            self.write_json(status, {"error": str(exc)})
        except Exception as exc:
            self.write_json(500, {"error": str(exc)})

    def do_DELETE(self) -> None:
        if not self.authorize_admin():
            return
        try:
            if self.path.startswith("/instances/"):
                team_id = unquote(self.path.removeprefix("/instances/"))
                self.write_json(200, destroy(team_id))
            else:
                self.write_json(404, {"error": "not found"})
        except InstancerError as exc:
            self.write_json(404, {"error": str(exc)})
        except Exception as exc:
            self.write_json(500, {"error": str(exc)})


def serve(host: str, port: int) -> None:
    if not os.environ.get("INSTANCER_ADMIN_TOKEN", "").strip():
        raise InstancerError("INSTANCER_ADMIN_TOKEN must be set before starting the HTTP server")
    cfg = config()
    if cfg["cleanup_interval"] > 0:
        worker = threading.Thread(target=cleanup_loop, args=(cfg["cleanup_interval"],), daemon=True)
        worker.start()
        print(f"DejaVu cleanup loop running every {cfg['cleanup_interval']} seconds", flush=True)
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"DejaVu instancer listening on http://{host}:{port}", flush=True)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="DejaVu per-team Docker Compose instancer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    spawn_p = sub.add_parser("spawn")
    spawn_p.add_argument("team_id")
    spawn_p.add_argument("--ttl-seconds", type=int)

    destroy_p = sub.add_parser("destroy")
    destroy_p.add_argument("team_id")

    sub.add_parser("list")
    sub.add_parser("cleanup")

    serve_p = sub.add_parser("serve")
    serve_p.add_argument("--host", default=os.environ.get("INSTANCER_HOST", "127.0.0.1"))
    serve_p.add_argument("--port", type=int, default=int(os.environ.get("INSTANCER_PORT", "9000")))

    args = parser.parse_args()

    try:
        if args.cmd == "spawn":
            print(json.dumps(spawn(args.team_id, args.ttl_seconds), indent=2))
        elif args.cmd == "destroy":
            print(json.dumps(destroy(args.team_id), indent=2))
        elif args.cmd == "list":
            print(json.dumps(list_instances(), indent=2, sort_keys=True))
        elif args.cmd == "cleanup":
            print(json.dumps(cleanup(), indent=2))
        elif args.cmd == "serve":
            serve(args.host, args.port)
    except InstancerError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
