import azure.functions as func
import logging
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = func.FunctionApp()

@app.route(route="SapiensiaCrawler", auth_level=func.AuthLevel.ANONYMOUS)
def SapiensiaCrawler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Configuração do Selenium para usar Chrome em modo headless
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    base_url = "https://sapiensia.atlassian.net/wiki/spaces/SIA/overview?homepageId=578912377"
    driver.get(base_url)

    # Espera a página carregar
    time.sleep(5)

    # Expande todos os menus e submenus
    def expand_all_menus():
        menus = driver.find_elements(By.CSS_SELECTOR, '.cc-9693te')
        for menu in menus:
            try:
                menu.click()
                time.sleep(1)  # Espera o menu expandir
            except Exception as e:
                logging.warning(f"Erro ao expandir menu: {e}")

    expand_all_menus()

    # Coleta o HTML da página após expandir os menus
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

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

    driver.quit()

    return func.HttpResponse("Scraping concluído com sucesso!", status_code=200)