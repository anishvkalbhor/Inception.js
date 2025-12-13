import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher([
  '/chat(.*)',
  '/upload(.*)',
  '/search(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  // TEMPORARY: Disable Clerk protection for offline mode testing
  // TODO: Re-enable when network is available
  
  // if (isProtectedRoute(req)) {
  //   await auth.protect()
  // }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}