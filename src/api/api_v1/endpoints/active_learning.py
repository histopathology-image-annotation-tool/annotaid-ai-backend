import uuid
from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from redis import Redis
from sqlalchemy import and_, func, join, outerjoin, select
from sqlalchemy.ext.asyncio import AsyncSession

import src.db_models as db_models
from celery.result import AsyncResult
from src.celery import AL_QUEUE, READER_QUEUE
from src.core.celery import celery_app
from src.core.database import get_async_session
from src.core.redis import get_redis_session
from src.schemas.active_learning import (
    ALPredictSlideRequest,
    Annotation,
    AnnotationMetadata,
    Counts,
    PaginatedResponse,
    Prediction,
    PredictionWithMetadata,
    UpsertSlideAnnotationRequest,
    UpsertSlideAnnotationResponse,
    WholeSlideImageWithMetadata,
)
from src.schemas.celery import AsyncTaskResponse
from src.schemas.shared import CUID, HTTPError
from src.utils.api import exist_task
from src.utils.pagination import PaginatedParams, paginate

router = APIRouter()

PROCESS_SLIDE_TASK_NAME = 'src.celery.active_learning.tasks.process_slide'


@router.get(
    '/active_learning/models/mc',
    response_model=AsyncTaskResponse,
    responses={
        202: {'model': AsyncTaskResponse},
        404: {'model': HTTPError}
    }
)
async def get_slide_prediction_result(
    task_id: uuid.UUID,
    db_redis: Redis = Depends(get_redis_session)
) -> AsyncTaskResponse:
    """Endpoint for retrieving the result of a slide mitosis detection task."""
    if not exist_task(db_redis, task_id):
        raise HTTPException(status_code=404, detail='Task not found')

    task = AsyncResult(str(task_id))

    if task.name != PROCESS_SLIDE_TASK_NAME:
        raise HTTPException(status_code=404, detail='Task not found')

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
    If the provided task_id doesn't belong to any submitted task,
    the PENDING status is returned.
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
        PROCESS_SLIDE_TASK_NAME,
        kwargs={
            'path': Path(slide.path).as_posix()
        },
        queue=AL_QUEUE
    )

    return {'task_id': task.task_id, 'status': task.status}


@router.get('/active_learning/slides')
async def get_slides(
    params: PaginatedParams = Depends(),
    user_id: CUID | None = None,
    search: Annotated[
        str | None,
        Query(
            max_length=100,
            description="Full-text search by path (ignore-case)"
        )
    ] = None,
    only_predicted: Annotated[
        bool,
        Query(
            description="Filter only slides with predictions"
        )
    ] = False,
    db: AsyncSession = Depends(get_async_session)
) -> PaginatedResponse[WholeSlideImageWithMetadata]:
    """Endpoint for retrieving a list of slides with metadata for active learning."""
    slides_query = select(
        db_models.WholeSlideImage,
    )

    if only_predicted:
        slides_query = slides_query.distinct().select_from(
            join(
                db_models.WholeSlideImage,
                db_models.Prediction,
                db_models.WholeSlideImage.id == db_models.Prediction.slide_id
            )
        )

    if search is not None:
        slides_query = slides_query.where(
            db_models.WholeSlideImage.path.icontains(search)
        )

    print(str(slides_query))

    slides = await paginate(
        db,
        slides_query,
        params.page,
        params.per_page
    )

    slide_ids = [
        slide.id for slide in slides['items']
    ]

    slides_total_count = await get_total_predictions_count(db, slide_ids)

    results: list[WholeSlideImageWithMetadata] = [
        WholeSlideImageWithMetadata(
            slide=slide.__dict__,
            metadata=AnnotationMetadata(
                total=Counts.from_dict(slides_total_count.get(slide.id, {}))
            )
        ) for slide in slides['items']
    ]

    if user_id is not None:
        user_counts = await get_total_annotations_count(db, slide_ids, user_id)

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
    user_id: CUID | None = None,
    db: AsyncSession = Depends(get_async_session)
) -> WholeSlideImageWithMetadata:
    """Endpoint for retrieving a slide with metadata for active learning."""

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

    slides_total_count = await get_total_predictions_count(db, [slide_id])

    result = WholeSlideImageWithMetadata(
        slide=slide.__dict__,
        metadata=AnnotationMetadata(
            total=Counts.from_dict(slides_total_count.get(slide.id, {}))
        )
    )

    if user_id is not None:
        user_counts = await get_total_annotations_count(db, [slide_id], user_id)

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
    """Endpoint for initiating a slide synchronization task with the slide store.
    """

    task = celery_app.send_task(
        'src.celery.active_learning.tasks.synchronize_slides',
        ignore_result=True,
        queue=READER_QUEUE
    )

    return {'task_id': task.task_id, 'status': task.status}


@router.get(
    '/active_learning/slides/{slide_id}/predictions',
    responses={
        200: {'model': Optional[Prediction]},
        204: {'model': None},
        404: {'model': HTTPError}
    },
)
async def get_slide_prediction_for_annotation(
    slide_id: uuid.UUID,
    user_id: CUID,
    db: AsyncSession = Depends(get_async_session)
) -> PredictionWithMetadata | None:
    """Endpoint for retrieving the next prediction for annotation on a slide
    for specified user.
    """

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

    prediction = await get_next_annotation(db, slide_id, user_id)

    if prediction is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    user_annotated_count = await get_total_annotations_count(db, [slide_id], user_id)
    total_count = await get_total_predictions_count(db, [slide_id])

    return {
        'prediction': prediction,
        'metadata': AnnotationMetadata(
            user_annotated=Counts.from_dict(user_annotated_count.get(slide_id, {})),
            total=Counts.from_dict(total_count.get(slide_id, {}))
        )
    }


