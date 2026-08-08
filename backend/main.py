from __future__ import annotations

import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


app = FastAPI(title="AI Academic English Training Platform", version="1.0.0")


class Exercise(BaseModel):
    id: int
    skill: Literal["abstract", "vocabulary", "translation", "revision"]
    title: str
    prompt: str
    reference_answer: str
    hints: list[str]


class Submission(BaseModel):
    exercise_id: int = Field(..., ge=1)
    answer: str = Field(..., min_length=1, max_length=4000)


class Evaluation(BaseModel):
    exercise_id: int
    score: int
    band: Literal["needs-work", "developing", "strong"]
    feedback: list[str]
    suggested_revision: str


EXERCISES: list[Exercise] = [
    Exercise(
        id=1,
        skill="abstract",
        title="Rewrite an abstract sentence",
        prompt=(
            "Rewrite this sentence in concise academic English: "
            "This paper wants to talk about how AI can help students write better English."
        ),
        reference_answer=(
            "This paper examines how artificial intelligence can support students' English writing development."
        ),
        hints=["Use an objective research verb.", "Avoid informal phrases such as 'wants to talk about'."],
    ),
    Exercise(
        id=2,
        skill="vocabulary",
        title="Choose precise academic vocabulary",
        prompt=(
            "Improve the wording: The results are very good and show the method is useful."
        ),
        reference_answer=(
            "The results are promising and demonstrate the effectiveness of the proposed method."
        ),
        hints=["Replace vague intensifiers.", "Use nouns such as 'effectiveness' or 'performance'."],
    ),
    Exercise(
        id=3,
        skill="translation",
        title="Translate a research claim",
        prompt="Translate into academic English: 本研究表明，持续反馈可以显著提高学习者的写作准确性。",
        reference_answer=(
            "This study shows that sustained feedback can significantly improve learners' writing accuracy."
        ),
        hints=["Keep the claim cautious and direct.", "Use 'significantly' for 显著."],
    ),
    Exercise(
        id=4,
        skill="revision",
        title="Revise for formal tone",
        prompt="Revise: We got a lot of data, and it tells us our idea is right.",
        reference_answer=(
            "We collected substantial data, which supports the validity of our hypothesis."
        ),
        hints=["Avoid conversational verbs.", "Use 'hypothesis' for a research idea."],
    ),
]


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/exercises", response_model=list[Exercise])
def list_exercises() -> list[Exercise]:
    return EXERCISES


@app.get("/api/exercises/{exercise_id}", response_model=Exercise)
def get_exercise(exercise_id: int) -> Exercise:
    for exercise in EXERCISES:
        if exercise.id == exercise_id:
            return exercise
    raise HTTPException(status_code=404, detail="Exercise not found")


def _keywords(text: str) -> set[str]:
    stop_words = {"the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "this", "that", "can"}
    return {word for word in re.findall(r"[a-zA-Z']+", text.lower()) if word not in stop_words and len(word) > 2}


@app.post("/api/evaluate", response_model=Evaluation)
def evaluate(submission: Submission) -> Evaluation:
    exercise = next((item for item in EXERCISES if item.id == submission.exercise_id), EXERCISES[0])
    answer = submission.answer.strip()
    reference = exercise.reference_answer
    similarity = SequenceMatcher(None, answer.lower(), reference.lower()).ratio()
    keyword_overlap = len(_keywords(answer) & _keywords(reference)) / max(len(_keywords(reference)), 1)
    length_score = 1.0 if 8 <= len(answer.split()) <= 28 else 0.65
    raw_score = (similarity * 0.45 + keyword_overlap * 0.4 + length_score * 0.15) * 100
    score = max(1, min(100, round(raw_score)))

    feedback: list[str] = []
    if keyword_overlap < 0.45:
        feedback.append("Include more key academic concepts from the task and reference meaning.")
    else:
        feedback.append("Your response captures several important academic concepts.")
    if re.search(r"\b(very|a lot|got|talk about|good)\b", answer, flags=re.IGNORECASE):
        feedback.append("Replace informal or vague wording with precise academic expressions.")
    else:
        feedback.append("The tone is generally appropriate for academic writing.")
    if len(answer.split()) > 28:
        feedback.append("Consider making the sentence more concise.")
    elif len(answer.split()) < 8:
        feedback.append("Add enough detail to express the complete research meaning.")
    else:
        feedback.append("The length is suitable for a concise academic sentence.")

    band: Literal["needs-work", "developing", "strong"]
    if score >= 78:
        band = "strong"
    elif score >= 50:
        band = "developing"
    else:
        band = "needs-work"

    return Evaluation(
        exercise_id=exercise.id,
        score=score,
        band=band,
        feedback=feedback,
        suggested_revision=reference,
    )


app.mount("/static", StaticFiles(directory="static"), name="static")
