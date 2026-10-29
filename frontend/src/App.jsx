import { useEffect, useMemo, useState } from "react";
import {
  checkHealth,
  createModelVersion,
  exportRankings,
  getModelStatus,
  recommendUploadedResume,
  retrainModels,
  submitFeedback,
} from "./api.js";

const SAMPLE_JD =
  "Hiring a data scientist with Python, SQL, machine learning, NLP, model evaluation, API development, Docker, and AWS experience.";

function classNames(...values) {
  return values.filter(Boolean).join(" ");
}

function formatPercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function HighlightedText({ text, terms }) {
  const words = [...new Set((terms || []).filter(Boolean))].sort((a, b) => b.length - a.length);
  if (!text || words.length === 0) return <p>{text || "No preview available."}</p>;

  // Whole words only, so "java" does not light up inside "javascript".
  const pattern = new RegExp(`(?<!\\w)(${words.map(escapeRegExp).join("|")})(?!\\w)`, "gi");
  const parts = text.split(pattern);

  return (
    <p>
      {parts.map((part, index) =>
        index % 2 === 1 ? <mark key={index}>{part}</mark> : <span key={index}>{part}</span>
      )}
    </p>
  );
}

const MODEL_LABELS = { role: "Role", match: "Match", screening: "Screening" };

function ModelSources({ sources }) {
  const entries = Object.entries(sources || {});
  if (!entries.length) return null;

  return (
    <div className="model-sources">
      {entries.map(([name, source]) => (
        <span key={name} className={classNames("source-chip", source === "ml" ? "ml" : "fallback")}>
          {MODEL_LABELS[name] || name}: {source === "ml" ? "ML model" : "backup formula"}
        </span>
      ))}
    </div>
  );
}

function PieChart({ score }) {
  const match = Math.max(0, Math.min(100, Number(score) || 0));
  const gap = 100 - match;
  const background = `conic-gradient(var(--accent) 0 ${match}%, var(--danger-soft) ${match}% 100%)`;

  return (
    <div className="pie-wrap" aria-label={`Match ${match.toFixed(0)} percent, gap ${gap.toFixed(0)} percent`}>
      <div className="pie" style={{ background }}>
        <span>{match.toFixed(0)}%</span>
      </div>
      <div className="chart-legend">
        <span><i className="legend-dot match" /> Match</span>
        <span><i className="legend-dot gap" /> Gap</span>
      </div>
    </div>
  );
}

const BREAKDOWN_PARTS = [
  ["match_probability_component", "Match", "35% x resume-job match probability"],
  ["skill_match_component", "Skills", "25% x share of the job's skills found"],
  ["screening_score_component", "Screening", "25% x AI score x skill match"],
  ["role_confidence_component", "Role", "15% x probability the person's field suits the job"],
];

function ScoreBreakdown({ breakdown, total }) {
  if (!breakdown) return null;

  return (
    <p className="score-breakdown">
      <span>Score built from:</span>
      {BREAKDOWN_PARTS.map(([key, label, hint], index) => (
        <span key={key} title={hint}>
          {index > 0 && "+ "}
          {label} <strong>{Number(breakdown[key] || 0).toFixed(1)}</strong>
        </span>
      ))}
      <span>
        = <strong>{Number(total).toFixed(1)}</strong>
      </span>
    </p>
  );
}

