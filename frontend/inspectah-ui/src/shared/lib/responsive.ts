export const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
};

export function isMobile(width: number): boolean {
  return width < breakpoints.md;
}

export function isTablet(width: number): boolean {
  return width >= breakpoints.md && width < breakpoints.lg;
}

export function isDesktop(width: number): boolean {
  return width >= breakpoints.lg;
}
