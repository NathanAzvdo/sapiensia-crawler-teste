import requests
import re
import os

# Configurações
base_url = "https://sapiensia.atlassian.net/wiki/rest/api"
space_key = "SIA"

# Função para obter páginas filhas
def get_child_pages(page_id):
    url = f"{base_url}/content/{page_id}/child/page"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["results"]

# Função para salvar conteúdo HTML em arquivo
def save_html(content, path):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

# Função para criar estrutura de pastas e salvar páginas
def save_page_and_children(page, parent_path, processed_pages):
    page_id = page["id"]
    if page_id in processed_pages:
        return
    processed_pages.add(page_id)

    title = re.sub(r'[\\/*?:"<>|]', "", page["title"])
    content_url = f"{base_url}/content/{page_id}?expand=body.view"
    response = requests.get(content_url)
    response.raise_for_status()
    content = response.json()["body"]["view"]["value"]

    # Obter páginas filhas
    child_pages = get_child_pages(page_id)

    # Criar diretório para a página apenas se tiver páginas filhas
    if child_pages:
        page_path = os.path.join(parent_path, title)
        os.makedirs(page_path, exist_ok=True)
        save_html(content, os.path.join(page_path, f"{title}.html"))
    else:
        save_html(content, os.path.join(parent_path, f"{title}.html"))
        page_path = parent_path

    # Salvar páginas filhas
    for child_page in child_pages:
        save_page_and_children(child_page, page_path, processed_pages)

# Função principal
def fetch_and_save_pages():
    # Obter a página raiz do espaço
    url = f"{base_url}/content?spaceKey={space_key}&expand=body.view"
    response = requests.get(url)
    response.raise_for_status()
    root_pages = [page for page in response.json()["results"] if page["title"] == "Sapiensia Help Desk"]

    # Criar diretório raiz para o espaço
    root_path = os.path.join(os.getcwd(), "documents")
    os.makedirs(root_path, exist_ok=True)

    # Salvar páginas raiz e suas páginas filhas
    processed_pages = set()
    for root_page in root_pages:
        save_page_and_children(root_page, root_path, processed_pages)
