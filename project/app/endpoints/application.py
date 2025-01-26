from pathlib import Path as PathlibPath

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func, desc, asc, distinct

# from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
import jinja_partials

from app.database import get_db
from app.models.artists import Artist, ArtistRead  # noqa: F401
from app.models.albums import Album, AlbumRead  # noqa: F401
from app.models.tracks import Track, TrackRead  # noqa: F401
from app.models.playlists import Playlist, PlaylistRead  # noqa: F401
from app.models.invoices import Invoice, InvoiceRead  # noqa: F401
from app.models.invoice_items import InvoiceItem, InvoiceItemRead  # noqa: F401
from app.models.playlist_track import PlaylistTrack  # noqa: F401
from app.models.customers import Customer, CustomerRead  # noqa: F401
from app.models.employees import Employee, EmployeeRead  # noqa: F401


# initialize the Jinja2 templates
templates_dir = PathlibPath(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)
jinja_partials.register_starlette_extensions(templates)


# create a router for the model
router = APIRouter(
    tags=["Application"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_db)],
)


@router.get("/test", response_class=HTMLResponse)
async def test(
    request: Request,
):
    request.query_params.get("tab", "artists")
    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={
            "request": request,
        },
    )


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
):
    basename = request.query_params.get("tab", "artists")
    return templates.TemplateResponse(
        request=request,
        name="application.html",
        context={
            "request": request,
            "partial_template": f"{basename}.html",
        },
    )


@router.get("/template/{template_name}", response_class=HTMLResponse)
async def get_template(
    request: Request,
    template_name: str,
):
    return templates.TemplateResponse(
        request=request,
        name=f"{template_name}.html",
        context={
            "request": request,
        },
    )


@router.get("/artists", response_class=HTMLResponse)
async def get_artists(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sort: str = Query(None, alias="sort"),
    direction: str = Query(None, alias="direction"),
    offset: int = 0,
    items_per_page: int = Query(10, alias="items_per_page"),
):
    limit = items_per_page
    async with db as session:
        query = (
            select(
                Artist.id,
                Artist.name,
                func.count(distinct(Album.id)).label("album_count"),
                func.count(distinct(Track.id)).label("track_count"),
            )
            .outerjoin(Artist.albums)
            .outerjoin(Album.tracks)
            .offset(offset)
            .limit(limit)
            .group_by(Artist.name)
        )
        query = query_order_by(
            query=query, path=request.url.path, sort=sort, direction=direction
        )
        results = await session.execute(query)

    # Convert each row to a dictionary
    results_list = [row._mapping for row in results.fetchall()]

    return templates.TemplateResponse(
        name="partials/artists.html",
        context={
            "request": request,
            "artists": results_list,
        },
    )


@router.get("/albums", response_class=HTMLResponse)
async def get_albums(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sort: str = Query(None, alias="sort"),
    direction: str = Query(None, alias="direction"),
    offset: int = 0,
    items_per_page: int = Query(10, alias="items_per_page"),
):
    limit = items_per_page
    async with db as session:
        query = (
            select(
                Album.title,
                Artist.name,
                func.sum(Track.milliseconds).label("album_duration"),
                func.sum(Track.unit_price).label("album_price"),
            )
            .join(Album.artist)
            .join(Album.tracks)
            .offset(offset)
            .limit(limit)
            .group_by(Album.title)
        )
        query = query_order_by(query=query, sort=sort, direction=direction)
        results = await session.execute(query)

    # Convert each row to a dictionary
    results_list = []
    for row in results.fetchall():
        duration_seconds = row.album_duration / 1000
        minutes, seconds = divmod(duration_seconds, 60)
        results_list.append(
            {
                "title": row.title,
                "artist": row.name,
                "minutes": int(minutes),
                "seconds": int(seconds),
                "price": row.album_price,
            }
        )
    return templates.TemplateResponse(
        name="partials/albums.html",
        context={
            "request": request,
            "albums": results_list,
        },
    )


