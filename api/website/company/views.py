from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from api.website.company.models import TBL_COMPANY
from api.website.company.schemas import CompanyCreate, CompanySingleResponse, CompanyListResponse, CompanyUpdate
from core.db import RecordStatus, get_db
from core.permission import *
from core.securerity import User
from core.custom_id import PrefixId, generate_prefixed_id
from language.language import Language, LanguageKey, getLang
from main import website


@website.post("/company-create", tags=["Company"], response_model=CompanySingleResponse)
def company_create(
    schemas     : CompanyCreate,
    db          : Session  = Depends(get_db),
    current_user: User     = Depends(SuperUserPermission),
    language    : Language = Language.en,
):
    try:

        company = TBL_COMPANY(
            id = generate_prefixed_id(db, TBL_COMPANY, prefix=PrefixId.Company),

            **schemas.dict(exclude_none=True),

            company_id = current_user.working_company_id,
            branch_id  = current_user.working_branch_id,
            created_by = current_user.username,
        )

        db.add(company)
        db.commit()
        db.refresh(company)

        return CompanySingleResponse(
            success = True,
            message = getLang(LanguageKey.success_message, lang=language.value),
            data    = company,
        )
    except Exception as e:
        print(f"Company Module ${e}")
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.company_create_failed, lang=language.value))
    finally:
        db.close()


@website.get("/company-get", tags=["Company"], response_model=CompanyListResponse)
def company_get(
    db: Session = Depends(get_db),
    current_user: User = Depends(SuperUserPermission),
    page: int = 1,
    size: int = 10,
    search: str = None,
    record_type: RecordStatus = RecordStatus.active,
):
    query = db.query(TBL_COMPANY).filter(TBL_COMPANY.record_status == record_type.value)

    if search:
        query = query.filter(
            or_(
                TBL_COMPANY.name.ilike(f"%{search}%"),
                TBL_COMPANY.id.ilike(f"%{search}%"),
            )
        )

    rows = query.offset((page - 1) * size).limit(size).all()
    total_count = query.count()

    return CompanyListResponse(
        success     = True,
        message     = "Company retrieved successfully",
        total       = total_count,
        page        = page,
        size        = size,
        total_pages = (total_count + size - 1) // size if total_count else 0,
        data        = rows
    )


@website.get("/company-get/{company_id}", tags=["Company"], response_model=CompanySingleResponse)
def company_get(
    company_id : str,
    db: Session = Depends(get_db),
    current_user: User = Depends(SuperUserPermission),
    language    : Language = Language.en,
):
    try:
        get_company = (
                db.query(TBL_COMPANY)
                .filter(TBL_COMPANY.record_status == RecordStatus.active.value)
                .filter(TBL_COMPANY.id == company_id)
                .first()
            )

        if not get_company:
            return HTTPException(
                status_code=404,
                detail=getLang(LanguageKey.company_not_found, lang=language.value),
            )
        
        return CompanySingleResponse(
            success = True,
            message = getLang(LanguageKey.success_message, lang=language.value),
            data    = get_company,
        )
    except Exception as e:
        print(f"Company Module ${e}")
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.company_create_failed, lang=language.value))
    finally:
        db.close()


@website.put("/company-update/{company_id}", tags=["Company"], response_model=CompanySingleResponse)
def company_update(
    company_id  : str,
    schemas     : CompanyUpdate,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(SuperUserPermission),
    language    : Language = Language.en,
):
    try:
        get_company = (
            db.query(TBL_COMPANY)
            .filter(TBL_COMPANY.record_status == RecordStatus.active.value)
            .filter(TBL_COMPANY.id == company_id)
            .first()
        )

        if not get_company:
            raise HTTPException(
                status_code=404,
                detail=getLang(LanguageKey.company_not_found, lang=language.value),
            )

        update_data = schemas.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(get_company, field, value)

        get_company.updated_by = current_user.username
        get_company.updated_at = datetime.now()

        db.commit()
        db.refresh(get_company)

        return CompanySingleResponse(
            success=True,
            message=getLang(LanguageKey.company_update_success, lang=language.value),
            data=get_company,
        )
    except Exception as e:
        print(f"Company Module ${e}")
        raise HTTPException(
            status_code=500,
            detail=getLang(LanguageKey.company_update_failed, lang=language.value),
        )
    finally:
        db.close()


@website.delete("/company-delete/{company_id}", tags=["Company"])
def company_delete(
    company_id  : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(SuperUserPermission),
    language    : Language = Language.en,
):
    try:
        get_company = (
            db.query(TBL_COMPANY)
            .filter(TBL_COMPANY.record_status == RecordStatus.active.value)
            .where(TBL_COMPANY.id == company_id)
            .first()
        )

        if not get_company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        get_company.record_status = RecordStatus.deleted.value
        get_company.updated_by = current_user.username
        get_company.updated_at = datetime.now()

        db.commit()

        return {
            "success" : True,
            "message" : "Company retrieved successfully",
        }
    except Exception as e:
        print(f"Company Module ${e}")
        raise HTTPException(
            status_code=500,
            detail=getLang(LanguageKey.company_update_failed, lang=language.value),
        )
    finally:
        db.close()