"""
URL configuration for the project.

WHAT GOES HERE:
- Maps URL patterns to view functions or class-based views.
- Use path() for simple routes, re_path() for regex patterns.
- Include app-level urlconf with include() for modular routing.
- Best practice: Keep the root urls.py lean; delegate to app urls with include().

URL PATTERN SYNTAX:
    path("route/", view_function, name="url_name")
    path("article/<int:pk>/", view_function)  # Captures pk as integer
"""

from django.contrib import admin
from django.urls import path, include

from app.views import job_search

urlpatterns = [
    # Admin site - available at /admin/
    path("admin/", admin.site.urls),

    # Default page - job search
    path("", job_search, name="job_search"),
]
