import os
from flask import Flask, send_from_directory
from sdk.conf_sdk import conf_bp
from sdk.down_sdk import down_bp
from sdk.clear_zip_sdk import conf_clear_zip
from sdk.change_sdk import conf_change
from sdk.gen_sdk import gen_cvat
from flask_cors import CORS

app = Flask(__name__, static_folder='dist', static_url_path='')

CORS(app)  # 允许所有域名的请求

# 注册子接口
app.register_blueprint(conf_bp)
app.register_blueprint(down_bp)
app.register_blueprint(conf_clear_zip)
app.register_blueprint(conf_change)
app.register_blueprint(gen_cvat)

# 添加路由来提供静态文件
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'dist'), 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
