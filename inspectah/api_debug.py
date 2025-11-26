from inspectah.api import build_app

def main():
    app = build_app()
    for route in app.routes:
        methods = getattr(route, "methods", []) or []
        try:
            methods_str = ",".join(sorted(methods))
        except Exception:
            methods_str = ""
        print(f"{methods_str:15} {route.path}")

if __name__ == "__main__":
    main()
