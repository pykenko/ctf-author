# DejaVu

Web exploitation challenge with a standalone per-team instancer.

CTFd is used only as the identity source:

```text
http://103.185.52.173/
```

Players open the instancer, paste their own CTFd access token, and receive a private challenge URL:

```text
http://103.152.242.110:9000/
```

Spawned challenge instances default to:

```text
http://103.152.242.110:<assigned-port>
```

## Behavior

- The player sends their CTFd token to the instancer.
- The instancer validates it with `CTFD_BASE_URL/api/v1/users/me`.
- The instancer extracts the CTFd user and team.
- One team can have only one active DejaVu instance.
- If the same team requests again before expiry, the current URL is returned.
- Instances live for at most 20 minutes by default.
- Expired instances are killed by the instancer cleanup loop, every 60 seconds by default.
- Spawn requests are logged with the CTFd user/team profile.

Players never submit `team_id`; the instancer derives it from CTFd.

## Direct Challenge Test

```bash
cd src
PUBLIC_PORT=19080 COMPOSE_PROJECT_NAME=dejavu-test docker compose up -d --build
```

Open:

```text
http://127.0.0.1:19080/
```

Stop it:

```bash
PUBLIC_PORT=19080 docker compose down -v
```

`src/start.sh` does not run the raw challenge. It starts the standalone instancer Docker container on port `9000`; the challenge containers are spawned later per team on ports from `PORT_MIN` to `PORT_MAX`.

## Instancer API

Run the API:

```bash
cd src/instancer
cp dejavu-instancer.env.example .env
set -a
. ./.env
set +a
./serve.sh
```

Health check:

```bash
curl http://127.0.0.1:9000/health
```

Check the instancer container:

```bash
docker ps --filter name=dejavu-instancer
docker logs dejavu-instancer-instancer-1
```

Player spawn/get-current request:

```bash
curl -X POST http://103.152.242.110:9000/spawn \
  -H 'Authorization: Bearer <PLAYER_CTFD_TOKEN>'
```

For stronger token protection, expose `/spawn` through HTTPS with a reverse
proxy and set `INSTANCER_BIND=127.0.0.1`.

The instancer accepts either `Bearer <token>` or `Token <token>` from the player. When validating against CTFd, it forwards the access token as CTFd expects: `Authorization: Token <token>`.

The same endpoint also accepts JSON:

```bash
curl -X POST http://103.152.242.110:9000/spawn \
  -H 'Content-Type: application/json' \
  -d '{"token":"<PLAYER_CTFD_TOKEN>"}'
```

Example response:

```json
{
  "team_id": "team:12",
  "ctfd_team_id": 12,
  "ctfd_team_name": "example-team",
  "user_id": 44,
  "user_name": "alice",
  "project": "dejavu_team_12",
  "port": 23456,
  "url": "http://103.152.242.110:23456",
  "created_at": 1783500000,
  "expires_at": 1783501200,
  "ttl_seconds": 1200,
  "reused": false
}
```

If another player from the same team requests during those 20 minutes, `reused` is `true` and the same `url` is returned.

## Admin API

Admin endpoints use `INSTANCER_ADMIN_TOKEN`, not a player CTFd token.

List active instances:

```bash
curl http://127.0.0.1:9000/instances \
  -H 'Authorization: Bearer <INSTANCER_ADMIN_TOKEN>'
```

Destroy an instance manually:

```bash
curl -X DELETE 'http://127.0.0.1:9000/instances/team:12' \
  -H 'Authorization: Bearer <INSTANCER_ADMIN_TOKEN>'
```

Run cleanup:

```bash
curl -X POST http://127.0.0.1:9000/cleanup \
  -H 'Authorization: Bearer <INSTANCER_ADMIN_TOKEN>'
```

Manual CLI spawn still exists for operator testing:

```bash
cd src/instancer
DEJAVU_STATE_DIR="$PWD/state" INSTANCE_HOST=103.152.242.110 ./spawn.sh 'team:12'
```

## Production Install

Assuming this repo is copied to `/opt/ctf/DejaVu`:

```bash
sudo cp src/instancer/dejavu-instancer.env.example /etc/dejavu-instancer.env
sudo editor /etc/dejavu-instancer.env
```

Minimum production values:

```env
CTFD_BASE_URL=http://103.185.52.173/
INSTANCE_HOST=103.152.242.110
PUBLIC_SCHEME=http
INSTANCER_BIND=0.0.0.0
INSTANCER_HOST=0.0.0.0
INSTANCER_PORT=9000
INSTANCER_ADMIN_TOKEN=<long-random-secret>
PORT_MIN=20000
PORT_MAX=30000
INSTANCE_TTL_SECONDS=1200
MAX_INSTANCE_TTL_SECONDS=1200
CLEANUP_INTERVAL_SECONDS=60
REQUIRE_TEAM=1
```

Install systemd units:

```bash
sudo cp src/instancer/dejavu-instancer.service /etc/systemd/system/
sudo cp src/instancer/dejavu-cleanup.service /etc/systemd/system/
sudo cp src/instancer/dejavu-cleanup.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now dejavu-instancer.service
sudo systemctl enable --now dejavu-cleanup.timer
```

Firewall:

- allow `INSTANCER_PORT` from players
- allow `PORT_MIN` through `PORT_MAX` from players
- do not expose the Docker daemon

Example:

```bash
sudo ufw allow 9000/tcp
sudo ufw allow 20000:30000/tcp
```

## CTFd Token

Players need a CTFd access token. In CTFd, this is normally generated from the user's profile/settings page. They paste that token into the DejaVu instancer page, not into the challenge app itself.

## Notes

The Compose file uses a named volume instead of `./shared_tmp`. This is required for isolation; otherwise all teams would share `/challenge_tmp/ping.txt`.
