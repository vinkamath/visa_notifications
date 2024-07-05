from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

logger = logging.getLogger(__name__)

# Health check HTTP server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        logger.debug("Responded to health check with 200")

def run_health_check_server(port):
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f'Starting health check server on port {port}')
    server.serve_forever()

