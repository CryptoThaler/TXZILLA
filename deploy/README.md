# Runtime Deployment

## GitHub release path
1. Push TXZILLA to GitHub.
2. Merge to `main` or push a `v*` tag.
3. GitHub Actions publishes a container image to GHCR.

## Runtime host procedure
1. Copy `deploy/runtime.env.example` to `deploy/runtime.env`.
2. Set `TXZILLA_IMAGE` to the GHCR image/tag you want to deploy.
3. Set production secrets for PostgreSQL and Redis.
4. Start the stack with:
   `docker compose --env-file deploy/runtime.env -f deploy/docker-compose.runtime.yml up -d`
5. Check:
   - `http://<host>:8000/live`
   - `http://<host>:8000/ready`
   - `http://<host>:8000/providers/runs`

## Notes
- `bootstrap` runs once before the API starts.
- `api`, `worker`, and `beat` all use the same published image.
- county artifacts are persisted in the shared `county_downloads` volume.
- Bexar remains intentionally blocked until BCAD access is formalized.
