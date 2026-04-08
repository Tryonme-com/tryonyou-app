from src.logic.zero_size_engine import ZeroSizeEngine
from src.logic.make_sync import sync_to_bunker

def run_bunker():
    print("🚀 Inicializando Protocolo de Soberanía V10...")
    engine = ZeroSizeEngine(chest=105, shoulder=48, waist=85)
    res = engine.calculate_fit()
    print(f"Resultado del Motor: {res['msg']} (Índice: {res['index']})")
    print(engine.white_peacock_validation())
    sync_to_bunker(res)
    print("✅ ¡A FUEGO! Sistema consolidado.")

if __name__ == "__main__":
    run_bunker()