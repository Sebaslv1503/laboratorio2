import socket
import csv
import json
import os

ARCHIVO_NRC = 'nrcs.csv'
PUERTO = 12346
HOST = 'localhost'

def inicializar_nrcs():
    """Inicializa el archivo CSV de NRCs si no existe"""
    if not os.path.exists(ARCHIVO_NRC):
        with open(ARCHIVO_NRC, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['NRC', 'Materia'])
            nrcs_ejemplo = [
                ['MAT101', 'Matemáticas Básicas'],
                ['FIS101', 'Física General'],
                ['QUI101', 'Química General'],
                ['PRO101', 'Programación I'],
                ['BDD101', 'Bases de Datos']
            ]
            writer.writerows(nrcs_ejemplo)
        print("Archivo nrcs.csv creado con datos de ejemplo")

def buscar_nrc(nrc):
    """Busca un NRC en el archivo CSV"""
    try:
        with open(ARCHIVO_NRC, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['NRC'].strip().upper() == nrc.strip().upper():
                    return {"status": "ok", "data": row}
        return {"status": "not_found", "mensaje": "NRC no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_nrcs():
    """Lista todos los NRCs disponibles"""
    try:
        with open(ARCHIVO_NRC, 'r', newline='') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0].strip()
    
    if op == 'BUSCAR_NRC' and len(partes) == 2:
        return buscar_nrc(partes[1])
    elif op == 'LISTAR_NRC':
        return listar_nrcs()
    else:
        return {"status": "error", "mensaje": "Comando inválido"}

def main():
    inicializar_nrcs()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PUERTO))
    server_socket.listen(5)
    print(f"Servidor de NRCs escuchando en {HOST}:{PUERTO}...")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Conexión aceptada desde {addr}")
            try:
                data = client_socket.recv(1024).decode('utf-8').strip()
                if data:
                    print(f"Comando recibido: {data}")
                    respuesta = procesar_comando(data)
                    client_socket.sendall(json.dumps(respuesta).encode('utf-8'))
            except Exception as e:
                print(f"Error en comunicación: {e}")
            finally:
                client_socket.close()
                print(f"Conexión con {addr} cerrada")
    except KeyboardInterrupt:
        print("\nServidor de NRCs detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
