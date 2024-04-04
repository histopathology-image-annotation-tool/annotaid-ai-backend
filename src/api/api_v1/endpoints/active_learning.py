import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import and_, func, join, outerjoin, select
from sqlalchemy.ext.asyncio import AsyncSession

import src.db_models as db_models
from celery.result import AsyncResult
from src.core.celery import celery_app
from src.core.database import get_async_session
from src.schemas.active_learning import (
    ALPredictSlideRequest,
    Annotation,
    AnnotationMetadata,
    Counts,
    PaginatedResponse,
    Prediction,
    UpsertSlideAnnotationRequest,
    UpsertSlideAnnotationResponse,
    WholeSlideImageWithMetadata,
)
from src.schemas.celery import AsyncTaskResponse
from src.schemas.shared import HTTPError
from src.utils.pagination import PaginatedParams, paginate

router = APIRouter()


@router.get(
    '/active_learning/models/mc',
    response_model=AsyncTaskResponse,
    status_code=200,
)
async def get_slide_prediction_result(task_id: uuid.UUID) -> AsyncTaskResponse:
    task = AsyncResult(str(task_id))

    if not task.ready():
        return {
            'task_id': str(task_id),
            'status': task.state
        }

    for children_task in task.children:
        children_task.forget()
    task.forget()

    return {
        'task_id': str(task_id),
        'status': task.state
    }


@router.post(
    '/active_learning/models/mc',
    status_code=202,
    responses={
        202: {'model': AsyncTaskResponse},
        404: {'model': HTTPError}
    }
)
async def predict_slide(
    request: ALPredictSlideRequest,
    db: AsyncSession = Depends(get_async_session)
) -> AsyncTaskResponse:
    """Endpoint for initiating a mitosis detection task on a slide for active learning.
    """
    # Check if the slide is in database
    result = await db.execute(
        select(
            db_models.WholeSlideImage.path
        ).where(
            db_models.WholeSlideImage.id == request.id
        )
    )

    slide = result.fetchone()

    if slide is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Send task to process the slide
    task = celery_app.send_task(
        'src.celery.active_learning.tasks.process_wsi',
        kwargs={
            'path': Path(slide.path).as_posix()
        }
    )

    return {'task_id': task.task_id, 'status': task.status}


@router.get('/active_learning/slides')
async def get_slides(
    params: PaginatedParams = Depends(),
    user_id: str | None = None,
    db: AsyncSession = Depends(get_async_session)
) -> PaginatedResponse[WholeSlideImageWithMetadata]:
    slides_query = select(db_models.WholeSlideImage)

    slides = await paginate(
        db,
        slides_query,
        params.page,
        params.per_page
    )

    slide_ids = [
        slide.id for slide in slides['items']
    ]

    total_count_query = select(
        db_models.Prediction.wsi_id,
        db_models.Prediction.label,
        func.count(db_models.Prediction.label).label('count')
    ).select_from(
        db_models.Prediction
    ).where(
        db_models.Prediction.wsi_id.in_(slide_ids)
    ).group_by(
        db_models.Prediction.wsi_id,
        db_models.Prediction.label
    )

    total_counts_result = await db.execute(total_count_query)
    total_counts_result = total_counts_result.fetchall()

    slides_total_count: dict[uuid.UUID, dict[str, int]] = {}

    for row in total_counts_result:
        slide_id: uuid.UUID = row[0]
        label: str = row[1]
        count: int = row[2]

        if slide_id not in slides_total_count:
            slides_total_count[slide_id] = {}

        slides_total_count[slide_id].update({label: count})

    results: list[WholeSlideImageWithMetadata] = [
        WholeSlideImageWithMetadata(
            slide=slide.__dict__,
            metadata=AnnotationMetadata(
                total=Counts.from_dict(slides_total_count.get(slide.id, {}))
            )
        ) for slide in slides['items']
    ]

    if user_id is not None:
        user_annotation_count_query = select(
            db_models.Prediction.wsi_id,
            db_models.Annotation.label,
            func.count().label('count')
        ).select_from(
            outerjoin(
                db_models.Annotation,
                db_models.Prediction,
                and_(
                    db_models.Prediction.wsi_id.in_(slide_ids),
                    db_models.Annotation.user_id == user_id,
                    db_models.Prediction.id == db_models.Annotation.prediction_id
                )
            )
        ).group_by(
            db_models.Prediction.wsi_id,
            db_models.Annotation.label
        )

        user_annotation_count_result = await db.execute(user_annotation_count_query)
        user_annotation_count_result = user_annotation_count_result.fetchall()

        user_counts: dict[uuid.UUID, dict[str, int]] = {}

        for row in user_annotation_count_result:
            slide_id: uuid.UUID = row[0]  # type: ignore
            label: str = row[1]  # type: ignore
            count: int = row[2]  # type: ignore

            if slide_id not in user_counts:
                user_counts[slide_id] = {}

            user_counts[slide_id].update({label: count})

        for result in results:
            result.metadata.user_annotated = Counts.from_dict(
                user_counts.get(result.slide.id, {})
            )

    return PaginatedResponse(
        total=slides['total'],
        items=results,
        page=slides['page'],
        pages=slides['pages'],
        next_page=slides['next_page'],
        previous_page=slides['previous_page']
    )


