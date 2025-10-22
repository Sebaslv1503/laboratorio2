import socket
import json

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n--- Menú de Calificaciones ---")
    print("1. Agregar calificación")
    print("2. Buscar por ID")
    print("3. Actualizar calificación")
    print("4. Listar todas")
    print("5. Eliminar por ID")
    print("6. Salir")
    return input("Elija opción: ")

def enviar_comando(comando):
    """Envía un comando al servidor y recibe la respuesta"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))
        client_socket.send(comando.encode('utf-8'))
        respuesta = client_socket.recv(1024).decode('utf-8')
        client_socket.close()
        return json.loads(respuesta)
    except Exception as e:
        return {"status": "error", "mensaje": f"Error de conexión: {str(e)}"}

def main():
    """Función principal del cliente"""
    print("Cliente del Sistema de Calificaciones")
    print("Conectando al servidor...")
    
    while True:
        try:
            opcion = mostrar_menu()
            
            if opcion == '1':
                id_est = input("ID: ")
                nombre = input("Nombre: ")
                materia = input("Materia: ")
                calif = input("Calificación: ")
                res = enviar_comando(f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}")
                print(res['mensaje'])
                
            elif opcion == '2':
                id_est = input("ID: ")
                res = enviar_comando(f"BUSCAR|{id_est}")
                if res['status'] == 'ok':
                    data = res['data']
                    print(f"Nombre: {data['Nombre']}, Materia: {data['Materia']}, Calificación: {data['Calificación']}")
                else:
                    print(res['mensaje'])
                    
            elif opcion == '3':
                id_est = input("ID: ")
                nueva_calif = input("Nueva calificación: ")
                res = enviar_comando(f"ACTUALIZAR|{id_est}|{nueva_calif}")
                print(res['mensaje'])
                
            elif opcion == '4':
                res = enviar_comando("LISTAR")
                if res['status'] == 'ok':
                    if res['data']:
                        print("\n--- Todas las Calificaciones ---")
                        for row in res['data']:
                            print(f"ID: {row['ID_Estudiante']}, Nombre: {row['Nombre']}, Materia: {row['Materia']}, Calificación: {row['Calificación']}")
                    else:
                        print("No hay calificaciones registradas")
                else:
                    print(res['mensaje'])
                    
            elif opcion == '5':
                id_est = input("ID: ")
                res = enviar_comando(f"ELIMINAR|{id_est}")
                print(res['mensaje'])
                
            elif opcion == '6':
                print("Saliendo...")
                break
                
            else:
                print("Opción inválida")
                
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()