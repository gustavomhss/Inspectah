from __future__ import annotations

from typing import Any, Dict

from app.core import pipeline

from . import schemas, view_models


def post_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = schemas.UserQueryRequest(**payload)
    response = pipeline.run_pipeline(request.query)
    dto = schemas.UserQueryResponse.from_user_response(response)
    view = view_models.build_user_response_view(response)
    return {"dto": dto.to_dict(), "view": view}
