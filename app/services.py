"""
Services handle business logic, data processing, and external API integrations.

WHAT GOES HERE:
- Functions that process data, call APIs, or perform complex operations.
- Independent of HTTP requests/responses (no request/response logic).
- Reusable across views and other parts of the app.
- Best practice: Keep services focused; delegate to models for data access.
"""
# Gemini API integration/infrastructure
from google import genai
import os
import json
import requests
# Loads the .env file into the environment variables
def _load_dotenv_if_present(dotenv_path: str = ".env") -> bool:
    try:
        if not os.path.exists(dotenv_path):
            return False
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)
        return True
    except Exception:
        return False


dotenv_loaded = _load_dotenv_if_present(".env")
gemini_api_key = os.getenv("GEMINI_API_KEY")
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
if not gemini_api_key:
    raise ValueError("Missing GEMINI_API_KEY in environment (did you load .env?)")
client = genai.Client(api_key=gemini_api_key)

# Checks if the python-docx library is installed
try:
    import docx  # type: ignore[import-not-found]
except ImportError as e:
    print("'python-docx' library required to read resume, install it in the virtual environment with 'pip install python-docx'")
# Jsearch API Function
def genSummarizedJobOutputJSON(query, country="us"):

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": query,
        "page":"1",
        "num_pages":"1",
        "country": country,
        "date_posted":"all"
        }

    headers = {
        "x-rapidapi-key": os.getenv("JSEARCH_API_KEY"),
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    # print(response.json())

    with open("FullOutput.json", "w", encoding="utf-8") as file:
        json.dump(response.json(), file, indent=4)

    with open("FullOutput.json", "r", encoding="utf-8") as file:
        fullJobDict = json.load(file)

    sumJobDict = {}

    for jobIndex in range(len(fullJobDict["data"])):
        # sets up the format for each job in the summarized dictionary
        fullJobDictRef = fullJobDict["data"][jobIndex] # partial dictionary reference, will give the dictionary for each job during that job's interation of the loop
        jobSumTitle = f"{jobIndex + 1}. {fullJobDictRef["job_title"]}"
        sumJobDict[jobSumTitle] = {}

        # create summarized dictionary
        sumJobDict[jobSumTitle]["jobTitle"] = fullJobDictRef["job_title"]
        sumJobDict[jobSumTitle]["employer"] = fullJobDictRef["employer_name"]
        sumJobDict[jobSumTitle]["timeType"] = fullJobDictRef["job_employment_type"]
        sumJobDict[jobSumTitle]["applyOptions"] = fullJobDictRef["apply_options"]
        sumJobDict[jobSumTitle]["description"] = fullJobDictRef["job_description"]
        sumJobDict[jobSumTitle]["location"] = fullJobDictRef["job_location"]

        try:
            sumJobDict[jobSumTitle]["qualificationsList"] = fullJobDictRef["job_highlights"]["Qualifications"]
        except KeyError:
            sumJobDict[jobSumTitle]["qualificationsList"] = None

        try:
            sumJobDict[jobSumTitle]["responsibilitiesList"] = fullJobDictRef["job_highlights"]["Responsibilities"]
        except KeyError:
            sumJobDict[jobSumTitle]["responsibilitiesList"] = None

    with open("ExampleSummarizedOutput.json", "w") as file:
        json.dump(sumJobDict, file, indent=4)

    return sumJobDict
# Checks if the resume file exists

# job = json.load(open("oneJob.json", "r", encoding="utf-8"))
# Generates the Gemini response for the jobs
# Writes the response to a file
def generate_gemini_response(resume, job_dict): #job_dict
    resume_text = "\n".join(p.text for p in docx.Document(resume).paragraphs if p.text.strip())
    response = None
    for job in job_dict.keys():
        base_prompt = "Role: Career Coach;" # Check indentation when swapping between full Jsearch API call and one job for testing Gemini response
        prompt = (
            " Step 2: Identify gaps in the resume relative to this job title and description: "
            + job_dict[job]["jobTitle"] + "at" + job_dict[job]["employer"]
            # + job["jobTitle"] + " at " + job["employer"] + "\n" + job["description"]
            + """\nStep 3: Provide a list of 3 key skills to develop, 
                and a list of 3 concise resume changes to make (50 words or less).
                Step 4: Format output as follows:
                <job title>: job title at company name
                <resume gaps>: list of identified gaps
                <key skills to develop>: list of 3 key skills to develop
                <resume changes to make>: list of 3 concise resume changes to make (50 words or less)
                All labeled clearly with headers and use bulleted lists. Optimize for concise and readable output."""
        )

        full_prompt =base_prompt + "Step 1:Read this resume content:\n\n" + resume_text + "\n\n" + prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[full_prompt],
            config={"http_options": {"timeout": 60000}},
        )
        with open("gemini_response_test.txt", "a", encoding="utf-8") as file:
            file.write(response.text)
    print("Gemini response generated and saved to gemini_response.txt")
    return response.text if response is not None else ""

# job_dict = jobOutput(input("Enter a job title and location (e.g. 'Data Analyst (Intern) in Washington, DC'): ")) <- Full Jsearch API call
# job_dict = json.load(open("ExampleSummarizedOutput.json", "w", encoding="utf-8")) <- Example output from Jsearch API call (several jobs   )
# generate_gemini_response(doc, job_dict) <- Full Jsearch API call and Gemini response
 # One job for testing Gemini response
