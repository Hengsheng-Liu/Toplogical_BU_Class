import json
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin

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
        for a in course.find_all('a'):
            if a.get('href') != "http://www.bu.edu/hub/what-is-the-hub/":
                link = urljoin(url, a.get('href')).strip()
                course_data = {
                    'name': name,
                    'prerequisites': pre_req,
                    'link': link,
                    'description': description
                }
                convert_to_json.append(course_data)
with open("output.json", "w") as outfile:
    json.dump(convert_to_json, outfile)