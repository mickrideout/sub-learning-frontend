"""Content service for movie discovery and subtitle management."""
from typing import List, Dict, Optional
from sqlalchemy import text, exc
from app import db


class ContentService:
    """Service class for managing movie content and subtitle availability."""

    @staticmethod
    def get_available_movies(native_language_id: int, target_language_id: int, search_query: Optional[str] = None, letter_filter: Optional[str] = None) -> List[Dict]:
        """
        Get movies available for a specific language pair, optionally filtered by search query and/or letter.
        
        Args:
            native_language_id: User's native language ID
            target_language_id: User's target language ID
            search_query: Optional search query for partial title matching (case-insensitive)
            letter_filter: Optional letter filter (A-Z, #, or 'all')
            
        Returns:
            List of movie dictionaries with id, title, and subtitle availability info
            
        Raises:
            ValueError: If language IDs are invalid or letter filter is invalid
            Exception: For database connection issues
        """
        if not native_language_id or not target_language_id:
            raise ValueError("Both native_language_id and target_language_id are required")
            
        if native_language_id == target_language_id:
            raise ValueError("Native and target languages must be different")

        # Validate letter filter if provided
        if letter_filter is not None and letter_filter != 'all':
            if not ContentService._is_valid_letter_filter(letter_filter):
                raise ValueError("Letter filter must be A-Z, #, or 'all'")

        try:
            # Base query for movies with available subtitle links between the language pair
            base_query = """
                SELECT DISTINCT st.id, st.title,
                       COUNT(sl.id) as subtitle_links_count
                FROM sub_titles st
                JOIN sub_links sl ON st.id = sl.fromid OR st.id = sl.toid
                WHERE ((sl.fromlang = :native_lang AND sl.tolang = :target_lang) 
                    OR (sl.fromlang = :target_lang AND sl.tolang = :native_lang))
            """
            
            # Add search filter if search query is provided
            if search_query:
                base_query += " AND LOWER(st.title) LIKE LOWER(:search_pattern)"
            
            # Add letter filter if provided and not 'all'
            if letter_filter and letter_filter != 'all':
                if letter_filter == '#':
                    # Filter for titles starting with numbers
                    base_query += " AND SUBSTR(st.title, 1, 1) REGEXP '^[0-9]'"
                else:
                    # Filter for titles starting with specific letter
                    base_query += " AND UPPER(SUBSTR(st.title, 1, 1)) = UPPER(:letter_filter)"
            
            base_query += """
                GROUP BY st.id, st.title
                ORDER BY st.title ASC
            """

            query = text(base_query)
            query_params = {
                'native_lang': native_language_id,
                'target_lang': target_language_id
            }
            
            # Add search pattern parameter if search query is provided
            if search_query:
                # Sanitize search query to prevent SQL injection
                sanitized_query = search_query.replace('%', r'\%').replace('_', r'\_')
                query_params['search_pattern'] = f'%{sanitized_query}%'
            
            # Add letter filter parameter if provided and not '#' or 'all'
            if letter_filter and letter_filter != 'all' and letter_filter != '#':
                query_params['letter_filter'] = letter_filter

            with db.engine.connect() as conn:
                result = conn.execute(query, query_params)
                
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

    @staticmethod
    def get_letter_counts(native_language_id: int, target_language_id: int, search_query: Optional[str] = None) -> Dict[str, int]:
        """
        Get count of movies available for each letter (A-Z, #) for a specific language pair.
        
        Args:
            native_language_id: User's native language ID
            target_language_id: User's target language ID
            search_query: Optional search query to filter counts (case-insensitive)
            
        Returns:
            Dictionary with letters as keys and movie counts as values
            
        Raises:
            ValueError: If language IDs are invalid
            Exception: For database connection issues
        """
        if not native_language_id or not target_language_id:
            raise ValueError("Both native_language_id and target_language_id are required")
            
        if native_language_id == target_language_id:
            raise ValueError("Native and target languages must be different")

        try:
            # Base query for letter counts
            base_query = """
                SELECT 
                    CASE 
                        WHEN SUBSTR(st.title, 1, 1) REGEXP '^[0-9]' THEN '#'
                        ELSE UPPER(SUBSTR(st.title, 1, 1))
                    END as letter,
                    COUNT(DISTINCT st.id) as count
                FROM sub_titles st
                JOIN sub_links sl ON st.id = sl.fromid OR st.id = sl.toid
                WHERE ((sl.fromlang = :native_lang AND sl.tolang = :target_lang) 
                    OR (sl.fromlang = :target_lang AND sl.tolang = :native_lang))
            """
            
            # Add search filter if search query is provided
            if search_query:
                base_query += " AND LOWER(st.title) LIKE LOWER(:search_pattern)"
            
            base_query += """
                GROUP BY 
                    CASE 
                        WHEN SUBSTR(st.title, 1, 1) REGEXP '^[0-9]' THEN '#'
                        ELSE UPPER(SUBSTR(st.title, 1, 1))
                    END
                ORDER BY letter ASC
            """

            query = text(base_query)
            query_params = {
                'native_lang': native_language_id,
                'target_lang': target_language_id
            }
            
            # Add search pattern parameter if search query is provided
            if search_query:
                # Sanitize search query to prevent SQL injection
                sanitized_query = search_query.replace('%', r'\%').replace('_', r'\_')
                query_params['search_pattern'] = f'%{sanitized_query}%'

            with db.engine.connect() as conn:
                result = conn.execute(query, query_params)
                
                letter_counts = {}
                for row in result:
                    letter_counts[row.letter] = row.count

            return letter_counts

        except exc.SQLAlchemyError as e:
            raise Exception(f"Database error while fetching letter counts: {str(e)}")

    @staticmethod
    def get_movie_subtitle_availability(movie_id: int) -> Dict:
        """
        Get subtitle availability information for a specific movie.
        
        Args:
            movie_id: Movie ID to check subtitle availability for
            
        Returns:
            Dictionary with subtitle availability information
            
        Raises:
            ValueError: If movie_id is invalid
            Exception: For database connection issues
        """
        if not movie_id:
            raise ValueError("movie_id is required")

        try:
            # Check if movie exists and get available subtitle languages
            query = text("""
                SELECT st.id, st.title,
                       GROUP_CONCAT(DISTINCT sl.language_id) as available_languages
                FROM sub_titles st
                LEFT JOIN sub_lines sl ON st.id = sl.movie_id
                WHERE st.id = :movie_id
                GROUP BY st.id, st.title
            """)

            with db.engine.connect() as conn:
                result = conn.execute(query, {'movie_id': movie_id}).fetchone()
                
                if not result:
                    raise ValueError(f"Movie with ID {movie_id} not found")

                available_languages = []
                if result.available_languages:
                    # Convert comma-separated string to list of integers
                    available_languages = [
                        int(lang_id) for lang_id in result.available_languages.split(',')
                        if lang_id.strip()
                    ]

                return {
                    'movie_id': result.id,
                    'title': result.title,
                    'has_subtitles': len(available_languages) > 0,
                    'available_language_ids': available_languages,
                    'subtitle_count': len(available_languages)
                }

        except exc.SQLAlchemyError as e:
            raise Exception(f"Database error while checking subtitle availability: {str(e)}")

    @staticmethod
    def _is_valid_letter_filter(letter: str) -> bool:
        """
        Validate letter filter parameter.
        
        Args:
            letter: Letter to validate
            
        Returns:
            True if letter is valid (A-Z or #), False otherwise
        """
        if not letter or len(letter) != 1:
            return False
        
        return letter == '#' or (letter.isalpha() and letter.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')