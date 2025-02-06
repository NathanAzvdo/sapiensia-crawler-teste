import re
import os
import json
from bs4 import BeautifulSoup
from atlassian import Confluence
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

base_url = "https://sapiensia.atlassian.net/wiki"
space_key = "SIA"
connection_string = os.environ["AzureWebJobsStorage"]
container_name = "sapiensia-help-desk"

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

# def save_json(content, path):
#     with open(path, "w", encoding="utf-8") as file:
#         json.dump(content, file, ensure_ascii=False, indent=4)
#     print(f"Saved: {path}")

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

    root_path = os.path.join(".", "documents")
    os.makedirs(root_path, exist_ok=True)
    
    processed_pages = set()
    for root_page in root_pages:
        save_page_and_children(root_page, root_path, processed_pages)

def fetch_and_save_pages_since(date):
    cql = f'space="{space_key}" and type=page and lastmodified >= "{date}"'
    pages = confluence.cql(cql, limit=1000)["results"]
    
    if not pages:
        print(f"Nenhuma página modificada desde {date}.")
        return
    
    root_path = os.path.join(".", "documents")
    os.makedirs(root_path, exist_ok=True)
    
    processed_pages = set()
    for page in pages:
        page_id = page["content"]["id"]
        ancestors = confluence.get_page_ancestors(page_id)
        if ancestors:
            parent_path = root_path
            for ancestor in ancestors:
                ancestor_title = re.sub(r'[\\/*?:"<>|]', "", ancestor["title"])
                parent_path = os.path.join(parent_path, ancestor_title)
                os.makedirs(parent_path, exist_ok=True)
            save_page_and_children(page["content"], parent_path, processed_pages)
        else:
            save_page_and_children(page["content"], root_path, processed_pages)

def save_json(content, blob_name):
    base_path = "/home/nathan-azevedo/Documentos/sapiensia-crawler-teste"
    relative_blob_name = os.path.relpath(blob_name, base_path)
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    blob_client = container_client.get_blob_client(relative_blob_name)
    blob_client.upload_blob(json.dumps(content, ensure_ascii=False, indent=4), overwrite=True)
    print(f"Saved to storage account: {relative_blob_name}")
