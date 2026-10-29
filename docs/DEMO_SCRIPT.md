# Live Demo Script (about 10 minutes)

## The day before

**Presenting the online version?** Follow the demo-day checklist in [DEPLOYMENT.md](DEPLOYMENT.md) instead of the first three boxes below, and in "Start" just open your Vercel link 2–3 minutes early.

- [ ] Run `setup.bat` on the laptop you will present with (only needed once per laptop).
- [ ] Run `backend\venv\Scripts\python.exe backend\check_models.py` → every line must say **[OK]**.
- [ ] Run the tests: in `backend\`, `venv\Scripts\python.exe -m pytest` → all must pass.
- [ ] Do one full **dry run** of this script and write down the real scores you see (they replace the "expected" notes below).
- [ ] Charge the laptop. The demo works **offline** — no internet needed.
- [ ] Keep `data\samples\resumes\` and `data\raw\job_descriptions\` open in File Explorer.
- [ ] Optional: open `docs\VIVA_QA.md` once more.

## Start (30 seconds)

1. Double-click **`run_all.bat`**. Two black windows open (backend + frontend) and the browser opens `http://127.0.0.1:5173` after about 8 seconds.
2. Point at the green dot: **"API connected"** — the website is talking to the Python backend.

> Say: "The frontend is React, the backend is FastAPI in Python, and the AI models are trained with scikit-learn."

## Demo 1 — Rank candidates for a Data Scientist job (3 minutes)

1. The job description box already contains a Data Scientist description (or paste `data_scientist.txt`).
2. Click **Choose Files**, select **all 8** files in `data\samples\resumes\`, click **Screen resumes**.
3. Expected: **Ananya** (data scientist) at the top, **Rohit** (ML engineer) near the top, **Neha** (accountant) and **Vikram** (HR) at the bottom.
4. On the top card, explain:
   - **Score out of 100** and the fit level (Strong / Good / Moderate / Weak).
   - Blue labels **"Role / Match / Screening: ML model"** — every score came from a trained model.
   - **Pie chart** = skill match; **bars** = matched / missing / extra skills.
   - **Green chips** = skills the job needs and the candidate has; **orange** = missing.
   - Open **"Resume preview"** → matched skills are highlighted, including synonyms (PostgreSQL counts as SQL).

> Say: "Four judges score each resume: the matching model 35%, the skill engine 25%, the screening model 25% and the role classifier 15%."

## Demo 2 — Same resumes, different job (1 minute)

1. Replace the job description with `cybersecurity_analyst.txt`. Click **Screen resumes** again.
2. Expected: **Arjun** (cybersecurity) jumps to the top.

> Say: "Nothing is hard-coded — the ranking changes with the job."

## Demo 3 — Filters (1 minute)

1. Drag **Minimum score** to about 60 → weak candidates disappear.
2. **Filter type: Has skill**, **Skill: python** → only candidates who know Python.
3. Reset both filters (slider to 0, "All skills").

## Demo 4 — Export (30 seconds)

Click **Export CSV** → a ranked spreadsheet downloads; open it in Excel.

## Demo 5 — Feedback loop (1 minute)

1. On the top candidate click **Hire** → "Feedback saved".
2. In **Model operations** click **Status** → feedback rows increase.
3. Click **Snapshot** → a backup version of all models is saved.

> Say: "Recruiter feedback is stored so the models can be retrained and improved over time."

## Demo 6 — For technical examiners (optional, 2 minutes)

- Open **`http://127.0.0.1:8000/docs`** → interactive API documentation. Try `POST /api/analyze-skills`.
- Show `notebooks\02_model_evaluation.ipynb` → confusion matrices, ROC curve, metrics.
- Run `venv\Scripts\python.exe -m pytest` in `backend\` → automated tests pass.

## If something goes wrong

| Problem | Fix |
|---|---|
| "API unavailable" (red dot) | The backend window closed or crashed. Run `run_backend.bat` and read its error. |
| Red **"backup formula"** label on a card | A model file did not load. Run `check_models.py` to see which one; run `setup.bat` again. |
| "Unsupported resume format" | Only PDF, DOCX and TXT are accepted. |
| A PDF gives "Could not extract enough readable text" | It is a scanned image PDF — use another file (no OCR; a known limitation). |
| "No candidates match these filters" | Move the minimum-score slider back to 0 and set Skill to "All skills". |
| Browser did not open | Open `http://127.0.0.1:5173` yourself. |
| Port already in use | Close old backend/frontend windows, then run `run_all.bat` again. |

## 30-second closing

> "This system turns hours of manual resume screening into seconds. It combines three machine-learning models with a transparent skill engine, explains every score, and learns from recruiter feedback. In future I'd add BERT embeddings, automatic retraining and fairness checks."
