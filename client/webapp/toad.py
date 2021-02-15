import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from webapp.db import get_db
from webapp.auth import login_required

from webapp.blockchainClient import Client

bp = Blueprint('toad', __name__, url_prefix='/')

@bp.route('/')
def index():
    
    return render_template('toad/index.html')

@bp.route('/group_creation/')
@login_required
def group_creation():
    return render_template('toad/group_creation.html')

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
    contract_address = '0xB21d06B32Db32c4756f67F172DcC13062F670544'
    port = '9545'
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