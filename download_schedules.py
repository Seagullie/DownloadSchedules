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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
schedules_listing_page_html = requests.get(
    Constants.SCHEDULE_LISTING_PAGE_URL, headers=headers
).text

# extract date of last update.

last_updated_text = extract_last_update_text(schedules_listing_page_html)
print("Last updated: " + last_updated_text)

# cut off irrelevant parts from the html.
# the relevant partg starts after element with text "022 Дизайн".
# the irrelevant part starts after element with text "ЗАОЧНА ФОРМА НАВЧАННЯ".


first_specialty_text_pos = schedules_listing_page_html.find(
    Constants.FIRST_SPECIALTY_TEXT
)
part_time_education_text_pos = schedules_listing_page_html.find(
    Constants.PART_TIME_EDUCATION_TEXT, first_specialty_text_pos
)

schedules_listing_page_html = schedules_listing_page_html[
    first_specialty_text_pos:part_time_education_text_pos
]


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

    schedule_pdf = requests.get(link_href)
    schedule_pdf_filename = link_text + ".pdf"

    with open(
        os.path.join(Constants.PATH_TO_OUTPUT_DIRECTORY, schedule_pdf_filename), "wb"
    ) as f:
        f.write(schedule_pdf.content)


print("Done downloading all schedules.")