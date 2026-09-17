import matplotlib.pyplot as plt
import numpy as np

# Datos
frecuencia = np.array([821917808219178, 740740740740741, 688073394495413,
                       549450549450549, 519031141868512], dtype=float)
U0 = np.array([1.75, 1.43, 1.21, 0.72, 0.6])

# Carga del electrón (C)
e = 1.602176634e-19

# Energía cinética máxima en julios
Ek = U0 * e

# Pendiente impuesta (constante de Planck experimental)
m = 6.408e-34  # J·s

# Intercepto calculado con mínimos cuadrados para esa pendiente fija
b = np.mean(Ek) - m * np.mean(frecuencia)

# R²
y_pred = m * frecuencia + b
r2 = 1 - np.sum((Ek - y_pred)**2) / np.sum((Ek - np.mean(Ek))**2)

# Escalado para graficar
factor = 1e14
freq_scaled = frecuencia / factor
x_real = np.linspace(frecuencia.min(), frecuencia.max(), 100)
y_line = m * x_real + b
x_line_scaled = x_real / factor

# Figura pensada para hoja
fig, ax = plt.subplots(figsize=(8, 5.5))

# Datos experimentales
ax.plot(freq_scaled, Ek, marker='o', linestyle='', color='steelblue',
        markersize=9, label='Datos experimentales')

# Recta ajustada
ax.plot(x_line_scaled, y_line, linestyle='--', color='crimson', linewidth=2,
        label=(f'Ajuste:  y = {m:.3e}x − {abs(b):.3e}\n'
               f'R² = {r2:.4f}'))

# Etiquetas eje X con ×10¹⁴ al lado
xticks = np.linspace(freq_scaled.min(), freq_scaled.max(), 6)
ax.set_xticks(xticks)
ax.set_xticklabels([f'{x:.2f} ×10¹⁴' for x in xticks])

# Etiquetas y título
ax.set_xlabel('Frecuencia (Hz)', fontsize=12)
ax.set_ylabel('Energía cinética máxima (J)', fontsize=12)
ax.set_title('Energía cinética máxima en función de la frecuencia',
             fontsize=14, fontweight='bold')

ax.grid(True, linestyle='--', alpha=0.6)

# --- LEYENDA GRANDE Y VISIBLE ---
ax.legend(
    fontsize=14,
    loc='best',
    frameon=True,
    framealpha=1,
    edgecolor='black',
    borderpad=0.8,
    labelspacing=0.6,
    handlelength=2.5,
)

plt.tight_layout()

# Guardar en alta resolución
plt.savefig('grafico_Ek.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('grafico_Ek.pdf', bbox_inches='tight', facecolor='white')

plt.show()

# Mostrar resultados numéricos
print(f"Pendiente (h experimental): {m:.3e} J·s")
print(f"Intercepto: {b:.3e} J")
print(f"R² = {r2:.4f}")