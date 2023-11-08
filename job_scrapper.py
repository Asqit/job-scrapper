URL = ""

from bs4 import BeautifulSoup
import requests
import time
import csv
import os


def get_soup(url: str) -> BeautifulSoup:
    page = requests.get(url)

    if page.status_code != 200:
        raise Exception(f"HTTP_CODE: {page.status_code}\n{url}")

    soup = BeautifulSoup(page.content, "html.parser")

    return soup


def get_titles_from_page(soup: BeautifulSoup) -> list:
    titles = soup.find_all("a", class_="link-primary SearchResultCard__titleLink")
    results = []

    for title in titles:
        title_text = title.text.strip()
        link = title["href"]

        results.append([title_text, link])

    return results


def get_pages(soup: BeautifulSoup) -> list | None:
    pagination = soup.find_all("li", class_="Pagination__item")
    pages = []

    for p in pagination:
        a = p.find("a")
        href = a["href"]
        if href not in pages:
            pages.append(href)

    if len(pages) == 0:
        return None

    return pages


def collect_titles(links: list | None) -> list:
    BASE_URL = ""
    result = []

    iters = links

    for link in iters:
        url = BASE_URL + link
        print(url)
        soup = get_soup(url)
        titles = get_titles_from_page(soup)

        last_link = links[-1]
        if link == last_link:
            new_links = get_pages(soup)
            iters.extend([link for link in new_links if link not in iters])

        result.extend(titles)

    return result


def init() -> None:
    try:
        start_delta = time.perf_counter()
        print(f"Gathering data from {URL}")
        soup = get_soup(URL)
        pages = get_pages(soup)
        titles = collect_titles(pages)
        output_location = os.path.join(os.getcwd(), "jobs-" + str(time.time()) + ".csv")

        fields = ["Title", "Link"]

        with open(output_location, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(fields, delimiter=",")
            writer.writerows(titles, delimiter=",")

        end_delta = time.perf_counter()
        print(f"Final time: {end_delta - start_delta}")
        print(f"Data saved at: {output_location}")

    except Exception as e:
        print(
            f"\033[38;2;255;0;0mUnexpected error occurred:\n{e}\033[38;2;255;255;255m"
        )


if __name__ == "__main__":
    init()
