import socket
import threading
import csv
import json
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ARCHIVO_ESTUDIANTES = os.path.join(BASE, 'estudiantes.csv')
ARCHIVO_CALIFICACIONES = os.path.join(BASE, 'calificaciones.csv')

HOST = 'localhost'
PORT = 12345
NRC_SERVER_HOST = 'localhost'
NRC_SERVER_PORT = 12346
CLIENT_TIMEOUT = 30
MAX_RECV = 4096

CSV_LOCK = threading.Lock()

AGREGAR_ESTUDIANTE = "AGREGAR_ESTUDIANTE"
AGREGAR = "AGREGAR"
BUSCAR = "BUSCAR"
ACTUALIZAR = "ACTUALIZAR"
LISTAR = "LISTAR"
ELIMINAR = "ELIMINAR"

# ---------------- Inicialización ---------------- #
def inicializar_csvs():
    if not os.path.exists(ARCHIVO_ESTUDIANTES):
        with open(ARCHIVO_ESTUDIANTES, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre'])
        print("Archivo estudiantes.csv creado")

    if not os.path.exists(ARCHIVO_CALIFICACIONES):
        with open(ARCHIVO_CALIFICACIONES, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Materia', 'Calificación'])
        print("Archivo calificaciones.csv creado")

# ---------------- Funciones NRC ---------------- #
def consultar_nrc(nrc):
    """Consulta al servidor de NRCs si el NRC existe."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((NRC_SERVER_HOST, NRC_SERVER_PORT))
            comando = f"BUSCAR_NRC|{nrc.strip().upper()}"
            s.sendall(comando.encode('utf-8'))
            resp = s.recv(4096).decode('utf-8')
            print(f"[DEBUG] Respuesta NRC: {resp}")  # Log de depuración
            return json.loads(resp)
    except socket.timeout:
        return {"status": "error", "mensaje": "Tiempo de espera agotado al contactar servidor NRC"}
    except ConnectionRefusedError:
        return {"status": "error", "mensaje": "Servidor NRC no disponible (conexión rechazada)"}
    except json.JSONDecodeError as e:
        return {"status": "error", "mensaje": f"Respuesta inválida del servidor NRC: {e}"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error consultando NRC: {e}"}

# ---------------- Funciones Estudiantes ---------------- #
def agregar_estudiante(id_est, nombre):
    with CSV_LOCK:
        if os.path.exists(ARCHIVO_ESTUDIANTES):
            with open(ARCHIVO_ESTUDIANTES, 'r', newline='') as f:
                for row in csv.DictReader(f):
                    if row['ID_Estudiante'] == id_est:
                        return {"status": "error", "mensaje": "Estudiante ya registrado"}
        with open(ARCHIVO_ESTUDIANTES, 'a', newline='') as f:
            csv.writer(f).writerow([id_est, nombre])
    return {"status": "ok", "mensaje": f"Estudiante {nombre} registrado correctamente"}

def estudiante_existe(id_est):
    if not os.path.exists(ARCHIVO_ESTUDIANTES):
        return False
    with CSV_LOCK:
        with open(ARCHIVO_ESTUDIANTES, 'r', newline='') as f:
            for row in csv.DictReader(f):
                if row['ID_Estudiante'] == id_est:
                    return True
    return False

# ---------------- Calificaciones ---------------- #
def agregar_calificacion(id_est, materia, calif):
    if not estudiante_existe(id_est):
        return {"status": "error", "mensaje": "Estudiante no registrado"}

    res_nrc = consultar_nrc(materia)
    if res_nrc.get("status") != "ok":
        return {"status": "error", "mensaje": res_nrc.get("mensaje", "NRC no válido")}

    try:
        calif_float = float(calif)
        if not (0 <= calif_float <= 20):
            return {"status": "error", "mensaje": "Calificación fuera de rango (0–20)"}
    except ValueError:
        return {"status": "error", "mensaje": "Calificación no numérica"}

    with CSV_LOCK:
        with open(ARCHIVO_CALIFICACIONES, 'a', newline='') as f:
            csv.writer(f).writerow([id_est, materia.upper(), calif_float])

    return {"status": "ok", "mensaje": f"Calificación agregada para {id_est}"}

def buscar_por_id(id_est):
    if not estudiante_existe(id_est):
        return {"status": "error", "mensaje": "Estudiante no registrado"}
    with CSV_LOCK:
        if not os.path.exists(ARCHIVO_CALIFICACIONES):
            return {"status": "ok", "data": []}
        with open(ARCHIVO_CALIFICACIONES, 'r', newline='') as f:
            data = [r for r in csv.DictReader(f) if r['ID_Estudiante'] == id_est]
    return {"status": "ok", "data": data}

def listar_todas():
    with CSV_LOCK:
        if not os.path.exists(ARCHIVO_CALIFICACIONES):
            return {"status": "ok", "data": []}
        with open(ARCHIVO_CALIFICACIONES, 'r', newline='') as f:
            return {"status": "ok", "data": list(csv.DictReader(f))}

# ---------------- Servidor con hilos ---------------- #
def procesar_comando(cmd):
    p = cmd.strip().split('|')
    op = p[0]
    if op == AGREGAR_ESTUDIANTE and len(p) == 3:
        return agregar_estudiante(p[1], p[2])
    elif op == AGREGAR and len(p) == 4:
        return agregar_calificacion(p[1], p[2], p[3])
    elif op == BUSCAR and len(p) == 2:
        return buscar_por_id(p[1])
    elif op == LISTAR:
        return listar_todas()
    else:
        return {"status": "error", "mensaje": "Comando inválido"}

def manejar_cliente(sock, addr):
    sock.settimeout(CLIENT_TIMEOUT)
    hilo = threading.current_thread().name
    try:
        data = sock.recv(MAX_RECV).decode('utf-8')
        if not data:
            return
        print(f"[{hilo}] Comando recibido: {data}")
        res = procesar_comando(data)
        sock.sendall(json.dumps(res).encode('utf-8'))
    except Exception as e:
        print(f"[{hilo}] Error: {e}")
    finally:
        sock.close()
        print(f"[{hilo}] Conexión con {addr} cerrada")

def main():
    inicializar_csvs()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(10)
    print(f"Servidor concurrente activo en {HOST}:{PORT}")
    try:
        while True:
            cli, addr = s.accept()
            threading.Thread(target=manejar_cliente, args=(cli, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        s.close()

if __name__ == "__main__":
    main()
