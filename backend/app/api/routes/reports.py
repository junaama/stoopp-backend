import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Report, ReportCreate, ReportUpdate, ReportPublic

router = APIRouter()


@router.post("/", response_model=ReportPublic)
def create_report(
    report: ReportCreate,
    db: SessionDep,
    current_user: CurrentUser
) -> ReportPublic:
    db_report = Report.model_validate(report, update={"reporter_id": current_user.id})
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.get("/", response_model=List[ReportPublic])
def get_reports(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> List[ReportPublic]:
    query = select(Report).where(
        (Report.reporter_id == current_user.id) | (Report.reported_user_id == current_user.id)
    ).offset(skip).limit(limit)
    reports = db.exec(query).all()
    return reports

@router.patch("/{report_id}", response_model=ReportPublic)
def update_report(
    report_id: uuid.UUID,
    report_update: ReportUpdate,
    db: SessionDep,
    current_user: CurrentUser
) -> ReportPublic:
    db_report = db.get(Report, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    if db_report.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this report")
    for key, value in report_update.dict(exclude_unset=True).items():
        setattr(db_report, key, value)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report