@router.get(
    '/active_learning/slides/{slide_id}/annotations',
    responses={
        200: {'model': list[Annotation]},
        404: {'model': HTTPError}
    }
)
async def get_slide_annotations(
    slide_id: uuid.UUID,
    user_id: CUID,
    db: AsyncSession = Depends(get_async_session)
) -> list[Annotation]:
    """Endpoint for retrieving user annotations for a slide."""

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
                db_models.Prediction.slide_id == slide_id,
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
    """Endpoint for upserting an annotation for a prediction.
    If the annotation with given prediction_id and user_id exists,
    it will be updated, otherwise created.
    """

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

    annotation = annotation_result.scalar()

    if annotation is None:
        new_annotation = db_models.Annotation(
            user_id=request.user_id,
            prediction_id=prediction_id,
            bbox=request.bbox.convert_to_wkt(),
            label=request.label,
            message=request.message
        )

        db.add(new_annotation)
        await db.commit()
        await db.refresh(new_annotation)

        response.status_code = status.HTTP_201_CREATED

        annotation = new_annotation
    else:
        if annotation.prediction_id != prediction_id:
            raise HTTPException(status_code=404, detail="Annotation not found")

        annotation.user_id = request.user_id
        annotation.bbox = request.bbox.convert_to_wkt()
        annotation.label = request.label
        annotation.message = request.message

        await db.commit()
        await db.refresh(annotation)

    next_annotation = await get_next_annotation(
        db,
        prediction.slide_id,
        request.user_id
    )

    user_annotated_count = await get_total_annotations_count(
        db,
        [prediction.slide_id],
        request.user_id
    )
    total_count = await get_total_predictions_count(db, [prediction.slide_id])

    return {
        'annotation': annotation,
        'next_annotation': next_annotation,
        'metadata': AnnotationMetadata(
            user_annotated=Counts.from_dict(user_annotated_count.get(
                prediction.slide_id, {}
            )),
            total=Counts.from_dict(total_count.get(prediction.slide_id, {}))
        )
    }


async def get_next_annotation(
    db: AsyncSession,
    slide_id: uuid.UUID,
    user_id: CUID
) -> Prediction | None:
    """Get the next prediction for annotation for the given slide and user."""

    # Get annotation (prediction) for the slide for the given user
    query = select(db_models.Prediction).select_from(
        outerjoin(
            db_models.Prediction,
            db_models.Annotation,
            and_(
                db_models.Prediction.id == db_models.Annotation.prediction_id,
                db_models.Annotation.user_id == user_id
            )
        )
    ).where(
        db_models.Annotation.prediction_id.is_(None)
    ).where(
        db_models.Prediction.slide_id == slide_id
    ).order_by(
        db_models.Prediction.probability.asc()
    )

    annotation = await db.execute(query)
    annotation = annotation.first()

    return annotation[0] if annotation is not None else None


async def get_total_predictions_count(
    db: AsyncSession,
    slide_ids: list[uuid.UUID]
) -> dict[uuid.UUID, dict[str, int]]:
    """Get the total count of predictions for the given slides.

    Args:
        db: AsyncSession: Database session
        slide_ids: list[uuid.UUID]: List of slide ids

    Returns:
        dict[uuid.UUID, dict[str, int]]: Total count of predictions for each slide
    """

    total_count_query = select(
        db_models.Prediction.slide_id,
        db_models.Prediction.label,
        func.count(db_models.Prediction.label).label('count')
    ).select_from(
        db_models.Prediction
    ).where(
        db_models.Prediction.slide_id.in_(slide_ids)
    ).group_by(
        db_models.Prediction.slide_id,
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

    return slides_total_count


async def get_total_annotations_count(
    db: AsyncSession,
    slide_ids: list[uuid.UUID],
    user_id: CUID
) -> dict[uuid.UUID, dict[str, int]]:
    """Get the total count of annotations for the given slides and user.

    Args:
        db: AsyncSession: Database session
        slide_ids: list[uuid.UUID]: List of slide ids
        user_id: CUID: User id

    Returns:
        dict[uuid.UUID, dict[str, int]]: Total count of annotations for each slide
        and user"""
    user_annotation_count_query = select(
        db_models.Prediction.slide_id,
        db_models.Annotation.label,
        func.count().label('count')
    ).select_from(
        join(
            db_models.Annotation,
            db_models.Prediction,
            and_(
                db_models.Prediction.slide_id.in_(slide_ids),
                db_models.Annotation.user_id == user_id,
                db_models.Prediction.id == db_models.Annotation.prediction_id
            )
        )
    ).group_by(
        db_models.Prediction.slide_id,
        db_models.Annotation.label
    )

    user_annotation_count_result = await db.execute(user_annotation_count_query)
    user_annotation_count_result = user_annotation_count_result.fetchall()

    user_counts: dict[uuid.UUID, dict[str, int]] = {}

    for row in user_annotation_count_result:
        slide_id: uuid.UUID = row[0]
        label: str = row[1]
        count: int = row[2]

        if slide_id not in user_counts:
            user_counts[slide_id] = {}

        user_counts[slide_id].update({label: count})

    return user_counts
