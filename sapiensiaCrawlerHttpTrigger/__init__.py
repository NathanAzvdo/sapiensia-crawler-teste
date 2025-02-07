import azure.functions as func
import logging
from fetch_and_save import *
import datetime
from time import time

def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> None:
    start = time()
    logging.info('Python HTTP trigger started.')

    try:
        date = req.params.get('date')
        if date:
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
            except:
                res.set(func.HttpResponse("Data inválida. Formato esperado: 'YYYY-MM-DD'.", status_code=400))
                return
        else:
            fetch_and_save_pages()
            end = time()
            res.set(func.HttpResponse(f"Requisição completa feita com sucesso via HTTP Trigger! Tempo de execução: {end - start} segundos.", status_code=200))  
        
        if date:
            fetch_and_save_pages_since(date)
            end = time()
            res.set(func.HttpResponse(f"Requisição completa feita com sucesso via HTTP Trigger! Tempo de execução: {end - start} segundos.", status_code=200))
    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        res.set(func.HttpResponse(f"Erro: {str(e)}", status_code=500))