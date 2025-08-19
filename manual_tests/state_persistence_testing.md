# State Persistence Manual Testing Checklist

## Story 3.2 - Playback State Saving and Restoration

### Test Environment Setup
- [ ] Browser: Chrome/Firefox/Safari
- [ ] Device: Desktop/Tablet/Mobile
- [ ] Test subtitle file loaded with known alignment count
- [ ] Clear browser localStorage before starting (for clean slate)
- [ ] Developer tools available for localStorage inspection

## Playback Preferences Persistence

### Speed Setting Persistence
- [ ] **Speed setting across page refreshes**
  - [ ] Set speed to "Fast (1s)" using dropdown
  - [ ] Refresh the page (F5 or Ctrl+R)
  - [ ] Verify speed selector shows "Fast (1s)" after reload
  - [ ] Verify auto-play uses fast speed when started

- [ ] **Speed setting across browser sessions**
  - [ ] Set speed to "Slow (5s)"
  - [ ] Close browser tab/window completely
  - [ ] Reopen URL in new tab/window
  - [ ] Verify speed selector shows "Slow (5s)"

- [ ] **Speed changes via keyboard shortcuts**
  - [ ] Press "3" key to set fast speed
  - [ ] Refresh page
  - [ ] Verify keyboard shortcut speed is persisted
  - [ ] Test with keys "1", "2", "3" individually

### Playback State Persistence
- [ ] **Play/pause state handling**
  - [ ] Start auto-play, verify it's playing
  - [ ] Refresh page during auto-play
  - [ ] After refresh, playback should be paused (not auto-resume)
  - [ ] Play button should be in "Play" state, not "Pause"

- [ ] **Last playback state preference**
  - [ ] Start auto-play and let it run
  - [ ] Pause manually using button or spacebar
  - [ ] Refresh page
  - [ ] Verify playback preference is saved as "paused"

## Session State Persistence

### Position Maintenance
- [ ] **Current alignment position**
  - [ ] Navigate to alignment 15 (of known total)
  - [ ] Refresh page
  - [ ] Verify still at alignment 15
  - [ ] Progress bar should show correct position

- [ ] **Position during auto-play**
  - [ ] Start auto-play at alignment 5
  - [ ] Let it advance to alignment 8-10  
  - [ ] Refresh page immediately
  - [ ] Position should be maintained around alignment 8-10

- [ ] **Position after manual navigation**
  - [ ] Use keyboard shortcuts to navigate to middle
  - [ ] Use first/last buttons to jump around
  - [ ] Refresh and verify last position is maintained

### Session Data Validation
- [ ] **Recent session restoration (within 24 hours)**
  - [ ] Set up test session with specific speed/position
  - [ ] Close and reopen browser within minutes
  - [ ] Verify session data is restored completely
  - [ ] Check both position and playback preferences

- [ ] **Expired session handling (simulated)**
  - [ ] Modify localStorage timestamp manually (if possible)
  - [ ] Set timestamp to >24 hours ago
  - [ ] Reload page
  - [ ] Should fall back to defaults gracefully
  - [ ] No errors in console

## Cross-Browser Session Isolation

