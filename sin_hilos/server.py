import socket
import csv
import json
import os

# Archivos
ARCHIVO_ESTUDIANTES = '../estudiantes.csv'
ARCHIVO_CALIFICACIONES = '../calificaciones.csv'

# Constantes de comandos
AGREGAR_ESTUDIANTE = "AGREGAR_ESTUDIANTE"
AGREGAR = "AGREGAR"
BUSCAR = "BUSCAR"
ACTUALIZAR = "ACTUALIZAR"
LISTAR = "LISTAR"
ELIMINAR = "ELIMINAR"

# ---------------- FUNCIONES DE ARCHIVOS ---------------- #

def inicializar_csvs():
    """Crea los archivos si no existen"""
    # Estudiantes
    if not os.path.exists(ARCHIVO_ESTUDIANTES):
        with open(ARCHIVO_ESTUDIANTES, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre'])
        print("Archivo estudiantes.csv creado")

    # Calificaciones
    if not os.path.exists(ARCHIVO_CALIFICACIONES):
        with open(ARCHIVO_CALIFICACIONES, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Materia', 'Calificación'])
        print("Archivo calificaciones.csv creado")

# ---------------- FUNCIONES DE ESTUDIANTES ---------------- #

def agregar_estudiante(id_est, nombre):
    """Registra un nuevo estudiante"""
    try:
        # Verificar si ya existe
        with open(ARCHIVO_ESTUDIANTES, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    return {"status": "error", "mensaje": "El estudiante ya está registrado"}

        # Agregar nuevo
        with open(ARCHIVO_ESTUDIANTES, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre])
        return {"status": "ok", "mensaje": f"Estudiante {nombre} agregado con éxito"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def estudiante_existe(id_est):
    """Verifica si el estudiante existe"""
    try:
        with open(ARCHIVO_ESTUDIANTES, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    return True
        return False
    except Exception:
        return False

# ---------------- FUNCIONES DE CALIFICACIONES ---------------- #

def agregar_calificacion(id_est, materia, calif):
    """Agrega calificación validando estudiante"""
    try:
        if not estudiante_existe(id_est):
            return {"status": "error", "mensaje": "El estudiante no está registrado"}

        calif_float = float(calif)
        if calif_float < 0 or calif_float > 20:
            return {"status": "error", "mensaje": "Calificación debe estar entre 0 y 20"}

        with open(ARCHIVO_CALIFICACIONES, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, materia, calif_float])
        return {"status": "ok", "mensaje": f"Calificación registrada para ID {id_est}"}
    except ValueError:
        return {"status": "error", "mensaje": "Calificación debe ser un número"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_por_id(id_est):
    """Muestra todas las calificaciones de un estudiante"""
    try:
        if not estudiante_existe(id_est):
            return {"status": "error", "mensaje": "Estudiante no registrado"}

        with open(ARCHIVO_CALIFICACIONES, 'r') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader if row['ID_Estudiante'] == id_est]
        if not data:
            return {"status": "not_found", "mensaje": "Sin calificaciones registradas"}
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def actualizar_calificacion(id_est, materia, nueva_calif):
    """Actualiza calificación de una materia"""
    try:
        if not estudiante_existe(id_est):
            return {"status": "error", "mensaje": "Estudiante no registrado"}

        nueva_calif_float = float(nueva_calif)
        if nueva_calif_float < 0 or nueva_calif_float > 20:
            return {"status": "error", "mensaje": "Calificación debe estar entre 0 y 20"}

        rows = []
        found = False
        with open(ARCHIVO_CALIFICACIONES, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est and row['Materia'] == materia:
                    row['Calificación'] = nueva_calif_float
                    found = True
                rows.append(row)

        if not found:
            return {"status": "not_found", "mensaje": "No existe calificación para esa materia"}

        with open(ARCHIVO_CALIFICACIONES, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Materia', 'Calificación'])
            writer.writeheader()
            writer.writerows(rows)
        return {"status": "ok", "mensaje": "Calificación actualizada"}
    except ValueError:
        return {"status": "error", "mensaje": "Calificación inválida"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_todas():
    """Lista todas las calificaciones"""
    try:
        with open(ARCHIVO_CALIFICACIONES, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def eliminar_por_id(id_est):
    """Elimina todas las calificaciones de un estudiante"""
    try:
        rows = []
        found = False
        with open(ARCHIVO_CALIFICACIONES, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] != id_est:
                    rows.append(row)
                else:
                    found = True
        if not found:
            return {"status": "not_found", "mensaje": "El estudiante no tiene registros"}
        with open(ARCHIVO_CALIFICACIONES, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Materia', 'Calificación'])
            writer.writeheader()
            writer.writerows(rows)
        return {"status": "ok", "mensaje": f"Registros eliminados para ID {id_est}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

# ---------------- PROCESAMIENTO DE COMANDOS ---------------- #

def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0]

    if op == AGREGAR_ESTUDIANTE and len(partes) == 3:
        return agregar_estudiante(partes[1], partes[2])
    elif op == AGREGAR and len(partes) == 4:
        return agregar_calificacion(partes[1], partes[2], partes[3])
    elif op == BUSCAR and len(partes) == 2:
        return buscar_por_id(partes[1])
    elif op == ACTUALIZAR and len(partes) == 4:
        return actualizar_calificacion(partes[1], partes[2], partes[3])
    elif op == LISTAR:
        return listar_todas()
    elif op == ELIMINAR and len(partes) == 2:
        return eliminar_por_id(partes[1])
    else:
        return {"status": "error", "mensaje": "Comando inválido o parámetros incorrectos"}

# ---------------- MAIN ---------------- #

def main():
    inicializar_csvs()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Servidor secuencial escuchando en puerto 12345...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Cliente conectado desde {addr}")
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Comando recibido: {data}")
                respuesta = procesar_comando(data)
                client_socket.send(json.dumps(respuesta).encode('utf-8'))
            client_socket.close()
            print("Cliente desconectado.")
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
