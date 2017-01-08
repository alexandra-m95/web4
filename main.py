from wsgiref.simple_server import make_server
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from jinja2.exceptions import TemplateNotFound


class WSGIMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        response_body_bytes = self.app(environ, start_response)
        response_body = " ".join(bytes.decode(x) for x in response_body_bytes)
        body_start_ind = response_body.find("<body>")
        response_body = response_body[:body_start_ind + 6] + "<div class='top'>Middleware TOP</div>" + \
                        response_body[body_start_ind + 6:]
        body_end_ind = response_body.find("</body>")
        response_body = response_body[:body_end_ind] + "<div class='botton'>Middleware BOTTOM</div>" +\
                        response_body[body_end_ind:]
        return [response_body.encode('utf-8')]


class WSGIApp:
    def __init__(self, templates_dir, resourses_files_matches):
        self.env = Environment()
        self.env.loader = FileSystemLoader(templates_dir)
        self.resourses_files_matches = resourses_files_matches

    def __call__(self, environ, start_response):
        headers = []
        response_body = ''
        if environ["REQUEST_METHOD"] != "GET":
            status = "501 Not Implemented"
            headers.append(("Content-Type", "text/plain"))
        else:
            resourse_addr = self.resourses_files_matches[environ["PATH_INFO"][1:]]
            try:
                tmpl = self.env.get_template(resourse_addr)
                response_body = tmpl.render()
                status = "200 OK"
            except TemplateNotFound:
                status = "404 Not Found"
                tmpl = self.env.get_template("404.jinja2")
                response_body = tmpl.render()
            headers.append(("Content-Type", "text/html;charset=utf-8"))
            headers.append(("Content-Language", "en"))
            headers.append(("Content-Length", str(len(response_body))))
        start_response(status, headers)
        return [response_body.encode('utf-8')]


if __name__ == "__main__":
    resourses_files_matches = {}
    resourses_files_matches[""] = "index.jinja2"
    resourses_files_matches["index.html"] = "index.jinja2"
    resourses_files_matches["about/aboutme.html"] = "about/aboutme.jinja2"
    wsgi_app = WSGIApp('templates', resourses_files_matches)
    wsgi_middleware = WSGIMiddleware(wsgi_app)
    wsgi_server = make_server('', 8000, wsgi_middleware)
    wsgi_server.serve_forever()

