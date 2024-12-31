from pathlib import Path as PathlibPath
from typing import List, Tuple, TypeVar

from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.endpoints import crud
from app.models.artists import Artist



# initialize the Jinja2 templates
templates_dir = PathlibPath(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


# create a router for the model
router = APIRouter(
    tags=["Application"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_db)],
)


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )


@router.get("/artists", response_class=HTMLResponse)
async def get_artists(
    request: Request,
    db: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    async with db as session:
        artists, total_count = await crud.read_items(
            session=session,
            offset=offset,
            limit=limit,
            model_class=Artist,
        )
        
    return templates.TemplateResponse(
        name="partials/artists.html",
        context={
            "request": request,
            "artists": artists,
        }
    )