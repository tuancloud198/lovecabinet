# Tủ Thương · Love Cabinet

A private memory cabinet for two people, implemented with Django REST Framework, Vue 3, PostgreSQL and MinIO. The Vietnamese UI follows the colors, typography, rounded cards and jar collections in `task/ui-source/`. Layouts adapt to mobile and desktop; dog illustrations are represented by emoji, rather than extracted from the reference screenshots.

## Run with Docker

```sh
cp .env.example .env
docker compose up --build -d
```

Open **http://localhost:8080**. The MinIO console is at **http://localhost:9001**, using the MinIO credentials in `.env`. PostgreSQL and the MinIO object API are internal to the Compose network. MinIO is built from its pinned upstream Go source release, avoiding the removed upstream container images. The init container creates a **private** bucket; the migration container applies committed migrations before the API starts. Database and images persist in named volumes.

Create an account and generate an invitation. In another browser/private window, create a second account and enter the invitation code. The sender can click “Kiểm tra kết nối” to refresh. Invitations expire after 48 hours and may be accepted once. Pairing creates the shared cabinet. Add jars, save memories with photos, react, comment, and add upcoming events. The shared pet progresses with the number of saved memories.

```sh
docker compose logs -f backend
docker compose exec backend python manage.py test common
docker compose down
```

Before exposing this app publicly, set unique secrets in `.env`, configure `ALLOWED_HOSTS`, and serve it behind HTTPS. The provided stack is a local deployment. Tokens are sent in the Authorization header and kept in browser session storage; logging out revokes the token.

## Backend layout

Each domain is a separate Django app: `users`, `couple_invitations`, `couples`, `cabinets`, `jars`, `memories`, `photos`, and `events`.

```text
backend/<app>/
  models.py
  migrations/
  serializers/    # input validation and response representation
  services/       # business rules and persistence operations
  views/          # HTTP handlers and scoped resource lookup
```

`common/services.py` supplies shared couple ownership checks and scoped writes. `common/api.py` supplies reusable viewset behavior. Each app's service layer uses these where applicable. Invitations lock user rows in a transaction to prevent double pairing. A membership is unique per user. Memories, jars, events and photographs are accessible only to the two members of their couple, including when a request changes a parent relation.

Photo uploads accept verified JPEG, PNG and WebP files up to 10 MB each. The database stores object keys, while bytes live in MinIO. Photos are streamed through the authenticated API so the bucket and object URLs are never public. Deleting a cabinet, jar or memory removes its associated MinIO objects first. Keep database and object storage backups together; object deletion and relational transactions cannot be atomic across the two systems.

## API

All routes use `/api/` and trailing slashes. Except registration/login, send `Authorization: Token <token>`.

| Route | Methods / purpose |
| --- | --- |
| `auth/register/`, `auth/login/` | POST; return token and user |
| `auth/logout/` | POST; revoke token |
| `users/me/` | GET, PATCH profile |
| `couple-invitations/` | POST; generate code |
| `couple-invitations/accept/` | POST `{ "code": "..." }`; accept pairing |
| `couples/`, `couples/<id>/` | GET shared couple, members and memory count |
| `cabinets/`, `jars/`, `memories/`, `events/` | CRUD collection and detail routes |
| `memories/<id>/comment/` | POST `{ "text": "..." }` |
| `memories/<id>/react/` | POST; toggle heart |
| `photos/` | POST multipart `memory` ID and `file` |
| `photos/<id>/content/` | GET authenticated image stream |
| `photos/<id>/` | DELETE object and metadata |

## Local development

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

Without `POSTGRES_HOST`, Django uses SQLite for local development and unit tests. For uploads, start MinIO and its bucket initializer with `docker compose up -d minio minio-init`, then expose its object API locally by adding `127.0.0.1:9000:9000` to the MinIO service's ports. The default backend MinIO endpoint is `http://localhost:9000`; credentials match `.env.example`.

```sh
cd frontend
npm ci
npm run dev
```

Vite proxies `/api/` to `localhost:8000`. In another terminal:

```sh
python backend/manage.py check
python backend/manage.py makemigrations --check --dry-run
python backend/manage.py test common
npm run build --prefix frontend
```

The API tests cover authentication, invitation expiry/self-pairing/reuse, partner access, cross-couple read/write protection, reactions, comments, image validation and private image access. Unit tests mock object storage; a running Compose stack exercises actual PostgreSQL and MinIO.

The current implementation uses invitation codes (no QR scanner), a dated event list and memory timeline, and a simple pet growth view. Email delivery, password reset, camera capture, push notifications and animated pet artwork are not included.
