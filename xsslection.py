import sys
import concurrent.futures
import urllib3
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
import time
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def replace_parameter(url, parameter, placeholder):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if parameter in query_params:
        query_params[parameter] = [placeholder]

    updated_query = urlencode(query_params, doseq=True)
    updated_url = urlunparse(parsed_url._replace(query=updated_query))

    return updated_url

def test_reflection(url, parameter, placeholder, verbose=False, reflected_urls=None):
    try:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "close",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Referer": "https://www.site.com/teams/",
            "Accept-Language": "en-US,en;q=0.8"
        }

        start_time = time.time()
        response = requests.head(url, headers=headers, verify=False, timeout=5)
        end_time = time.time()

        if verbose:
            print(f"Debug: URL: {url} Elapsed Time: {end_time - start_time} seconds")

        content_type = response.headers.get("content-type", "")
        if content_type.startswith("image/") or url.lower().endswith(('.js', '.css')):
            if verbose:
                print(f"Debug: Skipping URL: {url}")
            return
        elif ".jpeg" in url.lower() or ".jpg" in url.lower() or ".png" in url.lower():
            if verbose:
                print(f"Debug: Skipping image URL: {url}")
            return
        else:
            if verbose:
                print(f"Debug: Testing URL: {url}")
            full_response = requests.get(url, headers=headers, verify=False, timeout=60)
            content = full_response.content

            try:
                json_content = json.loads(content)
                if placeholder in json.dumps(json_content):
                    print(f"Possible false positive [JSON response]: {url}")
            except json.JSONDecodeError:
                if placeholder.encode() in content:
                    print(f"Reflection found in parameter '{parameter}': {url}")
                    if reflected_urls is not None:
                        reflected_urls.append(url)
    except (requests.exceptions.RequestException, requests.exceptions.Timeout, UnicodeDecodeError):
        pass

def process_url(url, parameter, placeholder, verbose=False, reflected_urls=None):
    replaced_url = replace_parameter(url, parameter, placeholder)
    test_reflection(replaced_url, parameter, placeholder, verbose, reflected_urls)

def process_urls(urls, placeholder, verbose=False):
    reflected_urls = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for url in urls:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            for parameter in query_params.keys():
                future = executor.submit(process_url, url, parameter, placeholder, verbose, reflected_urls)
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()

    return reflected_urls

def main(verbose=False):
    urls = []
    placeholder = '"><xssleaction>'
    try:
        for line in sys.stdin:
            url = line.strip()
            urls.append(url)

        reflected_urls = process_urls(urls, placeholder, verbose)

        if reflected_urls:
            with open("reflected.txt", "a") as file:
                file.write("\n".join(reflected_urls) + "\n")
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    verbose_mode = "-v" in sys.argv[1:]
    main(verbose=verbose_mode)
