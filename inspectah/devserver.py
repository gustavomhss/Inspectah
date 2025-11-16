from __future__ import annotations
import argparse
import os
import sys
import threading
import time
from typing import Optional

try:  # pragma: no cover
    import uvicorn
except ModuleNotFoundError:  # pragma: no cover
    uvicorn = None  # type: ignore


def _wait_for_shutdown(shutdown_path: Optional[str]) -> None:
    if not shutdown_path:
        return
    print(f"[devserver] Aguardando sinal em {shutdown_path}")
    while True:
        if os.path.exists(shutdown_path):
            try:
                os.remove(shutdown_path)
            except OSError:
                pass
            break
        time.sleep(1)


def _idle_mode(shutdown_path: Optional[str]) -> None:
    print("[devserver] Ambiente sem suporte a sockets ou sem uvicorn instalado; entrando em modo idle.")
    _wait_for_shutdown(shutdown_path)


def run_server(host: str, port: int, shutdown_path: Optional[str]) -> None:
    if uvicorn is None:
        _idle_mode(shutdown_path)
        return

    config = uvicorn.Config("inspectah.api:build_app", host=host, port=port, factory=True, log_level="info")
    server = uvicorn.Server(config)

    def watcher() -> None:
        if not shutdown_path:
            return
        while not server.should_exit:
            if os.path.exists(shutdown_path):
                try:
                    os.remove(shutdown_path)
                except OSError:
                    pass
                server.should_exit = True
                break
            time.sleep(1)

    watcher_thread = threading.Thread(target=watcher, daemon=True)
    watcher_thread.start()
    try:
        server.run()
    except PermissionError:
        _idle_mode(shutdown_path)
    finally:
        if shutdown_path and os.path.exists(shutdown_path):
            try:
                os.remove(shutdown_path)
            except OSError:
                pass


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Inspectah dev server wrapper")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--shutdown-file", default=None)
    args = parser.parse_args(argv)

    run_server(args.host, args.port, args.shutdown_file)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
