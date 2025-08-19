# Keyboard Navigation Manual Testing Checklist

## Story 3.2 - Comprehensive Keyboard Shortcut Validation

### Test Environment Setup
- [ ] Browser: Chrome/Firefox/Safari
- [ ] Device: Desktop with physical keyboard
- [ ] Test subtitle file loaded with multiple alignments (>10)
- [ ] Focus not on any input fields (avoid interference)

## Basic Navigation Shortcuts

### Arrow Key Navigation (Extended from Story 3.1)
- [ ] **Left Arrow (←)**
  - [ ] Moves to previous alignment
  - [ ] Works from any alignment position
  - [ ] Disabled/no effect when at first alignment
  - [ ] Stops auto-play if currently playing

- [ ] **Right Arrow (→)**  
  - [ ] Moves to next alignment
  - [ ] Works from any alignment position
  - [ ] Disabled/no effect when at last alignment
  - [ ] Stops auto-play if currently playing

### Jump Navigation Shortcuts
- [ ] **HOME key**
  - [ ] Jumps to first alignment (index 0)
  - [ ] Works from any current position
  - [ ] Updates progress bar to 0%
  - [ ] Pauses auto-play if currently playing
  - [ ] Scrolls to show first alignment in view

- [ ] **END key**
  - [ ] Jumps to last alignment
  - [ ] Works from any current position  
  - [ ] Updates progress bar to 100%
  - [ ] Pauses auto-play if currently playing
  - [ ] Scrolls to show last alignment in view

## Playback Control Shortcuts

### Play/Pause Control
- [ ] **Spacebar**
  - [ ] Toggles between play and pause states
  - [ ] Works when no UI elements are focused
  - [ ] Does not conflict with page scrolling
  - [ ] Visual feedback matches button state change
  - [ ] Starts playback at current alignment position

### Speed Selection Shortcuts  
- [ ] **Number key 1**
  - [ ] Sets playback speed to "Slow (5s)"
  - [ ] Updates speed selector dropdown
  - [ ] Takes effect immediately if auto-play is active
  - [ ] Works from any current speed setting

- [ ] **Number key 2**
  - [ ] Sets playback speed to "Normal (3s)" 
  - [ ] Updates speed selector dropdown
  - [ ] Takes effect immediately if auto-play is active
  - [ ] This is the default speed

- [ ] **Number key 3**  
  - [ ] Sets playback speed to "Fast (1s)"
  - [ ] Updates speed selector dropdown
  - [ ] Takes effect immediately if auto-play is active
  - [ ] Works from any current speed setting

### Emergency Controls
- [ ] **ESC key**
  - [ ] Pauses auto-play if currently playing
  - [ ] Does not affect paused state
  - [ ] Returns focus to manual controls
  - [ ] Can be used as "panic stop" during fast playback

## Help and Information

### Keyboard Shortcuts Help
- [ ] **? key (Shift + /)**
  - [ ] Opens keyboard shortcuts help modal
  - [ ] Modal displays all available shortcuts clearly
  - [ ] Modal can be closed with ESC or close button
  - [ ] Help is accessible and well-formatted

- [ ] **Keyboard button in UI**
  - [ ] Clicking keyboard icon opens same help modal
  - [ ] Button is visible and accessible
  - [ ] Tooltip shows "Keyboard Shortcuts" on hover

## Context and Focus Management

### Input Field Avoidance
- [ ] **When focused on input fields**
  - [ ] Keyboard shortcuts should NOT trigger when typing in search boxes
  - [ ] Shortcuts should NOT trigger when typing in forms
  - [ ] Speed selector dropdown focus should allow arrow navigation
  - [ ] Tab navigation should work normally

- [ ] **Focus management**
  - [ ] Focus returns appropriately after shortcut actions
  - [ ] Tab order remains logical after shortcut usage
  - [ ] No focus traps or lost focus situations

## Shortcut Combinations and Sequences

### Multiple Key Usage
- [ ] **Rapid key presses**
  - [ ] Arrow keys work smoothly with rapid presses
  - [ ] Speed changes (1,2,3) work with rapid presses  
  - [ ] No conflicts between different shortcut types
  - [ ] System remains responsive during rapid input

