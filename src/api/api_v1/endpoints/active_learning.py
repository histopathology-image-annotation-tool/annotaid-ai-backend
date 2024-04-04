import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import and_, func, outerjoin, select
from sqlalchemy.ext.asyncio import AsyncSession

import src.db_models as db_models
from celery.result import AsyncResult
from src.core.celery import celery_app
from src.core.database import get_async_session
from src.schemas.active_learning import (
    ALPredictSlideRequest,
    Annotation,
    Counts,
    PaginatedResponse,
    Prediction,
    UpdateSlideAnnotationRequest,
    WholeSlideImageWithCounts,
)
from src.schemas.celery import AsyncTaskResponse
from src.schemas.shared import HTTPError
from src.utils.pagination import paginate

router = APIRouter()


@router.get(
    '/active_learning/models/mc',
)
async def get_slide_prediction_result(task_id: uuid.UUID):
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
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_async_session)
) -> PaginatedResponse[WholeSlideImageWithCounts]:
    # TODO: dať tam iba počet anotácií

    # TODO: pridat tam pocet anotacii pre konkretneho usera

    slides_query = select(db_models.WholeSlideImage)
    
    slides = await paginate(
        db,
        slides_query,
        page,
        per_page
    )

    print(slides)

    slide_ids = [
        slide.id for slide in slides['items']
    ]

    print(slide_ids)

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

    print(total_counts_result)

    results: list[WholeSlideImageWithCounts] = []

    slides_data = {}

    for row in total_counts_result:
        slide_id = str(row[0])
        label = 'mitosis' if row[1] == '0' else 'hard_negative_mitosis'
        count = row[2]

        if slide_id not in slides_data:
            slides_data[slide_id] = {
                'mitosis': 0,
                'hard_negative_mitosis': 0
            }

        slides_data[slide_id][label] = count

    print(slides_data)

    for slide in slides['items']:
        counts = slides_data.get(str(slide.id), {
            'mitosis': 0,
            'hard_negative_mitosis': 0
        })

        print(slide, counts)

        results.append(
            WholeSlideImageWithCounts(
                slide=slide.__dict__,
                counts=Counts(**counts)
            )
        )

    return PaginatedResponse(
        total=slides['count'],
        items=results,
        page=slides['page'],
        pages=slides['pages'],
        next_page=slides['next_page'],
        previous_page=slides['previous_page']
    )


@router.post(
    '/active_learning/slides',
    status_code=202,
    response_model=AsyncTaskResponse
)
async def synchronize_slides() -> AsyncTaskResponse:
    task = celery_app.send_task(
        'src.celery.active_learning.tasks.discover_wsi_files'
    )

    return {'task_id': task.task_id, 'status': task.status}


@router.get(
    '/active_learning/slides/{slide_id}/predictions',
    responses={
        404: {'model': HTTPError}
    }
)
async def get_slide_predictions_for_annotation(
    slide_id: uuid.UUID,
    user_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> Prediction:
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

    # Get annotation for the slide for the given user
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
    annotation = annotation.first()[0]

    return annotation


@router.post(
    '/active_learning/predictions/{prediction_id}/annotations',
    status_code=200,
    responses={
        200: {'model': Annotation},
        201: {'model': Annotation},
        404: {'model': HTTPError}
    }
)
async def upsert_slide_annotations(
    prediction_id: uuid.UUID,
    request: UpdateSlideAnnotationRequest,
    response: Response,
    db: AsyncSession = Depends(get_async_session)
) -> Annotation:
    # Check if the prediction is in database
    prediction_result = await db.execute(
        select(1).where(
            db_models.Prediction.id == prediction_id
        )
    )

    prediction = prediction_result.fetchone()

    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

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

    # TODO: return next annotation

    return annotation


@router.get('/active_learning/slides/{slide_id}/annotations/download')
async def download_slide_annotations():
    pass


@router.get('/active_learning')
async def active_learning():
    task = celery_app.send_task(
        'src.celery.active_learning.tasks.process_wsi',
        kwargs={
            'path': 'mnt/10_HE.vsi'
        }
    )
    return {'task_id': task.task_id, 'status': task.status}


@router.get('/active_learning_2')
async def active_learning_2():
    task = celery_app.send_task(
        'src.celery.active_learning.tasks.test',
    )
    return {'task_id': task.task_id, 'status': task.status}