# Tủ Thương · Love Cabinet

A private memory cabinet for two people, implemented with Django REST Framework, Vue 3, PostgreSQL and MinIO. The Vietnamese UI follows the screens and design system in `task/ui-source/`: a phone-width app with a bottom navigation (Lịch, Tủ, Camera, Nhân Vật, Hồ Sơ), onboarding and pairing flows, jars on wooden cabinet shelves, the pet's growth stages and a month calendar. The dog characters in `frontend/src/assets/characters/` are cropped from those reference images. On wider screens the app is shown as a centered phone-width column.

## Run with Docker

```sh
cp .env.example .env
docker compose up --build -d
```

Open **http://localhost:8080**. The MinIO console is at **http://localhost:9001**, using the MinIO credentials in `.env`. PostgreSQL and the MinIO object API are internal to the Compose network. MinIO is built from its pinned upstream Go source release, avoiding the removed upstream container images. The init container creates a **private** bucket; the migration container applies committed migrations before the API starts. Database and images persist in named volumes.

Every account gets a unique tag such as `#A7K2M9QX` (`#` + 8 uppercase letters and digits), shown with a copy button on the pairing screen and profile. Create two accounts in separate browser/private windows, copy one account's tag, and send an invitation to it from the other. The recipient sees the invitation after clicking “Kiểm tra lời mời · Làm mới” and accepts or declines it. Invitations expire after 48 hours and may be accepted once, by the recipient only. Pairing creates the shared cabinet. Add jars, save memories with photos, react, comment, and add upcoming events. The shared pet progresses with the number of saved memories.

```sh
docker compose logs -f backend
docker compose exec backend python manage.py test common
docker compose down
```

Before exposing this app publicly, set unique secrets in `.env`, configure `ALLOWED_HOSTS`, and serve it behind HTTPS. The provided stack is a local deployment. Tokens are sent in the Authorization header and kept in browser local storage, so users stay signed in across browser restarts; logging out (in any tab) revokes the token.

## Sign in with Google

1. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials), create an **OAuth client ID** of type **Web application** (configure the OAuth consent screen first if asked).
2. Under **Authorized JavaScript origins**, add every origin the app is opened from, e.g. `http://localhost:8080` and `http://localhost:5173`. No redirect URI or client secret is needed.
3. Put the client ID in `.env` as `GOOGLE_CLIENT_ID=…apps.googleusercontent.com` and restart the backend.

The button uses Google Identity Services: the browser receives a Google ID token, and `POST /api/auth/google/` verifies its signature, audience and verified email before returning the usual API token. The first sign-in creates an account (username = the Gmail address, no password) and opens profile setup; later sign-ins match the Google account ID. The backend must be able to reach `www.googleapis.com` to fetch Google's signing keys. With `GOOGLE_CLIENT_ID` empty the button is hidden.

## Images

The frontend and backend are separate images, defined in `infra/`. Build them from the repo root:

```sh
docker build -f infra/backend/Dockerfile -t lovecabinet-backend .
docker build -f infra/frontend/Dockerfile -t lovecabinet-frontend .
```

PostgreSQL and object storage are separate services the backend connects to through env vars (`POSTGRES_*`, `MINIO_*`; see the comments in `infra/backend/Dockerfile`). The frontend's nginx forwards `/api/` to `BACKEND_URL` (default `http://backend:8000`).

## Backend layout

Each domain is a separate Django app: `users`, `couple_invitations`, `couples`, `cabinets`, `jars`, `memories`, `photos`, and `events`.

```text
backend/<app>/
  models.py
  migrations/
  serializers/    # <entity>_serializers.py: input validation and response representation
  services/       # business rules and persistence operations
  views/          # HTTP handlers and scoped resource lookup
```

`common/services.py` supplies shared couple ownership checks and scoped writes. `common/api.py` supplies reusable viewset behavior. Each app's service layer uses these where applicable. Invitations lock user rows in a transaction to prevent double pairing. A membership is unique per user. Memories, jars, events and photographs are accessible only to the two members of their couple, including when a request changes a parent relation.

Photo uploads accept verified JPEG, PNG and WebP files up to 10 MB each. The database stores object keys (`{jar id}/{memory id}/{random}.{ext}`; moved when a memory changes jar), while bytes live in MinIO. Photos are streamed through the authenticated API so the bucket and object URLs are never public. Deleting a cabinet, jar or memory removes its associated MinIO objects first. Keep database and object storage backups together; object deletion and relational transactions cannot be atomic across the two systems.

## API

All routes use `/api/` and trailing slashes. Except registration/login, send `Authorization: Token <token>`.

| Route | Methods / purpose |
| --- | --- |
| `auth/register/`, `auth/login/` | POST; return token and user |
| `auth/logout/` | POST; revoke token |
| `auth/google/` | POST `{ "credential": "<Google ID token>" }`; returns token, user and `created` |
| `auth/config/` | GET public sign-in settings (`google_client_id`) |
| `users/me/` | GET, PATCH profile (`tag` is read-only) |
| `couple-invitations/` | GET pending `received` and `sent` invitations; POST `{ "tag": "#A7K2M9QX" }` to invite that user |
| `couple-invitations/<id>/accept/` | POST; recipient accepts pairing |
| `couple-invitations/<id>/decline/` | POST; recipient declines (204); the sender may invite again |
| `couples/`, `couples/<id>/` | GET shared couple, members and memory count; PATCH `name`, `anniversary`, `pet_name`, `pet_type` (`dog`, `cat`, `capybara`) |
| `cabinets/`, `jars/`, `memories/`, `events/` | CRUD collection and detail routes |
| `memories/<id>/comment/` | POST `{ "text": "..." }` |
| `memories/<id>/react/` | POST; toggle heart |
| `photos/` | POST multipart `memory` ID and `file` |
| `photos/<id>/content/` | GET authenticated image stream |
| `photos/<id>/` | DELETE object and metadata |

## Local development

```sh
uv venv
uv pip install -r backend/requirements.txt
uv run python backend/manage.py migrate
uv run python backend/manage.py runserver
```

Without `POSTGRES_HOST`, Django uses SQLite for local development and unit tests. For uploads, start MinIO and its bucket initializer with `docker compose up -d minio minio-init`, then expose its object API locally by adding `127.0.0.1:9000:9000` to the MinIO service's ports. The default backend MinIO endpoint is `http://localhost:9000`; credentials match `.env.example`.

```sh
cd frontend
npm ci
npm run dev
```

Vite proxies `/api/` to `localhost:8000`. In another terminal:

```sh
uv run python backend/manage.py check
uv run python backend/manage.py makemigrations --check --dry-run
uv run python backend/manage.py test common
npm run build --prefix frontend
```

The API tests cover authentication, invitation expiry/self-pairing/reuse, partner access, cross-couple read/write protection, reactions, comments, image validation and private image access. Unit tests mock object storage; a running Compose stack exercises actual PostgreSQL and MinIO.

The current implementation uses invitation codes (no QR scanner), a dated event list and memory timeline, and a simple pet growth view. Email delivery, password reset, camera capture, push notifications and animated pet artwork are not included.
