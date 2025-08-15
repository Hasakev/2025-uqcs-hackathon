from flask import Blueprint, jsonify, request
from datetime import datetime
import app.src.grade_extractor as ge

api = Blueprint('api', __name__)

@api.route('/health')
def health():
    health = 200 ## Health should always be 200 for now, scalability not a concern
    if health == 200: # Service is healthy
        return jsonify(
            {
                "healthy": True
            }
            ), 200

@api.route('/courses/<string:course_code>/assessments', methods=['GET'])
def get_assessments(course_code: str, semester: ge.Semester=ge.Semester.SEM1, year: int=2025):
    """
    Get assessments for a course
    """
    extractor = ge.CourseExtractor(courses=[course_code])
    try:
        site = extractor.get_page(course_code, semester, year)
        table = extractor.get_table(site)
        return jsonify(table), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@api.route('/test/<string:url>', methods=['GET'])
def get_website_content(url: str) -> str:
    """
    Get the HTML content of a website.
    """
    base = f"https://learn.uq.edu.au/ultra/courses/{url}/grades"
    extractor = ge.CourseExtractor(courses=[])
    return extractor.open_website(base)
