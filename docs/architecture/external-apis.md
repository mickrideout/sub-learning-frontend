# External APIs

## Google OAuth 2.0 API

- **Purpose:** Enable Google account authentication for streamlined user registration and login
- **Documentation:** https://developers.google.com/identity/protocols/oauth2/web-server
- **Base URL(s):** https://accounts.google.com/o/oauth2/v2/auth, https://oauth2.googleapis.com/token
- **Authentication:** OAuth 2.0 client credentials (client_id, client_secret)
- **Rate Limits:** 10,000 requests per day (more than sufficient for Pi deployment)

**Key Endpoints Used:**
- `GET /o/oauth2/v2/auth` - Authorization code request with scope=openid email profile
- `POST /token` - Exchange authorization code for access token
- `GET /oauth2/v2/userinfo` - Retrieve user profile information for account creation

**Integration Notes:** Requires HTTPS callback URL configuration; will need dynamic DNS or port forwarding for Pi external access. Store client credentials in environment variables for security.

## Facebook Login API

- **Purpose:** Facebook social authentication integration for user convenience
- **Documentation:** https://developers.facebook.com/docs/facebook-login/web
- **Base URL(s):** https://www.facebook.com/v18.0/dialog/oauth, https://graph.facebook.com/v18.0
- **Authentication:** App ID and App Secret from Facebook Developer Console
- **Rate Limits:** 200 calls per hour per user (sufficient for authentication flows)

**Key Endpoints Used:**
- `GET /v18.0/dialog/oauth` - Facebook authorization dialog with scope=email
- `POST /v18.0/oauth/access_token` - Exchange code for access token
- `GET /v18.0/me` - Retrieve user profile data including email and name

**Integration Notes:** Requires app verification for production use; Facebook Login requires HTTPS callback. Consider Facebook's data privacy requirements for user information handling.

## Apple Sign-In API

- **Purpose:** Apple ID authentication for iOS/macOS user convenience and privacy-focused authentication
- **Documentation:** https://developer.apple.com/documentation/sign_in_with_apple
- **Base URL(s):** https://appleid.apple.com/auth/authorize, https://appleid.apple.com/auth/token
- **Authentication:** Team ID, Key ID, and private key from Apple Developer Account
- **Rate Limits:** Not explicitly documented but designed for high-volume applications

**Key Endpoints Used:**
- `GET /auth/authorize` - Apple ID authorization with scope=name email
- `POST /auth/token` - Token exchange using JWT client assertion
- JWT token validation for user identity verification

**Integration Notes:** Most complex OAuth integration requiring JWT signing with Apple private key. Apple provides minimal user data (email may be private relay). Requires Apple Developer Account ($99/year).
