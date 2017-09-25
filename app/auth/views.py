# app/auth/views.py

from flask import render_template, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, RestorePasswordForm, ForgotPasswordForm
from app import db
from ..email import send_email

######################################
# Functionality for restore password #
######################################

# send generated token to user, in case if
# user with current email is exist
# and then, hold user email in session object
# for further handling
@auth.route('/restore', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # User is exist.
        if user is not None:
            # Generate token for current user.
            token = user.generate_restore_token()
            # Send mail to user with restore token link.
            send_email(user.email,
                        'Restore Your account password',
                        'auth/email/restore',
                        user=user, token=token)
            # Hold user email in session.
            session['email'] = user.email
            flash('A new restore password token has been sent to you by email.')
            return redirect(url_for('main.index'))
    return render_template('auth/forgotpassword.html', form=form)

# restoring user password in case if
# received token is valid for current user
# and if its's true provide form for restore password
@auth.route('/restore/<token>', methods=['GET', 'POST'])
def restore(token):
    # Get current user.
    user = User.query.filter_by(email=session.get('email')).first()
    if user is not None:
        # Token is valid.
        if user.restore(token):
            form = RestorePasswordForm()
            if form.validate_on_submit():
                user.password = form.password.data
                db.session.add(user)
                db.session.commit()
                flash('You have restored access to your account.')
                return redirect(url_for('auth.login'))
            return render_template('auth/restore.html', form=form)
        else:
            flash('The restoring link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,
                'Confirm Your account',
                'auth/email/confirm',
                user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        # ping logged-in user
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', \
                    'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # User exist and password is valid.
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
