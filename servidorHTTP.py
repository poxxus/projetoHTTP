#implementação de um servidor base para interpratação de métodos HTTP

import socket

#definindo o endereço IP do host
SERVER_HOST = ""
#definindo o número da porta em que o servidor irá escutar pelas requisições HTTP
SERVER_PORT = 80

#vamos criar o socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#vamos setar a opção de reutilizar sockets já abertos
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#atrela o socket ao endereço da máquina e ao número de porta definido
server_socket.bind((SERVER_HOST, SERVER_PORT))

#coloca o socket para escutar por conexões
server_socket.listen(1)

#mensagem inicial do servidor
print("Servidor em execução...")
print("Escutando por conexões na porta %s" % SERVER_PORT)

#cria o while que irá receber as conexões
while True:
    #espera por conexões
    client_connection, client_address = server_socket.accept()
    client_connection.settimeout(0.5)

    #pega a solicitação do cliente (pode ser enviada em vários segmentos TCP)
    request_data = b""
    while True:
        try:
            chunk = client_connection.recv(4096)
            if not chunk:
                break
            request_data += chunk
        except socket.timeout:
            break

    #verifica se a request possui algum conteúdo
    if request_data:
        try:
            #separa cabecalho do corpo para suportar dados binários no post
            parts = request_data.split(b"\r\n\r\n", 1)
            headers_part = parts[0].decode("utf-8", errors="replace")
            body_part = parts[1] if len(parts) > 1 else b""
            
            #analisa a solicitação HTTP
            headers = headers_part.split("\n")
            #imprime a primeira linha da requisição
            print(headers[0].strip())
            
            request_line = headers[0].strip().split()
            if len(request_line) >= 2:
                method = request_line[0]
                filename = request_line[1]

                #verifica qual arquivo está sendo solicitado
                if filename == "/":
                    filename = "/index.html"

                #utiliza o diretório raiz atual
                filepath = "." + filename

                if method == "GET":
                    #try e except para tratamento de erro quando um arquivo solicitado não existir
                    try:
                        #abrir o arquivo em modo binário (para suportar imagens) e enviar para o cliente
                        fin = open(filepath, "rb")
                        content = fin.read()
                        fin.close()
                        #envia a resposta
                        response_header = b"HTTP/1.1 200 OK\r\n\r\n"
                        client_connection.sendall(response_header + content)
                    except FileNotFoundError:
                        #caso o arquivo solicitado não exista no servidor, gera uma resposta de erro
                        response = b"HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>ERROR 404!<br>File Not Found!</h1>"
                        client_connection.sendall(response)
                        
                elif method == "POST":
                    try:
                        #criar e armazenar o recurso a partir dos dados da solicitação
                        fout = open(filepath, "wb")
                        fout.write(body_part)
                        fout.close()
                        response = b"HTTP/1.1 200 OK\r\n\r\n<h1>Salvo com sucesso!</h1><a href='/'>Voltar</a>"
                        client_connection.sendall(response)
                    except Exception as e:
                        response = b"HTTP/1.1 500 INTERNAL SERVER ERROR\r\n\r\n<h1>Erro Interno</h1>"
                        client_connection.sendall(response)

        except Exception as e:
            print("Erro ao processar:", e)

    client_connection.close()

server_socket.close()


