# Learning Interface Manual Test Checklist

## Split-Screen Layout and Navigation Tests

### Test Environment Setup
- [ ] Ensure test user has language preferences set (native and target languages)
- [ ] Verify subtitle data exists for test language pair
- [ ] Clear browser cache and localStorage before testing

### AC1: Split-Screen Layout (Native | Target Languages)
- [ ] **Test 1.1**: Page loads with two distinct columns visible
- [ ] **Test 1.2**: Left column displays source language subtitles
- [ ] **Test 1.3**: Right column displays target language subtitles
- [ ] **Test 1.4**: Columns have equal width by default
- [ ] **Test 1.5**: Visual separation line appears between columns

### AC2: Subtitle Line Synchronization
- [ ] **Test 2.1**: Source and target lines display corresponding translations
- [ ] **Test 2.2**: Line highlighting synchronizes between both columns
- [ ] **Test 2.3**: Empty lines display correctly when no translation exists
- [ ] **Test 2.4**: Multiple lines per alignment render properly
- [ ] **Test 2.5**: Alignment index consistency maintained across columns

### AC4: Visual Separation Between Columns
- [ ] **Test 4.1**: Clear visual divider between language columns
- [ ] **Test 4.2**: Adequate spacing prevents text overlap
- [ ] **Test 4.3**: Column headers clearly identify languages
- [ ] **Test 4.4**: Background colors differentiate columns appropriately

### AC6: Navigation Controls (Previous/Next Buttons)
- [ ] **Test 6.1**: Previous button disabled on first alignment
- [ ] **Test 6.2**: Next button disabled on last alignment
- [ ] **Test 6.3**: Previous button navigates to correct alignment
- [ ] **Test 6.4**: Next button navigates to correct alignment
- [ ] **Test 6.5**: Navigation buttons have appropriate visual feedback
- [ ] **Test 6.6**: Keyboard shortcuts work (Left/Right arrows)
- [ ] **Test 6.7**: Progress bar updates with navigation

### AC7: Current Subtitle Line Highlighting
- [ ] **Test 7.1**: Current alignment highlighted in both columns
- [ ] **Test 7.2**: Highlighting style clearly differentiates active line
- [ ] **Test 7.3**: Only one alignment highlighted at a time
- [ ] **Test 7.4**: Highlighting persists during column width changes
- [ ] **Test 7.5**: Scroll position follows highlighted alignment

### Progress Indicator Testing
- [ ] **Test P.1**: Progress bar shows current position accurately
- [ ] **Test P.2**: Progress text displays "X / Total" format correctly
- [ ] **Test P.3**: Progress updates immediately on navigation
- [ ] **Test P.4**: Progress percentage calculation is accurate

### Error Handling
- [ ] **Test E.1**: Graceful handling of missing alignment data
- [ ] **Test E.2**: Network error recovery and retry mechanisms
- [ ] **Test E.3**: Invalid subtitle data format handling
- [ ] **Test E.4**: User feedback for loading states

### Data Loading and Pagination
- [ ] **Test D.1**: Initial batch of 50 alignments loads correctly
- [ ] **Test D.2**: Additional batches load when navigating beyond current set
- [ ] **Test D.3**: Loading indicator displays during data fetch
- [ ] **Test D.4**: Cached data improves subsequent load times

## Test Results

### Passed Tests
- List test IDs that passed

### Failed Tests
- List test IDs that failed with descriptions

### Notes
- Any additional observations or issues discovered

## Test Sign-off

**Tester**: _______________  
**Date**: _______________  
**Status**: [ ] Pass [ ] Fail [ ] Needs Revision