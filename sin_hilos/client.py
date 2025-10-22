import socket
import json

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n--- Menú del Sistema de Calificaciones ---")
    print("0. Registrar estudiante")
    print("1. Agregar calificación")
    print("2. Buscar calificaciones por ID")
    print("3. Actualizar calificación")
    print("4. Listar todas las calificaciones")
    print("5. Eliminar calificaciones por ID")
    print("6. Salir")
    return input("Elija opción: ")

def enviar_comando(comando):
    """Envía un comando al servidor y recibe la respuesta"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))
        client_socket.send(comando.encode('utf-8'))
        respuesta = client_socket.recv(4096).decode('utf-8')
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

            if opcion == '0':
                # Registrar estudiante
                id_est = input("ID del estudiante: ")
                nombre = input("Nombre: ")
                res = enviar_comando(f"AGREGAR_ESTUDIANTE|{id_est}|{nombre}")
                print(res['mensaje'])

            elif opcion == '1':
                # Agregar calificación (sin nombre)
                id_est = input("ID del estudiante: ")
                materia = input("Materia: ")
                calif = input("Calificación: ")
                res = enviar_comando(f"AGREGAR|{id_est}|{materia}|{calif}")
                print(res['mensaje'])

            elif opcion == '2':
                # Buscar calificaciones de un estudiante
                id_est = input("ID: ")
                res = enviar_comando(f"BUSCAR|{id_est}")
                if res['status'] == 'ok':
                    print("\n--- Calificaciones ---")
                    for row in res['data']:
                        print(f"Materia: {row['Materia']}, Calificación: {row['Calificación']}")
                else:
                    print(res['mensaje'])

            elif opcion == '3':
                # Actualizar calificación
                id_est = input("ID del estudiante: ")
                materia = input("Materia a actualizar: ")
                nueva = input("Nueva calificación: ")
                res = enviar_comando(f"ACTUALIZAR|{id_est}|{materia}|{nueva}")
                print(res['mensaje'])

            elif opcion == '4':
                # Listar todas las calificaciones
                res = enviar_comando("LISTAR")
                if res['status'] == 'ok':
                    if res['data']:
                        print("\n--- Todas las Calificaciones ---")
                        for row in res['data']:
                            print(f"ID: {row['ID_Estudiante']}, Materia: {row['Materia']}, Calificación: {row['Calificación']}")
                    else:
                        print("No hay calificaciones registradas")
                else:
                    print(res['mensaje'])

            elif opcion == '5':
                # Eliminar todas las calificaciones de un estudiante
                id_est = input("ID del estudiante: ")
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