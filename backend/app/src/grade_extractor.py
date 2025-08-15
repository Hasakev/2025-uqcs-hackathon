import requests
import json
from bs4 import BeautifulSoup
import os
import time
import pandas as pd
from pathlib import Path
import enum

# Semester Enumerate
class Semester(enum.Enum):
    SEM1 = 'Semester 1'
    SEM2 = 'Semester 2'
    SUMMER = 'Summer Semester'

class CourseExtractor():
    
    def __init__(self, courses: list[str]):
        self.courses = courses

    @staticmethod
    def get_course_url(course_code: str) -> str:
        return f'https://my.uq.edu.au/programs-courses/course.html?course_code={course_code}'
    
    @staticmethod
    def get_page(code: str, semester: Semester, year: int):
        url = CourseExtractor.get_course_url(code)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        header = requests.utils.default_headers()
        header.update(
            {
                "User-Agent": "My User Agent 1.0",
            }
        )
        page = requests.get(url, headers=header)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        if soup.find(id="course-notfound") is not None:
            raise ValueError(f"Course {code} not found for {semester.value} {year}.")
        box = soup.find_all('tr')

        for item in box:
            text = item.text.strip()
            if (str(year) in text and semester.value in text
            and 'unavailable' not in text):
                h = item.find_all('a', class_="profile-available")
                href = h[0]["href"]
                #report the last part of the href
                return href
        raise ValueError(f"Course {code} not found for {semester.value} {year}.")

    def get_table(self, site: str):
        headers = requests.utils.default_headers()
        headers.update(
            {
                'User-Agent': 'My User Agent 1.0',
            }
        )
        assessment = f"{site}#assessment"
        page = requests.get(assessment, headers=headers)
        html_content = page.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove <ul class="icon-list"> elements
        for ul in soup.find_all('ul', class_='icon-list'):
            ul.decompose()
        
        # Extract table headings + rows for pandas df
        table = soup.find('table')
        if table is None:
            raise ValueError(f"No table found on assessment page for {site}.")
        headers = [header.text.strip() for header in table.find_all('th')]
        rows = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            rows.append([col.text.strip() for col in cols])
            
        df = pd.DataFrame(rows, columns=headers)
        df = df.drop(columns=["Category", "Due date"])

        # Edge case where weight = 0% and UQ left the weight 'blank'
        df = df.dropna()
        df['Weight'] = df['Weight'].astype(str)
        
        # Edge Case: Identify rows where Weighting does not contain "%" (e.g. DECO2200, DECO7200)
        non_percentage_rows = df.loc[~df['Weight'].str.contains("%"), 'Weight']
        
        # If all entries are numeric and equal, convert them to percentages
        if len(non_percentage_rows) > 0 and non_percentage_rows.apply(lambda x: x.isdigit()).all():
            total_tasks = len(non_percentage_rows)
            percentage = 100 / total_tasks
            df.loc[~df['Weight'].str.contains("%"), 'Weight'] = f"{percentage:.2f}%"

        # Convert weightings
        df.loc[df['Weight'].str.contains("%"), ['Weight']] = df['Weight'].str.partition('%')[0]
        return df.to_dict(orient='records')
        


if __name__ == "__main__":
    extractor = CourseExtractor(courses=["CSSE1001"])
    a = extractor.get_page("ELEC4620", Semester.SEM2, 2025)
    table = extractor.get_table(a)
    print(table)