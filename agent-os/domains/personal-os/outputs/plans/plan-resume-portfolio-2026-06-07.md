# Project Plan: Resume Portfolio Website (`resume-portfolio`)
Date: 2026-06-07

## 1. Goal
Build and deploy a high-performance, responsive personal resume and portfolio website. The site must showcase engineering projects with interactive elements, load extremely fast, and use an easily updatable content structure (file-based) to ensure low maintenance overhead.

---

## 2. Assumptions
* **Tech Stack**: A static site generator (SSG) like **Astro** or **Vite + React** is preferred over heavy server-rendered frameworks to guarantee fast load times and simple hosting.
* **Content Management**: Content (projects, experience, skills) will be stored in local Markdown or JSON files. This satisfies the "easily updatable" requirement without needing a database or external CMS.
* **Hosting**: The site will be hosted on a global CDN (e.g., GitHub Pages, Vercel, or Netlify) for maximum speed and zero-cost scaling, or containerized and served via Nginx on the existing Oracle VPS. (GitHub Pages/Vercel is recommended to keep frontend traffic separate from the Agent OS VPS).
* **Design**: Mobile-first, clean, professional, and optimized for accessibility and performance.

---

## 3. Scope

### In Scope
* **Responsive Layout**: Seamless experience across mobile, tablet, and desktop.
* **Interactive Project Showcase**: A dedicated section where users can filter projects by technology tags (e.g., Python, React, Docker) and view project details.
* **Optimized Media**: Automatic image compression, modern formats (WebP/AVIF), and lazy loading.
* **Structured Content**: Markdown/JSON schemas for easy updates to experience, projects, and skills.
* **CI/CD Pipeline**: Automated build and deployment on git push.

### Out of Scope
* **Database/CMS Integration**: No external databases, WordPress, or headless CMS.
* **User Authentication**: No login or admin portal (updates are made via git).
* **Complex Backend**: No custom backend API (contact forms will use static form handlers or simple mailto links).
* **Heavy Animations**: No heavy 3D libraries (e.g., Three.js) that degrade performance and load times.

---

## 4. Milestones
* **Milestone 1: Architecture & Tech Stack Setup** (Astro + Tailwind CSS, content schemas defined)
* **Milestone 2: Core Responsive UI** (Hero, Experience, and Skills sections implemented)
* **Milestone 3: Interactive Project Showcase** (Project grid, tag filtering, and detail modals/pages)
* **Milestone 4: Performance Optimization & Content Population** (Asset optimization, real data entry, Lighthouse audit)
* **Milestone 5: Deployment & CI/CD** (Production deployment, custom domain, automated workflow)

---

## 5. Step-by-Step Plan

### Phase 1: Setup & Architecture (Milestone 1)
* **Step 1.1**: Initialize the repository using Astro (recommended for content-heavy static sites) and Tailwind CSS.
* **Step 1.2**: Define the content structure:
  * Create `src/content/projects/` for project Markdown files (metadata: title, description, tags, image, github_url, live_url).
  * Create `src/content/experience/` for work history Markdown files.
* **Step 1.3**: Set up global layout, typography, and dark/light mode configuration.

### Phase 2: Core Responsive UI (Milestone 2)
* **Step 2.1**: Build the Navigation and Footer components (ensure mobile-responsive hamburger menu).
* **Step 2.2**: Implement the Hero section (clean introduction, call-to-action to resume/contact).
* **Step 2.3**: Implement the Experience timeline component, dynamically rendering from the local Markdown files.
* **Step 2.4**: Implement the Skills grid (categorized by languages, frameworks, tools).

### Phase 3: Interactive Project Showcase (Milestone 3)
* **Step 3.1**: Build the Project Card component to display project thumbnail, title, short description, and technology tags.
* **Step 3.2**: Implement client-side interactive filtering (allow users to click tags to filter projects instantly).
* **Step 3.3**: Create project detail views (either lightweight modal overlays or dedicated static subpages generated from Markdown).

### Phase 4: Optimization & Content (Milestone 4)
* **Step 4.1**: Populate the site with real, high-quality project descriptions and professional experience.
* **Step 4.2**: Optimize all images: convert to WebP, resize to target display resolutions, and configure Astro's built-in image optimization.
* **Step 4.3**: Run Lighthouse/PageSpeed audits. Optimize CSS, eliminate render-blocking resources, and ensure a 95+ performance score.

### Phase 5: Deployment & CI/CD (Milestone 5)
* **Step 5.1**: Configure deployment target (e.g., GitHub Pages via GitHub Actions, or Vercel).
* **Step 5.2**: Set up custom domain and SSL certificate.
* **Step 5.3**: Perform final cross-browser testing (Safari, Chrome, Firefox) and mobile device testing.

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Heavy media slows down load times** | High | Use Astro's native `<Image />` component to automatically compress, resize, and convert images to WebP. Implement lazy loading for all off-screen assets. |
| **Maintenance overhead for updates** | Medium | Keep content strictly file-based (Markdown/JSON). Updating the site should be as simple as adding a new `.md` file to the projects folder and pushing to GitHub. |
| **VPS resource competition** | Low | If hosted on the Oracle VPS, serve the site as pre-rendered static files via Nginx. This consumes negligible CPU/RAM, leaving VPS resources free for the Gemini Agent OS. |

---

## 7. Decisions Needed
1. **Framework Choice**: Confirm Astro + Tailwind CSS as the stack (highly recommended for performance and Markdown integration).
2. **Hosting Target**: Decide between GitHub Pages/Vercel (free, globally distributed CDN, zero maintenance) or hosting on the Oracle VPS (keeps everything self-hosted but requires Nginx configuration).
3. **Contact Form**: Decide between a simple `mailto:` link or a lightweight, free third-party form handler (e.g., Formspree, Web3Forms).

---

## 8. Cut Order (If Timeline/Resources Shrink)
1. **Interactive Tag Filtering**: Fall back to a static grid displaying all projects without client-side filtering.
2. **Project Detail Modals/Subpages**: Fall back to linking project cards directly to their respective GitHub repositories or live external sites.
3. **Custom Contact Form**: Fall back to a simple, styled `mailto:` email button.
4. **Multi-page Layout**: Fall back to a single-page resume layout.

---

## 9. Next Action
* **Action**: Confirm framework choice (Astro vs. React/Vite) and hosting target (GitHub Pages vs. Oracle VPS) with Damian to initialize the repository.