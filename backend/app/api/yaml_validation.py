from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.services.yaml_validator import validate_script_yaml

router = APIRouter()


class ValidateYamlRequest(BaseModel):
    yaml_text: str = Field(default="")


class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/validate-yaml", response_model=ApiResponse)
def validate_yaml_endpoint(request: ValidateYamlRequest) -> ApiResponse:
    result = validate_script_yaml(request.yaml_text)

    return ApiResponse(
        success=True,
        data={
            "is_parseable": result.is_parseable,
            "is_valid": result.is_valid,
            "message": result.message,
            "errors": result.errors,
            "top_level_fields": result.top_level_fields,
            "summary": result.summary,
            "characters_preview": result.characters_preview,
            "scenes_preview": result.scenes_preview,
        },
        error=None,
    )