function SkillBars({ matched = [], missing = [], extra = [] }) {
  const values = [
    { label: "Matched", value: matched.length, tone: "good" },
    { label: "Missing", value: missing.length, tone: "warn" },
    { label: "Extra", value: extra.length, tone: "neutral" },
  ];
  const max = Math.max(...values.map((item) => item.value), 1);

  return (
    <div className="bars">
      {values.map((item) => (
        <div className="bar-row" key={item.label}>
          <span>{item.label}</span>
          <div className="bar-track">
            <div className={classNames("bar-fill", item.tone)} style={{ width: `${(item.value / max) * 100}%` }} />
          </div>
          <strong>{item.value}</strong>
        </div>
      ))}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function buildCsvContent(rows) {
  const headers = [
    "rank",
    "filename",
    "final_score",
    "fit_level",
    "match_probability",
    "skill_match_score",
    "screening_decision",
    "hire_probability",
    "ai_score",
    "matched_skills",
    "missing_skills",
    "recommended_skills",
  ];

  const csvRows = rows.map((row, index) => ({
    rank: index + 1,
    filename: row.filename,
    final_score: row.final_score,
    fit_level: row.fit_level,
    match_probability: row.match_probability,
    skill_match_score: row.skill_match_score,
    screening_decision: row.screening_decision,
    hire_probability: row.hire_probability,
    ai_score: row.ai_score,
    matched_skills: (row.matched_skills || []).join("; "),
    missing_skills: (row.missing_skills || []).join("; "),
    recommended_skills: (row.recommended_skills || []).join("; "),
  }));

  const escapeCell = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  return `\uFEFF${[headers.join(","), ...csvRows.map((row) => headers.map((header) => escapeCell(row[header])).join(","))].join("\n")}`;
}

function downloadCsv(rows) {
  const blob = new Blob([buildCsvContent(rows)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  const link = document.createElement("a");
  link.href = url;
  link.download = `resume_rankings_${stamp}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

const FEEDBACK_ACTIONS = [
  { type: "good_match", label: "Good Match" },
  { type: "wrong_match", label: "Wrong Match" },
  { type: "hire", label: "Hire" },
  { type: "reject", label: "Reject" },
  { type: "correct_role", label: "Correct Role" },
  { type: "wrong_role", label: "Wrong Role" },
];

function ResultCard({ result, rank, onFeedback, feedbackStatus }) {
  const matchPercent = Math.round((result.skill_match_score || 0) * 100);
  const topRole = result.role_predictions?.[0]?.role || "Unknown";

  return (
    <article className="result-card">
      <div className="result-head">
        <div>
          <span className="rank">#{rank}</span>
          <h3>{result.filename}</h3>
          <p>
            {result.fit_level} · top role: {topRole}
            {result.screening_role && <> · screened as: {result.screening_role}</>}
          </p>
        </div>
        <div className="score-pill">{Number(result.final_score).toFixed(1)}</div>
      </div>

      <ModelSources sources={result.model_sources} />
      <ScoreBreakdown breakdown={result.score_breakdown} total={result.final_score} />

      <div className="result-grid">
        <div className="chart-panel">
          <PieChart score={matchPercent} />
        </div>
        <div className="chart-panel">
          <SkillBars matched={result.matched_skills} missing={result.missing_skills} extra={result.extra_skills} />
        </div>
        <div className="metrics-panel">
          <Metric label="Match probability" value={formatPercent(result.match_probability)} />
          <Metric label="Skill match" value={formatPercent(result.skill_match_score)} />
          <Metric label="Hire probability" value={formatPercent(result.hire_probability)} />
          <Metric label="AI score" value={Number(result.ai_score).toFixed(1)} />
        </div>
      </div>

      <div className="skill-cloud">
        {(result.matched_skills || []).map((skill) => (
          <span className="chip match-chip" key={skill}>{skill}</span>
        ))}
        {(result.missing_skills || []).map((skill) => (
          <span className="chip gap-chip" key={skill}>{skill}</span>
        ))}
      </div>

      <details className="preview">
        <summary>Resume preview with matched skill highlights</summary>
        <HighlightedText text={result.parsed_text_preview} terms={result.highlight_terms || result.matched_skills} />
      </details>

      <div className="feedback-panel">
        <span>Recruiter feedback</span>
        <div className="feedback-actions">
          {FEEDBACK_ACTIONS.map((action) => (
            <button key={action.type} type="button" onClick={() => onFeedback(result, action.type)}>
              {action.label}
            </button>
          ))}
        </div>
        {feedbackStatus && <p>{feedbackStatus}</p>}
      </div>
    </article>
  );
}

export default function App() {
  const [theme, setTheme] = useState("light");
  const [files, setFiles] = useState([]);
  const [jobText, setJobText] = useState(SAMPLE_JD);
  const [experienceYears, setExperienceYears] = useState("");
  const [education, setEducation] = useState("");
  const [certifications, setCertifications] = useState("");
  const [projectsCount, setProjectsCount] = useState(0);
  const [results, setResults] = useState([]);
  const [errors, setErrors] = useState([]);
  const [exportMessage, setExportMessage] = useState("");
  const [feedbackMessages, setFeedbackMessages] = useState({});
  const [isScreening, setIsScreening] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [modelStatus, setModelStatus] = useState(null);
  const [modelMessage, setModelMessage] = useState("");
  const [isModelBusy, setIsModelBusy] = useState(false);
  const [minimumScore, setMinimumScore] = useState(0);
  const [skillFilterMode, setSkillFilterMode] = useState("has");
  const [skillFilter, setSkillFilter] = useState("");
  const [backendReady, setBackendReady] = useState(null);

  useEffect(() => {
    // A sleeping free-tier server can take about a minute to wake up, so keep retrying until it answers.
    let timer;
    let cancelled = false;
    async function poll() {
      const ready = await checkHealth().catch(() => false);
      if (cancelled) return;
      setBackendReady(ready);
      if (!ready) timer = setTimeout(poll, 10000);
    }
    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const rankedResults = useMemo(() => {
    return [...results].sort((a, b) => Number(b.final_score) - Number(a.final_score));
  }, [results]);

  const allSkills = useMemo(() => {
    const skills = new Set();
    results.forEach((result) => {
      [...(result.matched_skills || []), ...(result.missing_skills || []), ...(result.resume_skills || [])].forEach((skill) => skills.add(skill));
    });
    return [...skills].sort();
  }, [results]);

  const filteredResults = useMemo(() => {
    return rankedResults.filter((result) => {
      const scorePass = Number(result.final_score) >= Number(minimumScore);
      let skillPool = [];
      if (skillFilterMode === "matched") {
        skillPool = result.matched_skills || [];
      } else if (skillFilterMode === "missing") {
        skillPool = result.missing_skills || [];
      } else {
        skillPool = result.resume_skills || [];
      }
      const skillPass = !skillFilter || skillPool.includes(skillFilter);
      return scorePass && skillPass;
    });
  }, [rankedResults, minimumScore, skillFilter, skillFilterMode]);

  async function handleScreen() {
    setErrors([]);
    setExportMessage("");
    setFeedbackMessages({});
    setResults([]);

    if (!files.length) {
      setErrors(["Upload at least one resume file."]);
      return;
    }
    if (jobText.trim().length < 20) {
      setErrors(["Paste a job description with at least 20 characters."]);
      return;
    }

    setIsScreening(true);
    const completed = [];
    const failed = [];

    for (const file of files) {
      try {
        const result = await recommendUploadedResume({
          file,
          jobText,
          experienceYears,
          education,
          certifications,
          projectsCount,
        });
        completed.push(result);
        setResults([...completed]);
      } catch (error) {
        failed.push(`${file.name}: ${error.message}`);
      }
    }

    setErrors(failed);
    setIsScreening(false);
  }

  async function handleExport() {
    if (!filteredResults.length) return;

    setIsExporting(true);
    setExportMessage("");
    downloadCsv(filteredResults);
    try {
      const response = await exportRankings(filteredResults);
      setExportMessage(`Downloaded ${response.rows_exported} rows. A copy was also saved on the server: ${response.file_path}`);
    } catch (error) {
      setExportMessage(`Downloaded ${filteredResults.length} rows. (Server copy not saved: ${error.message})`);
    } finally {
      setIsExporting(false);
    }
  }

  async function handleFeedback(result, feedbackType) {
    const key = `${result.filename}-${feedbackType}`;
    setFeedbackMessages((current) => ({ ...current, [key]: "Saving..." }));

    try {
      const response = await submitFeedback({
        filename: result.filename,
        feedback_type: feedbackType,
        final_score: result.final_score,
        fit_level: result.fit_level,
        match_probability: result.match_probability,
        skill_match_score: result.skill_match_score,
        screening_decision: result.screening_decision,
        hire_probability: result.hire_probability,
        ai_score: result.ai_score,
        role_predictions: result.role_predictions || [],
        matched_skills: result.matched_skills || [],
        missing_skills: result.missing_skills || [],
        resume_text: result.resume_text || result.parsed_text_preview || "",
        job_text: jobText,
      });
      setFeedbackMessages((current) => ({ ...current, [key]: response.message }));
    } catch (error) {
      setFeedbackMessages((current) => ({ ...current, [key]: error.message }));
    }
  }

  async function refreshModelStatus() {
    setModelMessage("");
    try {
      setModelStatus(await getModelStatus());
    } catch (error) {
      setModelMessage(error.message);
    }
  }

  async function handleCreateVersion() {
    setIsModelBusy(true);
    try {
      const response = await createModelVersion("manual_dashboard_snapshot");
      setModelMessage(`Created ${response.version_id} with ${response.artifact_count} artifacts.`);
      await refreshModelStatus();
    } catch (error) {
      setModelMessage(error.message);
    } finally {
      setIsModelBusy(false);
    }
  }

  async function handleRetrainPlan() {
    setIsModelBusy(true);
    try {
      const response = await retrainModels();
      setModelMessage(`${response.message} Matching feedback rows: ${response.prepared_feedback.matching_rows}. Screening feedback rows: ${response.prepared_feedback.screening_rows}.`);
      await refreshModelStatus();
    } catch (error) {
      setModelMessage(error.message);
    } finally {
      setIsModelBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI Resume Screening System</p>
          <h1>Candidate ranking dashboard</h1>
        </div>
        <button className="theme-toggle" type="button" onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
          {theme === "light" ? "Dark mode" : "Light mode"}
        </button>
      </header>

      <section className="workspace">
        <aside className="control-panel">
          <div className="status-line">
            <span className={classNames("status-dot", backendReady ? "ready" : backendReady === false ? "down" : "")} />
            {backendReady === null
              ? "Connecting to API... (a sleeping free server can take up to a minute)"
              : backendReady
                ? "API connected"
                : "API unavailable - retrying every 10 seconds"}
          </div>

          <label className="field">
            <span>Resume files</span>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              multiple
              onChange={(event) => setFiles([...event.target.files])}
            />
          </label>

          <label className="field">
            <span>Job description</span>
            <textarea value={jobText} onChange={(event) => setJobText(event.target.value)} rows={8} />
          </label>

          <div className="compact-fields">
            <label className="field">
              <span>Experience</span>
              <input type="number" min="0" value={experienceYears} onChange={(event) => setExperienceYears(event.target.value)} />
            </label>
            <label className="field">
              <span>Projects</span>
              <input type="number" min="0" value={projectsCount} onChange={(event) => setProjectsCount(event.target.value)} />
            </label>
          </div>

          <label className="field">
            <span>Education</span>
            <input value={education} onChange={(event) => setEducation(event.target.value)} placeholder="B.Tech, MBA, M.Sc" />
          </label>

          <label className="field">
            <span>Certifications</span>
            <input value={certifications} onChange={(event) => setCertifications(event.target.value)} placeholder="AWS, Google ML, Cisco" />
          </label>

          <button className="primary-action" type="button" onClick={handleScreen} disabled={isScreening}>
            {isScreening ? "Screening resumes..." : "Screen resumes"}
          </button>

          <div className="admin-panel">
            <span>Model operations</span>
            <div className="admin-actions">
              <button type="button" onClick={refreshModelStatus}>Status</button>
              <button type="button" onClick={handleCreateVersion} disabled={isModelBusy}>Snapshot</button>
              <button type="button" onClick={handleRetrainPlan} disabled={isModelBusy}>Retrain Prep</button>
            </div>
            {modelStatus && (
              <p>
                Feedback rows: {modelStatus.feedback.rows} · Versions: {modelStatus.versions.length}
              </p>
            )}
            {modelMessage && <p>{modelMessage}</p>}
          </div>
        </aside>

        <section className="results-area">
          <div className="filter-row">
            <label className="slider-field">
              <span>Minimum score: {minimumScore}</span>
              <input type="range" min="0" max="100" value={minimumScore} onChange={(event) => setMinimumScore(event.target.value)} />
            </label>

            <label className="select-field">
              <span>Filter type</span>
              <select value={skillFilterMode} onChange={(event) => setSkillFilterMode(event.target.value)}>
                <option value="has">Has skill</option>
                <option value="matched">Matched skill</option>
                <option value="missing">Missing skill</option>
              </select>
            </label>

            <label className="select-field">
              <span>Skill</span>
              <select value={skillFilter} onChange={(event) => setSkillFilter(event.target.value)}>
                <option value="">All skills</option>
                {allSkills.map((skill) => (
                  <option key={skill} value={skill}>{skill}</option>
                ))}
              </select>
            </label>

            <button
              className="secondary-action"
              type="button"
              onClick={handleExport}
              disabled={!filteredResults.length || isExporting}
            >
              {isExporting ? "Saving CSV..." : "Export CSV"}
            </button>
          </div>

          {errors.length > 0 && (
            <div className="error-box">
              {errors.map((error) => (
                <p key={error}>{error}</p>
              ))}
            </div>
          )}

          {exportMessage && <div className="success-box"><p>{exportMessage}</p></div>}

          {filteredResults.length === 0 ? (
            <div className="empty-state">
              {results.length ? (
                <div>
                  <h2>No candidates match these filters</h2>
                  <p>
                    Lower the minimum score or clear the skill filter to see{" "}
                    {results.length === 1 ? "the 1 screened resume" : `all ${results.length} screened resumes`}.
                  </p>
                </div>
              ) : (
                <div>
                  <h2>No rankings yet</h2>
                  <p>Upload resumes, paste a job description, then screen candidates to see ranked results.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="result-list">
              {filteredResults.map((result, index) => (
                <ResultCard
                  key={`${result.filename}-${index}`}
                  result={result}
                  rank={index + 1}
                  onFeedback={handleFeedback}
                  feedbackStatus={
                    feedbackMessages[
                      FEEDBACK_ACTIONS.map((action) => `${result.filename}-${action.type}`).find((key) => feedbackMessages[key])
                    ]
                  }
                />
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
