import azure.functions as func
import logging
import os
import requests
from fetch_and_save import fetch_and_save_pages_since
import datetime

app = func.FunctionApp()

def main(myTimer:func.TimerRequest):
    logging.info('Python Timer trigger function executada.')

    try:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        fetch_and_save_pages_since(yesterday.strftime("%Y-%m-%d"))
        logging.info(" concluído com sucesso via Timer Trigger!")
    except Exception as e:
        logging.error(f"Erro: {str(e)}")