- [ ] **Modifier key conflicts**
  - [ ] Shortcuts work without accidental Ctrl/Alt/Shift
  - [ ] Browser shortcuts (Ctrl+R, etc.) still work normally
  - [ ] No interference with system shortcuts

## Auto-Play Integration

### Shortcuts During Auto-Play
- [ ] **Navigation during auto-play**
  - [ ] Arrow keys pause auto-play and navigate manually
  - [ ] HOME/END keys pause auto-play and jump
  - [ ] Speed changes (1,2,3) update timing immediately
  - [ ] ESC pauses playback cleanly

- [ ] **Resume after manual navigation**
  - [ ] Spacebar can resume auto-play from new position
  - [ ] Previous speed setting is maintained
  - [ ] No timing conflicts or double-advancement

## Edge Cases and Error Conditions

### Boundary Conditions
- [ ] **At first alignment**
  - [ ] LEFT arrow has no effect (graceful)
  - [ ] HOME key has no effect (already there)
  - [ ] Speed shortcuts still work
  - [ ] Spacebar still toggles playback

- [ ] **At last alignment**
  - [ ] RIGHT arrow has no effect (graceful)
  - [ ] END key has no effect (already there)
  - [ ] Auto-play cannot start (or stops immediately)
  - [ ] All other shortcuts work normally

### Loading States
- [ ] **During data loading**
  - [ ] Shortcuts should be disabled or gracefully handled
  - [ ] No errors in browser console
  - [ ] User feedback for unavailable actions

## Accessibility Testing

### Screen Reader Integration
- [ ] **Shortcut announcements**
  - [ ] Navigation changes are announced
  - [ ] Speed changes are announced
  - [ ] Play/pause state changes are announced

- [ ] **Help accessibility**
  - [ ] Keyboard shortcuts help modal is screen reader accessible
  - [ ] All shortcut descriptions are readable
  - [ ] Modal navigation works with screen readers

### High Contrast Mode
- [ ] **Visual feedback**
  - [ ] Keyboard focus indicators are visible
  - [ ] Help modal remains readable
  - [ ] Button state changes are visible

## Performance Testing

### Responsiveness
- [ ] **Key response time**
  - [ ] All shortcuts respond within 100ms
  - [ ] No lag during rapid key sequences
  - [ ] System remains responsive during shortcuts

- [ ] **Memory usage**  
  - [ ] Extended keyboard usage doesn't increase memory
  - [ ] Event listeners are properly managed
  - [ ] No memory leaks from shortcut handling

## Cross-Browser Compatibility

### Browser-Specific Tests
- [ ] **Chrome**
  - [ ] All shortcuts work as expected
  - [ ] No conflicts with Chrome shortcuts
  - [ ] Help modal functions properly

- [ ] **Firefox**
  - [ ] All shortcuts work as expected  
  - [ ] No conflicts with Firefox shortcuts
  - [ ] Shortcut key detection accurate

- [ ] **Safari** (if available)
  - [ ] All shortcuts work as expected
  - [ ] CMD key handling on macOS
  - [ ] No Safari-specific conflicts

---

## Complete Keyboard Shortcut Reference

| Action | Shortcut | Expected Behavior |
|--------|----------|-------------------|
| Previous alignment | ← | Navigate backward |
| Next alignment | → | Navigate forward |
| Jump to start | HOME | Go to first alignment |  
| Jump to end | END | Go to last alignment |
| Play/Pause toggle | SPACE | Start/stop auto-play |
| Slow speed | 1 | Set 5-second intervals |
| Normal speed | 2 | Set 3-second intervals |
| Fast speed | 3 | Set 1-second intervals |
| Emergency pause | ESC | Stop auto-play |
| Show help | ? | Display shortcuts modal |

## Test Results Summary

**Date:** _____________  
**Tester:** _____________  
**Browser/Device:** _____________  
**Keyboard Layout:** _____________

**Overall Status:** ☐ Pass ☐ Fail  
**Issues Found:** _____________  
**Accessibility Notes:** _____________  
**Performance Notes:** _____________