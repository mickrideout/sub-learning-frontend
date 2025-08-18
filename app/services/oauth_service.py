"""OAuth service for handling social login providers."""
import secrets
from typing import Optional, Dict, Any, Tuple
from flask import current_app, session, url_for
from flask_login import login_user
from app import oauth, db
from app.models.user import User


class OAuthService:
    """Service for handling OAuth authentication with external providers."""

    @staticmethod
    def generate_oauth_state() -> str:
        """Generate secure state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_authorization_url(provider: str, redirect_uri: str) -> Tuple[str, str]:
        """
        Get OAuth authorization URL for the specified provider.
        
        Args:
            provider: OAuth provider name (google, facebook, apple)
            redirect_uri: Callback URL for OAuth flow
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if provider not in ['google', 'facebook', 'apple']:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        
        client = oauth.create_client(provider)
        if not client:
            raise ValueError(f"OAuth client not configured for provider: {provider}")
        
        state = OAuthService.generate_oauth_state()
        session['oauth_state'] = state
        session['oauth_provider'] = provider
        
        if provider == 'apple':
            # Apple Sign-In requires response_mode=form_post
            authorization_url = client.create_authorization_url(
                redirect_uri, 
                state=state,
                response_mode='form_post'
            )
        else:
            authorization_url = client.create_authorization_url(redirect_uri, state=state)
        
        return authorization_url['url'], state

    @staticmethod
    def validate_state(received_state: str) -> bool:
        """
        Validate OAuth state parameter against session stored state.
        
        Args:
            received_state: State parameter received from OAuth callback
            
        Returns:
            True if state is valid, False otherwise
        """
        stored_state = session.get('oauth_state')
        return stored_state and secrets.compare_digest(stored_state, received_state)

    @staticmethod
    def get_user_info(provider: str, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token and retrieve user info.
        
        Args:
            provider: OAuth provider name
            code: Authorization code from OAuth callback
            redirect_uri: Callback URL used in OAuth flow
            
        Returns:
            User info dictionary or None if failed
        """
        try:
            client = oauth.create_client(provider)
            if not client:
                current_app.logger.error(f"OAuth client not found for provider: {provider}")
                return None
            
            # Exchange code for token
            token = client.authorize_access_token(redirect_uri=redirect_uri)
            if not token:
                current_app.logger.error(f"Failed to exchange code for token: {provider}")
                return None
            
            # Get user info based on provider
            if provider == 'google':
                return OAuthService._get_google_user_info(client, token)
            elif provider == 'facebook':
                return OAuthService._get_facebook_user_info(client, token)
            elif provider == 'apple':
                return OAuthService._get_apple_user_info(client, token)
            
        except Exception as e:
            current_app.logger.error(f"OAuth user info retrieval failed for {provider}: {e}")
            return None
        
        return None

    @staticmethod
    def _get_google_user_info(client, token: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get user info from Google OAuth."""
        try:
            resp = client.parse_id_token(token)
            if not resp:
                # Fallback to userinfo endpoint
                resp = client.get('userinfo', token=token).json()
            
            return {
                'oauth_id': resp.get('sub'),
                'email': resp.get('email'),
                'name': resp.get('name'),
                'given_name': resp.get('given_name'),
                'family_name': resp.get('family_name'),
                'picture': resp.get('picture')
            }
        except Exception as e:
            current_app.logger.error(f"Google user info parsing failed: {e}")
            return None

    @staticmethod
    def _get_facebook_user_info(client, token: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get user info from Facebook OAuth."""
        try:
            resp = client.get('me?fields=id,email,name,first_name,last_name,picture', token=token)
            if resp.status_code != 200:
                current_app.logger.error(f"Facebook API error: {resp.status_code}")
                return None
            
            user_data = resp.json()
            return {
                'oauth_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'given_name': user_data.get('first_name'),
                'family_name': user_data.get('last_name'),
                'picture': user_data.get('picture', {}).get('data', {}).get('url')
            }
        except Exception as e:
            current_app.logger.error(f"Facebook user info parsing failed: {e}")
            return None

    @staticmethod
    def _get_apple_user_info(client, token: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get user info from Apple OAuth (JWT token)."""
        try:
            # Apple returns user info in the ID token
            id_token = token.get('id_token')
            if not id_token:
                current_app.logger.error("No ID token in Apple OAuth response")
                return None
            
            # Parse JWT token to get user info
            user_info = client.parse_id_token(token)
            return {
                'oauth_id': user_info.get('sub'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'given_name': None,  # Apple doesn't provide separated names in JWT
                'family_name': None,
                'picture': None  # Apple doesn't provide profile pictures
            }
        except Exception as e:
            current_app.logger.error(f"Apple user info parsing failed: {e}")
            return None

    @staticmethod
    def find_or_create_user(provider: str, user_info: Dict[str, Any]) -> Optional[User]:
        """
        Find existing user or create new user from OAuth data.
        
        Args:
            provider: OAuth provider name
            user_info: User information from OAuth provider
            
        Returns:
            User object or None if creation failed
        """
        try:
            oauth_id = user_info.get('oauth_id')
            email = user_info.get('email')
            
            if not oauth_id or not email:
                current_app.logger.error(f"Missing required user data from {provider}")
                return None
            
            # First, check if user exists with this OAuth provider and ID
            existing_user = User.query.filter_by(
                oauth_provider=provider, 
                oauth_id=oauth_id
            ).first()
            
            if existing_user:
                return existing_user
            
            # Check if user exists with same email (for account linking)
            existing_email_user = User.query.filter_by(email=email).first()
            if existing_email_user:
                # Link OAuth to existing account if no OAuth provider set
                if not existing_email_user.oauth_provider:
                    existing_email_user.oauth_provider = provider
                    existing_email_user.oauth_id = oauth_id
                    existing_email_user.email_verified = True  # OAuth emails are verified
                    db.session.commit()
                    return existing_email_user
                # If same provider but different oauth_id, return existing user (no change)
                elif existing_email_user.oauth_provider == provider:
                    return existing_email_user
                else:
                    current_app.logger.warning(f"Email {email} already linked to different OAuth provider")
                    return None
            
            # Create new user
            new_user = User(
                email=email,
                oauth_provider=provider,
                oauth_id=oauth_id,
                email_verified=True  # OAuth emails are considered verified
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            current_app.logger.info(f"Created new OAuth user: {email} via {provider}")
            return new_user
            
        except Exception as e:
            current_app.logger.error(f"User creation/linking failed for {provider}: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def login_oauth_user(user: User) -> bool:
        """
        Login user via Flask-Login after OAuth authentication.
        
        Args:
            user: User object to login
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            login_user(user, remember=True)
            current_app.logger.info(f"OAuth user logged in: {user.email}")
            return True
        except Exception as e:
            current_app.logger.error(f"OAuth login failed for user {user.email}: {e}")
            return False

    @staticmethod
    def cleanup_oauth_session():
        """Clean up OAuth-related session data."""
        session.pop('oauth_state', None)
        session.pop('oauth_provider', None)