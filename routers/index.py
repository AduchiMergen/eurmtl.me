import uuid
from flask import Blueprint, send_file

blueprint = Blueprint('index', __name__)


@blueprint.route('/')
def cmd_index():
    text = 'This is a technical domain montelibero.org. ' \
           'You can get more information on the website <a href="https://montelibero.org">montelibero.org</a> ' \
           'or in telegram <a href="https://t.me/Montelibero_org">Montelibero_org</a>' \
           '<br><br><br>' \
           'Это технический домен montelibero.org. ' \
           'Больше информации вы можете получить на сайте <a href="https://montelibero.org">montelibero.org</a> ' \
           'или в телеграм <a href="https://t.me/Montelibero_ru">Montelibero_ru</a>'
    return text


@blueprint.route('/mytest', methods=('GET', 'POST'))
def cmd_mytest():
    return '''
    <body>
        <script async src="https://telegram.org/js/telegram-widget.js?21" 
            data-telegram-login="MyMTLWalletBot" 
            data-size="small" 
            data-auth-url="https://eurmtl.me/login/telegram" 
            data-request-access="write">
        </script>
    </body>    
    '''


@blueprint.route('/uuid', methods=('GET', 'POST'))
def cmd_uuid():
    return uuid.uuid4().hex


@blueprint.route('/err', methods=('GET', 'POST'))
def cmd_send_err():
    debug = True
    if debug:
        file_name = '/home/c/cb61047/eurmtl.me/error_log'
        import os
        if os.path.isfile(file_name):
            return send_file(file_name, mimetype='text/plain')
            # with open(file_name, "r") as f:
            #    text = f.read()
        else:
            return "No error"
    else:
        return "need authority"
