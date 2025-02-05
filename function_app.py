import azure.functions as func
import logging
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

app = func.FunctionApp()

@app.route(route="SapiensiaCrawler", auth_level=func.AuthLevel.ANONYMOUS)
def SapiensiaCrawler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    main()
    return func.HttpResponse("Scraping concluído com sucesso via HTTP Trigger!", status_code=200)

@app.schedule(schedule="0 0 0 0 * *", arg_name="mytimer", run_on_startup=True)
def SapiensiaCrawlerTimer(mytimer: func.TimerRequest) -> None:
    logging.info('Python Timer trigger function executed.')
    main()
    logging.info('Scraping concluído com sucesso via Timer Trigger.')


def main(myTimer:func.TimerRequest):

    '''
    parte de configuração do selenium. nesse momento a linha--headless está 
    comentada pois é interessante acompanhar o processo do selenium pela interface.
    '''
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    base_url = "https://sapiensia.atlassian.net/wiki/spaces/SIA/overview?homepageId=578912377"
    driver.get(base_url)

    #aguarda a página carregar por completo
    time.sleep(5)

    '''Essa função é responsável por abrir todos os menus utilizando Js. Dessa forma, todos os links ficam disponíveis para
    serem acessados e salvos em html'''
    def expand_all_menus():
        while True:
            menus = driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="chevron-right"][aria-expanded="false"]')
            if not menus:
                break
            
            for menu in menus:
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", menu)
                    time.sleep(.5)
                    driver.execute_script("arguments[0].click();", menu)
                    time.sleep(1)
                except Exception as e:
                    logging.warning(f"Erro ao expandir menu: {e}")



    expand_all_menus()
    time.sleep(3)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    if not os.path.exists('docs'):
        os.makedirs('docs')

    '''nesse trecho estamos utilizando beautifulSoup, partindo do principio que todos os links
    <a></a> já estão abertos na div cc-q334zl. que no caso é a div que fica o conteudo do menu lateral
    '''
    time.sleep(15)  # Espera extra para garantir que todos os links tenham carregado

    links = driver.find_elements(By.CSS_SELECTOR, 'div.cc-q334zl a')

    if links:
        logging.info(f"Total de links capturados com Selenium: {len(links)}")
    else:
        logging.warning("Nenhum link encontrado.")



    def sanitize_filename(filename):
        return re.sub(r'[\/:*?"<>|]', '_', filename)  # Substitui caracteres inválidos

    #realiza uma iteração pela lista links[] e salva o arquivo HTMl de cada link da lista
    for link in links:
        try:
            page_url = link.get_attribute('href')
            if not page_url.startswith('http'):
                page_url = f"https://sapiensia.atlassian.net{page_url}"

            time.sleep(.5)

            page_response = requests.get(page_url, timeout=10)
            page_response.raise_for_status()

            page_soup = BeautifulSoup(page_response.content, 'html.parser')

            page_title = page_soup.title.string if page_soup.title else 'untitled'
            safe_filename = sanitize_filename(page_title)
            filename = f"docs/{safe_filename}.html"

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(str(page_soup))

            logging.info(f"Salvo {page_url} em {filename}")

        except Exception as e:
            logging.warning(f"Erro ao processar {page_url}: {e}")
            continue

