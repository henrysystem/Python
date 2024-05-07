import tkinter as tk
from tkinter import scrolledtext, Label, messagebox, Button
from datetime import datetime
from formateo_codigoPB import reformat_power_script  # Asegúrate de que esto importa correctamente tu función
import threading  # Para manejar el formateo en un hilo separado




def debounce(delay):
    """
    Decorador para retrasar la ejecución de la función hasta que pase un 'delay' después de la última llamada.
    
    Args:
        delay (float): El retraso en segundos antes de ejecutar la función.
    """
    def decorator(f):
        timer = [None]
        def debounced(*args, **kwargs):
            if timer[0] is not None:
                timer[0].cancel()
            timer[0] = threading.Timer(delay, lambda: f(*args, **kwargs))
            timer[0].start()
        return debounced
    return decorator

def formatear_codigo():
    codigo_entrada = txt_area_entrada.get('1.0', tk.END).rstrip()  # Eliminar espacios en blanco al final
    codigo_formateado_actual = txt_area_resultado.get('1.0', tk.END).rstrip()
    
    try:
        # Pre-formatear el código para la comparación sin modificar el área de resultados
        codigo_formateado = reformat_power_script(codigo_entrada)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al formatear el código: {e}")
        lbl_procesando.config(text='')
        ventana.config(cursor='')
        return
    
    if codigo_entrada == codigo_formateado_actual:
        messagebox.showinfo("Información", "El código que está ingresando es igual al del resultado anterior. Por favor, ingrese un código nuevo para el formateo.")
        lbl_procesando.config(text='')  # Asegurarse de limpiar el estado
        ventana.config(cursor='')
        return

    try:
        codigo = txt_area_entrada.get('1.0', tk.END)
        codigo_formateado = reformat_power_script(codigo)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al formatear el código: {e}")
        lbl_procesando.config(text='')
        ventana.config(cursor='')
    else:
        txt_area_resultado.configure(state='normal')
        txt_area_resultado.delete('1.0', tk.END)
        txt_area_resultado.insert(tk.END, codigo_formateado)
        txt_area_resultado.configure(state='disabled')
        ventana.clipboard_clear()
        ventana.clipboard_append(codigo_formateado)
        lbl_procesando.config(text='')  # Elimina el texto de "PROCESANDO..." una vez completado
        ventana.config(cursor='')  # Restaura el cursor normal

def actualizar_posicion_cursor(event=None):
    # Obtener la posición actual del cursor en el área de texto de entrada
    posicion = txt_area_entrada.index(tk.INSERT)
    # Actualizar el label con la posición del cursor
    lbl_posicion_cursor.config(text=f"Posición: Línea {posicion.split('.')[0]}, Columna {posicion.split('.')[1]}")


# Inicializar una variable para mantener el índice de la última ocurrencia encontrada
indice_ultima_ocurrencia = '1.0'
def buscar_texto(siguiente=False):
    global indice_ultima_ocurrencia

    texto_a_buscar = entrada_busqueda.get()
    if not texto_a_buscar:
        messagebox.showinfo("Información", "Por favor, ingrese el texto a buscar.")
        return

    if not siguiente:
        # Iniciar desde el principio si no estamos buscando la siguiente ocurrencia
        inicio = '1.0'
    else:
        # Iniciar la búsqueda desde la "última" ocurrencia encontrada, más un carácter
        inicio = txt_area_entrada.index(f"{indice_ultima_ocurrencia}+1c")

    indice = txt_area_entrada.search(texto_a_buscar, inicio, nocase=1, stopindex=tk.END)

    if not indice:
        if siguiente:
            # Si estamos buscando la siguiente ocurrencia y no encontramos nada, mostrar mensaje y reiniciar búsqueda
            messagebox.showinfo("Información", "No se encontraron más ocurrencias.")
            indice_ultima_ocurrencia = '1.0'  # Reiniciar para futuras búsquedas
        else:
            messagebox.showinfo("Información", "Texto no encontrado.")
        return

    # Encontramos una ocurrencia, ahora resaltarla
    ultimo_indice = f"{indice}+{len(texto_a_buscar)}c"
    txt_area_entrada.tag_remove('resaltado', '1.0', tk.END)
    txt_area_entrada.tag_add('resaltado', indice, ultimo_indice)
    txt_area_entrada.tag_config('resaltado', background='yellow', foreground='black')
    txt_area_entrada.see(indice)  # Asegurar que la ocurrencia esté visible

    # Actualizar índice de la última ocurrencia encontrada
    indice_ultima_ocurrencia = indice

    # Opcional: actualizar información de la línea actual si es necesario
    numero_linea = indice.split('.')[0]
    lbl_posicion_cursor.config(text=f"Línea actual: {numero_linea}")


