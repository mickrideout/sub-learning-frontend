/**
 * @jest-environment jsdom
 */
import { render, screen } from '@testing-library/react'
import { Navigation } from '@/components/navigation'

// Mock Next.js components
jest.mock('next/link', () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>
  }
})

jest.mock('next/image', () => {
  return function MockImage({ src, alt }: { src: string; alt: string }) {
    return <img src={src} alt={alt} />
  }
})

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/',
}))

describe('Navigation Component', () => {
  it('renders navigation with SubLearning branding', () => {
    render(<Navigation />)
    
    expect(screen.getByText('SubLearning')).toBeInTheDocument()
  })

  it('renders main navigation links', () => {
    render(<Navigation />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Browse')).toBeInTheDocument()
  })

  it('renders authentication links when not logged in', () => {
    render(<Navigation />)
    
    expect(screen.getByText('Sign In')).toBeInTheDocument()
    expect(screen.getByText('Sign Up')).toBeInTheDocument()
  })
})