@router.get("/customers", response_class=HTMLResponse)
async def get_customers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sort: str = Query(None, alias="sort"),
    direction: str = Query(None, alias="direction"),
    offset: int = 0,
    items_per_page: int = Query(10, alias="items_per_page"),
):
    limit = items_per_page
    async with db as session:
        query = (
            select(
                Customer.id,
                func.concat(Customer.last_name, ", ", Customer.first_name).label(
                    "fullname"
                ),
                func.count(Invoice.customer_id).label("orders_total"),
                func.sum(Invoice.total).label("orders_total_spent"),
            )
            .join(Invoice, Invoice.customer_id == Customer.id)
            .offset(offset)
            .limit(limit)
            .group_by("fullname")
        )
        query = query_order_by(query=query, sort=sort, direction=direction)
        results = await session.execute(query)

    # Convert each row to a dictionary
    results_list = []
    for row in results.fetchall():
        results_list.append(
            {
                "id": row.id,
                "full_name": row.fullname,
                "orders_total": row.orders_total,
                "orders_total_spent": row.orders_total_spent,
            }
        )
    return templates.TemplateResponse(
        name="partials/customers.html",
        context={
            "request": request,
            "customers": results_list,
        },
    )


@router.get("/employees", response_class=HTMLResponse)
async def get_employees(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sort: str = Query(None, alias="sort"),
    direction: str = Query(None, alias="direction"),
    offset: int = 0,
    items_per_page: int = Query(10, alias="items_per_page"),
):
    limit = items_per_page
    async with db as session:
        Manager = aliased(Employee)
        query = (
            select(
                Employee.id,
                func.concat(Employee.last_name, ", ", Employee.first_name).label(
                    "employee_fullname"
                ),
                func.concat(Manager.last_name, ", ", Manager.first_name).label(
                    "manager_fullname"
                ),
            )
            .outerjoin(Manager, Employee.reports_to == Manager.id)
            .offset(offset)
            .limit(limit)
            .group_by("employee_fullname")
        )
        query = query_order_by(query=query, sort=sort, direction=direction)
        results = await session.execute(query)

    # Convert each row to a dictionary
    results_list = []
    for row in results.fetchall():
        duration_seconds = row.album_duration / 1000
        minutes, seconds = divmod(duration_seconds, 60)
        results_list.append(
            {
                "title": row.title,
                "artist": row.name,
                "minutes": int(minutes),
                "seconds": int(seconds),
                "price": row.album_price,
            }
        )
    return templates.TemplateResponse(
        name="partials/albums.html",
        context={
            "request": request,
            "employees": results_list,
        },
    )


@router.get("/about", response_class=HTMLResponse)
async def get_about(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={"request": request},
    )


def query_order_by(query: Select, path: str, sort: str, direction: str) -> Select:
    """
    Modifies the passed in query to add an order_by clause with
    a direction determined by the class_ list
    
    :param query: the Select query to modify
    :param path: the path that brought us here
    :param sort: the data column to sort by
    :param direction: the sorting direction (asc, desc)
    :return: modified Select query
    """ ""
    sort_func = desc if direction == "desc" else asc

    match sort:
        case "artist_name":
            return query.order_by(sort_func(Artist.name))
        case "artist_album_count":
            return query.order_by(sort_func("album_count"))
        case "artist_track":
            return query.order_by(sort_func("track_count"))
        case "album_title":
            return query.order_by(sort_func(Album.title))
        case "album_duration":
            return query.order_by(sort_func("album_duration"))
        case "album_price":
            return query.order_by(sort_func("album_price"))
        case "customer_name":
            return query.order_by(sort_func("fullname"))
        case "customer_orders":
            return query.order_by(sort_func("orders_total"))
        case "customer_orders_spent":
            return query.order_by(sort_func("orders_total_spent"))
        case _:
            # Got here because @data-sort is undefined
            if path == "/application/artists":
                return query.order_by(sort_func(Artist.name))
