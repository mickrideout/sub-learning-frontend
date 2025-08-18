# Data Models

## User

**Purpose:** Store user account information, authentication credentials, and profile settings for personalized learning experience

**Key Attributes:**
- id: INTEGER (Primary Key) - Unique user identifier
- email: VARCHAR(255) - User's email address for login
- password_hash: VARCHAR(255) - Securely hashed password
- oauth_provider: VARCHAR(50) - OAuth provider (google, facebook, apple, null)
- oauth_id: VARCHAR(255) - OAuth provider user ID
- native_language_id: INTEGER - Foreign key to languages table
- target_language_id: INTEGER - Foreign key to languages table
- created_at: DATETIME - Account creation timestamp
- updated_at: DATETIME - Last profile update timestamp
- is_active: BOOLEAN - Account status flag

### TypeScript Interface
```typescript
interface User {
  id: number;
  email: string;
  oauth_provider?: 'google' | 'facebook' | 'apple' | null;
  oauth_id?: string;
  native_language_id: number;
  target_language_id: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}
```

### Relationships
- belongs_to: Language (native_language)
- belongs_to: Language (target_language)  
- has_many: UserProgress
- has_many: Bookmark

## Language

**Purpose:** Store available languages with display information and language codes

**Key Attributes:**
- id: SMALLINT (Primary Key) - Unique language identifier
- name: TEXT - Internal language name
- display_name: TEXT - Human-readable language name for UI
- code: TEXT - Language code (ISO or custom)

### TypeScript Interface
```typescript
interface Language {
  id: number;
  name: string;
  display_name: string;
  code: string;
}
```

### Relationships
- has_many: SubLink (as from_language and to_language)
- has_many: User (as native_language and target_language)

## SubTitle

**Purpose:** Store movie titles and metadata for the subtitle catalog

**Key Attributes:**
- id: INTEGER (Primary Key) - Unique movie identifier
- title: TEXT - Movie title for display and search

### TypeScript Interface
```typescript
interface SubTitle {
  id: number;
  title: string;
}
```

### Relationships
- has_many: SubLine
- has_many: SubLink (as from_movie and to_movie)

## SubLine

**Purpose:** Store individual subtitle lines with content and line sequence

**Key Attributes:**
- id: INTEGER (Primary Key) - Unique subtitle line identifier  
- lineid: SMALLINT - Sequential line number within the subtitle file
- content: TEXT - The actual subtitle text content

### TypeScript Interface
```typescript
interface SubLine {
  id: number;
  lineid: number;
  content: string;
}
```

### Relationships
- belongs_to: SubTitle (through SubLink association)
- referenced_by: SubLinkLine (through link_data JSON)

## SubLink

**Purpose:** Represents translation availability between movies in different languages

**Key Attributes:**
- id: INTEGER (Primary Key) - Unique translation link identifier
- fromid: INTEGER - Source movie ID (references sub_titles.id)
- fromlang: SMALLINT - Source language ID (references languages.id)  
- toid: INTEGER - Target movie ID (references sub_titles.id)
- tolang: SMALLINT - Target language ID (references languages.id)

### TypeScript Interface
```typescript
interface SubLink {
  id: number;
  fromid: number;
  fromlang: number;
  toid: number;
  tolang: number;
}
```

### Relationships
- belongs_to: Language (fromlang)
- belongs_to: Language (tolang)
- belongs_to: SubTitle (fromid)
- belongs_to: SubTitle (toid)
- has_many: SubLinkLine

## SubLinkLine

**Purpose:** Contains line-by-line alignment information between translated movie versions

**Key Attributes:**
- sub_link_id: INTEGER - Foreign key to sub_links table
- link_data: JSONB - Array of aligned line pairs between from/to languages

### TypeScript Interface
```typescript
interface SubLinkLine {
  sub_link_id: number;
  link_data: Array<[number[], number[]]>;
  // Example: [[1, 2], [3, 4], [5, 6]] 
  // where first array is line IDs in source language,
  // second array is corresponding line IDs in target language
}

// More detailed type for the alignment data
type LineAlignment = [number[], number[]]; // [source_line_ids, target_line_ids]

interface SubLinkLineDetailed {
  sub_link_id: number;
  link_data: LineAlignment[];
}
```

## UserProgress

**Purpose:** Track user learning progress through aligned subtitle pairs

**Key Attributes:**
- id: INTEGER (Primary Key) - Unique progress identifier
- user_id: INTEGER - Foreign key to users table
- sub_link_id: INTEGER - Foreign key to sub_links table (specific translation pair)
- current_alignment_index: INTEGER - Position in the link_data alignment array
- total_alignments_completed: INTEGER - Count of completed alignment pairs
- last_accessed: DATETIME - When user last studied this content
- session_duration_minutes: INTEGER - Time spent in current session

### TypeScript Interface
```typescript
interface UserProgress {
  id: number;
  user_id: number;
  sub_link_id: number;
  current_alignment_index: number; // Index into link_data array
  total_alignments_completed: number;
  last_accessed: string;
  session_duration_minutes: number;
}
```

## Bookmark

**Purpose:** Store user-marked alignment pairs for review

**Key Attributes:**
- id: INTEGER (Primary Key) - Unique bookmark identifier
- user_id: INTEGER - Foreign key to users table
- sub_link_id: INTEGER - Foreign key to sub_links table
- alignment_index: INTEGER - Specific alignment pair bookmarked (index in link_data)
- note: TEXT - Optional user note about the bookmark
- created_at: DATETIME - When bookmark was created

### TypeScript Interface
```typescript
interface Bookmark {
  id: number;
  user_id: number;
  sub_link_id: number;
  alignment_index: number; // Index into the link_data array
  note?: string;
  created_at: string;
}
```
