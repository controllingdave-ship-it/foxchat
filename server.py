import socket
import threading

CHAT_PORT = 5000

online_users = []
clients = {}

def broadcast_user_list():
    data = f"USERLIST|{','.join(online_users)}"
    for client in clients.values():
        try:
            client.send(data.encode())
        except:
            pass

def handle_client(client, username):
    global online_users, clients

    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break

            if data.startswith("MSG|"):
                # Relay message to target
                parts = data.split("|", 4)
                if len(parts) == 5:
                    _, msg_id, sender, target, msg = parts
                else:
                    _, sender, target, msg = data.split("|", 3)
                    msg_id = None

                if target in clients:
                    clients[target].send(data.encode())

            elif data.startswith("TYPING|"):
                _, sender, target, is_typing = data.split("|", 3)
                if target in clients:
                    clients[target].send(data.encode())

        except:
            break

    # Remove user on disconnect
    try:
        client.close()
    except:
        pass

    if username in online_users:
        online_users.remove(username)
    if username in clients:
        del clients[username]

    broadcast_user_list()

def run_server():
    global online_users, clients

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", CHAT_PORT))
    server_socket.listen(5)

    print(f"Server running on port {CHAT_PORT}")

    while True:
        client, _ = server_socket.accept()
        username = client.recv(1024).decode()

        clients[username] = client
        if username not in online_users:
            online_users.append(username)

        broadcast_user_list()

        threading.Thread(target=handle_client, args=(client, username), daemon=True).start()

if __name__ == "__main__":
    run_server()
