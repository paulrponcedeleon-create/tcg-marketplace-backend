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
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    cards = []
    for row in reader:
        market_price = float(row.get("Market Price", 0))
        margin_factor = 1.0 + (margin_percentage / 100.0)
        list_price = round(market_price * margin_factor, 2)
        
        cards.append({
            "code": row.get("Card Code", ""),
            "name": row.get("Card Name", ""),
            "market_price": market_price,
            "your_price": list_price,
            "image_url": f"https://raw.githubusercontent.com/optcg/optcg-data/main/cards/images/en/{row.get('Card Code', '')}.png"
        })
        
    return {"total_cards": len(cards), "cards": cards}
