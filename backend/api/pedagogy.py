from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from backend.pedagogy.bloom import BloomLevel
from backend.pedagogy.generator import (
    generate_questions,
    generate_assignments
)
from backend.pedagogy.rubric import generate_rubric


router = APIRouter(prefix="/pedagogy", tags=["Pedagogy"])


class QuestionRequest(BaseModel):
    topic: str
    bloom_level: BloomLevel
    num_items: int = 3


class AssignmentRequest(BaseModel):
    topic: str
    bloom_level: BloomLevel
    num_items: int = 2


class RubricRequest(BaseModel):
    topic: str
    bloom_level: BloomLevel


@router.post("/questions")
def pedagogy_questions(req: QuestionRequest):
    try:
        return {
            "topic": req.topic,
            "bloom_level": req.bloom_level,
            "items": generate_questions(
                topic=req.topic,
                bloom=req.bloom_level,
                num_items=req.num_items
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assignments")
def pedagogy_assignments(req: AssignmentRequest):
    try:
        return {
            "topic": req.topic,
            "bloom_level": req.bloom_level,
            "items": generate_assignments(
                topic=req.topic,
                bloom=req.bloom_level,
                num_items=req.num_items
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rubric")
def pedagogy_rubric(req: RubricRequest):
    try:
        return {
            "topic": req.topic,
            "bloom_level": req.bloom_level,
            "rubric": generate_rubric(
                topic=req.topic,
                bloom=req.bloom_level
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
