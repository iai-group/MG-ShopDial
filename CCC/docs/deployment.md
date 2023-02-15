# Deployment

This Flask application cannot be deployed with mod_wsgi/Apache because of flask-socketio package see [here](https://github.com/miguelgrinberg/Flask-SocketIO/issues/1207).

## Nginx deployment

Nginx is used as a front-end reverse proxy.  
*Note*: to support Websocket protocol use nginx 1.4 or newer.

1. Write nginx configuration at `/etc/nginx/sites-available/www.example.org`. And example of a minimal configuration can be found [here](https://flask-socketio.readthedocs.io/en/latest/deployment.html#using-nginx-as-a-websocket-reverse-proxy).
2. Enable site: `ln -s /etc/nginx/sites-available/www.example.org /etc/nginx/sites-enabled/`
3. Restart nginx: `sudo /etc/init.d/nginx stop`
4. Set up Flask application to handle proxy reverse in [main](../ccc/main.py). More information [here](https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/).
```
from werkzeug.middleware.proxy_fix import ProxyFix

# For 1 proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
```
5. Start Flask application locally: `$ gunicorn --worker-class eventlet -w 1 ccc.main:app`