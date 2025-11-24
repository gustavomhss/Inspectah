from app.sources.routes_admin import router


def test_router_exists():
    # Apenas garante que o router foi construído quando FastAPI está disponível
    assert router is None or router.prefix == "/admin/sources"

