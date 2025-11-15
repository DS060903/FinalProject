"""Authentication endpoints.

IMPORTANT: Use DAL functions only. No direct DB queries.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
import bcrypt

from ..data_access.dal import create_user, get_user_by_email
from ..models.user import UserRole

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role_str = request.form.get('role', 'student').strip().lower()
        
        # Map role string to enum
        role_map = {
            'student': UserRole.STUDENT,
            'staff': UserRole.STAFF,
            'admin': UserRole.ADMIN
        }
        role = role_map.get(role_str, UserRole.STUDENT)
        
        try:
            user = create_user(email, password, role)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
        
        return render_template('auth/register.html', email=email)
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user."""
    if request.method == 'POST':
        # Rate limiting: 5 attempts per minute per IP
        from ..services.rate_limit import allow
        rate_limit_key = f"{request.remote_addr}:login"
        if not allow(rate_limit_key, 5, 60):
            flash("Too many attempts. Please wait a minute and try again.", "warning")
            return redirect(url_for("auth.login"))
        
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = get_user_by_email(email)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user, remember=True)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('resources.list_resources'))
        else:
            flash('Invalid email or password.', 'error')
        
        return render_template('auth/login.html', email=email)
    
    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('resources.list_resources'))


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """Get current user info (JSON)."""
    return jsonify({
        'email': current_user.email,
        'role': current_user.role.value
    }), 200

