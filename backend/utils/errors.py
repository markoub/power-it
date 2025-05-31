import traceback
import functools
from typing import TypeVar, Callable, Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal, StepStatus, PresentationStep
from utils.database import update_step_status

T = TypeVar('T')


def handle_task_error(step: PresentationStep):
    """
    Decorator to handle errors in background tasks and update step status
    
    Args:
        step: The PresentationStep enum value for the task
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(presentation_id: int, *args, **kwargs) -> Optional[T]:
            async with SessionLocal() as db:
                try:
                    # Call the original function
                    result = await func(presentation_id, *args, **kwargs)
                    return result
                except Exception as e:
                    # Log the error with full traceback
                    print(f"Error in {func.__name__} for presentation {presentation_id}: {str(e)}")
                    print(traceback.format_exc())
                    
                    # Update step status to failed
                    await update_step_status(
                        db=db,
                        presentation_id=presentation_id,
                        step=step,
                        status=StepStatus.FAILED,
                        error=str(e)
                    )
                    return None
        return wrapper
    return decorator


class PresentationError(Exception):
    """Base exception for presentation-related errors"""
    pass


class StepNotFoundError(PresentationError):
    """Raised when a required step is not found"""
    def __init__(self, presentation_id: int, step: PresentationStep):
        self.presentation_id = presentation_id
        self.step = step
        super().__init__(f"Step {step.value} not found for presentation {presentation_id}")


class StepNotCompletedError(PresentationError):
    """Raised when a required step is not completed"""
    def __init__(self, presentation_id: int, step: PresentationStep):
        self.presentation_id = presentation_id
        self.step = step
        super().__init__(f"Step {step.value} not completed for presentation {presentation_id}")


class ImageGenerationError(PresentationError):
    """Raised when image generation fails"""
    pass


class PPTXGenerationError(PresentationError):
    """Raised when PPTX generation fails"""
    pass


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format an exception into a standardized error response
    
    Args:
        error: The exception to format
        
    Returns:
        Dictionary with error details
    """
    error_response = {
        "error": str(error),
        "type": type(error).__name__
    }
    
    # Add specific error details for custom exceptions
    if isinstance(error, StepNotFoundError):
        error_response["presentation_id"] = error.presentation_id
        error_response["step"] = error.step.value
    elif isinstance(error, StepNotCompletedError):
        error_response["presentation_id"] = error.presentation_id
        error_response["step"] = error.step.value
    
    return error_response