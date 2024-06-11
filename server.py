#server
import socket
import ssl
import pandas as pd
import threading

TCP_SERVER_HOST = 'ENTER IP ADDR'
TCP_SERVER_PORT = 5555
CERTFILE = 'cert.pem'
KEYFILE = 'key.pem'

def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TCP_SERVER_HOST, TCP_SERVER_PORT))
    server_socket.listen(2)

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    print("TCP Server is listening for connections...")

    while True:
        connection, address = server_socket.accept()
        print("TCP Connection from:", address)
        connection = ssl_context.wrap_socket(connection, server_side=True)

        # Handle the client connection in a separate thread
        threading.Thread(target=handle_client, args=(connection,)).start()

def handle_client(conn):
    tot = 0  # Initialize the total variable

    print("Handling client connection...")

    with conn:
        # Read the DataFrame from CSV file
        df = pd.read_csv('data.csv')

        # Convert the DataFrame to a string and send it
        df_str = str(df)
        conn.sendall(df_str.encode())

        while True:
            k = conn.recv(1024)
            ch = k.decode()

            if ch == '1':
                df = pd.read_csv('data.csv')

                # Receive item number from the client
                try:
                    item = conn.recv(1024)
                    item = int.from_bytes(item, byteorder='big')
                    print("Item:", item)

                    # Send the length of the DataFrame
                    availsr = len(df)
                    conn.sendall(str(availsr).encode())

                    if 0 <= item < availsr:
                        # Receive item quantity from the client
                        try:
                            qty = conn.recv(1024)
                            qty = int.from_bytes(qty, byteorder='big')
                            print("Quantity:", qty)

                            availqty = df.loc[item, 'Qty']
                            conn.sendall(str(availqty).encode())

                            if 1 <= qty <= availqty:
                                df.loc[item, 'Qty'] -= qty
                                df.to_csv('data.csv', index=False)

                                bill = df.loc[item, 'Cost'] * qty
                                print("BILL: Rs.", bill)
                                tot += bill  # Update the total

                                # Send the bill as a string
                                sendbill = str(bill)
                                conn.sendall(sendbill.encode())

                            elif qty==0:
                                conn.sendall("Error ... Zero Qty entered.".encode())
                            else:
                                conn.sendall("Error ... Qty asked not available".encode())

                        except ValueError:
                            break

                    else:
                        conn.sendall("SlNo entered is invalid.".encode())

                except ValueError:
                    break

            elif ch == '2':
                df = pd.read_csv('data.csv')

                # Convert the updated DataFrame to a string and send it
                df_str = str(df)
                conn.sendall(df_str.encode())

            elif ch == '3':
                tot_str = str(tot)
                conn.sendall(tot_str.encode())

            elif ch == '4':
                print("Exit Requested. Sending message to the client.")
                conn.sendall("Exiting Client ... ".encode())
                break

            else:
                print("Wrong Choice. Sending message to the client.")
                conn.sendall("Invalid Choice".encode())

# Uncomment the following line to run the server
tcp_server()