# Building Modern Web Applications with HTMX, Hyperscript, and FastAPI

![HTMX / Hyperscript Example Application title slide](docs/images/title_slide.png)

## Introduction

In today's web development landscape, creating interactive, responsive web applications often means reaching for heavy JavaScript frameworks like React, Angular, or Vue. But what if there was a simpler way? What if we could build dynamic, modern web applications with minimal JavaScript, leveraging the power of HTML and HTTP instead?

This repository demonstrates exactly that: a modern web application built with [HTMX](https://htmx.org/), [Hyperscript](https://hyperscript.org/), and [FastAPI](https://fastapi.tiangolo.com/). It's the companion code to a presentation I gave at work, showcasing how these technologies can work together to create a responsive, interactive web application with significantly less code and complexity than traditional JavaScript frameworks.

## What is HTMX?

HTMX is a small (~14KB min.gz), dependency-free JavaScript library that allows you to access modern browser features directly from HTML, rather than using JavaScript. With HTMX, you can:

- Make AJAX requests directly from HTML elements
- Implement WebSockets and Server-Sent Events
- Perform complex DOM updates without writing JavaScript
- Create smooth CSS transitions between page states

HTMX follows the HATEOAS (Hypermedia as the Engine of Application State) principle, allowing your web application to be driven by hypermedia controls provided by the server.

## What is Hyperscript?

Hyperscript is a small, elegant scripting language designed for handling user interactions on the web. It's inspired by HyperTalk and provides a readable, approachable syntax for defining behaviors directly in your HTML. Hyperscript complements HTMX by handling client-side interactions that don't require server communication.

With Hyperscript, you can:
- Handle user events (clicks, hovers, etc.)
- Manipulate the DOM
- Manage state
- Create animations
- And much more, all with a syntax that's more readable than JavaScript

## Why Use HTMX and Hyperscript?

The combination of HTMX and Hyperscript offers several advantages:

1. **Simplicity**: Write less code and focus on your application logic
2. **Performance**: Smaller payload sizes and targeted DOM updates
3. **Maintainability**: More declarative, easier to understand code
4. **Progressive Enhancement**: Works with or without JavaScript
5. **Server-Side Rendering**: Leverage the power of server-side templates

## FastAPI Backend

This application is powered by [FastAPI](https://fastapi.tiangolo.com/), a modern, high-performance web framework for building APIs with Python. FastAPI provides:

- High performance, on par with NodeJS and Go
- Automatic API documentation with OpenAPI
- Data validation with Pydantic
- Asynchronous request handling
- Type hints that help with development

The backend uses SQLModel to interact with a SQLite database (the [Chinook sample database](https://www.sqlitetutorial.net/sqlite-sample-database/)), providing a clean API for our HTMX frontend to consume.

## Example Application

The application in this repository demonstrates how to build a music library browser using HTMX, Hyperscript, and FastAPI. It showcases:

- Dynamic content loading without page refreshes
- Sorting and filtering data
- Pagination
- Modal dialogs
- Form submissions
- And more, all with minimal JavaScript

### Key Features Demonstrated

#### Server-Side Rendering with Partial Updates

Instead of sending JSON and rendering it client-side, the server sends HTML fragments that HTMX swaps directly into the DOM. This approach:

- Reduces client-side complexity
- Leverages server-side templates (Jinja2 in this case)
- Minimizes the amount of data transferred

```html
<!-- Example: Loading artist data with HTMX -->
<div 
    id="application-content"
    hx-get="/application/template/artists"
    hx-trigger="load from:body"
>
</div>
```

#### Client-Side Interactions with Hyperscript

Hyperscript handles client-side interactions that don't require server communication:

```html
<!-- Example: Tab switching with Hyperscript -->
<li
    id="artists-tab"
    hx-get="/application/template/artists"
    hx-trigger="click, updateDisplay"
    hx-target="#application-content"
    class="is-active"
    data-tab="artists"
    _=" on click or updateDisplay
      -- Reset other <li> elements 
      set items to <li/> in closest <ul/>
      remove .is-active from items
      add .is-active to me
    "
>
    <a>
        <span class="icon"><i class="fas fa-microphone"></i></span>
        <span>Artists</span>
    </a>
</li>
```

#### Pagination

The application demonstrates server-side pagination with HTMX:

```html
<!-- Pagination controls -->
<nav class="pagination" role="navigation" aria-label="pagination">
    <ul class="pagination-list">
        {% for link in pagination_links %}
            {% if link == "..." %}
                <li><span class="pagination-ellipsis">&hellip;</span></li>
            {% else %}
                <li>
                    <a 
                        class="pagination-link {% if link == current_page %}is-current{% endif %}"
                        hx-get="/application/{{ tab }}?current_page={{ link }}&items_per_page={{ items_per_page }}"
                        hx-target="#table-content"
                    >
                        {{ link }}
                    </a>
                </li>
            {% endif %}
        {% endfor %}
    </ul>
</nav>
```

#### Sorting and Filtering

The application allows for dynamic sorting and filtering of data:

```html
<!-- Column header with sorting -->
<th 
    hx-get="/application/artists?sort=artist_name&direction=asc" 
    hx-target="#table-content"
    data-sort="artist"
>
    Artist Name
    <span class="icon"><i class="fas fa-sort"></i></span>
</th>
```

## Architecture

The application follows a clean architecture:

1. **FastAPI Backend**: Provides REST API endpoints and HTML templates
2. **Jinja2 Templates**: Server-side rendering of HTML
3. **HTMX**: Handles AJAX requests and DOM updates
4. **Hyperscript**: Manages client-side interactions
5. **Bulma CSS**: Provides styling without JavaScript dependencies

This architecture allows for a clean separation of concerns while minimizing the amount of JavaScript needed.

## Benefits Over Traditional SPA Frameworks

Compared to traditional Single Page Application (SPA) frameworks like React, Angular, or Vue, this approach offers several benefits:

1. **Smaller Bundle Size**: No need for large JavaScript frameworks
2. **Simpler Mental Model**: HTML-first approach is easier to understand
3. **Better Performance**: Less client-side processing and smaller payloads
4. **Progressive Enhancement**: Works even with JavaScript disabled
5. **SEO-Friendly**: Server-rendered content is easier for search engines to index

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (optional)

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/htmx_presentation.git
   cd htmx_presentation
   ```

2. Create a virtual environment and install dependencies using the 
[uv dependency management tool](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Run the application:
   ```bash
   cd project/app
   uvicorn project.app.main:app --reload
   ```

4. Open your browser to http://localhost:8000

### Using Docker

Alternatively, you can use Docker:

```bash
docker-compose up
```

## Conclusion

HTMX and Hyperscript, combined with FastAPI, offer a compelling alternative to traditional JavaScript frameworks for building modern web applications. This approach leverages the strengths of both the server and the client, resulting in applications that are simpler, faster, and more maintainable.

By returning to a hypermedia-driven approach while still providing modern interactivity, we can build web applications that are both powerful and simple.

## Resources

- [HTMX Documentation](https://htmx.org/docs/)
- [Hyperscript Documentation](https://hyperscript.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Bulma CSS Framework](https://bulma.io/)
