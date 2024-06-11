
#client
import socket
import ssl

HOST = "ENTER IP ADDR"
PORT = 5555

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Load SSL context without server certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Wrap the socket with SSL
ssl_socket = ssl_context.wrap_socket(client_socket, server_hostname=HOST)

try:
    # Connect to the server
    ssl_socket.connect((HOST, PORT))
    print()
    print("--------------------------------")
    print("Welcome to Customer Management Project using socket programming")
    print("List of available items: ")
    data = ssl_socket.recv(1024)
    print(data.decode())

    while True:
        choice = input("\n1. Purchase\n2. Read the data\n3. Generate Bill\n4. Exit\nEnter your choice: ")

        try:
            choice = int(choice)
            ssl_socket.sendall(str(choice).encode())
        except ValueError:
            print("Invalid choice. Please enter a valid number.")
            continue

        if choice == 1:
            # Getting item serial number & quantity and sending to the server
            try:
                item_no = input("Enter serial number of item: ")
                item_no_to_send = int(item_no).to_bytes(4, byteorder='big')
                ssl_socket.sendall(item_no_to_send)

                availsr = int(ssl_socket.recv(1024).decode())
                item = int(item_no)

                if item >= availsr or item < 0:
                    leave = ssl_socket.recv(1024)
                    print(leave.decode())
                    break

                qty = input("Enter quantity of item to be purchased: ")
                try:
                    qty = int(qty)
                    qty_to_send = qty.to_bytes(4, byteorder='big')
                    ssl_socket.sendall(qty_to_send)

                    availqty = int(ssl_socket.recv(1024).decode())

                    if availqty < qty or qty==0:
                        leave = ssl_socket.recv(1024)
                        print(leave.decode())
                        break
                    
                    else:
                        # Receiving bill amount from the server
                        data = ssl_socket.recv(1024)
                        if "Invalid Quantity" in data.decode():
                            print(data.decode())
                        else:
                            print("Amount: Rs.", data.decode())

                except ValueError:
                    print("Invalid input. Exiting Client ...")
                    break

            except ValueError:
                print("Invalid Input. Exiting Client ...")
                break

        elif choice == 2:
            print("List of available items: ")
            df = ssl_socket.recv(1024)
            print(df.decode())

        elif choice == 3:
            bill = ssl_socket.recv(1024)
            print("Total bill is Rs.", bill.decode())

        elif choice == 4:
            # Receive server's message and print before exiting
            exit_message = ssl_socket.recv(1024)
            print(exit_message.decode())
            break

        else:
            mess = ssl_socket.recv(1024)
            print(mess.decode())

except ssl.SSLError as e:
    print(f"SSL Error: {e}")
except socket.error as e:
    print(f"Socket Error: {e}")
except Exception as e:
    print(f"Error: {e}")

finally:
    ssl_socket.close()
