# Error Handling Strategy

## Error Flow

```mermaid
sequenceDiagram
    participant U as User Interface
    participant F as Flask Backend
    participant DB as SQLite Database
    participant L as Logging System

    Note over U,L: Error Handling Flow

    U->>F: API Request (e.g., get subtitles)
    F->>DB: Database Query
    
    alt Database Lock Error (Pi-specific)
        DB->>F: SQLite "database is locked"
        F->>F: Retry with exponential backoff (3 attempts)
        F->>DB: Retry query
        
        alt Retry succeeds
            DB->>F: Successful response
            F->>U: Return data with retry warning
        else All retries fail
            F->>L: Log database lock issue
            F->>U: 503 Service Unavailable with retry suggestion
            U->>U: Queue request for automatic retry
        end
    end
    
    alt Memory Exhaustion (Pi hardware limit)
        F->>F: Memory usage check fails
        F->>L: Log memory pressure warning
        F->>F: Clear subtitle cache
        F->>U: 503 with "system busy" message
        U->>U: Display user-friendly error with retry option
    end
    
    alt User Authentication Error
        F->>F: Session validation fails
        F->>L: Log authentication attempt
        F->>U: 401 Unauthorized
        U->>U: Redirect to login with session expired message
    end
    
    alt Network Connectivity Issues
        U->>F: Request timeout (10 seconds)
        U->>U: Display offline mode indicator
        U->>U: Queue progress updates for later sync
        U->>U: Allow continued learning with cached content
    end
```

## Error Response Format

```typescript
interface ApiError {
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable error message
    details?: Record<string, any>;  // Additional error context
    timestamp: string;      // ISO timestamp for debugging
    requestId: string;      // Unique request identifier for Pi logs
    retryable?: boolean;    // Whether client should retry request
    retryAfter?: number;    // Seconds to wait before retry
  };
}
```
