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
    contract_address = '0xC1C062DEdC0F90E3759a65207E741c5CAd6f98F2'
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
