from typing import TypedDict

from fastapi import Query
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.middlewares import request_object


class PaginatedParams:
    """Represents the query parameters for pagination."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(50, ge=1, le=100, description="Page size")
    ) -> None:
        self.page = page
        self.per_page = per_page


class PaginationResult(TypedDict):
    """Represents the response of a paginated query."""
    total: int
    next_page: str | None
    previous_page: str | None
    items: list[dict]
    page: int
    pages: int


class Paginator:
    """Paginator is a helper class for paginating queries."""

    def __init__(
        self,
        session: AsyncSession,
        query: Select,
        page: int,
        per_page: int
    ) -> None:
        """Initializes the paginator.

        Args:
            session (AsyncSession): The database session.
            query (Select): The query to paginate.
            page (int): The page number.
            per_page (int): The number of items per page.

        Returns:
            None: The paginator is initialized.
        """
        self.session = session
        self.query = query
        self.page = page
        self.per_page = per_page
        self.limit = per_page * page
        self.offset = (page - 1) * per_page
        self.request = request_object.get()
        # computed later
        self.number_of_pages = 0
        self.next_page = ''
        self.previous_page = ''

    def _get_next_page(self) -> str | None:
        """Returns the URL for the next page.

        Returns:
            str | None: The URL for the next page.
        """
        if self.page >= self.number_of_pages:
            return None
        url = self.request.url.include_query_params(page=self.page + 1)
        return str(url)

    def _get_previous_page(self) -> str | None:
        """Returns the URL for the previous page.

        Returns:
            str | None: The URL for the previous page.
        """
        if self.page == 1 or self.page > self.number_of_pages + 1:
            return None
        url = self.request.url.include_query_params(page=self.page - 1)
        return str(url)

    async def get_response(self) -> PaginationResult:
        """Returns the paginated response.

        Returns:
            PaginationResult: The paginated response.
        """
        return {
            'total': await self._get_total_count(),
            'next_page': self._get_next_page(),
            'previous_page': self._get_previous_page(),
            'items': [
                todo
                for todo in await self.session.scalars(
                    self.query.limit(self.limit).offset(self.offset)
                )
            ],
            'page': self.page,
            'pages': self.number_of_pages,
        }

    def _get_number_of_pages(self, count: int) -> int:
        """Returns the number of pages.

        Args:
            count (int): The total number of items.

        Returns:
            int: The number of pages.
        """
        rest = count % self.per_page
        quotient = count // self.per_page
        return quotient if not rest else quotient + 1

    async def _get_total_count(self) -> int:
        """Returns the total number of items.

        Returns:
            int: The total number of items.
        """
        count = await self.session.scalar(
            select(func.count()).select_from(self.query.subquery())
        )
        self.number_of_pages = self._get_number_of_pages(count)
        return count


async def paginate(
    db: AsyncSession,
    query: Select,
    page: int,
    per_page: int
) -> PaginationResult:
    """Paginates a query and returns the response.

    Args:
        db (AsyncSession): The database session.
        query (Select): The query to paginate.
        page (int): The page number.
        per_page (int): The number of items per page.

    Returns:
        PaginationResult: The paginated response.
    """
    paginator = Paginator(db, query, page, per_page)
    return await paginator.get_response()
