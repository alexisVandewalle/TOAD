import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app)
from werkzeug.security import check_password_hash, generate_password_hash

from webapp.db import get_db
from webapp.auth import login_required

from webapp.blockchainClient import Client
from werkzeug.utils import secure_filename

bp = Blueprint('toad', __name__, url_prefix='/')

@bp.route('/')
def index():
    """
    Show info about user and received messages.
    """
    db = get_db()
    messages = db.execute("""
    select encrypted_file.*, count(share.round) as "nb_shares"
    from encrypted_file
    left join share on share.round=encrypted_file.id
    group by encrypted_file.id
    """).fetchall()
    return render_template('toad/index.html', messages=messages)

@bp.route('/group_creation/', methods=['GET', 'POST'])
@login_required
def group_creation():
    db = get_db()
    accounts = db.execute(
        "SELECT account_address FROM eth_public_key"
    ).fetchall()
    accounts = [row['account_address'] for row in accounts]

    if request.method == 'POST':
        selected_accounts = request.form.getlist('accounts')
        try:
            g.client.group_creation(selected_accounts)
        except ValueError:
            flash('The group has already been created, you cannot create a group anymore')
    return render_template('toad/group_creation.html', accounts=accounts)

@bp.route('/send_file/', methods=['GET','POST'])
@login_required
def send_file():
    """
    Contain a form to send encrypted files and send encrypted files calling
    :meth:`webapp.Client.Client.send_msg` if the user has uploaded a file
    and clicked on browse.
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_to_encrypt = file.read()
            # TODO encryption of file
            g.client.send_file(file_to_encrypt)

        else:
            flash('File extension is not valid')

    return render_template('toad/send_file.html')

@bp.route('/list_of_shares/')
def shares_list():
    """
    Show a list of all valid shares received.
    """
    db = get_db()
    shares = db.execute("""
    SELECT share.file_id, share.ui
    FROM share
    """).fetchall()
    return render_template("toad/shares.html", shares=shares)

@bp.before_request
def blockchain_connect():
    """
    warning:
        This function is called before each request

    Connect the current user to the blockchain, retrieve informations
    about ETHDKG contracts. Send the group key of the user if it is
    associated with a group secret key and if it is his first connection
    calling :meth:`webapp.Client.Client.register`.

    finally call update_db the database (see :meth:`webapp.auth.update_db`).
    """
    contract_address = '0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    port = '8545'
    g.client = Client(contract_address, port)
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        g.client.login(g.user['private_key'], g.user['account_address'])


def allowed_file(filename):
    """
    Check if a file have an allowed extension. The allowed extension are
    ('txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','py').
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']