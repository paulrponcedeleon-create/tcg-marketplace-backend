from fastapi import FastAPI, UploadFile, File
import csv
import io

app = FastAPI(title="TCG Marketplace API")

@app.get("/")
def home():
    return {"status": "ok", "message": "API de TCG Marketplace funcionando"}

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), margin_percentage: float = 5.0):
    content = await file.read()
    decoded = content.decode('utf-8-sig') # Maneja codificaciones con BOM
    reader = csv.DictReader(io.StringIO(decoded))
    
    cards = []
    for row in reader:
        # Convertir todas las llaves del CSV a minúsculas para buscar coincidencias
        normalized_row = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k}
        
        # Buscar el código de la carta
        code = (normalized_row.get("card code") or 
                normalized_row.get("code") or 
                normalized_row.get("card number") or 
                normalized_row.get("number") or 
                normalized_row.get("id") or "")
        
        # Buscar el nombre
        name = (normalized_row.get("card name") or 
                normalized_row.get("name") or 
                normalized_row.get("title") or "")
        
        # Buscar el precio de mercado
        raw_price = (normalized_row.get("market price") or 
                     normalized_row.get("price") or 
                     normalized_row.get("market_price") or 
                     normalized_row.get("avg price") or "0")
        
        # Limpiar caracteres de moneda como '$'
        raw_price_clean = raw_price.replace("$", "").replace(",", "").strip()
        try:
            market_price = float(raw_price_clean)
        except ValueError:
            market_price = 0.0
            
        margin_factor = 1.0 + (margin_percentage / 100.0)
        list_price = round(market_price * margin_factor, 2)
        
        if code or name:
            cards.append({
                "code": code,
                "name": name,
                "market_price": market_price,
                "your_price": list_price,
                "image_url": f"https://raw.githubusercontent.com/optcg/optcg-data/main/cards/images/en/{code}.png" if code else ""
            })
        
    return {"total_cards": len(cards), "cards": cards}
