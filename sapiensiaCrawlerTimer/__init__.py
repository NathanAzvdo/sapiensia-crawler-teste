import azure.functions as func
import logging
import os
import requests
from fetch_and_save import fetch_and_save_pages


app = func.FunctionApp()

# @app.route(route="SapiensiaCrawler", auth_level=func.AuthLevel.ANONYMOUS)
# def SapiensiaCrawler(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')
#     main()
#     return func.HttpResponse("Scraping concluído com sucesso via HTTP Trigger!", status_code=200)

def main(myTimer:func.TimerRequest):
    fetch_and_save_pages()

