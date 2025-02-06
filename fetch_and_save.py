import re
import os
import json
from bs4 import BeautifulSoup
from atlassian import Confluence

base_url = "https://sapiensia.atlassian.net/wiki"
space_key = "SIA"

confluence = Confluence(
    url=base_url,
)

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
    content = confluence.get_page_by_id(page_id, expand='body.view')['body']['view']['value']
    content = clean_html(content)
    content_dict = html_to_dict(BeautifulSoup(content, 'html.parser'))

    child_pages = get_child_pages(page_id)
    child_pages = [child_page for child_page in child_pages if child_page["title"] != "Sapiensia Help Desk"]
    print(page["title"], child_pages)
    # Se a página tiver filhos, cria uma pasta para ela
    if child_pages:
        page_path = os.path.join(parent_path, title)
        os.makedirs(page_path, exist_ok=True)
        save_json(content_dict, os.path.join(page_path, f"{title}.json"))
    else:
        # Se não tiver filhos, salva no diretório do pai (sem criar uma pasta nova)
        save_json(content_dict, os.path.join(parent_path, f"{title}.json"))
        page_path = parent_path

    for child_page in child_pages:
        save_page_and_children(child_page, page_path, processed_pages)

def get_child_pages(page_id):
    return confluence.get_child_pages(page_id)

def fetch_and_save_pages():
    # Obtendo apenas a página raiz "Sapiensia Help Desk"
    root_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=1000)
    root_pages = [page for page in root_pages if page["title"] == "Sapiensia Help Desk"]
    
    if not root_pages:
        print("Página raiz 'Sapiensia Help Desk' não encontrada.")
        return

    root_path = os.path.join(os.getcwd(), "documents")
    os.makedirs(root_path, exist_ok=True)
    
    processed_pages = set()
    for root_page in root_pages:
        save_page_and_children(root_page, root_path, processed_pages)
