---
layout: default
title: Research Archive
description: Complete index of all published AI research notes and experiments.
---

<div class="glass-panel" style="padding: 2.5rem; margin: 3rem 0;">

    <div class="section-header">
        <h1 class="section-title gradient-text" style="font-size: 2.25rem;">
            <i class="fa-solid fa-box-archive"></i> Complete Research Archive
        </h1>
    </div>

    <p style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 1.05rem;">
        Explore all research notes, mathematical breakdowns, and codebase implementations organized by topic tags.
    </p>

    {% for tag in site.tags %}
    <div style="margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border-subtle);">
        <h2 style="font-size: 1.35rem; color: var(--accent-cyan); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <i class="fa-solid fa-hashtag"></i> {{ tag[0] }}
        </h2>
        <ul style="list-style: none; padding-left: 0; display: flex; flex-direction: column; gap: 0.75rem;">
            {% for post in tag[1] %}
            <li style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; padding: 0.5rem 0.75rem; background: rgba(30, 41, 59, 0.4); border-radius: 8px; border: 1px solid var(--border-subtle);">
                <a href="{{ post.url }}" style="font-weight: 600; font-family: var(--font-heading); color: var(--text-primary);">
                    {{ post.title }}
                </a>
                <span style="font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-code);">
                    {{ post.date | date: "%B %d, %Y" }}
                </span>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}

</div>