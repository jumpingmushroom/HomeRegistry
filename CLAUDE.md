# HomeRegistry - Claude Code Instructions

## Deployment Workflow

After completing a new feature or fix, always:

1. **Rebuild and test locally:**
   ```bash
   docker compose up -d --build && sleep 3 && docker compose logs --tail=50 backend
   ```
   Review the startup logs to verify the backend starts without errors.

2. **Commit and push to GitHub:**
   ```bash
   git add -A && git commit -m "description" && git push origin main
   ```

3. **Deploy to production server:**
   ```bash
   ssh -p 2222 equ@vault.jumpingmushroom.com "cd /docker/HomeRegistry && git pull origin main && docker compose up -d --build"
   ```

## Server Details

- **Host:** vault.jumpingmushroom.com
- **SSH Port:** 2222
- **User:** equ
- **Project path:** /docker/HomeRegistry
- **Frontend port:** 8180

## Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Vue 3 with Vite
- **Database:** SQLite
- **Containerization:** Docker Compose
