import logging
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST # Optional but good practice
from django.views.decorators.csrf import csrf_exempt # Use carefully, or ensure CSRF is handled (we handle it in JS)

# Get an instance of your app's logger
# Using __name__ is common; it will give the logger name 'myapp.views'
logger = logging.getLogger(__name__)

# Get the 'django' logger defined in settings, to simulate messages from Django itself
django_logger = logging.getLogger('django')


def index_view(request):
    """
    Renders the main index.html template.
    """
    return render(request, 'index.html')


# @csrf_exempt # Only use if you cannot send the CSRF token in the header
@require_POST # Ensure this view only accepts POST requests
def log_message(request):
    """
    Receives a log level via POST and triggers the corresponding logger.
    """
    try:
        # Load the JSON data from the request body
        data = json.loads(request.body)
        level_str = data.get('level') # Get the log level string

        if not level_str:
            return JsonResponse({"status": "error", "message": "Log level not provided"}, status=400)

        # Map the string level to the logging module's integer level
        # Or, even better, get the method directly from the logger instance
        level_lower = level_str.lower()

        # Check if the requested level is a valid logging method name
        if not hasattr(logger, level_lower) or not callable(getattr(logger, level_lower)):
             return JsonResponse({"status": "error", "message": f"Invalid log level: {level_str}"}, status=400)

        # Get the logging method (e.g., logger.debug, logger.info)
        log_method = getattr(logger, level_lower)

        # Trigger the log message
        # Use the django_logger to see messages routed through the 'django' logger config
        # Or use the app logger 'logger' (logging.getLogger(__name__))
        django_logger.log(
            getattr(logging, level_str.upper()), # Get the integer level (logging.DEBUG, logging.INFO, etc.)
            f"Log message triggered from button: {level_str.upper()}"
        )
        # Using the specific method is also common and clearer:
        # log_method(f"Log message triggered from button: {level_str.upper()}")
        # Note: If you use logger.debug(), it goes to logger 'myapp.views', not 'django'.
        # The original LOGGING config only sets up handlers for 'django'.
        # Let's stick to using django_logger for demonstration based on the provided LOGGING config.

        return JsonResponse({"status": "success", "level": level_str})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"An unexpected error occurred in log_message view: {e}", exc_info=True)
        return JsonResponse({"status": "error", "message": "An internal error occurred"}, status=500)

