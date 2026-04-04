# Elysium WEB - TODO

## High Priority

- [ ] Make sidebar responsive - add mobile navigation drawer
- [ ] Implement model selection - clicking a model sets it as active for chat
- [ ] Implement search/filter functionality in Models page
- [ ] Fix VOXELS and ARCHIVE nav items to use navigation instead of `<a>` tags
- [ ] Unify header styles between Chat and Models pages
- [ ] Add localStorage persistence for chat sessions

## Medium Priority

- [ ] Add voice input functionality (microphone button)
- [ ] Add file attachment functionality
- [ ] Add session management (save/load/delete sessions)
- [ ] Improve API error handling with specific error messages
- [ ] Add loading states for navigation between pages
- [ ] Implement sort/filter parameters dropdown in Models page

## Low Priority

- [ ] Add animations for page transitions
- [ ] Add keyboard shortcuts help modal
- [ ] Implement Voxels page (placeholder exists)
- [ ] Implement Archive page (placeholder exists)
- [ ] Add dark/light theme toggle
- [ ] Add user settings panel

## Technical Debt

- [ ] Move hardcoded model data to separate config file or API
- [ ] Add proper TypeScript types for all components
- [ ] Extract repeated UI components (Header, Sidebar, MessageBubble)
- [ ] Add error boundaries for better error handling
- [ ] Write unit tests for API functions and components

## Backlog

- [ ] Add markdown rendering for assistant messages
- [ ] Add code syntax highlighting
- [ ] Implement streaming responses from API
- [ ] Add typing indicators
- [ ] Add message reactions
- [ ] Add message editing
