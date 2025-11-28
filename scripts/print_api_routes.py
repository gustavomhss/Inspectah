from inspectah.api import app


def main() -> None:
    print("Registered routes in Inspectah API:\n")
    for route in app.routes:
        methods = ", ".join(sorted(route.methods)) if hasattr(route, "methods") else ""
        path = getattr(route, "path", "")
        endpoint = getattr(route, "endpoint", None)
        name = getattr(route, "name", "")
        module = getattr(endpoint, "__module__", "")
        func = getattr(endpoint, "__name__", "")
        print(f"{methods:15} {path:40} {name:20} {module}.{func}")


if __name__ == "__main__":
    main()
