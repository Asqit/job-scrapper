# root of the website: https://www.google.com/
BASE_URL = ""

# root + additional params: https://www.google.com/search?hl=en&q=ee
FULL_URL = ""

from bs4 import BeautifulSoup
import requests
import time
import csv
import os


def get_soup(url: str) -> BeautifulSoup:
    """A function, that takes a URL and converts it's HTML to soup.
    Raises exception if HTTP code is not 200
    """
    page = requests.get(url)

    if page.status_code != 200:
        raise Exception(f"HTTP_CODE: {page.status_code}\n{url}")

    soup = BeautifulSoup(page.content, "html.parser")

    return soup


def get_data_from_soup(soup: BeautifulSoup) -> list:
    """A function that takes a soup and retrieves a required data"""
    results = []
    titles = soup.find_all("a", class_="link-primary SearchResultCard__titleLink")

    if titles is None or len(titles) == 0:
        return results

    for title in titles:
        title_text = title.text
        title_link = title["href"]

        if title_text and title_link:
            results.append([title_text.strip(), title_link])

    return results


def get_paging(soup: BeautifulSoup) -> list | None:
    """A function that takes a soup and finds all links to next pages"""
    pagination = soup.find_all("li", class_="Pagination__item")

    if pagination is None or len(pagination) == 0:
        return None

    results = []

    for p in pagination:
        link = p.find("a")
        href = link["href"]

        if href not in results:
            results.append(href)

    return results


def collect_data(links: list | None) -> list:
    """A function that takes list of links as parameter and for each link it searches for data"""
    if links is None or len(links) == 0:
        return []

    result = []
    for link in links:
        link_url = BASE_URL + link

        print(f"Fetching HTML from {link_url}\n")

        soup = get_soup(link_url)
        data = get_data_from_soup(soup)

        # check for continuos pagination
        last_link = links[-1]
        if link == last_link:
            new_links = get_paging(soup)
            links.extend([link for link in new_links if link not in links])

        result.append(data)

    return data


def save_as_csv(results: list) -> None:
    """function that tries to save results to file"""
    file_name = os.path.join(os.getcwd(), "jobs-" + str(time.time()) + ".csv")
    csv_titles = ["TITLE", "LINK"]

    try:
        with open(file_name, "w", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(csv_titles)
            writer.writerows(results)

    except Exception as e:
        print(f"Failed to save data as CSV, trying as TXT")
        fail_path = os.path.join(os.getcwd(), "failed.txt")

        try:
            with open(fail_path, "w") as f:
                f.writelines(results)
        except Exception as e:
            print("Even failed to save results as txt file...sorry")
        else:
            print(f"Results were saved in: {fail_path}")
    else:
        print(f"Results were saved in: {file_name}")


def init() -> None:
    try:
        start_delta = time.perf_counter()

        print(f"Gathering data from {BASE_URL}")
        print(
            "I advice you go and make yourself some beverage, since I am retard and concurrency is hard\n"
        )
        initial_soup = get_soup(FULL_URL)
        initial_data = get_data_from_soup(initial_soup)
        links = get_paging(initial_soup)

        if links is None:
            data = initial_data
        else:
            data = collect_data([link for link in links if link != FULL_URL])
            data.extend(initial_data)

        save_as_csv(data)

        end_delta = time.perf_counter()
        print("Finished")
        print(f"Final time: {end_delta - start_delta}s")
    except Exception as e:
        print(
            f"\033[38;2;255;0;0mUnexpected error occurred:\n{e}\033[38;2;255;255;255m"
        )


if __name__ == "__main__":
    init()
else:
    print("This file is suppose to be run as a script")
