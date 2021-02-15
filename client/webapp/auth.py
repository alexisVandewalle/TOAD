import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from webapp.db import get_db

from eth_keys import keys
from eth_utils.exceptions import ValidationError

from webapp.Crypto_utils import compute_public_key

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register the private key and account address of
    an ethereum account in the database.

    Returns:
        The template of register.html if the form is empty
        and redirect to login page else.
    """
    if request.method == 'POST':
        username = request.form['username']
        private_key = request.form['private_key']
        account_address = request.form['account_address']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not private_key:
            error = 'Private key is required.'
        elif not account_address:
            error = 'Account address is required'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        else:
            try:
                pk = keys.PrivateKey(bytearray.fromhex(private_key[2:]))
                if pk.public_key.to_checksum_address() != account_address:
                    error = 'The couple account address and private key is wrong'
            except (ValidationError,ValueError):
                error = "Invalid private key"


        if error is None:
            db.execute(
                'INSERT INTO user (username, private_key, account_address) VALUES (?, ?, ?)',
                (username, private_key, account_address)
            )
            pk_x, pk_y = compute_public_key(private_key)
            db.execute(
                "INSERT INTO eth_public_key (account_address, pk_x, pk_y) VALUES (?,?,?)",
                [account_address, hex(pk_x), hex(pk_y)]
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Login a user in the webapp.

    Returns:
        The page index if login succeed and the login page else
    """
    if request.method == 'POST':
        username = request.form['username']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('toad.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('toad.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
