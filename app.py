from quart import Quart, send_file, abort, Response
from werkzeug.middleware.proxy_fix import ProxyFix
import asyncio
import os
import re
from datetime import datetime
from pyppeteer import launch

app = Quart(__name__)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

async def download_pdf_content(url, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            browser = await launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = await browser.newPage()
            await page.goto(url, {'waitUntil': 'networkidle2'})

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            pdf_file_name = sanitize_filename(f"BOLETO_{timestamp}.pdf")
            temp_dir = "/tmp"
            pdf_file_path = os.path.join(temp_dir, pdf_file_name)

            await page.pdf({'path': pdf_file_path, 'format': 'A4'})
            await browser.close()
            print(f"✅ PDF salvo em {pdf_file_path}")
            return pdf_file_path
        except Exception as e:
            print(f"❌ Erro ao baixar PDF: {e}")
            attempt += 1
            await asyncio.sleep(2)
    return None

@app.route("/boletos/<boleto_id>", methods=["GET"])
async def baixar_boleto(boleto_id):
    url_boleto = f"https://api.pagar.me/1/boletos/{boleto_id}"
    pdf_path = await download_pdf_content(url_boleto)

    if pdf_path and os.path.exists(pdf_path):
        response = await send_file(
            pdf_path,
            as_attachment=True,
            download_name=os.path.basename(pdf_path)
        )

        async def cleanup_file():
            await asyncio.sleep(1)
            try:
                os.remove(pdf_path)
                print(f"🧹 PDF apagado: {pdf_path}")
            except Exception as e:
                print(f"❌ Erro ao apagar PDF: {e}")

        asyncio.create_task(cleanup_file())
        return response
    else:
        abort(404, description="Não foi possível gerar o boleto PDF.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)