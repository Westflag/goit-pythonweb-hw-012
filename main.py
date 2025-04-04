import os

import uvicorn

from app.database import DATABASE_URL

if __name__ == "__main__":
    print(DATABASE_URL + "10")
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info", reload=True)