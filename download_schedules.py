# This script is designed to download schedule PDFs from the academy's website and save them to a local directory.
# It specifically focuses on downloading schedules for the full-time form of education.

import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Tuple, List

from constants import Constants
from utils import extract_last_update_text

# get html of academy's schedules listing page

# the page blocks requests that don't have a user agent header.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
schedules_listing_page_html = requests.get(
    Constants.SCHEDULE_LISTING_PAGE_URL, headers=headers
).text

# save the html to a file for debugging purposes.
with open("output/schedules_listing_page.html", "w", encoding="utf-8") as f:
    f.write(schedules_listing_page_html)

# extract date of last update.

last_updated_text = extract_last_update_text(schedules_listing_page_html)
print("Last updated: " + last_updated_text)

# cut off irrelevant parts from the html.
# the relevant partg starts after element with text "022 Дизайн".
# the irrelevant part starts after element with text "ДОКТОР ФІЛОСОФІЇ або ЗАОЧНА ФОРМА НАВЧАННЯ".


start_pos = full_time_education_text_pos = schedules_listing_page_html.find(
    Constants.FULL_TIME_EDUCATION_TEXT
)

end_text_pos = doctor_of_philosophy_text_pos = schedules_listing_page_html.find(
    Constants.DOCTOR_OF_PHILOSOPHY_TEXT, full_time_education_text_pos)

if end_text_pos == -1:    
    end_text_pos = part_time_education_text_pos = schedules_listing_page_html.find(
    Constants.PART_TIME_EDUCATION_TEXT, 
    full_time_education_text_pos
)

schedules_listing_page_html = schedules_listing_page_html[
    start_pos:end_text_pos
]

# save the html to a file for debugging purposes.
with open("output/schedules_listing_page_narrowed_down.html", "w", encoding="utf-8") as f:
    f.write(schedules_listing_page_html)


# extract all links to schedule PDFs from the html.
# each link starts with "https://drive.google.com/file/d/"

soup = BeautifulSoup(schedules_listing_page_html, "html.parser")
links = soup.find_all("a")
schedule_links: List[Tuple[str, str]] = []
for link in links:
    href: str = link.get("href")
    link_text: str = link.text
    if href is not None and href.startswith("https://drive.google.com/file/d/"):
        schedule_links.append((href, link_text))

# filter out irrelevant links at the top of listing.

schedule_links = list(
    filter(lambda link: not link[1].startswith("Про"), schedule_links)
)

# for each link, transform it to google drive download link.

schedule_download_links: List[Tuple[str, str]] = []
for link in schedule_links:

    link_href = link[0]
    link_text = link[1]

    file_id = link_href[link_href.find("d/") + 2 : link_href.rfind("/")]

    schedule_download_link = Constants.GOOGLE_DRIVE_FILE_DOWNLOAD_LINK_TEMPLATE.format(
        file_id
    )
    schedule_download_links.append((schedule_download_link, link_text))

# download each schedule PDF and save it to a local directory.

for link in tqdm(
    schedule_download_links, desc="Downloading files", unit="file"
):
    link_href = link[0]
    link_text = link[1]

    schedule_pdf = requests.get(link_href, headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }, allow_redirects=True)
    schedule_pdf_filename = link_text + ".pdf"

    with open(
        os.path.join(Constants.PATH_TO_OUTPUT_DIRECTORY, schedule_pdf_filename), "wb"
    ) as f:
        f.write(schedule_pdf.content)


print("Done downloading all schedules.")