def limpiar_y_pegar_desde_portapapeles():
    try:
        # Intentar obtener el texto del portapapeles antes de limpiar
        codigo_desde_portapapeles = ventana.clipboard_get()
    except tk.TclError:
        messagebox.showwarning("Advertencia", "No se pudo obtener el texto del portapapeles.")
        return

    # Obtener el texto actualmente mostrado en el área de resultado para comparar
    codigo_formateado_actual = txt_area_resultado.get('1.0', tk.END).rstrip()

    # Si el código del portapapeles es igual al último código formateado mostrado, informar al usuario
    if codigo_desde_portapapeles.rstrip() == codigo_formateado_actual:
        messagebox.showinfo("Información", "El código del portapapeles es igual al del resultado anterior. Por favor, ingrese un código nuevo para el formateo.")
        return
    elif codigo_desde_portapapeles.rstrip() == '':
        messagebox.showinfo("Información", "El código del portapapeles esta vacio, debe copiar un codigo antes de este proceso.")
        return  

    # Limpiar ambas áreas de texto
    txt_area_entrada.delete('1.0', tk.END)
    txt_area_resultado.configure(state='normal')  # Hacer editable temporalmente para limpiar
    txt_area_resultado.delete('1.0', tk.END)
    txt_area_resultado.configure(state='disabled')  # Volver a deshabilitar
    
    try:
        # Intentar obtener el texto del portapapeles
        codigo_desde_portapapeles = ventana.clipboard_get()
    except tk.TclError:
        messagebox.showwarning("Advertencia", "No se pudo obtener el texto del portapapeles.")
        return
    
    # Si se obtuvo el texto, colocarlo en el área de entrada
    txt_area_entrada.insert(tk.END, codigo_desde_portapapeles)
    
    # Opcionalmente, podría llamarse automáticamente a formatear_y_mostrar_codigo aquí
    formatear_y_mostrar_codigo()



# Ahora aplicamos el decorador con un retardo especificado
@debounce(delay=0.5)  # Retraso de 0.5 segundos
def formatear_y_mostrar_codigo(event=None):
    lbl_procesando.config(text='PROCESANDO...')  # Muestra "PROCESANDO..." durante el formateo
    ventana.config(cursor='watch')  # Cambia el cursor a cursor de espera
    threading.Thread(target=formatear_codigo_wrapper).start()

def formatear_codigo_wrapper():
    formatear_codigo()

ventana = tk.Tk()
ventana.state('zoomed')
ventana.title("Formateador de Código PowerScript")

frame_principal = tk.Frame(ventana)
frame_principal.pack(fill=tk.BOTH, expand=True)

frame_entrada = tk.Frame(frame_principal, padx=5, pady=5)
frame_entrada.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


frame_resultado = tk.Frame(frame_principal, padx=5, pady=5)
frame_resultado.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Crear un frame para los controles de búsqueda
frame_busqueda = tk.Frame(frame_entrada)
frame_busqueda.pack(side=tk.TOP,fill=tk.BOTH,pady=10)

# Botón para buscar la siguiente ocurrencia
boton_buscar_siguiente = tk.Button(frame_busqueda, text="Buscar Siguiente", command=lambda: buscar_texto(siguiente=True))
boton_buscar_siguiente.pack(side=tk.LEFT, padx=(5))
               
# Campo de entrada para el texto a buscar
entrada_busqueda = tk.Entry(frame_busqueda)
entrada_busqueda.pack(side=tk.LEFT, padx=(0, 10), anchor='e')

lbl_entrada = tk.Label(frame_entrada, text="Código Original:")
lbl_entrada.pack(anchor='nw')

# Crear un label en `frame_entrada` para mostrar la posición del cursor
lbl_posicion_cursor = tk.Label(frame_entrada, text="Posición: Línea 1, Columna 0")
lbl_posicion_cursor.pack(anchor='nw')

txt_area_entrada = scrolledtext.ScrolledText(frame_entrada, width=60, height=20)
txt_area_entrada.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
txt_area_entrada.bind('<KeyRelease>', actualizar_posicion_cursor)
txt_area_entrada.bind('<ButtonRelease-1>', actualizar_posicion_cursor)
txt_area_entrada.bind('<KeyRelease>', lambda event: formatear_y_mostrar_codigo())


lbl_resultado = tk.Label(frame_resultado, text="Código Formateado:")
lbl_resultado.pack(anchor='nw')

txt_area_resultado = scrolledtext.ScrolledText(frame_resultado, width=60, height=20)
txt_area_resultado.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
txt_area_resultado.configure(state='disabled')

# Crear botón para limpiar y pegar desde el portapapeles
btn_limpiar_pegar = Button(frame_entrada, text="Limpiar y Pegar desde Portapapeles", command=limpiar_y_pegar_desde_portapapeles)
btn_limpiar_pegar.pack(side=tk.LEFT, padx=(0,50))

lbl_procesando = Label(frame_resultado, text='', fg='red')
lbl_procesando.pack(side=tk.BOTTOM, fill=tk.X)

instrucciones = ("Este programa permite formatear codigo hecho en PowerScript(PowerBuilder).\n"
                 "Desarrollado por Henry Pinchao.\n"
                 "Instrucciones: Copie el texto en el área 'Código Original'. "
                 "El texto formateado aparecerá automáticamente en el área 'Código Formateado' y se guardará en el portapapeles.")
lbl_instrucciones = tk.Label(frame_entrada, text=instrucciones, justify=tk.LEFT)
lbl_instrucciones.pack(side=tk.BOTTOM, fill=tk.X)

fecha_actual = datetime.now().strftime("%Y%m%d")
version = f"Versión: v{fecha_actual}-5"
lbl_version = tk.Label(frame_resultado, text=version, justify=tk.RIGHT)
lbl_version.pack(side=tk.BOTTOM, fill=tk.X)

ventana.mainloop()