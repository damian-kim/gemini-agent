# Product Requirement Document (PRD)
## Project: Resume Portfolio Website
**Slug:** `resume-portfolio`  
**Date:** 2026-06-07  
**Author:** Gemini Agent OS (on behalf of Damian Kim)  
**Status:** Planning  

---

### 1. Executive Summary
The **Resume Portfolio Website** is a high-performance, responsive personal website designed to showcase Damian Kim's technical stack, complex engineering projects, and professional background. The site will serve as his primary professional landing page, optimized for speed, search engines (SEO), and seamless reading on both mobile and desktop devices. It will leverage a static-site generation (SSG) architecture to ensure near-instantaneous load times and zero-maintenance hosting.

---

### 2. Problem and Context
Damian needs a modern, professional online presence that accurately reflects his engineering capabilities. Existing portfolio builders (e.g., Squarespace, WordPress) introduce unnecessary bloat, slow load times, and high maintenance overhead. 

To stand out to recruiters, hiring managers, and technical collaborators, Damian requires a custom-built, developer-centric portfolio that:
1. Loads instantly (sub-second page loads).
2. Showcases complex technical projects with rich media and clean code snippets.
3. Is trivial to update via standard Git workflows (Markdown/MDX).
4. Demonstrates clean frontend engineering practices.

---

### 3. Goals and Non-Goals

#### Goals
*   **Ultra-High Performance:** Achieve a 100/100 Lighthouse performance score. Page load times under 1.2 seconds (Largest Contentful Paint) on mobile connections.
*   **Responsive & Accessible:** Fully responsive design (mobile, tablet, desktop) adhering to WCAG AA accessibility standards.
*   **Markdown-Driven Content:** All projects, experience, and blog/research posts must be manageable via local Markdown/MDX files.
*   **Modern Aesthetics:** Clean, minimalist developer-focused UI with a system-matching dark/light mode toggle.
*   **Zero-Cost Hosting:** Deployable to a global CDN edge network (e.g., Cloudflare Pages or Vercel) within the free tier.

#### Non-Goals
*   **No Dynamic Database:** The site will not use a live database (PostgreSQL, MongoDB, etc.). All content is compiled at build time.
*   **No User Authentication:** No login portal, admin dashboard, or user comments section.
*   **No Complex Backend:** No custom API server is required for the portfolio itself (contact forms will use a third-party static form handler).

---

### 4. Users and Use Cases

#### Users
1.  **Technical Recruiters & Hiring Managers:** Looking for quick access to Damian's resume, core skills, contact details, and high-level project summaries.
2.  **Technical Interviewers & Engineers:** Looking to dive deep into Damian's code quality, architecture decisions, and complex project write-ups.
3.  **Damian Kim (Owner):** Wants to update his resume, add a new project, or write a technical note quickly by pushing a Markdown file to GitHub.

#### Key Use Cases
*   *Use Case 1: Quick Scan.* A recruiter opens the site on a mobile device, immediately sees the core value proposition, downloads the PDF resume, and views the contact info in under 10 seconds.
*   *Use Case 2: Deep Dive.* An engineer clicks on a featured project, reads a detailed case study with embedded code blocks, system architecture diagrams, and links to the GitHub repository.
*   *Use Case 3: Content Update.* Damian completes a project, writes a quick Markdown file in VS Code, commits it, and the site automatically redeploys via CI/CD.

---

### 5. Requirements

#### Functional Requirements
*   **Homepage:** Minimalist hero section, core technical stack badges, featured projects grid, and a brief professional bio.
*   **Projects Section:** Filterable grid of projects by tag/technology. Individual project pages rendered from Markdown/MDX.
*   **Interactive Resume:** A clean, timeline-based view of professional experience and education, with a prominent "Download PDF" button.
*   **Contact Form:** A simple, validated contact form integrated with a static form provider (e.g., Formspree, Web3Forms, or Cloudflare Turnstile).
*   **Theme Toggle:** Persistent dark/light mode toggle based on user preference and system settings.

#### Non-Functional Requirements
*   **Framework:** Astro (Static Site Generation mode) for optimal performance and minimal client-side JavaScript.
*   **Styling:** Tailwind CSS for rapid, utility-first responsive styling.
*   **SEO & Metadata:** Open Graph (OG) tags for rich link previews on LinkedIn, Twitter, and GitHub. Automatic XML sitemap generation.
*   **Image Optimization:** Automatic WebP/AVIF conversion and responsive resizing for all project screenshots and media assets.

---

### 6. Architecture / Approach