### Browser-Specific Storage
- [ ] **Chrome to Firefox isolation**
  - [ ] Set specific preferences in Chrome
  - [ ] Open same URL in Firefox
  - [ ] Should start with default settings (not Chrome's)
  - [ ] Each browser maintains separate storage

- [ ] **Private/Incognito mode behavior**  
  - [ ] Set preferences in normal browsing mode
  - [ ] Open same URL in private/incognito window
  - [ ] Should start with defaults (not persistent)
  - [ ] Changes in private mode don't affect normal mode

### Multi-Tab Consistency
- [ ] **Same origin, multiple tabs**
  - [ ] Open same subtitle URL in two browser tabs
  - [ ] Change speed in tab 1
  - [ ] Refresh tab 2
  - [ ] Tab 2 should show updated speed from tab 1

- [ ] **Different subtitles, separate storage**
  - [ ] Use subtitle A with specific settings
  - [ ] Open subtitle B in new tab
  - [ ] Should start with default settings (not subtitle A's)
  - [ ] Each subtitle maintains separate session

## Storage Error Handling

### LocalStorage Availability
- [ ] **Storage disabled scenarios**
  - [ ] Disable localStorage in browser settings (if possible)
  - [ ] Reload page
  - [ ] Should function without errors
  - [ ] Defaults should be used gracefully

- [ ] **Storage quota exceeded**
  - [ ] Fill localStorage with large data (test scenario)
  - [ ] Try to save playback preferences
  - [ ] Should handle gracefully without breaking functionality
  - [ ] No critical errors in console

### Data Corruption Recovery
- [ ] **Invalid JSON in localStorage**  
  - [ ] Manually corrupt localStorage data (if possible)
  - [ ] Reload page
  - [ ] Should detect invalid data and use defaults
  - [ ] System should remain functional

- [ ] **Missing localStorage keys**
  - [ ] Delete specific localStorage keys manually
  - [ ] Reload page  
  - [ ] Should handle missing keys gracefully
  - [ ] Recreate defaults as needed

## Time-Based Persistence Testing

### Session Timing
- [ ] **Recent session (< 1 hour)**
  - [ ] Set up session and close browser
  - [ ] Reopen within 1 hour
  - [ ] Full session restoration expected
  - [ ] Position and preferences maintained

- [ ] **Medium-term session (1-12 hours)**
  - [ ] Set up session and close browser
  - [ ] Reopen after several hours
  - [ ] Preferences should persist
  - [ ] Position may be maintained if within 24h window

- [ ] **Old session (> 24 hours)**
  - [ ] Session data should expire gracefully
  - [ ] Falls back to saved preferences only
  - [ ] No position restoration for old sessions

## User Progress Integration

### Server Progress Sync
- [ ] **Local vs server position**
  - [ ] Navigate to position 20 locally
  - [ ] Refresh page
  - [ ] Should prioritize server progress if more recent
  - [ ] Local session provides fallback

- [ ] **Progress update frequency**
  - [ ] During auto-play, position updates every 5 alignments
  - [ ] Verify server calls are batched appropriately
  - [ ] Local storage updated more frequently than server

## Data Privacy and Security

### Sensitive Information
- [ ] **No sensitive data in localStorage**
  - [ ] Inspect localStorage contents manually
  - [ ] Should contain only position, speed preferences
  - [ ] No user credentials or sensitive data
  - [ ] Data is minimal and appropriate

- [ ] **Data cleanup**
  - [ ] Clear all learning data option works
  - [ ] Logout should clear session data
  - [ ] No orphaned data remains

## Performance Impact

### Storage Operations
- [ ] **Read/write performance**
  - [ ] Frequent preference saves don't cause lag
  - [ ] Page load time not significantly impacted
  - [ ] Auto-play performance unaffected by storage operations

- [ ] **Memory usage**
  - [ ] Extended usage doesn't increase memory from storage
  - [ ] Storage operations are efficient
  - [ ] No memory leaks from persistence features

## Development and Debug Support

### localStorage Inspection
- [ ] **Developer tools verification**
  - [ ] Open browser developer tools
  - [ ] Navigate to Application/Storage tab
  - [ ] Verify localStorage keys exist:
    - `learning_playbackPreferences`
    - `learning_session_[subLinkId]`
    - Other learning-prefixed keys

- [ ] **Data structure validation**
  - [ ] Inspect stored JSON structures
  - [ ] Verify data matches expected schema
  - [ ] No corrupted or invalid data structures

## Edge Cases and Error Scenarios

### Rapid State Changes
- [ ] **Fast preference changes**
  - [ ] Change speed rapidly multiple times
  - [ ] Each change should be persisted
  - [ ] No race conditions in storage operations

- [ ] **Simultaneous navigation and storage**
  - [ ] Navigate while auto-play is saving state
  - [ ] No conflicts between operations
  - [ ] Final state is consistent and accurate

### Browser Limitations
- [ ] **Storage size limits**
  - [ ] Large number of sessions doesn't break system
  - [ ] Old session cleanup works properly
  - [ ] No infinite growth of stored data

---

## localStorage Data Schema Reference

### Expected Storage Keys
- `learning_playbackPreferences` - General playback preferences
- `learning_session_{subLinkId}` - Session data per subtitle file
- `learning_fontSize` - Font size preference (existing)
- `learning_columnLayout` - Column layout preference (existing)

### Expected Data Structure
```json
// playbackPreferences
{
  "isAutoPlaying": false,
  "playbackSpeed": 3000,
  "lastPlaybackState": "paused",
  "preferredSpeed": "normal"
}

// session data  
{
  "currentIndex": 15,
  "isPlaying": false,
  "playbackSpeed": 3000,
  "lastUpdated": 1692123456789
}
```

## Test Results Summary

**Date:** _____________  
**Tester:** _____________  
**Browser/Device:** _____________  

**Preferences Persistence:** ☐ Pass ☐ Fail  
**Session Restoration:** ☐ Pass ☐ Fail  
**Error Handling:** ☐ Pass ☐ Fail  
**Cross-Browser:** ☐ Pass ☐ Fail  
**Performance:** ☐ Pass ☐ Fail

**Issues Found:** _____________  
**Data Validation:** _____________  
**Security Notes:** _____________