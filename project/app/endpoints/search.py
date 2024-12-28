from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.models import search

# create a router for the model
router = APIRouter(
    prefix="/{search}",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_db)],
)


@router.get("/search", response_model=search.SearchResponse)
async def search_text(
    query: str,
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Search across all text columns or specific table/column

    Args:
        query: Search term
        table_name: Optional filter by table name
        column_name: Optional filter by column name
        limit: Maximum number of results to return
        offset: Number of results to skip
    """
    try:
        async with db as session:
            conn = await session.connection()

            # Base query
            base_query = """
                SELECT table_name, column_name, content, content_rowid
                FROM text_search
                WHERE content MATCH :query
            """

            # Add filters if provided
            filters = []
            params = {"query": f'"{query}"'}

            if table_name:
                filters.append("table_name = :table_name")
                params.append(table_name)

            if column_name:
                filters.append("column_name = :column_name")
                params.append(column_name)

            if filters:
                base_query += f" AND {' AND '.join(filters)}"

            # Add ordering and pagination
            base_query += " ORDER BY rank LIMIT :limit OFFSET :offset"
            params.update(
                {
                    "limit": limit,
                    "offset": offset,
                }
            )

            # Execute search query
            results = await conn.execute(text(base_query), params)
            results = results.fetchall()

            # Get total count
            count_query = f"""
                SELECT COUNT(*) FROM text_search 
                WHERE content MATCH :query
                {f"AND {' AND '.join(filters)}" if filters else ""}
            """
            total_results = await conn.execute(text(count_query), params)
            total_count = total_results.fetchone()[0]

            # Format results
            formatted_results = [
                search.SearchResponse(
                    table_name=row[0],
                    column_name=row[1],
                    content=row[2],
                    content_rowid=row[3],
                )
                for row in results
            ]

            return search.SearchResponse(
                results=formatted_results, total_count=total_count
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
