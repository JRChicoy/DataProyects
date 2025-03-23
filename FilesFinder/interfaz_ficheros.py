# interfaz.py
import tkinter as tk
from func_ficheros import on_button_click

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Buscador de Documentos")
ventana.geometry("400x300")

# Etiquetas y campos de entrada
label_fecha_inicio = tk.Label(ventana, text="Fecha de inicio (DD-MM-YYYY):")
label_fecha_inicio.pack(pady=5)

entry_fecha_inicio = tk.Entry(ventana)
entry_fecha_inicio.pack(pady=5)

label_fecha_fin = tk.Label(ventana, text="Fecha de fin (DD-MM-YYYY):")
label_fecha_fin.pack(pady=5)

entry_fecha_fin = tk.Entry(ventana)
entry_fecha_fin.pack(pady=5)

label_formatos = tk.Label(ventana, text="Formatos a buscar (separados por ', '):")
label_formatos.pack(pady=5)

entry_formatos = tk.Entry(ventana)
entry_formatos.pack(pady=5)

# Botón para ejecutar la acción
boton_generar = tk.Button(ventana, text="Generar Reporte", command=lambda: on_button_click(entry_fecha_inicio, entry_fecha_fin, entry_formatos))
boton_generar.pack(pady=20)

# Iniciar el loop de la interfaz gráfica
ventana.mainloop()
