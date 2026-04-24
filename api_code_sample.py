import json
import os
from http.server import BaseHTTPRequestHandler

# Define the handler class for Vercel's Python runtime
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse the URL to determine which endpoint is being requested
        if self.path == '/api/course':
            self.handle_course_endpoint()
        elif self.path == '/api/chapters':
            self.handle_chapters_endpoint()
        else:
            self.send_error(404, 'Endpoint not found')

    def handle_course_endpoint(self):
        """Return the main course metadata from content.json"""
        try:
            # Read the content.json file
            with open('content.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        except FileNotFoundError:
            self.send_error(500, 'content.json file not found')
        except json.JSONDecodeError:
            self.send_error(500, 'Invalid JSON in content.json')
        except Exception as e:
            self.send_error(500, f'Internal server error: {str(e)}')

    def handle_chapters_endpoint(self):
        """Return the navigation index from chapters_index.json"""
        try:
            # Read the chapters_index.json file
            with open('chapters_index.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        except FileNotFoundError:
            self.send_error(500, 'chapters_index.json file not found')
        except json.JSONDecodeError:
            self.send_error(500, 'Invalid JSON in chapters_index.json')
        except Exception as e:
            self.send_error(500, f'Internal server error: {str(e)}')