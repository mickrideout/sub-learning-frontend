"""Subtitle service for database queries and caching."""
from typing import List, Dict, Optional
from sqlalchemy import text, exc, and_
from app import db
from app.models.subtitle import SubLine, SubTitle
from app.models.language import Language
from app.utils.cache import subtitle_cache
import logging

logger = logging.getLogger(__name__)


class SubtitleService:
    """Service class for subtitle retrieval and caching."""

    @staticmethod
    def get_subtitle_content(movie_id: int, language_id: int) -> List[Dict]:
        """
        Get subtitle content for a specific movie and language.
        
        Args:
            movie_id: Movie ID to get subtitles for
            language_id: Language ID for subtitle content
            
        Returns:
            List of subtitle line dictionaries with sequence and content
            
        Raises:
            ValueError: If movie_id or language_id are invalid
            Exception: For database connection issues
        """
        if not movie_id or not language_id:
            raise ValueError("Both movie_id and language_id are required")

        # Check cache first
        cached_content = subtitle_cache.get(movie_id, language_id)
        if cached_content is not None:
            logger.debug(f"Cache hit for movie {movie_id}, language {language_id}")
            return cached_content

        try:
            # Validate that movie exists
            if not SubtitleService._movie_exists(movie_id):
                raise ValueError(f"Movie with ID {movie_id} not found")

            # Validate that language exists
            if not SubtitleService._language_exists(language_id):
                raise ValueError(f"Language with ID {language_id} not found")

            # Query subtitle content with proper sequencing
            query = text("""
                SELECT sl.id, sl.sequence, sl.content, sl.language_id
                FROM sub_lines sl
                JOIN sub_titles st ON sl.movie_id = st.id
                WHERE sl.movie_id = :movie_id AND sl.language_id = :language_id
                ORDER BY sl.sequence ASC
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {
                    'movie_id': movie_id,
                    'language_id': language_id
                })
                
                subtitles = []
                for row in result:
                    subtitles.append({
                        'id': row.id,
                        'sequence': row.sequence,
                        'content': row.content,
                        'language_id': row.language_id
                    })

            # Cache the result
            subtitle_cache.set(movie_id, language_id, subtitles)
            logger.debug(f"Retrieved and cached {len(subtitles)} subtitle lines for movie {movie_id}, language {language_id}")
            
            return subtitles

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error retrieving subtitles for movie {movie_id}, language {language_id}: {str(e)}")
            raise Exception(f"Database error while fetching subtitles: {str(e)}")

    @staticmethod
    def get_available_languages(movie_id: int) -> List[Dict]:
        """
        Get available subtitle languages for a specific movie.
        
        Args:
            movie_id: Movie ID to check subtitle availability for
            
        Returns:
            List of language dictionaries with id and name
            
        Raises:
            ValueError: If movie_id is invalid
            Exception: For database connection issues
        """
        if not movie_id:
            raise ValueError("movie_id is required")

        try:
            # Validate that movie exists
            if not SubtitleService._movie_exists(movie_id):
                raise ValueError(f"Movie with ID {movie_id} not found")

            # Query available languages for the movie
            query = text("""
                SELECT DISTINCT sl.language_id, l.name as language_name, l.display_name
                FROM sub_lines sl
                JOIN languages l ON sl.language_id = l.id
                WHERE sl.movie_id = :movie_id
                ORDER BY l.name ASC
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {'movie_id': movie_id})
                
                languages = []
                for row in result:
                    languages.append({
                        'id': row.language_id,
                        'name': row.language_name,
                        'display_name': row.display_name
                    })

            logger.debug(f"Found {len(languages)} available languages for movie {movie_id}")
            return languages

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error retrieving available languages for movie {movie_id}: {str(e)}")
            raise Exception(f"Database error while fetching available languages: {str(e)}")

    @staticmethod
    def validate_subtitle_access(movie_id: int, language_id: int, user_native_lang: int, user_target_lang: int) -> bool:
        """
        Validate that user has access to subtitle content based on their language pair.
        
        Args:
            movie_id: Movie ID to validate access for
            language_id: Language ID to validate access for
            user_native_lang: User's native language ID
            user_target_lang: User's target language ID
            
        Returns:
            True if user has access, False otherwise
        """
        if not all([movie_id, language_id, user_native_lang, user_target_lang]):
            return False

        # User can access subtitles in their native or target language
        if language_id not in [user_native_lang, user_target_lang]:
            return False

        try:
            # Check if there are subtitle links for the user's language pair and this movie
            # Also ensure the specific language requested has subtitle content
            query = text("""
                SELECT COUNT(*) as count
                FROM sub_links sl
                JOIN sub_lines sline ON (sline.movie_id = sl.fromid OR sline.movie_id = sl.toid)
                WHERE (sl.fromid = :movie_id OR sl.toid = :movie_id)
                  AND sline.movie_id = :movie_id
                  AND sline.language_id = :language_id
                  AND ((sl.fromlang = :native_lang AND sl.tolang = :target_lang) 
                       OR (sl.fromlang = :target_lang AND sl.tolang = :native_lang))
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {
                    'movie_id': movie_id,
                    'language_id': language_id,
                    'native_lang': user_native_lang,
                    'target_lang': user_target_lang
                }).fetchone()
                
                return result.count > 0

        except exc.SQLAlchemyError:
            logger.error(f"Database error validating subtitle access for movie {movie_id}")
            return False

    @staticmethod
    def invalidate_cache(movie_id: int, language_id: Optional[int] = None) -> None:
        """
        Invalidate cached subtitle content.
        
        Args:
            movie_id: Movie ID to invalidate cache for
            language_id: Specific language ID to invalidate (optional)
        """
        subtitle_cache.invalidate(movie_id, language_id)
        logger.info(f"Invalidated subtitle cache for movie {movie_id}, language {language_id or 'all'}")

    @staticmethod
    def get_cache_stats() -> Dict:
        """Get subtitle cache performance statistics."""
        return subtitle_cache.get_stats()

    @staticmethod
    def _movie_exists(movie_id: int) -> bool:
        """Check if movie exists in database."""
        try:
            query = text("SELECT COUNT(*) as count FROM sub_titles WHERE id = :movie_id")
            
            with db.engine.connect() as conn:
                result = conn.execute(query, {'movie_id': movie_id}).fetchone()
                return result.count > 0
                
        except exc.SQLAlchemyError:
            return False

    @staticmethod
    def _language_exists(language_id: int) -> bool:
        """Check if language exists in database."""
        try:
            query = text("SELECT COUNT(*) as count FROM languages WHERE id = :language_id")
            
            with db.engine.connect() as conn:
                result = conn.execute(query, {'language_id': language_id}).fetchone()
                return result.count > 0
                
        except exc.SQLAlchemyError:
            return False

    @staticmethod
    def validate_subtitle_data(subtitle_lines: List[Dict]) -> bool:
        """
        Validate subtitle data integrity.
        
        Args:
            subtitle_lines: List of subtitle line dictionaries
            
        Returns:
            True if data is valid, False otherwise
        """
        if not isinstance(subtitle_lines, list):
            return False

        required_fields = ['id', 'sequence', 'content', 'language_id']
        
        for line in subtitle_lines:
            if not isinstance(line, dict):
                return False
                
            # Check required fields
            for field in required_fields:
                if field not in line:
                    return False
                    
            # Validate field types
            if not isinstance(line['id'], int) or line['id'] <= 0:
                return False
            if not isinstance(line['sequence'], int) or line['sequence'] < 0:
                return False
            if not isinstance(line['content'], str) or not line['content'].strip():
                return False
            if not isinstance(line['language_id'], int) or line['language_id'] <= 0:
                return False

        # Check sequence ordering
        sequences = [line['sequence'] for line in subtitle_lines]
        if sequences != sorted(sequences):
            return False

        return True