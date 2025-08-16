import json
import re
from bs4 import BeautifulSoup
import argparse
import html

def parse_grades_page(html_content):
    """
    Parses the HTML content of a Blackboard grades page to extract course
    and assessment information.

    Args:
        html_content (str): The HTML content of the page as a string.

    Returns:
        dict: A dictionary containing the course information and a list of
              assessments, ready to be serialized to JSON.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # --- 1. Extract Course Information ---
    course_info = {
        'course_code': None,
        'course_name': None,
        'course_id': None,
    }
    context_span = soup.find('span', class_='context')
    if context_span:
        context_text = context_span.get_text(strip=True)
        # Example: [ENGG3800] Team Project II (St Lucia). Semester 2, 2024 (ENGG3800_7460_60972)
        match = re.search(r'\[(.*?)\]\s*(.*?)\s*\((.*?)\)', context_text)
        if match:
            course_info['course_code'] = match.group(1).strip()
            course_info['course_name'] = match.group(2).strip()
            course_info['course_id'] = match.group(3).strip()

    # --- 2. Extract Assessment Information ---
    assessments = []
    # Each assessment item is in a div with this class
    assessment_rows = soup.select('#grades_wrapper > .sortable_item_row')

    for row in assessment_rows:
        assessment_data = {
            'name': None,
            'mark_achieved': None,
            'mark_possible': None,
            'feedback': None,
            'status': None,
        }

        # Extract Name from the first span or link in the 'gradable' cell
        name_cell = row.find('div', class_='gradable')
        if name_cell:
            name_tag = name_cell.find(['span', 'a'])
            if name_tag:
                assessment_data['name'] = name_tag.get_text(strip=True)

        # Extract Grade/Mark from the 'grade' cell
        grade_cell = row.find('div', class_='grade')
        if grade_cell:
            mark_span = grade_cell.find('span', class_='grade')
            if mark_span:
                mark_text = mark_span.get_text(strip=True)
                try:
                    assessment_data['mark_achieved'] = float(mark_text)
                except (ValueError, TypeError):
                    # Handle non-numeric grades like '-'
                    assessment_data['mark_achieved'] = None

            possible_span = grade_cell.find('span', class_='pointsPossible')
            if possible_span:
                possible_text = possible_span.get_text(strip=True).replace('/', '')
                try:
                    assessment_data['mark_possible'] = float(possible_text)
                except (ValueError, TypeError):
                    assessment_data['mark_possible'] = None

        # Extract Feedback from the 'onclick' attribute of the comment icon
        feedback_link = row.find('a', class_='grade-feedback')
        if feedback_link and 'onclick' in feedback_link.attrs:
            onclick_attr = feedback_link['onclick']
            # Regex to capture the second argument (the HTML content) of the JS function
            feedback_match = re.search(r"mygrades\.showInLightBox\s*\(\s*'.*?',\s*'(.*?)',\s*'.*?'\s*\);", onclick_attr)
            if feedback_match:
                # Use the html module to robustly unescape the string
                feedback_html = html.unescape(feedback_match.group(1))
                feedback_soup = BeautifulSoup(feedback_html, 'html.parser')
                assessment_data['feedback'] = feedback_soup.get_text(strip=True, separator=' ')

        # Extract Status from the alt text of the image in the 'gradeStatus' cell
        status_cell = row.find('div', class_='gradeStatus')
        if status_cell:
            status_img = status_cell.find('img')
            if status_img and 'alt' in status_img.attrs:
                assessment_data['status'] = status_img['alt']

        assessments.append(assessment_data)

    # --- 3. Combine and Return ---
    return {
        'course_info': course_info,
        'assessments': assessments
    }

if __name__ == '__main__':
    # Default file path if not provided via command line arguments
    # In a real application, you might get this from user input or configuration
    file_path = '/Users/felixpountney/Desktop/Hackathon/2025-uqcs-hackathon/gambler/Blackboard_example_grade.htm'
    
    

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        grade_data = parse_grades_page(html_content)
        print(json.dumps(grade_data, indent=2))

    except FileNotFoundError: # type: ignore
        print(f"Error: The file was not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
