import os
import pandas as pd
from datetime import datetime
from tkinter import messagebox

def obtener_archivos_por_fecha(directorio, fecha_inicio, fecha_fin, formatos):
    datos = []
    
    fecha_inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y").date()
    fecha_fin = datetime.strptime(fecha_fin, "%d-%m-%Y").date()
    
    for carpeta_raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            if not any(archivo.lower().endswith(ext.lower()) for ext in formatos):
                continue
            
            ruta_completa = os.path.join(carpeta_raiz, archivo)
            try:
                fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_completa)).date()
                
                if fecha_inicio <= fecha_modificacion <= fecha_fin:
                    hora_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_completa)).hour
                    periodo = "Mañana" if hora_modificacion < 12 else "Tarde"
                    datos.append([archivo, ruta_completa, fecha_modificacion.strftime('%d-%m-%Y'), periodo])
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
    
    df = pd.DataFrame(archivos, columns=["Documento", "Ruta", "Fecha", "Periodo"])
    nombre_excel = f"documentos_{fecha_inicio.replace('-', '')}_a_{fecha_fin.replace('-', '')}.xlsx"
    df.to_excel(nombre_excel, index=False)
    messagebox.showinfo("Resultado", f"Archivo Excel '{nombre_excel}' creado exitosamente.")

def on_button_click(entry_fecha_inicio, entry_fecha_fin, entry_formatos):
    fecha_inicio = entry_fecha_inicio.get()
    fecha_fin = entry_fecha_fin.get()
    formatos = [f.strip().lower() for f in entry_formatos.get().split(',')]
    
    if not fecha_inicio or not fecha_fin or not formatos:
        messagebox.showerror("Error", "Por favor complete todos los campos.")
        return
    
    try:
        datetime.strptime(fecha_inicio, "%d-%m-%Y")
        datetime.strptime(fecha_fin, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Error", "Las fechas deben tener el formato DD-MM-YYYY.")
        return
    
    crear_excel(fecha_inicio, fecha_fin, formatos)