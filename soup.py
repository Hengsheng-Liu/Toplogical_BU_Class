import json
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import re
url = "https://www.bu.edu/academics/cas/courses/computer-science/"
response = requests.get(url)

soup = BeautifulSoup(response.text, "lxml")
course_feed = soup.find('ul', class_="course-feed")
pagination  = soup.find('div', class_="pagination").find_all('a')
page_links = [a.get('href') for a in pagination]
page_links.insert(0, url)
convert_to_json = []
# Open the file in append mode
for link in page_links:
    response = requests.get(urljoin(url, link))
    soup = BeautifulSoup(response.text, "lxml")
    course_feed = soup.find('ul', class_="course-feed")
    for course in course_feed.find_all('li'):
        strong_tag = course.find('strong')
        name = strong_tag.text.strip() if strong_tag else None
        span = course.find('span')
        pre_req = span.text.strip() if span and "Undergraduate Prerequisites" in span.text else None
        description_parts = [content for content in course.contents if isinstance(content, NavigableString) and content.strip()]
        description = " ".join(part.strip() for part in description_parts).replace("\n", "")
        parsed_pre_req = re.split(r'[.!?;]', pre_req) if pre_req else None
        parsed_pre_req = [s.strip() for s in parsed_pre_req if s.strip()] if parsed_pre_req else None
        recommended = [s for s in parsed_pre_req if "recommended" in s] if parsed_pre_req else None
        print(recommended)
        for a in course.find_all('a'):
            if a.get('href') != "http://www.bu.edu/hub/what-is-the-hub/":
                link = urljoin(url, a.get('href')).strip()
                course_data = {
                    'name': name,
                    'prerequisites': parsed_pre_req,
                    'link': link,
                    'description': description,
                    'consent': True if parsed_pre_req and any(('consent of instructor' in s) or ('approved by the instructor' in s) for s in parsed_pre_req) else False,
                    'recommended': recommended if recommended else None
                }
                convert_to_json.append(course_data)
with open("output.json", "w") as outfile:
    json.dump(convert_to_json, outfile)