import pandas as pd
import numpy as np

# ============================================================
# 1. PEDIR LA RUTA DEL ARCHIVO
# ============================================================
ruta = input("Ingresa la ruta del archivo Excel: ").strip().strip('"')

# Leer la SEGUNDA hoja (índice 1)
df = pd.read_excel(ruta, sheet_name=1, header=2)

# Verificar que las columnas esperadas existan
columnas_esperadas = ["Intensidad", "Filtro", "Voltaje", "Corriente"]
faltantes = [c for c in columnas_esperadas if c not in df.columns]
if faltantes:
    raise ValueError(f"Faltan columnas en el Excel: {faltantes}. "
                     f"Columnas encontradas: {list(df.columns)}")

# Limpiar posibles valores nulos
df = df.dropna(subset=["Voltaje", "Corriente"]).copy()


# ============================================================
# 2. FUNCIÓN PARA DETECTAR EL POTENCIAL DE FRENADO (Vs)
# ============================================================
def detectar_Vs_definitivo(voltajes, corrientes, n_ruido=10):
    orden = np.argsort(voltajes)
    V = np.asarray(voltajes)[orden]
    I = np.asarray(corrientes)[orden]

    if len(I) < n_ruido + 3:
        return None

    # 1. Corriente de fondo
    I_fondo = np.median(I[:n_ruido])
    I_neta = I - I_fondo
    I_max_neta = np.max(I_neta)

    # Bajamos el corte minimo a 0.05 pA para capturar 546 nm
    if I_max_neta <= 0.05:
        return None

    # 2. Ventana adaptativa mas amplia (2% al 35% del maximo)
    mask = (I_neta >= 0.02 * I_max_neta) & (I_neta <= 0.35 * I_max_neta)
    V_sub = V[mask]
    sqrt_I_sub = np.sqrt(np.maximum(0, I_neta[mask]))

    # Si hay pocos puntos por la baja intensidad, tomar los primeros 4 puntos sobre el ruido
    if len(V_sub) < 3:
        indices_subida = np.where(I_neta > 0.05)[0]
        if len(indices_subida) < 3:
            return None
        idx_ini = indices_subida[0]
        idx_fin = min(idx_ini + 5, len(V))
        V_sub = V[idx_ini:idx_fin]
        sqrt_I_sub = np.sqrt(np.maximum(0, I_neta[idx_ini:idx_fin]))

    # 3. Ajuste lineal: sqrt(I_neta) = m * V + b
    m, b = np.polyfit(V_sub, sqrt_I_sub, 1)

    # Permitir pendientes menores para senales debiles como 546 nm
    if m <= 0.01:
        return None

    Vs = -b / m

    # 4. Validacion del rango fisico razonable
    if not (-4.5 <= Vs <= -0.1):
        return None

    return Vs


# ============================================================
# 3. APLICAR LA DETECCIÓN A CADA (INTENSIDAD, FILTRO)
# ============================================================
resultados = []

for (intensidad, filtro), grupo in df.groupby(["Intensidad", "Filtro"]):
    Vs = detectar_Vs_definitivo(grupo["Voltaje"].values, grupo["Corriente"].values)
    if Vs is not None:
        # En el efecto fotoeléctrico, Ek_max ≈ e * |Vs|
        # Con Vs en voltios, Ek queda directamente en eV
        Ek = abs(Vs)
        resultados.append({
            "Intensidad": intensidad,
            "Filtro (nm)": filtro,
            "Vs (V)": round(Vs, 3),
            "Ek_max (eV)": round(Ek, 3)
        })

df_res = pd.DataFrame(resultados)


# ============================================================
# 4. TABLA RESUMEN: FILTROS x INTENSIDADES
# ============================================================
tabla_pivot = df_res.pivot(index="Filtro (nm)",
                           columns="Intensidad",
                           values="Ek_max (eV)")

# Estadísticas por filtro
stats = df_res.groupby("Filtro (nm)")["Ek_max (eV)"].agg(
    Promedio="mean",
    Desviación="std",
    Mínimo="min",
    Máximo="max"
).round(3)

# Reemplazar valores absurdos (fuera del rango fisico razonable de 0.1 a 3.5 eV) por NaN
df_res.loc[(df_res["Ek_max (eV)"] > 3.5) | (df_res["Ek_max (eV)"] < 0.1), "Ek_max (eV)"] = np.nan

# Recalcular la tabla pivot sin outliers
tabla_pivot_limpia = df_res.pivot(index="Filtro (nm)", columns="Intensidad", values="Ek_max (eV)")

# Ordenar filtros numéricamente (por si vienen como string)
tabla_pivot = tabla_pivot.sort_index()
stats = stats.sort_index()


# ============================================================
# 5. IMPRIMIR RESULTADOS EN PANTALLA
# ============================================================
print("\n" + "=" * 70)
print("  POTENCIAL DE FRENADO (Vs) POR INTENSIDAD Y FILTRO")
print("=" * 70)
print(df_res.to_string(index=False))


print("\n" + "=" * 70)
print("  ENERGÍA CINÉTICA MÁXIMA (eV) — TABLA COMPARATIVA")
print("=" * 70)
print(tabla_pivot.to_string())


print("\n" + "=" * 70)
print("  ESTADÍSTICAS POR FILTRO")
print("=" * 70)
print(stats.to_string())


print("\n" + "=" * 70)
print("  VERIFICACIÓN TEÓRICA")
print("=" * 70)
print("En teoría, Ek_max debe ser CONSTANTE entre intensidades")
print("para un mismo filtro. Observa la columna 'Desviación':")
print("si es pequeña (< 0.1 eV), la teoría se cumple.\n")