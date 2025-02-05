import azure.functions as func
import logging
import os
import requests
from bs4 import BeautifulSoup

app = func.FunctionApp()

@app.route(route="SapiensiaCrawler", auth_level=func.AuthLevel.ANONYMOUS)
def SapiensiaCrawler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    base_url = "https://sapiensia.atlassian.net/wiki/spaces/SIA/overview?homepageId=578912377"
    requisition_response = requests.get(base_url)
    soup = BeautifulSoup(requisition_response.content, 'html.parser')

    sidebar = soup.find('div', {'class': 'cc-q334zl'}) 
    if sidebar:
        links = sidebar.find_all('a', href=True)
    
    if not os.path.exists('docs'):
        os.makedirs('docs')

    for link in links:
        page_url = link['href']
        if not page_url.startswith('http'):
            page_url = f"https://sapiensia.atlassian.net{page_url}"
        
        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')

        # Salvar o conteúdo da página em um arquivo HTML
        page_title = page_soup.title.string if page_soup.title else 'untitled'
        filename = f"docs/{page_title.replace('/', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(str(page_soup))

        logging.info(f"Salvo {page_url} em {filename}")



    return func.HttpResponse("Scraping concluído com sucesso!", status_code=200)