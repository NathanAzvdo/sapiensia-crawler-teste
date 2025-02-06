import requests
import re
import os
import json
from bs4 import BeautifulSoup

base_url = "https://sapiensia.atlassian.net/wiki/rest/api"
space_key = "SIA"

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for script in soup(["script", "style", "noscript", "meta", "link", "head"]):
        script.decompose()

    for tag in soup():
        for attribute in ["class", "id", "style", "onclick", "onload", "onerror"]:
            del tag[attribute]

    for tag in soup():
        if not tag.contents:
            tag.decompose()

    return soup.prettify()

def html_to_dict(element):
    if not element.name:
        return element.string
    
    result = {element.name: [] if element.find_all() else element.text}
    for child in element.find_all(recursive=False):
        result[element.name].append(html_to_dict(child))
    return result

def save_json(content, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=4)
    print(f"Saved: {path}")


def save_page_and_children(page, parent_path, processed_pages):
    page_id = page["id"]
    if page_id in processed_pages:
        return
    processed_pages.add(page_id)

    title = re.sub(r'[\\/*?:"<>|]', "", page["title"])
    content_url = f"{base_url}/content/{page_id}?expand=body.view"
    response = requests.get(content_url)
    response.raise_for_status()

    content = clean_html(response.json()["body"]["view"]["value"])
    content_dict = html_to_dict(BeautifulSoup(content, 'html.parser'))

    child_pages = get_child_pages(page_id)

    if child_pages:
        page_path = os.path.join(parent_path, title)
        os.makedirs(page_path, exist_ok=True)
        save_json(content_dict, os.path.join(page_path, f"{title}.json"))
    else:
        save_json(content_dict, os.path.join(parent_path, f"{title}.json"))
        page_path = parent_path

    for child_page in child_pages:
        save_page_and_children(child_page, page_path, processed_pages)
    

def get_child_pages(page_id):
    url = f"{base_url}/content/{page_id}/child/page"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["results"]

def fetch_and_save_pages():
    url = f"{base_url}/content?spaceKey={space_key}&expand=body.view"
    response = requests.get(url)
    response.raise_for_status()
    root_pages = [page for page in response.json()["results"] if page["title"] == "Sapiensia Help Desk"]
    
    root_path = os.path.join(os.getcwd(), "documents")
    os.makedirs(root_path, exist_ok=True)
    
    processed_pages = set()
    for root_page in root_pages:
        save_page_and_children(root_page, root_path, processed_pages)