```
+---------------------------------------------------------------+
|                         Astro (SSG)                           |
+---------------------------------------------------------------+
       |                         |                        |
       v                         v                        v
+--------------+          +--------------+         +------------+
|  Markdown/   |          | Tailwind CSS |         | Assets     |
|  MDX Content |          |  (Styling)   |         | (Optimized)|
+--------------+          +--------------+         +------------+
       |                         |                        |
       +-------------------------+------------------------+
                                 |
                                 v
                     +-----------------------+
                     |  Static Build Output  |
                     +-----------------------+
                                 |
                                 v
                     +-----------------------+
                     |   Cloudflare Pages    |
                     +-----------------------+
```

*   **Framework Choice:** **Astro** is selected over Next.js because it outputs zero client-side JavaScript by default, resulting in superior performance for content-heavy sites.
*   **Content Management:** Astro's native **Content Collections** will be used to enforce strict TypeScript schemas on Markdown frontmatter.
*   **Deployment:** **Cloudflare Pages** connected to the GitHub repository. Every push to `main` triggers an automated build and edge deployment.

---

### 7. Data Model (Content Collections Schema)

Astro Content Collections will enforce the following schemas:

#### Projects Schema (`src/content/projects/`)
```typescript
import { z, defineCollection } from 'astro:content';

const projectsCollection = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishDate: z.date(),
    tags: z.array(z.string()),
    image: z.string().optional(),
    githubUrl: z.string().url().optional(),
    liveUrl: z.string().url().optional(),
    featured: z.boolean().default(false),
  })
});
```

#### Experience Schema (`src/content/experience/`)
```typescript
const experienceCollection = defineCollection({
  schema: z.object({
    role: z.string(),
    company: z.string(),
    location: z.string(),
    startDate: z.string(), // e.g., "June 2024"
    endDate: z.string(),   // e.g., "Present" or "August 2025"
    current: z.boolean().default(false),
    highlights: z.array(z.string()),
  })
});
```

---

### 8. Build Plan

#### Phase 1: Setup & Architecture (Estimated: 2 hours)
*   Initialize Astro project with Tailwind CSS template.
*   Configure TypeScript, ESLint, and Prettier.
*   Set up directory structure (`src/components`, `src/layouts`, `src/content`).
*   Configure Astro Content Collections for `projects` and `experience`.

#### Phase 2: Content & Data Layer (Estimated: 2 hours)
*   Create initial Markdown files for Damian's existing projects (including Gemini Agent OS and Resume Portfolio).
*   Populate professional experience Markdown files.
*   Verify TypeScript schema validation during the build process.

#### Phase 3: UI/UX Implementation (Estimated: 3 hours)
*   Build responsive Layout component (Header, Footer, Theme Toggle).
*   Implement Homepage hero, skills grid, and featured projects list.
*   Implement Projects index page with client-side tag filtering (using minimal vanilla JS or Astro islands).
*   Implement individual Project MDX rendering with syntax highlighting for code blocks.
*   Design and build the interactive Resume timeline.

#### Phase 4: Optimization & SEO (Estimated: 1 hour)
*   Integrate Astro's `<Image />` component for asset optimization.
*   Configure SEO meta tags, Open Graph images, and `robots.txt`.
*   Generate XML sitemap.
*   Run local Lighthouse audits and resolve performance bottlenecks.

#### Phase 5: Deployment & CI/CD (Estimated: 1 hour)
*   Create a GitHub repository for `resume-portfolio`.
*   Configure Cloudflare Pages deployment pipeline.
*   Set up custom domain and SSL.
*   Verify contact form submission pipeline.

---

### 9. Risks and Guardrails

| Risk | Impact | Mitigation Guardrail |
| :--- | :--- | :--- |
| **Asset Bloat** (Large project screenshots slowing down mobile load times) | High | Use Astro's built-in image optimization component to automatically compress, resize, and convert images to `.webp` format at build time. |
| **Broken Links / Missing Metadata** | Medium | Implement automated build-time checks. Use Astro's sitemap generator and run a post-build link checker. |
| **Form Spam** | Medium | Integrate Cloudflare Turnstile (lightweight, privacy-focused CAPTCHA alternative) or use built-in honeypot fields on the contact form. |

---

### 10. Open Questions

1.  **Domain Strategy:** Will this site be hosted on a custom domain (e.g., `damiankim.com` / `damian.dev`) or as a subdomain of an existing domain?
2.  **Resume PDF Generation:** Should the PDF resume be manually uploaded and linked, or should we implement a print stylesheet that allows printing the interactive resume page directly to a clean PDF? (Recommendation: Start with a manually curated PDF link for pixel-perfect layout control).
3.  **Analytics:** Do we want lightweight, privacy-respecting analytics (e.g., Cloudflare Web Analytics or Plausible) to track visitor counts and referral sources without cookies?