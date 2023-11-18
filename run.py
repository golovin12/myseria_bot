import uvicorn

from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        ssl_keyfile=settings.SSL_PRIVATE_PATH,
        ssl_certfile=settings.SSL_PUBLIC_PATH,
    )
