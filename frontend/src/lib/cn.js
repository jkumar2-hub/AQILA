// clsx + tailwind-merge utility — standard shadcn/ui pattern
// M3: Use cn() everywhere instead of raw string concatenation for class names.
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merges class names with Tailwind conflict resolution.
 * @param {...import('clsx').ClassValue} inputs
 * @returns {string}
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
