# Viva Questions & Answers

Short, simple answers to the questions examiners usually ask. Read them aloud a few times — say them in your own words, don't memorise.

## About the project

**1. What does your project do?**
It ranks job applicants automatically. A recruiter uploads resumes and a job description; the system scores every resume out of 100, ranks them, and shows which required skills each person has or is missing.

**2. Why is this problem important?**
One job can get hundreds of resumes. Reading them by hand is slow and inconsistent. The system does the first screening in seconds and applies the same rules to everyone.

**3. Who are the users?**
Recruiters and HR teams. Candidates also benefit indirectly, because the missing-skill list shows what they need to learn.

**4. Is this a replacement for recruiters?**
No. It is a decision-support tool. It shortlists and explains; a human makes the final hiring decision.

## Data and NLP

**5. What datasets did you use?**
Three: (1) a Kaggle dataset of about 2,400 resumes in 24 job categories for the role classifier; (2) resume–job pairs labelled fit / no fit for the matching model — the original model learned from a Russian dataset, and I added a pipeline to retrain it on 8,000 English pairs from Hugging Face; (3) a Kaggle dataset of candidate profiles with hire/reject decisions for the screening model.

**6. What preprocessing do you do?**
Lower-case the text, remove emails, phone numbers and links, protect tech words like C++ and C#, remove punctuation, and remove very common words like "the" and "and".

**7. What is TF-IDF?**
A way to turn text into numbers. A word gets a high score if it appears often in this resume (TF) but rarely in other resumes (IDF). So "TensorFlow" scores high, "the" scores almost zero.

**8. Why remove emails and phone numbers?**
They carry no information about skills, add noise, and are personal data.

**9. How do you read PDF and Word files?**
`pdfminer.six` for PDF, `python-docx` for DOCX, and normal text decoding for TXT. Scanned image-only PDFs can't be read because there is no OCR — that is a known limitation.

## Machine learning

**10. Which ML models are used and why?**
- Role classifier — Linear SVM: very good for text with thousands of features.
- Matching model — Logistic Regression: gives a probability, simple and fast.
- Screening decision — Logistic Regression: gives a hire probability.
- AI score — Random Forest Regressor: predicts a number from 0 to 100 and handles non-linear patterns.

**11. Is the skill engine machine learning?**
No, it is rule-based: a dictionary of 65 skills with synonyms (e.g. "sklearn" = scikit-learn), matched as whole words. It is transparent, which makes the results easy to explain.

**12. What is supervised learning? Is your project supervised?**
Learning from examples that already have the right answer (labels). Yes — every dataset has labels: job category, fit / no fit, hire / reject.

**13. How did you split the data?**
80% for training, 20% for testing, with stratification (each class keeps the same proportion in both parts). The role classifier also uses 5-fold cross-validation.

**14. What is cross-validation?**
Split the data into 5 parts, train on 4 and test on 1, repeat 5 times, and average. It gives a more reliable accuracy than a single split.

**15. What is overfitting? How do you avoid it?**
When a model memorises the training data and fails on new data. We avoid it by testing on unseen data, using cross-validation, limiting the number of features, and using regularised models.

**16. Why does the screening model show ~94% accuracy when the others are lower?**
Dataset 3 appears to be computer-generated, so its patterns are very clean and easy to learn. On real hiring data the accuracy would likely be lower. I mention this as a limitation.

**17. What does "calibrated" mean for the SVM?**
A Linear SVM only gives a raw score, not a probability. Calibration (CalibratedClassifierCV) converts the score into a probability between 0 and 1, which we need for the "role confidence" part of the final score.

**18. How does the matching model compare a resume with a job?**
It turns both into character-level TF-IDF vectors, then builds features from them: how similar they are (cosine similarity), their lengths, where they differ and where they overlap. Logistic Regression learns from those features which pairs were judged a fit.

## Scoring and evaluation

