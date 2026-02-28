"""
Views handle HTTP requests and return HTTP responses.

WHAT GOES HERE:
- Function-based views (FBV): Simple functions that take request, return HttpResponse.
- Class-based views (CBV): Reusable view classes (ListView, DetailView, etc.).
- Request handling: Parse query params, form data, JSON.
- Response types: HttpResponse, JsonResponse, redirect, render (template).

BEST PRACTICES:
- Keep views thin: business logic belongs in models or services.
- Use render() for HTML; JsonResponse for APIs.
- Return appropriate status codes (404, 403, etc.).
"""

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from app.services import genSummarizedJobOutputJSON, generate_gemini_response




def template_example(request):
    """
    Renders an HTML template (requires templates/home.html to exist).
    Uncomment and create the template to use.
    """
    return render(request, "home.html", {"title": "Home"})


def job_search(request):
    """
    Serves the job search form. Handles GET and POST.
    """
    output = ""
    job_title = ""
    location = ""
    if request.method == "POST":
        job_title = request.POST.get("job_title", "")
        location = request.POST.get("location", "")
        resume = request.FILES.get("resume")
        query = f"{job_title} in {location}"
        jSearchOutput = genSummarizedJobOutputJSON(query)
        geminiOutput = generate_gemini_response(resume, jSearchOutput)
        output = geminiOutput
    return render(request, "job_search.html", {
        "job_title": job_title,
        "location": location,
        "job_search_output": output,
    })
