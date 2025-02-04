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
    

    return func.HttpResponse(str(soup), mimetype="text/html")