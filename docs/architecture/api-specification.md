# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: SubLearning API
  version: 1.0.0
  description: REST API for dual-language subtitle learning platform
servers:
  - url: http://localhost:5000/api
    description: Local Raspberry Pi development server
  - url: http://[PI_IP]:5000/api
    description: Raspberry Pi production server

paths:
  # Authentication Endpoints
  /auth/register:
    post:
      summary: Register new user account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password, native_language_id, target_language_id]
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                native_language_id:
                  type: integer
                target_language_id:
                  type: integer
      responses:
        201:
          description: User created successfully
        400:
          description: Invalid input data
        409:
          description: Email already exists

  /auth/login:
    post:
      summary: User login with email/password
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
      responses:
        200:
          description: Login successful
        401:
          description: Invalid credentials

  /auth/oauth/{provider}:
    get:
      summary: OAuth authentication redirect
      parameters:
        - name: provider
          in: path
          required: true
          schema:
            type: string
            enum: [google, facebook, apple]
      responses:
        302:
          description: Redirect to OAuth provider

  # Language Endpoints
  /languages:
    get:
      summary: Get all available languages
      responses:
        200:
          description: List of languages

  # Movie/Content Discovery Endpoints
  /movies:
    get:
      summary: Get available movies for user's language pair
      security:
        - sessionAuth: []
      parameters:
        - name: search
          in: query
          schema:
            type: string
          description: Search by movie title
        - name: letter
          in: query
          schema:
            type: string
            pattern: ^[A-Z]$
          description: Filter by first letter
      responses:
        200:
          description: List of available movies

  # Subtitle Learning Endpoints
  /subtitles/{sub_link_id}:
    get:
      summary: Get subtitle alignment data for learning session
      security:
        - sessionAuth: []
      parameters:
        - name: sub_link_id
          in: path
          required: true
          schema:
            type: integer
        - name: start_index
          in: query
          schema:
            type: integer
            default: 0
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
      responses:
        200:
          description: Subtitle alignment data

  # Progress Tracking Endpoints
  /progress/{sub_link_id}:
    get:
      summary: Get user progress for specific subtitle pair
      security:
        - sessionAuth: []
      parameters:
        - name: sub_link_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: User progress data
        404:
          description: No progress found

    put:
      summary: Update user progress
      security:
        - sessionAuth: []
      parameters:
        - name: sub_link_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                current_alignment_index:
                  type: integer
                session_duration_minutes:
                  type: integer
      responses:
        200:
          description: Progress updated successfully

  # Bookmark Endpoints
  /bookmarks:
    get:
      summary: Get user bookmarks
      security:
        - sessionAuth: []
      responses:
        200:
          description: List of user bookmarks

    post:
      summary: Create new bookmark
      security:
        - sessionAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [sub_link_id, alignment_index]
              properties:
                sub_link_id:
                  type: integer
                alignment_index:
                  type: integer
                note:
                  type: string
      responses:
        201:
          description: Bookmark created successfully

components:
  securitySchemes:
    sessionAuth:
      type: apiKey
      in: cookie
      name: session
```
