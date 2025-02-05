import azure.functions as func
import logging
from fetch_and_save import fetch_and_save_pages  # Importe a função que você deseja executar

def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> None:
    logging.info('Python HTTP trigger started.')

    try:
        fetch_and_save_pages()
        res.set(func.HttpResponse("Requisição feita com sucesso via HTTP Trigger!", status_code=200))
    except Exception as e:
        logging.error(f"Erro durante o scraping: {str(e)}")
        res.set(func.HttpResponse(f"Erro: {str(e)}", status_code=500))