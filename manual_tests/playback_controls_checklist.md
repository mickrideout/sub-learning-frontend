# Playback Controls Manual Testing Checklist

## Story 3.2 - Auto-play and Speed Control Testing

### Test Environment Setup
- [ ] Browser: Chrome/Firefox/Safari
- [ ] Device: Desktop/Tablet/Mobile  
- [ ] Test subtitle file loaded with multiple alignments (>20)
- [ ] No browser console errors on page load

## Auto-Play Functionality Tests

### Basic Auto-Play Controls
- [ ] **Play button functionality**
  - [ ] Click Play button starts automatic progression
  - [ ] Button changes to "Pause" with pause icon when playing
  - [ ] Button changes color from green to yellow when playing
  - [ ] Current alignment advances automatically at set interval

- [ ] **Pause button functionality**  
  - [ ] Click Pause button stops automatic progression
  - [ ] Button changes back to "Play" with play icon when paused
  - [ ] Button changes color from yellow to green when paused
  - [ ] Current alignment stops advancing

- [ ] **Auto-pause at end**
  - [ ] Playback automatically pauses when reaching last alignment
  - [ ] Button reverts to "Play" state
  - [ ] Progress bar shows 100% completion

### Speed Control Tests

- [ ] **Slow speed (5 seconds)**
  - [ ] Select "Slow (5s)" from speed dropdown
  - [ ] Start auto-play and verify ~5 second intervals between alignments
  - [ ] Verify smooth transitions at slow speed
  - [ ] Speed change takes effect immediately if already playing

- [ ] **Normal speed (3 seconds)**
  - [ ] Select "Normal (3s)" from speed dropdown  
  - [ ] Start auto-play and verify ~3 second intervals between alignments
  - [ ] This should be the default selection on page load
  - [ ] Speed change takes effect immediately if already playing

- [ ] **Fast speed (1 second)**
  - [ ] Select "Fast (1s)" from speed dropdown
  - [ ] Start auto-play and verify ~1 second intervals between alignments
  - [ ] Verify smooth transitions at fast speed
  - [ ] Speed change takes effect immediately if already playing

### Visual Feedback Tests

- [ ] **Playback indicator**
  - [ ] Small green pulsing dot appears on active alignment during auto-play
  - [ ] Indicator disappears when playback is paused
  - [ ] Indicator moves with the current alignment

- [ ] **Smooth transitions**
  - [ ] Alignments highlight with smooth animation during auto-play
  - [ ] No jarring jumps or flickers between alignments
  - [ ] Scrolling is smooth when alignment goes out of view
  - [ ] Alignment highlighting includes both source and target columns

### State Persistence Tests

- [ ] **Page refresh persistence**
  - [ ] Set speed to "Fast", start playback, then refresh page
  - [ ] Speed selection should be restored to "Fast"
  - [ ] Playback should be paused after refresh (not auto-resume)
  - [ ] Current position should be maintained

- [ ] **Browser tab visibility**  
  - [ ] Start auto-play and switch to another browser tab
  - [ ] Return to tab and verify playback automatically paused
  - [ ] Play button should be available to resume

## Edge Cases and Error Conditions

- [ ] **Start playback at end**
  - [ ] Navigate to last alignment manually
  - [ ] Try to start auto-play
  - [ ] Should not start (button remains inactive or shows appropriate state)

- [ ] **Speed changes during playback**
  - [ ] Start auto-play at normal speed  
  - [ ] Change speed while playing to fast
  - [ ] Verify new timing takes effect for next alignment
  - [ ] Try changing multiple times rapidly

- [ ] **Network interruption simulation**
  - [ ] Start auto-play
  - [ ] Disable network briefly (if possible)
  - [ ] Verify graceful handling of any errors
  - [ ] Re-enable network and verify recovery

## Accessibility Tests

- [ ] **Keyboard navigation**
  - [ ] Tab to play/pause button and activate with Enter/Space
  - [ ] Tab to speed selector and navigate options with arrow keys
  - [ ] Spacebar should toggle play/pause when not focused on controls

- [ ] **Screen reader compatibility**
  - [ ] Button states are announced correctly ("Play"/"Pause")
  - [ ] Speed selection changes are announced
  - [ ] Progress updates are accessible

## Performance Tests

- [ ] **Memory usage**
  - [ ] Run auto-play for 5+ minutes continuously
  - [ ] Check browser memory usage doesn't increase dramatically
  - [ ] No memory leaks from timers

- [ ] **CPU usage**  
  - [ ] Auto-play should not cause high CPU usage
  - [ ] Browser should remain responsive during playback
  - [ ] Animation performance is smooth

## Cross-Browser Testing

- [ ] **Chrome**
  - [ ] All functionality works as expected
  - [ ] Animations are smooth
  - [ ] State persistence functions correctly

- [ ] **Firefox**  
  - [ ] All functionality works as expected
  - [ ] Animations are smooth
  - [ ] State persistence functions correctly

- [ ] **Safari** (if available)
  - [ ] All functionality works as expected
  - [ ] Animations are smooth  
  - [ ] State persistence functions correctly

## Mobile Testing

- [ ] **Touch interface**
  - [ ] Play/pause button responds to touch
  - [ ] Speed selector works with touch
  - [ ] Auto-play functions normally on mobile

- [ ] **Battery optimization**
  - [ ] Auto-play respects device sleep/wake cycles
  - [ ] Pauses appropriately when device locks

---

## Test Results Summary

**Date:** _____________  
**Tester:** _____________  
**Browser/Device:** _____________  

**Overall Status:** ☐ Pass ☐ Fail  
**Issues Found:** _____________  
**Additional Notes:** _____________