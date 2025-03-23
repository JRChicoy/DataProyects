# func_ficheros.py
import os
import pandas as pd
from datetime import datetime
from tkinter import messagebox

def obtener_archivos_por_fecha(directorio, fecha_inicio, fecha_fin, formatos):
    datos = []
    
    fecha_inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
    fecha_fin = datetime.strptime(fecha_fin, "%d-%m-%Y")
    
    for carpeta_raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            if not any(archivo.endswith(ext) for ext in formatos):
                continue
            
            ruta_completa = os.path.join(carpeta_raiz, archivo)
            try:
                fecha_creacion = datetime.fromtimestamp(os.path.getctime(ruta_completa))
                fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                
                periodo_creacion = "Mañana" if fecha_creacion.hour < 12 else "Tarde"
                periodo_modificacion = "Mañana" if fecha_modificacion.hour < 12 else "Tarde"
                
                if fecha_inicio <= fecha_creacion <= fecha_fin:
                    datos.append([archivo, ruta_completa, fecha_creacion.strftime('%d-%m-%Y'), "Creado", periodo_creacion])
                elif fecha_inicio <= fecha_modificacion <= fecha_fin:
                    datos.append([archivo, ruta_completa, fecha_modificacion.strftime('%d-%m-%Y'), "Modificado", periodo_modificacion])
            except FileNotFoundError:
                print(f"Archivo no encontrado: {ruta_completa}")
            except PermissionError:
                print(f"Permiso denegado: {ruta_completa}")
            except Exception as e:
                print(f"Error con el archivo {ruta_completa}: {e}")
    
    return datos

def crear_excel(fecha_inicio, fecha_fin, formatos):
    directorio = os.getcwd()  
    
    archivos = obtener_archivos_por_fecha(directorio, fecha_inicio, fecha_fin, formatos)
    
    if not archivos:
        messagebox.showinfo("Resultado", "No se encontraron archivos en el rango de fechas especificado.")
        return
    
    df = pd.DataFrame(archivos, columns=["Documento", "Ruta", "Fecha", "Estado", "Periodo"])
    nombre_excel = f"documentos_{fecha_inicio.replace('-', '')}_a_{fecha_fin.replace('-', '')}.xlsx"
    df.to_excel(nombre_excel, index=False)
    messagebox.showinfo("Resultado", f"Archivo Excel '{nombre_excel}' creado exitosamente.")

def on_button_click(entry_fecha_inicio, entry_fecha_fin, entry_formatos):
    fecha_inicio = entry_fecha_inicio.get()
    fecha_fin = entry_fecha_fin.get()
    formatos = entry_formatos.get().split(', ')
    
    if not fecha_inicio or not fecha_fin or not formatos:
        messagebox.showerror("Error", "Por favor complete todos los campos.")
        return
    
    try:
        # Intentamos validar las fechas
        datetime.strptime(fecha_inicio, "%d-%m-%Y")
        datetime.strptime(fecha_fin, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Error", "Las fechas deben tener el formato DD-MM-YYYY.")
        return
    
    crear_excel(fecha_inicio, fecha_fin, formatos)