@router.get(
    '/active_learning/slides/{slide_id}',
    response_model=WholeSlideImageWithMetadata,
    status_code=200,
    responses={
        200: {'model': WholeSlideImageWithMetadata},
        404: {'model': HTTPError}
    }
)
async def get_slide(
    slide_id: uuid.UUID,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_async_session)
) -> WholeSlideImageWithMetadata:
    # Check if the slide is in database
    result = await db.execute(
        select(
            db_models.WholeSlideImage
        ).where(
            db_models.WholeSlideImage.id == slide_id
        )
    )

    slide = result.fetchone()

    if slide is None:
        raise HTTPException(status_code=404, detail="Item not found")

    slide = slide[0]

    total_count_query = select(
        db_models.Prediction.wsi_id,
        db_models.Prediction.label,
        func.count(db_models.Prediction.label).label('count')
    ).select_from(
        db_models.Prediction
    ).where(
        db_models.Prediction.wsi_id.in_([slide_id])
    ).group_by(
        db_models.Prediction.wsi_id,
        db_models.Prediction.label
    )

    total_counts_result = await db.execute(total_count_query)
    total_counts_result = total_counts_result.fetchall()

    slides_total_count: dict[uuid.UUID, dict[str, int]] = {}

    for row in total_counts_result:
        label: str = row[1]
        count: int = row[2]

        if slide_id not in slides_total_count:
            slides_total_count[slide_id] = {}

        slides_total_count[slide_id].update({label: count})

    result = WholeSlideImageWithMetadata(
        slide=slide.__dict__,
        metadata=AnnotationMetadata(
            total=Counts.from_dict(slides_total_count.get(slide.id, {}))
        )
    )

    if user_id is not None:
        user_annotation_count_query = select(
            db_models.Prediction.wsi_id,
            db_models.Annotation.label,
            func.count().label('count')
        ).select_from(
            outerjoin(
                db_models.Annotation,
                db_models.Prediction,
                and_(
                    db_models.Prediction.wsi_id.in_([slide_id]),
                    db_models.Annotation.user_id == user_id,
                    db_models.Prediction.id == db_models.Annotation.prediction_id
                )
            )
        ).group_by(
            db_models.Prediction.wsi_id,
            db_models.Annotation.label
        )

        user_annotation_count_result = await db.execute(user_annotation_count_query)
        user_annotation_count_result = user_annotation_count_result.fetchall()

        user_counts: dict[uuid.UUID, dict[str, int]] = {}

        for row in user_annotation_count_result:
            slide_id = row[0]
            label = row[1]
            count = row[2]

            if slide_id not in user_counts:
                user_counts[slide_id] = {}

            user_counts[slide_id].update({label: count})

        result.metadata.user_annotated = Counts.from_dict(
            user_counts.get(result.slide.id, {})
        )

    return result


@router.post(
    '/active_learning/slides',
    status_code=202,
    response_model=AsyncTaskResponse
)
async def synchronize_slides() -> AsyncTaskResponse:
    task = celery_app.send_task(
        'src.celery.active_learning.tasks.synchronize_slides'
    )

    return {'task_id': task.task_id, 'status': task.status}


