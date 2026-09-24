import random
import json

def fit_logic_algorithm(height, weight, chest, waist, hips):
    """
    Simulación del algoritmo Fit-Logic.
    Calcula la talla recomendada basada en métricas biométricas.
    """
    # Lógica simplificada basada en estándares de la industria para marcas de lujo (Balmain)
    # Estos rangos son representativos de una marca "Refined Parisian"
    
    # Cálculo de un índice de masa/forma
    bmi = weight / ((height / 100) ** 2)
    
    if height < 150 or height > 210 or weight < 40 or weight > 150:
        return "OUT_OF_RANGE"

    # Recomendación de talla basada en el pecho (chest) como métrica principal para Blazers
    if chest < 84:
        size = "34 (XS)"
    elif chest < 88:
        size = "36 (S)"
    elif chest < 92:
        size = "38 (M)"
    elif chest < 96:
        size = "40 (L)"
    elif chest < 100:
        size = "42 (XL)"
    else:
        size = "44 (XXL)"
        
    # Ajuste por cintura (waist) para asegurar el fit "Taille marquée"
    if waist > (chest * 0.85):
        # Si la cintura es proporcionalmente grande, sugerimos una talla más para comodidad
        sizes = ["34 (XS)", "36 (S)", "38 (M)", "40 (L)", "42 (XL)", "44 (XXL)"]
        current_idx = sizes.index(size)
        if current_idx < len(sizes) - 1:
            size = sizes[current_idx + 1]

    return size

def run_stress_test(iterations=100):
    results = []
    errors = 0
    
    print(f"🧪 Iniciando Stress Test: {iterations} perfiles biométricos aleatorios...")
    
    for i in range(iterations):
        # Generar métricas aleatorias incluyendo casos borde
        height = random.uniform(145, 215)
        weight = random.uniform(35, 160)
        chest = random.uniform(75, 120)
        waist = random.uniform(60, 110)
        hips = random.uniform(80, 130)
        
        try:
            recommendation = fit_logic_algorithm(height, weight, chest, waist, hips)
            
            # Verificar si la recomendación está dentro de los rangos de Balmain (34-44)
            valid_sizes = ["34 (XS)", "36 (S)", "38 (M)", "40 (L)", "42 (XL)", "44 (XXL)", "OUT_OF_RANGE"]
            
            if recommendation not in valid_sizes:
                raise ValueError(f"Talla no válida: {recommendation}")
                
            results.append({
                "id": i + 1,
                "metrics": {
                    "height": round(height, 2),
                    "weight": round(weight, 2),
                    "chest": round(chest, 2),
                    "waist": round(waist, 2),
                    "hips": round(hips, 2)
                },
                "recommendation": recommendation,
                "status": "SUCCESS"
            })
        except Exception as e:
            errors += 1
            results.append({
                "id": i + 1,
                "error": str(e),
                "status": "ERROR"
            })

    # Guardar resultados
    with open("biometric_stress_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"✅ Test completado. Errores: {errors}")
    print(f"📊 Reporte guardado en: biometric_stress_test_results.json")
    return results

if __name__ == "__main__":
    run_stress_test()