**19. How is the final score calculated?**
35% match probability + 25% skill match + 25% AI screening score (multiplied by skill match) + 15% role relevance (how likely the person's field suits the job). 85+ is Strong Fit, 70–84 Good Fit, 55–69 Moderate Fit, below 55 Weak Fit.

**20. Why these weights?**
Overall resume–job match is the most direct signal, so it gets the most weight. Skills and screening are equally important. Role confidence is the least specific, so it gets the least. The weights can be changed in one place (`DEFAULT_WEIGHTS` in `recommender.py`).

**20a. Why multiply the screening score by skill match?**
When I tested the live system, an HR manager with 8 years' experience ranked second for a Data Scientist job. The screening model rewards experience and education, but it was trained only on people applying for jobs in their own field, so it had never seen a mismatch. Multiplying by skill match means "strong candidate" only counts when the person also has the job's skills. For the same reason, the role judge now counts only fields that suit the job, so being confidently "HR" doesn't help for a tech job.

**21. Explain accuracy, precision, recall and F1.**
- Accuracy: how many predictions were right overall.
- Precision: when the model says "fit", how often it is right.
- Recall: of all real fits, how many the model found.
- F1: a balance of precision and recall — useful when classes are uneven.

**22. What is ROC-AUC?**
How well a model separates the two classes at every threshold. 0.5 = random guessing, 1.0 = perfect.

**23. What are MAP and NDCG?**
Ranking metrics. MAP checks whether relevant candidates appear near the top. NDCG also rewards putting the *most* relevant candidates first.

**24. What is a confusion matrix?**
A table of actual vs predicted classes. The diagonal shows correct predictions; everything else shows which classes get mixed up.

## Engineering

**25. Why FastAPI and React?**
FastAPI is fast, works naturally with Python ML code, and creates interactive API docs automatically (`/docs`). React makes it easy to build an interactive dashboard with reusable components.

**26. What happens if a model file is missing or broken?**
The system uses a simple backup formula for that part and **shows a red "backup formula" label** on the result card, so the user always knows. `check_models.py` tests all models before a demo.

**27. How did you test the project?**
Automated pytest tests for skill extraction, cleaning, role mapping, ranking metrics, file parsing, storage, model loading and the API; plus manual UI testing of upload, ranking, filters, export, feedback and error messages. Every upload to GitHub also runs all tests automatically on GitHub Actions (Linux servers), including the ML-model tests and a check that the right candidate ranks first for each of four jobs.

**28. How does the feedback loop work?**
Recruiter clicks (Good Match, Hire, Reject…) are saved to a CSV with the resume and job text. "Retrain Prep" snapshots the current models and converts feedback into training rows. `retrain_models.bat` retrains all models and backs up the old ones first.

## What did *you* do? (be ready for this one)

**29. What did you add or change compared with the original code?**
- Found and fixed a library-version mismatch that made all ML models silently fail.
- Fixed a mismatch between how text was processed in training and in prediction.
- Added a pipeline to retrain the matching model on an English dataset instead of the original Russian one.
- Fixed the screening model getting a job role it had never seen.
- Added labels showing whether each score came from ML or a backup formula.
- Removed skill false positives and added missing skills.
- Made models load once (faster), added browser CSV download and synonym highlighting, fixed the projector layout.
- Wrote automated tests, notebooks, setup/run/retrain scripts and documentation.
- Tested the deployed system, found an HR manager ranked #2 for a Data Scientist job, and fixed the scoring (screening × skill match, job-relevant role fields).
- Set up GitHub Actions to run every test and retrain the matcher in the cloud.

**30. What would you improve next?**
Use sentence embeddings (BERT) for better semantic matching, retrain automatically from validated feedback, move storage to a database, add login, add OCR for scanned resumes, and add fairness checks.

## Ethics

**31. Can the AI be biased?**
Yes. If past hiring decisions were biased, a model trained on them can learn that bias. That is why the system explains every score, keeps a human in the loop, and fairness analysis is in the future scope.

**32. What about privacy?**
Resumes are processed locally and are not sent anywhere else. Contact details are removed during preprocessing. In a real deployment you would add access control and data-retention rules.
