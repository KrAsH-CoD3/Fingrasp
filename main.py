import warnings

from app import create_app


# Suppress the httptools GIL RuntimeWarning
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=r".*httptools.parser.parser.*GIL.*"
)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
        server_header=False
    )

