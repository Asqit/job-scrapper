# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
#   Job Scraper
#   A simple script that scrapes job listings from a website (jobs.cz)
#   and saves the results in a CSV file.
#
#   The script can be used in two modes:
#   - scrape: scrapes the data from the provided URL
#   - search: searches the provided CSV file for the keywords
#
#   Author: Ondřej Tuček  (github.com/asqit)
#   Date: 25.5.2024
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import requests
import argparse
import time
import csv
import os


def print_error(error: str) -> None:
    """
    A Utility function used to print error messages in red color
    """
    print(f"\033[38;2;255;0;0m{error}\033[38;2;255;255;255m")


def get_base_url(url: str) -> str:
    """
    A function that takes a URL and extracts the base URL
    """
    url_parts = urlsplit(url)

    return url_parts.scheme + "://" + url_parts.netloc


def save_as_csv(results: list, file_name: str) -> None:
    """
    A Utility function used to save the results as a CSV file
    """

    try:
        with open(file_name, "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Link"])
            writer.writerows(row for row in results if any(row) or len(row) > 0)
    except Exception as e:
        print(f"Failed to save data as CSV, trying as TXT")
        fail_path = os.path.join(os.getcwd(), "failed.txt")

        try:
            with open(fail_path, "w") as f:
                f.writelines(results)
        except Exception as e:
            print(f"Failed to save results as txt file {e}")
        else:
            print(f"Results were saved in: {fail_path}")
    else:
        print(f"Results were saved in: {file_name}")


def get_soup(url: str) -> BeautifulSoup:
    """
    A function, that takes a URL and converts it's HTML to soup.
    Raises exception if HTTP code is not 200
    """
    page = requests.get(url)

    if page.status_code != 200:
        raise Exception(f"HTTP_CODE: {page.status_code}\n{url}")

    soup = BeautifulSoup(page.content, "html.parser")

    return soup


def get_data_from_soup(soup: BeautifulSoup, link_class: str | None) -> list:
    """
    A function that takes a soup and retrieves a required data
    """
    results = []

    titles = soup.find_all(
        "a", class_=link_class or "link-primary SearchResultCard__titleLink"
    )

    if titles is None or len(titles) == 0:
        return results

    for title in titles:
        title_text = title.text.strip()
        title_link = title["href"]

        if title_text and title_link:
            results.append((title_text, title_link))

    return results


def get_pagination(soup: BeautifulSoup, pagination_class: str | None) -> list | None:
    """
    A function that takes a soup and finds all links to next pages
    """

    pagination = soup.find_all("li", class_=pagination_class or "Pagination__item")

    if pagination is None or len(pagination) == 0:
        return None

    results = []

    for p in pagination:
        link = p.find("a")
        href = link["href"]

        if href not in results:
            results.append(href)

    return results


def collect_data(
    source_url: str, links: list | None, class_names: tuple[str, str]
) -> list:
    if links is None or len(links) == 0:
        return []

    results = []

    for link in links:
        url = f"{source_url}{link}"

        print(f"Collecting data from: {url}")

        soup = get_soup(url)
        data = get_data_from_soup(soup, class_names[0])

        last_link = links[-1]
        if link == last_link:
            pagination = get_pagination(soup, class_names[1])

            if pagination is not None:
                links.extend([p for p in pagination if p not in links])

        results.extend(data)

    return results


def search_by_keywords(filename: str, keywords: list[str]) -> list[list[str]]:
    results = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 0:
                    continue

                for keyword in keywords:
                    if keyword.lower() in row[0].lower():
                        results.append(row)
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        exit(1)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    modes = ["search", "scrape"]
    parser.add_argument("--mode", help="Mode of operation", choices=modes)
    parser.add_argument("--url", help="Base URL to scrape data from", type=str)
    parser.add_argument("--keywords", help="Keywords to search for", nargs="*")

    parser.add_argument(
        "--title-class", help="The css class for title/link in the page", type=str
    )

    parser.add_argument(
        "--pagination-class", help="The css class for pagination in the page", type=str
    )

    args = parser.parse_args()

    if args.mode == "scrape":
        start_timestamp = time.perf_counter()

        print("Fetching HTML from the URL")
        init_soup = get_soup(args.url)
        pagination = get_pagination(init_soup, args.pagination_class)

        if pagination is None:
            data = get_data_from_soup(init_soup, args.title_class)
        else:
            data = collect_data(
                get_base_url(args.url),
                [link for link in pagination if link != args.url],
                (args.title_class, args.pagination_class),
            )

        print(f"Collected {len(data)} results")
        filename = input("(optional) Provide a filename to save the results:")

        if filename is None or len(filename) == 0:
            filename = f"{args.url.split('/')[-1]}_{time.time()}_results.csv"

        save_as_csv(data, filename.split(".")[0] + ".csv")

        end_delta = time.perf_counter() - start_timestamp
        print(f"Operation took: {end_delta:.2f} seconds")

    elif args.mode == "search":
        start_timestamp = time.perf_counter()

        results = search_by_keywords(args.url, args.keywords)

        print(f"Found {len(results)} results")
        filename = input("(optional) Provide a filename to save the results:")

        if filename is None or len(filename) == 0:
            filename = f"{args.url}_{time.time()}_search_results.csv"

        save_as_csv(results, filename.split(".")[0] + ".csv")

        end_delta = time.perf_counter() - start_timestamp
        print(f"Operation took: {end_delta:.2f} seconds")
    else:
        print_error("Invalid usage of the script. Please provide correct arguments.")
        print("see: python main.py --help")
        exit(1)
