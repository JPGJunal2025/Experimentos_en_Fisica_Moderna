import matplotlib.pyplot as plt
import numpy as np

# Datos
frecuencia = np.array([821917808219178, 740740740740741, 688073394495413,
                       549450549450549, 519031141868512], dtype=float)
U0 = np.array([1.75, 1.43, 1.21, 0.72, 0.6])

# --- Ajuste lineal con los datos REALES (como hace Excel) ---
m, b = np.polyfit(frecuencia, U0, 1)
print(f"Ecuación: y = {m:.2e}x + {b:.4f}")

# --- Escalar solo para graficar ---
factor = 1e14
freq_scaled = frecuencia / factor

# Recta ajustada (evaluada con los valores reales, luego escalada)
x_real = np.linspace(frecuencia.min(), frecuencia.max(), 100)
y_line = m * x_real + b
x_line_scaled = x_real / factor

# Crear figura
fig, ax = plt.subplots(figsize=(10, 6))

# Datos experimentales
ax.plot(freq_scaled, U0, marker='o', linestyle='', color='steelblue',
        markersize=9, label='Datos experimentales')

# Recta ajustada
ax.plot(x_line_scaled, y_line, linestyle='--', color='crimson', linewidth=2,
        label=f'Ajuste: y = {m:.0e}x - {abs(b):.4f}')

# Etiquetas del eje X con "×10¹⁴" al lado de cada valor
xticks = np.linspace(freq_scaled.min(), freq_scaled.max(), 6)
ax.set_xticks(xticks)
ax.set_xticklabels([f'{x:.2f} ×10¹⁴' for x in xticks])

# Etiquetas y título
ax.set_xlabel('Frecuencia (×10¹⁴ Hz)', fontsize=12)
ax.set_ylabel('U0 (V)', fontsize=12)
ax.set_title('U0 en función de la frecuencia', fontsize=14)

# Cuadrícula y leyenda
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(fontsize=11)

plt.tight_layout()
plt.show()