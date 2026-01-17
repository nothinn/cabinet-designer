# Dynamic Preview System for Cabinet Designer

## Overview

This document explains the dynamic preview system that allows viewing previews of any branch or pull request without requiring separate GitHub Pages deployments.

## How It Works

### 1. Preview Index Page (`preview-index.html`)

The preview index page dynamically fetches all branches and pull requests from the GitHub API and displays them with dynamic preview links.

**Features:**
- Fetches branches from `https://api.github.com/repos/nothinn/cabinet-designer/branches`
- Fetches open PRs from `https://api.github.com/repos/nothinn/cabinet-designer/pulls?state=open`
- Creates dynamic preview URLs for all branches and PRs
- Shows preview type (production, branch, or PR)
- Includes last updated date

### 2. Dynamic Preview Page (`preview.html`)

The dynamic preview page loads content directly from GitHub's raw content delivery network.

**Features:**
- Accepts query parameters: `?branch=branch-name` or `?pr=pr-number`
- Fetches the `index.html` file from the specified branch or PR
- Displays preview information including source, type, and commit hash
- Loads the content in an iframe for a seamless experience
- Shows a loading spinner while fetching content
- Handles errors gracefully

### 3. Dynamic Preview URLs

The system creates dynamic preview URLs that follow this pattern:

- **Branches**: `https://nothinn.github.io/cabinet-designer/preview.html?branch=branch-name`
- **Pull Requests**: `https://nothinn.github.io/cabinet-designer/preview.html?pr=pr-number`

### 4. Content Loading

The preview page loads content from GitHub's raw content URLs:

- **Branches**: `https://raw.githubusercontent.com/nothinn/cabinet-designer/branch-name/index.html`
- **Pull Requests**: `https://raw.githubusercontent.com/head-repo/head-branch/index.html`

## Benefits

### 1. No Separate Deployments Required

Unlike traditional branch previews that require separate GitHub Pages deployments, this system loads content directly from GitHub's raw content delivery network. This means:

- No need to configure complex deployment workflows
- No environment protection rule conflicts
- Instant previews without waiting for deployments

### 2. Real-Time Previews

Since the content is loaded directly from GitHub, the previews are always up-to-date with the latest changes in the repository.

### 3. Support for All Branches and PRs

The system supports previews for:
- All branches in the repository
- All open pull requests
- Any commit in any branch

### 4. Seamless User Experience

The preview system provides a seamless experience:
- Loading indicators show progress
- Error messages are clear and helpful
- Preview information is displayed prominently
- The content is loaded in an iframe for isolation

## Limitations

### 1. PyScript Limitations

Since PyScript requires specific loading conditions, some PyScript features may not work perfectly in the dynamic preview. The system includes a warning banner to inform users about this limitation.

### 2. Relative Path Issues

Some relative paths in the original HTML may not work correctly in the dynamic preview. The system attempts to fix these issues by using a `<base>` tag and adjusting paths.

### 3. CORS Restrictions

Due to browser security restrictions (CORS), some resources may not load correctly in the preview. This is a limitation of loading content from raw GitHub URLs.

## Usage

### Viewing a Branch Preview

To view a preview of a specific branch:

1. Go to the preview index: `https://nothinn.github.io/cabinet-designer/preview-index.html`
2. Click on any branch name (except `main`)
3. The dynamic preview will load automatically

Or directly:
```
https://nothinn.github.io/cabinet-designer/preview.html?branch=branch-name
```

### Viewing a Pull Request Preview

To view a preview of a specific pull request:

1. Go to the preview index: `https://nothinn.github.io/cabinet-designer/preview-index.html`
2. Click on any pull request
3. The dynamic preview will load automatically

Or directly:
```
https://nothinn.github.io/cabinet-designer/preview.html?pr=pr-number
```

## Technical Implementation

### Preview Index JavaScript

The preview index uses the following JavaScript to fetch and display previews:

```javascript
async function loadPreviews() {
    try {
        // Fetch from GitHub API
        const [branchesResponse, prsResponse] = await Promise.all([
            fetch('https://api.github.com/repos/nothinn/cabinet-designer/branches'),
            fetch('https://api.github.com/repos/nothinn/cabinet-designer/pulls?state=open')
        ]);

        const branches = await branchesResponse.json();
        const prs = await prsResponse.json();

        // Create preview data with dynamic URLs
        allPreviews = [
            // Main branch (production)
            ...branches.filter(b => b.name === 'main').map(b => ({
                name: b.name,
                url: 'https://nothinn.github.io/cabinet-designer/',
                type: 'production',
                updated_at: b.commit.commit.author.date
            })),
            // Other branches (dynamic previews)
            ...branches.filter(b => b.name !== 'main').map(b => ({
                name: b.name,
                url: `https://nothinn.github.io/cabinet-designer/preview.html?branch=${b.name}`,
                type: 'branch',
                updated_at: b.commit.commit.author.date
            })),
            // Pull requests (dynamic previews)
            ...prs.map(pr => ({
                name: `pr-${pr.number}-${pr.head.ref}`,
                url: `https://nothinn.github.io/cabinet-designer/preview.html?pr=${pr.number}`,
                type: 'pr',
                updated_at: pr.updated_at
            }))
        ];
    } catch (error) {
        // Handle errors
    }
}
```

### Dynamic Preview JavaScript

The dynamic preview page uses the following JavaScript to load content:

```javascript
async function loadPreview() {
    try {
        // Get content from GitHub raw URLs
        const contentUrl = branch 
            ? `https://raw.githubusercontent.com/nothinn/cabinet-designer/${branch}/index.html`
            : `https://raw.githubusercontent.com/head-repo/head-branch/index.html`;

        const contentResponse = await fetch(contentUrl);
        const htmlContent = await contentResponse.text();

        // Create dynamic HTML
        const dynamicHtml = createDynamicPreview(htmlContent);

        // Load in iframe
        const blob = new Blob([dynamicHtml], { type: 'text/html' });
        previewIframe.src = URL.createObjectURL(blob);
    } catch (error) {
        // Handle errors
    }
}
```

## Future Enhancements

### 1. Caching

Implement caching to improve performance and reduce GitHub API calls.

### 2. Authentication

Add support for authenticated requests to avoid GitHub API rate limits.

### 3. Better Error Handling

Enhance error handling for various edge cases and network issues.

### 4. PyScript Support

Improve PyScript support in dynamic previews.

### 5. Mobile Optimization

Further optimize the preview experience for mobile devices.

## Conclusion

The dynamic preview system provides a powerful and flexible way to preview any branch or pull request without requiring separate deployments. It leverages GitHub's raw content delivery network to provide real-time previews with minimal configuration and maintenance overhead.