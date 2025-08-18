"""Content service for movie discovery and subtitle management."""
from typing import List, Dict, Optional
from sqlalchemy import text, exc
from app import db


class ContentService:
    """Service class for managing movie content and subtitle availability."""

    @staticmethod
    def get_available_movies(native_language_id: int, target_language_id: int) -> List[Dict]:
        """
        Get movies available for a specific language pair.
        
        Args:
            native_language_id: User's native language ID
            target_language_id: User's target language ID
            
        Returns:
            List of movie dictionaries with id, title, and subtitle availability info
            
        Raises:
            ValueError: If language IDs are invalid
            Exception: For database connection issues
        """
        if not native_language_id or not target_language_id:
            raise ValueError("Both native_language_id and target_language_id are required")
            
        if native_language_id == target_language_id:
            raise ValueError("Native and target languages must be different")

        try:
            # Query for movies with available subtitle links between the language pair
            query = text("""
                SELECT DISTINCT st.id, st.title,
                       COUNT(sl.id) as subtitle_links_count
                FROM sub_titles st
                JOIN sub_links sl ON st.id = sl.fromid OR st.id = sl.toid
                WHERE (sl.fromlang = :native_lang AND sl.tolang = :target_lang) 
                   OR (sl.fromlang = :target_lang AND sl.tolang = :native_lang)
                GROUP BY st.id, st.title
                ORDER BY st.title ASC
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {
                    'native_lang': native_language_id,
                    'target_lang': target_language_id
                })
                
                movies = []
                for row in result:
                    movies.append({
                        'id': row.id,
                        'title': row.title,
                        'subtitle_links_count': row.subtitle_links_count,
                        'has_subtitles': True  # All returned movies have subtitles
                    })

            return movies

        except exc.SQLAlchemyError as e:
            raise Exception(f"Database error while fetching movies: {str(e)}")

    @staticmethod
    def get_movie_subtitle_info(movie_id: int, native_language_id: int, target_language_id: int) -> Optional[Dict]:
        """
        Get detailed subtitle information for a specific movie and language pair.
        
        Args:
            movie_id: Movie ID to get info for
            native_language_id: User's native language ID
            target_language_id: User's target language ID
            
        Returns:
            Dictionary with movie and subtitle link information, or None if not found
        """
        try:
            query = text("""
                SELECT st.id, st.title, sl.id as link_id, sl.fromlang, sl.tolang
                FROM sub_titles st
                JOIN sub_links sl ON st.id = sl.fromid OR st.id = sl.toid
                WHERE st.id = :movie_id 
                  AND ((sl.fromlang = :native_lang AND sl.tolang = :target_lang) 
                       OR (sl.fromlang = :target_lang AND sl.tolang = :native_lang))
                LIMIT 1
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {
                    'movie_id': movie_id,
                    'native_lang': native_language_id,
                    'target_lang': target_language_id
                }).fetchone()
                
                if result:
                    return {
                        'movie_id': result.id,
                        'title': result.title,
                        'sub_link_id': result.link_id,
                        'from_language': result.fromlang,
                        'to_language': result.tolang
                    }
                
                return None

        except exc.SQLAlchemyError as e:
            raise Exception(f"Database error while fetching movie info: {str(e)}")

    @staticmethod
    def validate_language_pair(native_language_id: int, target_language_id: int) -> bool:
        """
        Validate that both languages exist in the database.
        
        Args:
            native_language_id: Native language ID to validate
            target_language_id: Target language ID to validate
            
        Returns:
            True if both languages exist, False otherwise
        """
        try:
            query = text("""
                SELECT COUNT(*) as count
                FROM languages 
                WHERE id IN (:native_lang, :target_lang)
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {
                    'native_lang': native_language_id,
                    'target_lang': target_language_id
                }).fetchone()
                
                return result.count == 2

        except exc.SQLAlchemyError:
            return False