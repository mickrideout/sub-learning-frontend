"""Authentication routes and endpoints."""
from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import (
    RegistrationForm, LoginForm, PasswordResetRequestForm, PasswordResetForm
)
from app.services.auth_service import AuthService, AuthenticationError
from app.services.oauth_service import OAuthService


def user_needs_language_selection(user):
    """Check if user needs to complete language selection."""
    return not user.native_language_id or not user.target_language_id


def get_redirect_after_auth(user):
    """Get the appropriate redirect URL after authentication based on user profile completion."""
    if user_needs_language_selection(user):
        return url_for('auth.language_selection')
    return url_for('auth.dashboard')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route with form handling and validation."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            AuthService.register_user(
                email=form.email.data,
                password=form.password.data
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except AuthenticationError as e:
            flash(str(e), 'error')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route with credential validation and session creation."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = AuthService.authenticate_user(
                email=form.email.data,
                password=form.password.data
            )
            login_user(user, remember=form.remember_me.data)

            # Redirect to next page if provided, otherwise check if language selection is needed
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(get_redirect_after_auth(user))

        except AuthenticationError as e:
            flash(str(e), 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route with session cleanup and redirect."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/password-reset-request', methods=['GET', 'POST'])
def password_reset_request():
    """Password reset request route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        try:
            # Generate password reset token (basic implementation)
            token = AuthService.generate_password_reset_token()

            # In a full implementation, we would:
            # 1. Store the token in database with expiration
            # 2. Send email with reset link containing the token
            # For now, we'll just flash a message with the token

            flash(f'Password reset instructions sent to {form.email.data}. '
                  f'Reset token: {token}', 'info')
            return redirect(url_for('auth.password_reset', token=token,
                                    email=form.email.data))

        except AuthenticationError as e:
            flash(str(e), 'error')

    return render_template('auth/password_reset_request.html', form=form)


@auth_bp.route('/password-reset')
def password_reset():
    """Password reset confirmation route."""
    token = request.args.get('token')
    email = request.args.get('email')

    if not token or not email:
        flash('Invalid password reset link.', 'error')
        return redirect(url_for('auth.login'))

    if not AuthService.validate_password_reset_token(token):
        flash('Invalid or expired password reset token.', 'error')
        return redirect(url_for('auth.login'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        try:
            AuthService.reset_password(email, form.password.data)
            flash('Your password has been reset successfully. '
                  'Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except AuthenticationError as e:
            flash(str(e), 'error')

    return render_template('auth/password_reset.html', form=form, email=email)


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile route displaying logged-in user information."""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """Basic dashboard route for authenticated users."""
    return render_template('auth/dashboard.html', user=current_user)


@auth_bp.route('/language-selection')
@login_required
def language_selection():
    """Language selection route for authenticated users to set native and target languages."""
    # If user has already completed language selection, redirect to dashboard
    if not user_needs_language_selection(current_user):
        return redirect(url_for('auth.dashboard'))
    
    return render_template('auth/language-selection.html', user=current_user)


# API endpoints for AJAX requests

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration."""
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Email and password are required',
                'code': 'MISSING_FIELDS'
            }), 400

        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            native_language_id=data.get('native_language_id'),
            target_language_id=data.get('target_language_id')
        )

        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201

    except AuthenticationError as e:
        return jsonify({
            'error': str(e),
            'code': 'REGISTRATION_FAILED'
        }), 400
    except Exception:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login."""
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Email and password are required',
                'code': 'MISSING_FIELDS'
            }), 400

        user = AuthService.authenticate_user(
            email=data['email'],
            password=data['password']
        )

        login_user(user, remember=data.get('remember_me', False))

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200

    except AuthenticationError as e:
        return jsonify({
            'error': str(e),
            'code': 'AUTHENTICATION_FAILED'
        }), 401
    except Exception:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for user logout."""
    logout_user()
    return jsonify({
        'message': 'Logout successful'
    }), 200


# OAuth routes

@auth_bp.route('/oauth/<provider>')
def oauth_login(provider):
    """
    Initiate OAuth login flow for the specified provider.
    
    Args:
        provider: OAuth provider (google, facebook, apple)
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    try:
        redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
        authorization_url, state = OAuthService.get_authorization_url(provider, redirect_uri)
        return redirect(authorization_url)
    
    except ValueError as e:
        flash(f'OAuth login failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash('OAuth service is temporarily unavailable. Please try email login.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/oauth/<provider>/callback', methods=['GET', 'POST'])
def oauth_callback(provider):
    """
    Handle OAuth callback from provider after user authorization.
    
    Args:
        provider: OAuth provider (google, facebook, apple)
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    try:
        # Get authorization code and state from callback
        code = request.args.get('code') or request.form.get('code')
        state = request.args.get('state') or request.form.get('state')
        error = request.args.get('error') or request.form.get('error')
        
        # Handle OAuth provider errors
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            flash(f'OAuth login cancelled or failed: {error_description}', 'error')
            return redirect(url_for('auth.login'))
        
        if not code or not state:
            flash('OAuth callback missing required parameters', 'error')
            return redirect(url_for('auth.login'))
        
        # Validate state parameter for CSRF protection
        if not OAuthService.validate_state(state):
            flash('OAuth security validation failed. Please try again.', 'error')
            return redirect(url_for('auth.login'))
        
        # Exchange code for user info
        redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
        user_info = OAuthService.get_user_info(provider, code, redirect_uri)
        
        if not user_info:
            flash('Failed to retrieve user information from OAuth provider', 'error')
            return redirect(url_for('auth.login'))
        
        # Find or create user
        user = OAuthService.find_or_create_user(provider, user_info)
        
        if not user:
            flash('Failed to create or link user account. Please try again or contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Login user
        if OAuthService.login_oauth_user(user):
            flash(f'Welcome! You have been logged in via {provider.title()}.', 'success')
            
            # Redirect to next page if provided, otherwise check if language selection is needed
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(get_redirect_after_auth(user))
        else:
            flash('Login failed after OAuth authentication. Please try again.', 'error')
            return redirect(url_for('auth.login'))
    
    except Exception as e:
        flash('OAuth login encountered an unexpected error. Please try email login.', 'error')
        return redirect(url_for('auth.login'))
    
    finally:
        # Clean up OAuth session data
        OAuthService.cleanup_oauth_session()


# API endpoints for OAuth (for AJAX requests)

@auth_bp.route('/api/oauth/<provider>')
def api_oauth_login(provider):
    """API endpoint to get OAuth authorization URL for AJAX clients."""
    try:
        redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
        authorization_url, state = OAuthService.get_authorization_url(provider, redirect_uri)
        
        return jsonify({
            'authorization_url': authorization_url,
            'state': state
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'INVALID_PROVIDER'
        }), 400
    except Exception:
        return jsonify({
            'error': 'OAuth service temporarily unavailable',
            'code': 'OAUTH_UNAVAILABLE'
        }), 503
