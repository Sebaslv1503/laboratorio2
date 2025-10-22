import socket
import csv
import json
import os

ARCHIVO_CSV = '../calificaciones.csv'

# Constantes para comandos
AGREGAR = "AGREGAR"
BUSCAR = "BUSCAR"
ACTUALIZAR = "ACTUALIZAR"
LISTAR = "LISTAR"
ELIMINAR = "ELIMINAR"

def inicializar_csv():
    """Inicializa el archivo CSV si no existe"""
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificación'])
        print("Archivo calificaciones.csv creado")

def agregar_calificacion(id_est, nombre, materia, calif):
    """Agrega una nueva calificación al CSV"""
    try:
        # Validar que la calificación sea un número
        calif_float = float(calif)
        if calif_float < 0 or calif_float > 20:
            return {"status": "error", "mensaje": "Calificación debe estar entre 0 y 20"}
        
        with open(ARCHIVO_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre, materia, calif_float])
        return {"status": "ok", "mensaje": f"Calificación agregada para {nombre}"}
    except ValueError:
        return {"status": "error", "mensaje": "Calificación debe ser un número"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_por_id(id_est):
    """Busca una calificación por ID de estudiante"""
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    return {"status": "ok", "data": row}
        return {"status": "not_found", "mensaje": "ID no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def actualizar_calificacion(id_est, nueva_calif):
    """Actualiza la calificación de un estudiante"""
    try:
        # Validar nueva calificación
        nueva_calif_float = float(nueva_calif)
        if nueva_calif_float < 0 or nueva_calif_float > 20:
            return {"status": "error", "mensaje": "Calificación debe estar entre 0 y 20"}
        
        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    row['Calificación'] = nueva_calif_float
                    found = True
                rows.append(row)
        
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificación'])
            writer.writeheader()
            writer.writerows(rows)
        
        return {"status": "ok", "mensaje": f"Calificación actualizada a {nueva_calif_float}"}
    except ValueError:
        return {"status": "error", "mensaje": "Calificación debe ser un número"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_todas():
    """Lista todas las calificaciones"""
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def eliminar_por_id(id_est):
    """Elimina una calificación por ID"""
    try:
        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] != id_est:
                    rows.append(row)
                else:
                    found = True
        
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificación'])
            writer.writeheader()
            writer.writerows(rows)
        
        return {"status": "ok", "mensaje": f"Registro eliminado para ID {id_est}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando(comando):
    """Procesa los comandos recibidos del cliente"""
    partes = comando.strip().split('|')
    op = partes[0]
    
    if op == AGREGAR and len(partes) == 5:
        return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
    elif op == BUSCAR and len(partes) == 2:
        return buscar_por_id(partes[1])
    elif op == ACTUALIZAR and len(partes) == 3:
        return actualizar_calificacion(partes[1], partes[2])
    elif op == LISTAR:
        return listar_todas()
    elif op == ELIMINAR and len(partes) == 2:
        return eliminar_por_id(partes[1])
    else:
        return {"status": "error", "mensaje": "Comando inválido"}

def main():
    """Función principal del servidor"""
    inicializar_csv()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Servidor secuencial escuchando en puerto 12345...")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Cliente conectado desde {addr}")
            
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    print(f"Comando recibido: {data}")
                    respuesta = procesar_comando(data)
                    client_socket.send(json.dumps(respuesta).encode('utf-8'))
            except Exception as e:
                print(f"Error en comunicación: {e}")
            finally:
                client_socket.close()
                print("Cliente desconectado.")
                
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()