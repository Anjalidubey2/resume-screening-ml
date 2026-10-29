# Put the Project Online (free)

About **40 minutes**, done once. Result: a link like `https://resume-screening-ml.vercel.app` that works on any phone or PC.

| Part | Service | What runs there |
|---|---|---|
| A | **GitHub** | Stores your code (also your GitHub submission) |
| B | **Render** (free) | The Python backend + AI models |
| C | **Vercel** (free) | The React website |
| D | — | Connect B and C |

You need a GitHub account. Render and Vercel let you sign in **with GitHub**, so no extra passwords. Both are free; do **not** enter card details. If either service asks for payment, stop and check that you picked the **Free** plan.

---

## A. Upload the code to GitHub (10 min)

1. In the project folder, double-click **`prepare_upload.bat`**. It creates a clean folder called **`resume-screening-ml-github`** next to the project (87 files, no `venv` or `node_modules`).
2. Go to **github.com** → sign in → **+** (top right) → **New repository**.
   - Name: `resume-screening-ml`
   - **Public**
   - Do **not** tick "Add a README file" (the project already has one)
   - Click **Create repository**.
3. On the new empty page, click the link **"uploading an existing file"**.
4. Open the `resume-screening-ml-github` folder, press **Ctrl+A**, and **drag everything** onto the GitHub page. Wait until every file shows in the list.
5. Commit message: `Initial upload` → **Commit changes**.
6. Check: you should see `backend`, `frontend`, `models`, `docs`… and the README below them.

> If GitHub says there are too many files, upload in two rounds: first `backend` and `models`, then everything else.

## B. Backend on Render (15 min)

1. Go to **render.com** → **Get Started** → **GitHub** → authorise.
2. **+ New** → **Web Service** → choose your `resume-screening-ml` repository (click "Configure account" and allow access if it isn't listed).
3. Fill in exactly:

| Field | Value |
|---|---|
| Name | `resume-screening-api` |
| Language | `Python 3` |
| Branch | `main` |
| Root Directory | **leave empty** (the models live outside `backend/`, and Render hides files outside the root directory) |
| Build Command | `pip install -r backend/requirements.txt` |
| Start Command | `uvicorn --app-dir backend main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |

4. Under **Environment Variables** add: `PYTHON_VERSION` = `3.11.11`
5. Click **Deploy Web Service**. Wait 3–8 minutes until it says **Live**.
6. Copy your URL from the top of the page, e.g. `https://resume-screening-api-abcd.onrender.com`.
7. Test it in the browser:
   - `<your URL>/health` → shows `{"status":"ok"}`
   - `<your URL>/docs` → the interactive API page

## C. Website on Vercel (10 min)

1. Go to **vercel.com** → **Sign Up** → **Hobby** → **Continue with GitHub**.
2. **Add New…** → **Project** → **Import** your `resume-screening-ml` repository.
3. **Root Directory** → **Edit** → choose **`frontend`**. Framework should show **Vite**.
4. Open **Environment Variables** and add: `VITE_API_BASE` = your Render URL from B6.
5. Click **Deploy**. After about a minute you get a link like `https://resume-screening-ml-xyz.vercel.app`.

## D. Connect them (5 min)

The backend only accepts requests from websites you allow.

1. In **Render** → your service → **Environment** → **Add Environment Variable**:
   `BACKEND_CORS_ORIGINS` = your Vercel link from C5 (starts with `https://`).
2. **Save, rebuild, and deploy**. Wait until **Live** again.
3. Open your **Vercel link**. The first time it may say *"Connecting to API… (a sleeping free server can take up to a minute)"* — then the dot turns **green**.
4. Upload resumes from `data/samples/resumes/` and click **Screen resumes**. Check the labels on the cards: blue **"ML model"** means the AI models are working.

**Send both links to Claude** — it will test the health check, the API, real resume scoring, whether every score comes from ML, and the connection between the two.

---

## Changing the code later

Upload the changed files to GitHub again (**Add file → Upload files**, same folders). Render and Vercel redeploy automatically within a few minutes.

## Free-plan facts

- The backend **sleeps after 15 minutes** without visitors and takes **about 1 minute** to wake.
- Feedback, CSV copies and model snapshots saved on the server are **lost when it restarts** (the CSV download in your browser is not affected).
- 750 free server hours per month — more than enough.

## Demo-day checklist (online)

- [ ] Open your Vercel link **2–3 minutes before** presenting so the server wakes up.
- [ ] If college Wi-Fi is weak, use your **phone's hotspot**.
- [ ] Keep a short **screen recording** of a working demo as a backup in case the internet fails.

## If something goes wrong

| What you see | What to do |
|---|---|
| Render build **Failed** | Open **Logs**, copy the last 30 lines, and send them to Claude. |
| Render logs say **out of memory** | Send the logs to Claude — the free plan has about 512 MB. |
| Website stuck on *"API unavailable – retrying"* for more than 2 minutes | Check Render shows **Live**; open `<Render URL>/health` directly. |
| Website works but every request fails | `BACKEND_CORS_ORIGINS` on Render must be exactly your Vercel link (`https://…`). |
| Website still talks to the wrong server after changing `VITE_API_BASE` | Vercel uses it only when building: **Deployments → ⋯ → Redeploy**. |
| Red **"backup formula"** labels on the cards | A model didn't load. Send the Render **Logs** (lines with "failed") to Claude. |
