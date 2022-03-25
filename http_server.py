import http.server             
import socketserver

PORT = 8000                               
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Servidor HTTP en el puerto 8000")
    httpd.serve_forever()
