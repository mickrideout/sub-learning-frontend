# Customization Features Manual Test Checklist

## Font Size and Column Width Testing

### Test Environment Setup
- [ ] Clear localStorage to reset user preferences
- [ ] Prepare test content with varying text lengths
- [ ] Test on multiple screen sizes for responsive behavior

### AC3: Adjustable Column Widths

#### Equal Column Layout (Default)
- [ ] **Test C.1**: Default layout shows equal column widths (50/50)
- [ ] **Test C.2**: "Equal" button is highlighted by default
- [ ] **Test C.3**: Both columns display content appropriately
- [ ] **Test C.4**: Visual separator remains centered

#### Left Column Preference
- [ ] **Test C.5**: Left button increases source column width (66/34)
- [ ] **Test C.6**: Target column adjusts to narrower width appropriately
- [ ] **Test C.7**: Content remains readable in both columns
- [ ] **Test C.8**: Button state updates to show active selection
- [ ] **Test C.9**: Visual separator adjusts to new column boundaries

#### Right Column Preference  
- [ ] **Test C.10**: Right button increases target column width (34/66)
- [ ] **Test C.11**: Source column adjusts to narrower width appropriately
- [ ] **Test C.12**: Content remains readable in both columns
- [ ] **Test C.13**: Button state updates to show active selection
- [ ] **Test C.14**: Visual separator adjusts to new column boundaries

#### Column Width Persistence
- [ ] **Test C.15**: Column preference persists after page refresh
- [ ] **Test C.16**: Column preference persists across sessions
- [ ] **Test C.17**: Column preference survives browser restart
- [ ] **Test C.18**: Different users maintain separate preferences

### AC5: Font Size Controls

#### Small Font Size
- [ ] **Test F.1**: Small font button activates 0.9em size
- [ ] **Test F.2**: Text remains readable at small size
- [ ] **Test F.3**: Button shows active state when selected
- [ ] **Test F.4**: All subtitle content adapts to new size
- [ ] **Test F.5**: UI elements scale appropriately

#### Medium Font Size
- [ ] **Test F.6**: Medium font button activates 1.0em size (default)
- [ ] **Test F.7**: Text displays at comfortable reading size
- [ ] **Test F.8**: Button shows active state when selected
- [ ] **Test F.9**: All subtitle content adapts to new size

#### Large Font Size
- [ ] **Test F.10**: Large font button activates 1.1em size
- [ ] **Test F.11**: Text is clearly enlarged and readable
- [ ] **Test F.12**: Button shows active state when selected
- [ ] **Test F.13**: All subtitle content adapts to new size
- [ ] **Test F.14**: No content overflow or layout breaking

#### Extra Large Font Size
- [ ] **Test F.15**: XL font button activates 1.3em size
- [ ] **Test F.16**: Text is significantly larger but not overwhelming
- [ ] **Test F.17**: Button shows active state when selected
- [ ] **Test F.18**: All subtitle content adapts to new size
- [ ] **Test F.19**: Layout remains stable with larger text

#### Font Size Persistence
- [ ] **Test F.20**: Font size preference persists after page refresh
- [ ] **Test F.21**: Font size preference persists across sessions
- [ ] **Test F.22**: Font size preference survives browser restart
- [ ] **Test F.23**: Different users maintain separate font preferences

### User Preference Validation

#### localStorage Functionality
- [ ] **Test L.1**: Preferences saved to localStorage correctly
- [ ] **Test L.2**: Invalid preferences are handled gracefully
- [ ] **Test L.3**: localStorage errors don't break functionality
- [ ] **Test L.4**: Preferences load correctly on initialization
- [ ] **Test L.5**: Preference format validation works properly

#### Cross-Session Persistence
- [ ] **Test S.1**: Open new browser tab - preferences maintained
- [ ] **Test S.2**: Close and reopen browser - preferences maintained
- [ ] **Test S.3**: Clear cookies but not localStorage - preferences maintained
- [ ] **Test S.4**: Incognito/private mode uses defaults appropriately

### Responsive Behavior with Customizations

#### Mobile Column Width Adaptation
- [ ] **Test R.1**: Column width preferences respect mobile stacking
- [ ] **Test R.2**: Font size controls remain functional on mobile
- [ ] **Test R.3**: Touch interactions work with customization controls
- [ ] **Test R.4**: Customizations don't break mobile layout

#### Tablet Adaptation
- [ ] **Test R.5**: Column preferences adapt to tablet layout
- [ ] **Test R.6**: Font sizes scale appropriately for tablet screens
- [ ] **Test R.7**: Control buttons remain accessible on tablets

### Accessibility with Customizations

#### High Contrast Mode
- [ ] **Test A.1**: Font size changes work with high contrast
- [ ] **Test A.2**: Column width changes maintain contrast
- [ ] **Test A.3**: Button states remain visible in high contrast

#### Screen Reader Compatibility
- [ ] **Test A.4**: Font size changes announced to screen readers
- [ ] **Test A.5**: Column width changes announced appropriately
- [ ] **Test A.6**: Button state changes communicated clearly

### Edge Cases and Error Handling

#### Extreme Customizations
- [ ] **Test E.1**: Very large font + narrow column handles gracefully
- [ ] **Test E.2**: Small font + wide column maintains readability
- [ ] **Test E.3**: Rapid customization changes don't cause errors
- [ ] **Test E.4**: Invalid localStorage data handled properly

#### Content Overflow
- [ ] **Test O.1**: Long words wrap appropriately in narrow columns
- [ ] **Test O.2**: Large fonts don't break container bounds
- [ ] **Test O.3**: Scrolling works properly with all combinations
- [ ] **Test O.4**: Text remains selectable in all configurations

## Performance Testing

### Customization Response Time
- [ ] **Test P.1**: Font size changes apply immediately (<100ms)
- [ ] **Test P.2**: Column width changes apply immediately (<100ms)
- [ ] **Test P.3**: Multiple rapid changes don't cause lag
- [ ] **Test P.4**: Preference saving doesn't block UI

## Test Results

### Customization Matrix
| Font Size | Column Width | Mobile | Tablet | Desktop | Status |
|-----------|--------------|--------|--------|---------|--------|
| Small     | Equal        |        |        |         |        |
| Small     | Left         |        |        |         |        |
| Small     | Right        |        |        |         |        |
| Medium    | Equal        |        |        |         |        |
| Large     | Equal        |        |        |         |        |
| XL        | Equal        |        |        |         |        |

### Failed Tests
- List failed test IDs with descriptions

### Performance Issues
- Note any performance concerns with specific combinations

## Test Sign-off

**Tester**: _______________  
**Date**: _______________  
**Status**: [ ] Pass [ ] Fail [ ] Needs Revision