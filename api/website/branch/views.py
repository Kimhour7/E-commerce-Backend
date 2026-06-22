from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from api.website.branch.schemas import BranchBase, BranchListResponse, BranchSingleResponse, BranchUpdate
from core.custom_id import PrefixId, generate_prefixed_id
from core.db import RecordStatus, get_db
from core.permission import AdminPermission
from core.securerity import User
from language.language import Language, LanguageKey, getLang
from .models import *

module_name   = "Branch"
branch_router = APIRouter(prefix="/branch", tags=[f"{module_name}"])

@branch_router.post("/create", response_model=BranchSingleResponse)
def create(
    schemas     : BranchBase,
    db          : Session  = Depends(get_db),
    current_user: User     = Depends(AdminPermission),
    language    : Language = Language.en,
):
    try:
        branch = TBL_BRANCH(
            id = generate_prefixed_id(db, TBL_BRANCH, prefix=PrefixId.Branch),

            **schemas.dict(exclude_none=True),

            company_id = current_user.working_company_id,
            branch_id  = current_user.working_branch_id,
            created_by = current_user.username,
        )

        db.add(branch)
        db.commit()
        db.refresh(branch)

        return BranchSingleResponse(
            success = True,
            message = getLang(LanguageKey.create_success, {"param": getLang(LanguageKey.branch, lang=language.value)}, language.value),
            data    = branch,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.create_failed, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value))
    finally:
        db.close()


@branch_router.get("/get", response_model=BranchListResponse)
def get(
    db           : Session      = Depends(get_db),
    current_user: User          = Depends(AdminPermission),
    page         : int          = 1,
    size         : int          = 10,
    search       : str          = None,
    language     : Language     = Language.en,
    record_type  : RecordStatus = RecordStatus.active,
):
    try:
        query = db.query(TBL_BRANCH).filter(TBL_BRANCH.record_status == record_type.value)

        if search:
            query = query.filter(
                or_(
                    TBL_BRANCH.name.ilike(f"%{search}%"),
                    TBL_BRANCH.id.ilike(f"%{search}%"),
                )
            )

        rows = query.offset((page - 1) * size).limit(size).all()
        total_count = query.count()

        return BranchListResponse(
            success     = True,
            message     = getLang(LanguageKey.get_success, {"param": getLang(LanguageKey.branch, lang=language.value)}, language.value),
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
        raise HTTPException(status_code=500, detail=getLang(LanguageKey.get_failed, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value))
    finally:
        db.close()


@branch_router.put("/update/{branch_id}", response_model=BranchSingleResponse)
def update(
    branch_id   : str,
    schemas     : BranchUpdate,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
    language    : Language = Language.en,
):
    try:
        get_branch = (
            db.query(TBL_BRANCH)
            .filter(TBL_BRANCH.record_status == RecordStatus.active.value)
            .filter(TBL_BRANCH.id == branch_id)
            .first()
        )

        if not get_branch:
            raise HTTPException(
                status_code=404,
                detail=getLang(LanguageKey.not_found, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value),
            )

        update_data = schemas.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(get_branch, field, value)

        get_branch.updated_by = current_user.username
        get_branch.updated_at = datetime.now()

        db.commit()
        db.refresh(get_branch)

        return BranchSingleResponse(
            success = True,
            message = getLang(LanguageKey.update_success, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value),
            data    = get_branch,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(
            status_code=500,
            detail=getLang(LanguageKey.update_failed, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value),
        )
    finally:
        db.close()


@branch_router.delete("/delete/{branch_id}", response_model=BranchSingleResponse)
def delete(
    branch_id   : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
    language    : Language= Language.en,
):
    try:
        get_branch = (
            db.query(TBL_BRANCH)
            .filter(TBL_BRANCH.record_status == RecordStatus.active.value)
            .where(TBL_BRANCH.id == branch_id)
            .first()
        )

        if not get_branch:
            raise HTTPException(status_code=404, detail=getLang(LanguageKey.not_found, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value))
        
        get_branch.record_status = RecordStatus.deleted.value
        get_branch.updated_by    = current_user.username
        get_branch.updated_at    = datetime.now()

        db.commit()

        return BranchSingleResponse(
            success = True,
            message = getLang(LanguageKey.delete_success, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value),
            data    = get_branch,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"{module_name} Module : {e}")
        raise HTTPException(
            status_code=500,
            detail=getLang(LanguageKey.delete_failed, {"param" : getLang(LanguageKey.branch, lang=language.value)}, lang=language.value),
        )
    finally:
        db.close()