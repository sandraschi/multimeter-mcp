from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import multimeter_mcp.tools  # noqa: F401
from multimeter_mcp import __version__
from multimeter_mcp.app import mcp
from multimeter_mcp.web import setup_webapp

app = FastAPI(title="MultimeterMCP", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "https://tauri.localhost"],
    allow_origin_regex=r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_webapp(app, mcp)
app.mount("/mcp", mcp.http_app(path="/"))


def main() -> None:
    import asyncio

    from multimeter_mcp.transport import run_stdio

    asyncio.run(run_stdio(mcp))


if __name__ == "__main__":
    main()