@router.get(
    '/active_learning/slides/{slide_id}/predictions',
    responses={
        200: {'model': Optional[Prediction]},
        404: {'model': HTTPError}
    }
)
async def get_slide_prediction_for_annotation(
    slide_id: uuid.UUID,
    user_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> Prediction | None:
    # Check if the slide is in database
    result = await db.execute(
        select(
            db_models.WholeSlideImage.path
        ).where(
            db_models.WholeSlideImage.id == slide_id
        )
    )

    slide = result.fetchone()

    if slide is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return await get_next_annotation(db, slide_id, user_id)


@router.get(
    '/active_learning/slides/{slide_id}/annotations',
    responses={
        200: {'model': list[Annotation]},
        404: {'model': HTTPError}
    }
)
async def get_slide_annotations(
    slide_id: uuid.UUID,
    user_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> list[Annotation]:
    # Check if the slide is in database
    result = await db.execute(
        select(
            db_models.WholeSlideImage
        ).where(
            db_models.WholeSlideImage.id == slide_id
        )
    )

    slide = result.fetchone()

    if slide is None:
        raise HTTPException(status_code=404, detail="Item not found")

    slide = slide[0]

    annotations_query = select(
        db_models.Annotation
    ).select_from(
        join(
            db_models.Annotation,
            db_models.Prediction,
            and_(
                db_models.Annotation.prediction_id == db_models.Prediction.id,
                db_models.Prediction.wsi_id == slide_id,
                db_models.Annotation.user_id == user_id
            )
        )
    ).order_by(
        db_models.Annotation.created_at.desc()
    )

    annotations_result = await db.execute(annotations_query)
    annotations_result = annotations_result.fetchall()

    return [
        result[0]
        for result in annotations_result
    ]


@router.post(
    '/active_learning/predictions/{prediction_id}/annotations',
    responses={
        200: {'model': UpsertSlideAnnotationResponse},
        201: {'model': UpsertSlideAnnotationResponse},
        404: {'model': HTTPError}
    }
)
async def upsert_slide_annotations(
    prediction_id: uuid.UUID,
    request: UpsertSlideAnnotationRequest,
    response: Response,
    db: AsyncSession = Depends(get_async_session)
) -> UpsertSlideAnnotationResponse:
    # Check if the prediction is in database
    prediction_result = await db.execute(
        select(db_models.Prediction).where(
            db_models.Prediction.id == prediction_id
        )
    )

    prediction = prediction_result.fetchone()

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    prediction = prediction[0]

    # Check if the annotation is in database
    annotation_result = await db.execute(
        select(
            db_models.Annotation
        ).where(
            db_models.Annotation.prediction_id == prediction_id
        ).where(
            db_models.Annotation.user_id == request.user_id
        )
    )

    annotation = annotation_result.fetchone()

    if annotation is None:
        new_annotation = db_models.Annotation(
            user_id=request.user_id,
            prediction_id=prediction_id,
            bbox=request.bbox.convert_to_wkt(),
            label=request.label
        )

        db.add(new_annotation)
        await db.commit()
        await db.refresh(new_annotation)

        response.status_code = status.HTTP_201_CREATED
        return new_annotation

    annotation = annotation[0]

    if annotation.prediction_id != prediction_id:
        raise HTTPException(status_code=404, detail="Annotation not found")

    annotation.user_id = request.user_id
    annotation.bbox = request.bbox.convert_to_wkt()
    annotation.label = request.label

    await db.commit()
    await db.refresh(annotation)

    next_annotation = await get_next_annotation(
        db,
        prediction.wsi_id,
        request.user_id
    )

    return {  # type: ignore
        'annotation': annotation,
        'next_annotation': next_annotation
    }


async def get_next_annotation(
    db: AsyncSession,
    slide_id: uuid.UUID,
    user_id: str
) -> Prediction | None:
    # Get annotation (prediction) for the slide for the given user
    query = select(db_models.Prediction).select_from(
        outerjoin(
            db_models.Prediction,
            db_models.Annotation,
            and_(
                db_models.Prediction.wsi_id == slide_id,
                db_models.Annotation.user_id == user_id,
                db_models.Prediction.id == db_models.Annotation.prediction_id
            )
        )
    ).where(db_models.Annotation.prediction_id.is_(None)).order_by(
        db_models.Prediction.probability.asc()
    )

    annotation = await db.execute(query)
    annotation = annotation.first()

    return annotation[0] if annotation is not None else None
