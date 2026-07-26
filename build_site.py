#!/usr/bin/env python3
import os
import re
import shutil
import yaml
import markdown
import http.server
import socketserver

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(ROOT_DIR, "_site")

def load_config():
    config_path = os.path.join(ROOT_DIR, "_config.yml")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_frontmatter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2]
            return fm, body
    return {}, content

def render_includes(html_content, includes_dir):
    def replace_include(match):
        inc_name = match.group(1).strip()
        inc_path = os.path.join(includes_dir, inc_name)
        if os.path.exists(inc_path):
            inc_content = read_file(inc_path)
            return render_includes(inc_content, includes_dir)
        return ""
    
    pattern = r'\{%\s*include\s+([^\s%]+)\s*%\}'
    return re.sub(pattern, replace_include, html_content)

def get_posts():
    posts_dir = os.path.join(ROOT_DIR, "_posts")
    posts = []
    if not os.path.exists(posts_dir):
        return posts

    for filename in sorted(os.listdir(posts_dir), reverse=True):
        if filename.endswith(".md") or filename.endswith(".markdown"):
            filepath = os.path.join(posts_dir, filename)
            fm, body = parse_frontmatter(read_file(filepath))
            
            # Generate permalink url
            slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename.replace('.md', ''))
            category = fm.get('category', 'research').lower().replace(' ', '-')
            url = f"/{category}/{slug}/"

            post_obj = {
                'title': fm.get('title', 'Untitled'),
                'subtitle': fm.get('subtitle', ''),
                'date': str(fm.get('date', '')),
                'category': fm.get('category', 'LLMs'),
                'tags': fm.get('tags', []),
                'read_time': fm.get('read_time', '5 min read'),
                'url': url,
                'excerpt': body[:200] + '...',
                'body_html': markdown.markdown(body, extensions=['fenced_code', 'tables', 'toc'])
            }
            posts.append(post_obj)
    return posts

