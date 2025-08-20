// Type declarations for lucide-react
declare module 'lucide-react' {
  import { ComponentType } from 'react'
  
  export interface IconProps {
    size?: string | number
    color?: string
    strokeWidth?: string | number
    className?: string
  }

  // All lucide-react icons - comprehensive list
  export const Eye: ComponentType<IconProps>
  export const EyeOff: ComponentType<IconProps>
  export const Mail: ComponentType<IconProps>
  export const Lock: ComponentType<IconProps>
  export const User: ComponentType<IconProps>
  export const Users: ComponentType<IconProps>
  export const Settings: ComponentType<IconProps>
  export const LogOut: ComponentType<IconProps>
  export const Menu: ComponentType<IconProps>
  export const X: ComponentType<IconProps>
  export const Search: ComponentType<IconProps>
  export const Play: ComponentType<IconProps>
  export const Pause: ComponentType<IconProps>
  export const SkipBack: ComponentType<IconProps>
  export const SkipForward: ComponentType<IconProps>
  export const Bookmark: ComponentType<IconProps>
  export const BookmarkPlus: ComponentType<IconProps>
  export const Star: ComponentType<IconProps>
  export const TrendingUp: ComponentType<IconProps>
  export const Clock: ComponentType<IconProps>
  export const Target: ComponentType<IconProps>
  export const BarChart3: ComponentType<IconProps>
  export const Activity: ComponentType<IconProps>
  export const ChevronDown: ComponentType<IconProps>
  export const ChevronUp: ComponentType<IconProps>
  export const ChevronLeft: ComponentType<IconProps>
  export const ChevronRight: ComponentType<IconProps>
  export const Check: ComponentType<IconProps>
  export const Circle: ComponentType<IconProps>
  export const BookOpen: ComponentType<IconProps>
  export const Languages: ComponentType<IconProps>
  export const ArrowRight: ComponentType<IconProps>
  export const ArrowLeft: ComponentType<IconProps>
  export const MoreHorizontal: ComponentType<IconProps>
  export const CheckIcon: ComponentType<IconProps>
  export const ChevronDownIcon: ComponentType<IconProps>
  export const ChevronLeftIcon: ComponentType<IconProps>
  export const ChevronRightIcon: ComponentType<IconProps>
  export const ChevronUpIcon: ComponentType<IconProps>
  export const XIcon: ComponentType<IconProps>
  export const SearchIcon: ComponentType<IconProps>
  export const CircleIcon: ComponentType<IconProps>
  export const MinusIcon: ComponentType<IconProps>
  export const MoreHorizontalIcon: ComponentType<IconProps>
  export const GripVerticalIcon: ComponentType<IconProps>
  export const PanelLeftIcon: ComponentType<IconProps>
  
  // Export all other icons as a generic type
  const LucideIcon: ComponentType<IconProps>
  export default LucideIcon
}