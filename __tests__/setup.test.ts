/**
 * Basic test to verify Jest setup is working
 */
describe('Jest Setup', () => {
  it('should be able to run tests', () => {
    expect(1 + 1).toBe(2)
  })
  
  it('should have access to Jest globals', () => {
    expect(jest).toBeDefined()
    expect(describe).toBeDefined()
    expect(it).toBeDefined()
    expect(expect).toBeDefined()
  })
})