def compile_site():
    print("🔨 Compiling Jekyll site for preview...")
    config = load_config()

    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR, exist_ok=True)

    # Copy assets
    assets_src = os.path.join(ROOT_DIR, "assets")
    assets_dst = os.path.join(SITE_DIR, "assets")
    if os.path.exists(assets_src):
        shutil.copytree(assets_src, assets_dst)

    includes_dir = os.path.join(ROOT_DIR, "_includes")
    layouts_dir = os.path.join(ROOT_DIR, "_layouts")

    posts = get_posts()

    # Helper liquid variable replacer
    def apply_variables(template, page_dict):
        def repl(m):
            key = m.group(1).strip()
            if key == 'content':
                return page_dict.get('content', '')
            if key.startswith('site.'):
                k = key[5:]
                return str(config.get(k, ''))
            if key.startswith('page.'):
                k = key[5:]
                val = page_dict.get(k, '')
                if k == 'tags' and isinstance(val, list):
                    return " ".join(val)
                return str(val)
            return m.group(0)

        # Basic liquid loop handler for posts
        if "{% for post in site.posts" in template or "{% for post in site.posts offset:0 limit:10 %}" in template:
            # Replace liquid post loop in article-grid / featured-post
            grid_html = ""
            for p in posts:
                tags_html = "".join([f'<span class="tag-pill">#{t}</span>' for t in p['tags']])
                grid_html += f'''
                <article class="article-card" data-category="{p['category']}" data-tags="{" ".join(p['tags'])}">
                    <div>
                        <div class="article-header-meta">
                            <span class="article-category">{p['category']}</span>
                            <span><i class="fa-regular fa-clock"></i> {p['read_time']}</span>
                        </div>
                        <h3 class="article-title" style="margin-top: 0.6rem;">
                            <a href="{p['url']}">{p['title']}</a>
                        </h3>
                        <p class="article-excerpt" style="margin-top: 0.5rem;">
                            {p['subtitle'] or p['excerpt']}
                        </p>
                    </div>
                    <div>
                        <div class="article-tags" style="margin-bottom: 0.75rem;">
                            {tags_html}
                        </div>
                        <div class="article-footer">
                            <span>{p['date'][:10]}</span>
                            <a href="{p['url']}" class="read-more-link">Read <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                </article>
                '''
            template = re.sub(r'\{%\s*for post in site\.posts.*?\%\}.*?\{%\s*endfor\s*%\}', grid_html, template, flags=re.DOTALL)

        # Handlers for liquid tag loops
        if "{% for tag in page.tags %}" in template:
            tag_pills = ""
            for t in page_dict.get('tags', []):
                tag_pills += f'<span class="tag-pill">#{t}</span>'
            template = re.sub(r'\{%\s*for tag in page\.tags\s*%\}.*?\{%\s*endfor\s*%\}', tag_pills, template, flags=re.DOTALL)

        # Handle {% if page.category %} block
        if page_dict.get('category'):
            template = re.sub(r'\{%\s*if page\.category\s*%\}(.*?)\{%\s*endif\s*%\}', r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(r'\{%\s*if page\.category\s*%\}.*?\{%\s*endif\s*%\}', '', template, flags=re.DOTALL)

        # Handle {% if page.subtitle %} block
        if page_dict.get('subtitle'):
            template = re.sub(r'\{%\s*if page\.subtitle\s*%\}(.*?)\{%\s*endif\s*%\}', r'\1', template, flags=re.DOTALL)
        else:
            template = re.sub(r'\{%\s*if page\.subtitle\s*%\}.*?\{%\s*endif\s*%\}', '', template, flags=re.DOTALL)

        # Simple variable substitution
        template = re.sub(r'\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}', repl, template)
        return template

    def render_page(layout_name, page_dict):
        layout_path = os.path.join(layouts_dir, f"{layout_name}.html")
        if not os.path.exists(layout_path):
            return page_dict.get('content', '')
        
        layout_raw = read_file(layout_path)
        fm, layout_body = parse_frontmatter(layout_raw)
        
        # Include expansion
        expanded = render_includes(layout_body, includes_dir)
        
        # Insert content into layout
        expanded = apply_variables(expanded, page_dict)

        # Check if parent layout exists (e.g. home -> default)
        parent_layout = fm.get('layout')
        if parent_layout:
            parent_dict = dict(page_dict)
            parent_dict['content'] = expanded
            return render_page(parent_layout, parent_dict)

        return expanded

    # 1. Render index.md -> index.html
    index_md = read_file(os.path.join(ROOT_DIR, "index.md"))
    fm_index, body_index = parse_frontmatter(index_md)
    page_dict = dict(fm_index)
    page_dict['content'] = markdown.markdown(body_index)
    index_html = render_page(fm_index.get('layout', 'home'), page_dict)
    with open(os.path.join(SITE_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)

    # 2. Render archive.md -> archive.html
    archive_path = os.path.join(ROOT_DIR, "archive.md")
    if os.path.exists(archive_path):
        fm_arc, body_arc = parse_frontmatter(read_file(archive_path))
        page_dict_arc = dict(fm_arc)

        archive_content = ""
        # Build tag index
        tags_map = {}
        for p in posts:
            for t in p['tags']:
                tags_map.setdefault(t, []).append(p)

        for tag_name, tag_posts in tags_map.items():
            archive_content += f'<div style="margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border-subtle);">'
            archive_content += f'<h2 style="font-size: 1.35rem; color: var(--accent-cyan); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;"><i class="fa-solid fa-hashtag"></i> {tag_name}</h2>'
            archive_content += '<ul style="list-style: none; padding-left: 0; display: flex; flex-direction: column; gap: 0.75rem;">'
            for tp in tag_posts:
                archive_content += f'<li style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0.75rem; background: rgba(30, 41, 59, 0.4); border-radius: 8px; border: 1px solid var(--border-subtle);">'
                archive_content += f'<a href="{tp["url"]}" style="font-weight: 600; font-family: var(--font-heading); color: var(--text-primary);">{tp["title"]}</a>'
                archive_content += f'<span style="font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-code);">{tp["date"][:10]}</span>'
                archive_content += '</li>'
            archive_content += '</ul></div>'

        page_dict_arc['content'] = f'''
        <div class="glass-panel" style="padding: 2.5rem; margin: 3rem 0;">
            <div class="section-header">
                <h1 class="section-title gradient-text" style="font-size: 2.25rem;">
                    <i class="fa-solid fa-box-archive"></i> Complete Research Archive
                </h1>
            </div>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 1.05rem;">
                Explore all research notes, mathematical breakdowns, and codebase implementations organized by topic tags.
            </p>
            {archive_content}
        </div>
        '''
        arc_html = render_page(fm_arc.get('layout', 'default'), page_dict_arc)
        with open(os.path.join(SITE_DIR, "archive.html"), 'w', encoding='utf-8') as f:
            f.write(arc_html)

    # 3. Render Posts -> _site/category/slug/index.html
    for p in posts:
        page_dict_p = dict(p)
        page_dict_p['content'] = p['body_html']
        post_html = render_page('post', page_dict_p)
        
        post_out_dir = os.path.join(SITE_DIR, p['url'].strip('/'))
        os.makedirs(post_out_dir, exist_ok=True)
        with open(os.path.join(post_out_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(post_html)

    print("✅ Site successfully compiled into _site/")

def serve_site(port=4000):
    os.chdir(SITE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Serving Neural Navigator Lab locally at http://localhost:{port}")
        print("Press Ctrl+C to stop server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == '__main__':
    compile_site()
    serve_site(port=4000)
