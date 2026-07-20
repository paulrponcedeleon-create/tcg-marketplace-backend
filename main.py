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
    decoded = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))
    
    rows = list(reader)
    if not rows:
        return {"error": "El archivo CSV está vacío"}
    
    # Extraemos los nombres de las columnas reales de tu archivo
    fieldnames = list(rows[0].keys())
    
    cards = []
    for row in rows:
        # Convertimos todo a minúsculas limpias para buscar
        norm = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k}
        
        # Código
        code = (norm.get("card code") or norm.get("code") or norm.get("card number") or 
                norm.get("number") or norm.get("custom code") or norm.get("id") or "")
        
        # Nombre (Búsqueda ampliada)
        name = (norm.get("card name") or norm.get("product name") or norm.get("name") or 
                norm.get("title") or norm.get("product") or norm.get("item name") or "")
        
        # Precio (Búsqueda ampliada)
        raw_price = (norm.get("market price") or norm.get("tcg market price") or 
                     norm.get("price") or norm.get("market_price") or norm.get("tcgplayer market") or 
                     norm.get("ext. market price") or norm.get("ext. price") or 
                     norm.get("avg price") or norm.get("purchase price") or "0")
        
        raw_price_clean = raw_price.replace("$", "").replace(",", "").strip()
        try:
            market_price = float(raw_price_clean)
        except ValueError:
            market_price = 0.0
            
        margin_factor = 1.0 + (margin_percentage / 100.0)
        list_price = round(market_price * margin_factor, 2)
        
        cards.append({
            "code": code,
            "name": name,
            "market_price": market_price,
            "your_price": list_price,
            "image_url": f"https://raw.githubusercontent.com/optcg/optcg-data/main/cards/images/en/{code}.png" if code else ""
        })
        
    return {
        "columnas_detectadas_en_tu_csv": fieldnames,
        "total_cards": len(cards), 
        "cards": cards
    }
