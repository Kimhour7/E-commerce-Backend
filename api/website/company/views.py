from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from api.website.company.models import TBL_COMPANY
from api.website.company.schemas import CompanyBase, CompanySingleResponse, CompanyListResponse, CompanyUpdate
from core.db import RecordStatus, get_db
from core.permission import *
from core.securerity import User
from core.custom_id import PrefixId, generate_prefixed_id
from language.language import Language, LanguageKey, getLang

module_name    = "Company"
company_router = APIRouter(prefix="/company", tags=[f"{module_name}"])

@company_router.post("/create", response_model=CompanySingleResponse)
def create(
    schemas     : CompanyBase,
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
            message = getLang(LanguageKey.create_success, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),
            data    = company,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.create_failed, lang=language.value))
    finally:
        db.close()


@company_router.get("/get", response_model=CompanyListResponse)
def get(
    db          : Session      = Depends(get_db),
    current_user: User         = Depends(SuperUserPermission),
    page        : int          = 1,
    size        : int          = 10,
    search      : str          = None,
    language    : Language     = Language.en,
    record_type : RecordStatus = RecordStatus.active,
):
    try:
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
            message     = getLang(LanguageKey.get_success, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),
            total       = total_count,
            page        = page,
            size        = size,
            total_pages = (total_count + size - 1) // size if total_count else 0,
            data        = rows
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.create_failed, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),)
    finally:
        db.close()


@company_router.get("/get/{company_id}", response_model=CompanySingleResponse)
def get_single_record(
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
            raise HTTPException(
                status_code=404,
                detail=getLang(LanguageKey.not_found, {"param" : getLang(LanguageKey.company, lang=language.value)}, lang=language.value),
            )
        
        return CompanySingleResponse(
            success = True,
            message = getLang(LanguageKey.get_success, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),
            data    = get_company,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.get_failed, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),)
    finally:
        db.close()


@company_router.put("/update/{company_id}", response_model=CompanySingleResponse)
def update(
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
                detail=getLang(LanguageKey.not_found, {"param" : getLang(LanguageKey.company, lang=language.value)}, lang=language.value),
            )

        update_data = schemas.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(get_company, field, value)

        get_company.updated_by = current_user.username
        get_company.updated_at = datetime.now()

        db.commit()
        db.refresh(get_company)

        return CompanySingleResponse(
            success = True,
            message = getLang(LanguageKey.update_success, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),
            data    = get_company,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(
            status_code=500,
            detail = getLang(LanguageKey.update_failed, {"param": getLang(LanguageKey.company, lang=language.value)}, language.value),
        )
    finally:
        db.close()


@company_router.delete("/delete/{company_id}")
def delete(
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
            raise HTTPException(status_code=404, detail=getLang(LanguageKey.not_found, {"param" : getLang(LanguageKey.company, lang=language.value)}, lang=language.value),)
        
        get_company.record_status = RecordStatus.deleted.value
        get_company.updated_by = current_user.username
        get_company.updated_at = datetime.now()

        db.commit()

        return {
            "success" : True,
            "message" : getLang(LanguageKey.delete_success, {"param" : getLang(LanguageKey.company, lang=language.value)}, lang=language.value),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(
            status_code=500,
            detail=getLang(LanguageKey.delete_failed, {"param" : getLang(LanguageKey.company, lang=language.value)}, lang=language.value),
        )
    finally:
        db.close()