from sqlmodel import select
from fastapi import APIRouter, HTTPException, Request, Depends
from app.core.database import SessionDep
from app.core.schema import CreateLinkSchema, UpdateLinkSchema, LinkResponse
from app.core.model import Links, Users
from app.core.deps import require_user
from datetime import datetime, UTC
import secrets

link_router = APIRouter(prefix="/links")

@link_router.post("/", response_model=LinkResponse)
async def create_link(request: Request, data: CreateLinkSchema, session: SessionDep, user: Users = Depends(require_user)):
    if user.bank_details is None:
        raise HTTPException(
            status_code=400,
            detail="Add your bank details before creating a link."
        )
    
    link_token = secrets.token_urlsafe(42)

    link = Links(
        creator=user.id,
        token=link_token,
        title=data.title,
        description=data.description,
        amount=data.amount,
        email=data.email,
        type=data.type
    )

    session.add(link)
    await session.commit()

    return link

@link_router.get("/", response_model=list[LinkResponse])
async def get_user_links(request: Request, session: SessionDep, user: Users = Depends(require_user)):
    result = await session.exec(select(Links).where(Links.creator==user.id))
    links = result.all()

    if links == []:
        raise HTTPException(
            status_code=404,
            detail="No links found"
        )

    return links

@link_router.get("/{link_id}", response_model=LinkResponse)
async def get_link_by_id(request: Request, link_id: int, session: SessionDep, user: Users = Depends(require_user)):
    result = await session.exec(select(Links).where(Links.creator==user.id, Links.id==link_id))
    link = result.first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )

    return link

@link_router.put("/{link_id}", response_model=LinkResponse)
async def update_link(request: Request, link_id: int, data: UpdateLinkSchema, session: SessionDep, user: Users = Depends(require_user)):
    result = await session.exec(select(Links).where(Links.creator==user.id, Links.id==link_id))
    link = result.first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )

    updated_link = data.model_dump(exclude_unset=True)

    link.sqlmodel_update(updated_link)
    link.updated_at = datetime.now(UTC)
    session.add(link)

    return link

@link_router.delete("/{link_id}")
async def delete_link(request: Request, link_id: int, session: SessionDep, user: Users = Depends(require_user)):
    result = await session.exec(select(Links).where(Links.creator==user.id, Links.id==link_id))
    link = result.first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )

    await session.delete(link)
    await session.commit()

    return {
        "message": "Link deleted successfully"
    }