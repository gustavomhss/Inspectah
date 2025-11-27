from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.cases import build_debunk_summary, load_case_by_id, load_cases, load_collections
from app.cases.schemas import CaseCollectionResponse, CaseResponse, CaseClaimSchema
from app.debunk.repository import DebunkRepository

cases_router = APIRouter(prefix="/cases", tags=["cases"])
collections_router = APIRouter(prefix="/collections", tags=["collections"])


def get_repo() -> DebunkRepository:
    return DebunkRepository()


@cases_router.get("", response_model=List[CaseResponse])
def list_cases(repo: DebunkRepository = Depends(get_repo)):
    cases = []
    for case in load_cases():
        summary = build_debunk_summary(repo, case)
        cases.append(
            CaseResponse(
                case_id=case.case_id,
                title=case.title,
                summary=case.summary,
                theme=case.theme,
                tags=case.tags,
                claims=[CaseClaimSchema(**c.__dict__) for c in case.claims],
                timeline=case.timeline,
                sources=case.sources,
                metadata=case.metadata,
                debunk_summary=summary,
            )
        )
    return cases


@collections_router.get("", response_model=List[CaseCollectionResponse])
def list_collections():
    collections = load_collections()
    return [
        CaseCollectionResponse(
            collection_id=c.collection_id,
            title=c.title,
            description=c.description,
            tags=c.tags,
            case_ids=c.case_ids,
        )
        for c in collections
    ]


@collections_router.get("/{collection_id}", response_model=CaseCollectionResponse)
def get_collection(collection_id: str):
    collection = next((c for c in load_collections() if c.collection_id == collection_id), None)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coleção não encontrada")
    return CaseCollectionResponse(
        collection_id=collection.collection_id,
        title=collection.title,
        description=collection.description,
        tags=collection.tags,
        case_ids=collection.case_ids,
    )


@cases_router.get("/collections", response_model=List[CaseCollectionResponse])
def list_collections_under_cases_prefix():
    return list_collections()


@cases_router.get("/collections/{collection_id}", response_model=CaseCollectionResponse)
def get_collection_under_cases_prefix(collection_id: str):
    return get_collection(collection_id)


@cases_router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, repo: DebunkRepository = Depends(get_repo)):
    case = load_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case não encontrado")
    summary = build_debunk_summary(repo, case)
    return CaseResponse(
        case_id=case.case_id,
        title=case.title,
        summary=case.summary,
        theme=case.theme,
        tags=case.tags,
        claims=[CaseClaimSchema(**c.__dict__) for c in case.claims],
        timeline=case.timeline,
        sources=case.sources,
        metadata=case.metadata,
        debunk_summary=summary,
    )
