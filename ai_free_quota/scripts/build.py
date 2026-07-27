#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "ai-free-quotas.json"
SOURCE_DIR = ROOT / "src"
TEMPLATE_DIR = SOURCE_DIR / "templates"
SEO_FILE = SOURCE_DIR / "seo.json"

COPY = {
    "zh": {
        "html_lang": "zh-CN",
        "updated": "最后更新：",
        "eyebrow": "基于官方来源 · 定期核验",
        "answer_title": "有哪些可以免费使用的 AI Token、Credits 和 API？",
        "answer_text": "这份清单覆盖大模型 API、AI 编程工具、智能体、多模态生成和推理平台，并为每条额度保留官方说明、核验日期与注册入口。",
        "notice_title": "使用前请注意",
        "notice_text": "免费额度、适用模型、地区限制和有效期可能变化，请以官方页面及账号中心显示为准。",
        "headers": ("平台", "免费额度说明", "参考文档", "注册入口"),
        "total": "已收录渠道",
        "china": "中国国内入口",
        "international": "国外 / 国际入口",
        "data": "下载 JSON 数据",
        "footer": "持续维护的 AI 免费额度清单",
        "nav_label": "语言导航",
        "expand": "展开详情",
        "collapse": "收起",
    },
    "en": {
        "html_lang": "en",
        "updated": "Last updated:",
        "eyebrow": "Official sources · Verified",
        "answer_title": "Where can developers get free AI tokens, credits, or API trials?",
        "answer_text": "This page lists international AI APIs, model routers, coding tools, agents, and multimodal services with official references, verification dates, and direct signup links.",
        "notice_title": "Important note",
        "notice_text": "Quotas, supported models, regional availability, and expiry dates can change. Verify the official page and account dashboard before use.",
        "headers": ("Platform", "Free quota details", "Reference", "Sign up"),
        "total": "international services",
        "data": "Download JSON data",
        "footer": "Maintained free AI quota list",
        "nav_label": "Language navigation",
        "expand": "Expand details",
        "collapse": "Collapse",
    },
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render(template_name: str, values: dict[str, str]) -> str:
    content = read(TEMPLATE_DIR / template_name)
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", content)))
    if unresolved:
        raise ValueError(f"unresolved template fields in {template_name}: {unresolved}")
    return content


def validate(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    for field in ("updated_at", "date_published"):
        try:
            date.fromisoformat(data[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be an ISO date") from exc

    sections = data.get("sections")
    entries = data.get("entries")
    if not isinstance(sections, list) or not isinstance(entries, list):
        raise ValueError("sections and entries must be arrays")
    section_ids = {section.get("id") for section in sections}
    if section_ids != {"china", "international"}:
        raise ValueError("sections must define china and international")

    seen: set[str] = set()
    required = {
        "id", "category", "platform_zh", "quota_zh", "reference", "signup",
        "verified_at",
    }
    for entry in entries:
        missing = required - entry.keys()
        if missing:
            raise ValueError(f"entry is missing fields: {sorted(missing)}")
        entry_id = entry["id"]
        if entry_id in seen:
            raise ValueError(f"duplicate entry id: {entry_id}")
        seen.add(entry_id)
        if entry["category"] not in section_ids:
            raise ValueError(f"unknown category for {entry_id}")
        if entry["category"] == "international":
            missing_english = {"platform_en", "quota_en"} - entry.keys()
            if missing_english:
                raise ValueError(
                    f"international entry {entry_id} is missing fields: {sorted(missing_english)}"
                )
        try:
            date.fromisoformat(entry["verified_at"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid verified_at for {entry_id}") from exc
        for link_name in ("reference", "signup"):
            link = entry[link_name]
            parsed = urlparse(link.get("url", ""))
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"invalid {link_name} URL for {entry_id}")


def ordered_entries(data: dict[str, Any], categories: set[str]) -> list[dict[str, Any]]:
    selected = [entry for entry in data["entries"] if entry["category"] in categories]
    return [
        pair[1]
        for pair in sorted(
            enumerate(selected),
            key=lambda pair: (pair[1].get("display_order", pair[0]), pair[0]),
        )
    ]


def absolute_url(site_url: str, path: str) -> str:
    return urljoin(site_url.rstrip("/") + "/", path)


def reference_label(item: dict[str, Any], language: str) -> str:
    key = "label_zh" if language == "zh" else "label_en"
    return item["reference"].get(key, "官方说明" if language == "zh" else "Official reference")


def signup_label(item: dict[str, Any], language: str) -> str:
    return "前往官网" if language == "zh" else "Open service"


def canonical_site_url(seo: dict[str, Any]) -> str:
    """Return the primary SEO origin shared by the primary and mirror builds."""
    return os.environ.get("CANONICAL_SITE_URL", seo["canonical_site_url"])


def structured_data(
    data: dict[str, Any],
    seo: dict[str, Any],
    language: str,
    canonical_url: str,
    selected: list[dict[str, Any]],
) -> str:
    zh = language == "zh"
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical_url,
                "url": canonical_url,
                "name": seo["title_zh" if zh else "title_en"],
                "description": seo["description_zh" if zh else "description_en"],
                "datePublished": data["date_published"],
                "dateModified": data["updated_at"],
                "inLanguage": "zh-CN" if zh else "en",
                "author": {"@type": "Person", "name": seo["author"]},
            },
            {
                "@type": "ItemList",
                "numberOfItems": len(selected),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": position,
                        "name": item["platform_zh" if zh else "platform_en"],
                        "url": item["signup"]["url"],
                    }
                    for position, item in enumerate(selected, 1)
                ],
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_rows(
    selected: list[dict[str, Any]],
    language: str,
    id_suffix: str = "",
) -> str:
    zh = language == "zh"
    headers = COPY[language]["headers"]
    rows = []
    for item in selected:
        quota = item["quota_zh" if zh else "quota_en"]
        is_collapsible = len(quota) > (58 if zh else 135)
        quota_details_id = item["id"] + id_suffix + "-quota"
        quota_toggle = ""
        if is_collapsible:
            quota_toggle = (
                '<button class="yw-disclosure quota-toggle" type="button" '
                f'data-quota-toggle data-expand-label="{escape(COPY[language]["expand"])}" '
                f'data-collapse-label="{escape(COPY[language]["collapse"])}" '
                f'aria-controls="{escape(quota_details_id)}" aria-expanded="false">'
                f'{escape(COPY[language]["expand"])}</button>'
            )
        rows.append(render("row.html", {
            "ENTRY_ID": escape(item["id"] + id_suffix),
            "PLATFORM": escape(item["platform_zh" if zh else "platform_en"]),
            "QUOTA": escape(quota),
            "QUOTA_COLLAPSIBLE_CLASS": " is-collapsible" if is_collapsible else "",
            "QUOTA_DETAILS_ID": escape(quota_details_id),
            "QUOTA_TOGGLE": quota_toggle,
            "REFERENCE_HEADER": escape(headers[2]),
            "REFERENCE_URL": escape(item["reference"]["url"]),
            "REFERENCE_LABEL": escape(reference_label(item, language)),
            "SIGNUP_HEADER": escape(headers[3]),
            "SIGNUP_URL": escape(item["signup"]["url"]),
            "SIGNUP_LABEL": escape(signup_label(item, language)),
            "SIGNUP_REL": "noopener noreferrer sponsored" if item["signup"].get("is_referral") else "noopener noreferrer",
        }))
    return "".join(rows)


def render_sections(
    data: dict[str, Any],
    language: str,
    categories: set[str],
    id_suffix: str = "",
) -> str:
    zh = language == "zh"
    headers = COPY[language]["headers"]
    rendered = []
    for section in data["sections"]:
        if section["id"] not in categories:
            continue
        selected = ordered_entries(data, {section["id"]})
        rendered.append(render("section.html", {
            "SECTION_ID": escape(section["id"] + id_suffix),
            "SECTION_TITLE": escape(section["title_zh" if zh else "title_en"]),
            "SECTION_DESCRIPTION": escape(section["description_zh" if zh else "description_en"]),
            "PLATFORM_HEADER": escape(headers[0]),
            "QUOTA_HEADER": escape(headers[1]),
            "REFERENCE_HEADER": escape(headers[2]),
            "SIGNUP_HEADER": escape(headers[3]),
            "ROWS": render_rows(selected, language, id_suffix),
        }))
    return "".join(rendered)


def stat(value: int, label: str) -> str:
    return f'<div class="stat"><strong>{value}</strong><span>{escape(label)}</span></div>'


def render_panel(
    data: dict[str, Any],
    seo: dict[str, Any],
    language: str,
    panel_attributes: str = "",
    data_url: str = "../data/ai-free-quotas.json",
) -> str:
    zh = language == "zh"
    categories = {"china", "international"} if zh else {"international"}
    selected = ordered_entries(data, categories)
    copy = COPY[language]
    suffix = "zh" if zh else "en"
    if zh:
        stats = (
            stat(len(selected), copy["total"])
            + stat(sum(item["category"] == "china" for item in selected), copy["china"])
            + stat(sum(item["category"] == "international" for item in selected), copy["international"])
        )
    else:
        stats = stat(len(selected), copy["total"])
    return render("panel.html", {
        "PANEL_ATTRIBUTES": panel_attributes,
        "EYEBROW": escape(copy["eyebrow"]),
        "SHORT_TITLE": escape(seo["short_title_zh" if zh else "short_title_en"]),
        "DESCRIPTION": escape(seo["description_zh" if zh else "description_en"]),
        "UPDATED_LABEL": escape(copy["updated"]),
        "UPDATED_AT": escape(data["updated_at"]),
        "STATS": stats,
        "ANSWER_TITLE_ID": f"answer-title-{suffix}",
        "ANSWER_TITLE": escape(copy["answer_title"]),
        "ANSWER_TEXT": escape(copy["answer_text"]),
        "SECTIONS": render_sections(
            data,
            language,
            categories,
            f"-{suffix}" if panel_attributes else "",
        ),
        "NOTICE_TITLE_ID": f"notice-title-{suffix}",
        "NOTICE_TITLE": escape(copy["notice_title"]),
        "NOTICE_TEXT": escape(copy["notice_text"]),
        "DATA_URL": data_url,
        "DATA_LABEL": escape(copy["data"]),
        "FOOTER_TEXT": escape(copy["footer"]),
    })


def render_page(data: dict[str, Any], seo: dict[str, Any], language: str) -> str:
    zh = language == "zh"
    copy = COPY[language]
    categories = {"china", "international"} if zh else {"international"}
    selected = ordered_entries(data, categories)
    site_url = canonical_site_url(seo)
    route = "zh/" if zh else "us/"
    canonical = absolute_url(site_url, route)
    root_url = absolute_url(site_url, "")
    zh_url = absolute_url(site_url, "zh/")
    en_url = absolute_url(site_url, "us/")
    title = seo["title_zh" if zh else "title_en"]
    description = seo["description_zh" if zh else "description_en"]
    if zh:
        language_nav = '<a class="yw-language-switch" href="../us/" lang="en">English</a>'
    else:
        language_nav = '<a class="yw-language-switch" href="../zh/" lang="zh-CN">中文</a>'
    return render("page.html", {
        "HTML_LANG": copy["html_lang"],
        "SEO_TITLE": escape(title),
        "DESCRIPTION": escape(description),
        "KEYWORDS": escape(", ".join(seo["keywords_zh" if zh else "keywords_en"])),
        "CANONICAL_URL": escape(canonical),
        "ZH_URL": escape(zh_url),
        "EN_URL": escape(en_url),
        "ROOT_URL": escape(root_url),
        "STRUCTURED_DATA": structured_data(data, seo, language, canonical, selected),
        "LANGUAGE_NAV": language_nav,
        "PANEL": render_panel(data, seo, language),
    })


def render_app(data: dict[str, Any], seo: dict[str, Any]) -> str:
    site_url = canonical_site_url(seo)
    root_url = absolute_url(site_url, "")
    zh_url = absolute_url(site_url, "zh/")
    en_url = absolute_url(site_url, "us/")
    selected = ordered_entries(data, {"china", "international"})
    zh_attributes = (
        f' data-language-panel="zh" data-title="{escape(seo["title_zh"])}"'
        f' data-description="{escape(seo["description_zh"])}"'
    )
    en_attributes = (
        f' data-language-panel="en" data-title="{escape(seo["title_en"])}"'
        f' data-description="{escape(seo["description_en"])}"'
    )
    return render("app.html", {
        "SEO_TITLE": escape(seo["title_zh"]),
        "DESCRIPTION": escape(seo["description_zh"]),
        "KEYWORDS": escape(", ".join(seo["keywords_zh"])),
        "CANONICAL_URL": escape(root_url),
        "ZH_URL": escape(zh_url),
        "EN_URL": escape(en_url),
        "STRUCTURED_DATA": structured_data(data, seo, "zh", root_url, selected),
        "ZH_PANEL": render_panel(
            data,
            seo,
            "zh",
            zh_attributes,
            "./data/ai-free-quotas.json",
        ),
        "EN_PANEL": render_panel(
            data,
            seo,
            "en",
            en_attributes,
            "./data/ai-free-quotas.json",
        ),
    })


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build(output: Path) -> None:
    data = load_json(DATA_FILE)
    seo = load_json(SEO_FILE)
    validate(data)
    resolved = output.resolve()
    if resolved in {Path("/"), ROOT.resolve()}:
        raise ValueError(f"refusing unsafe output directory: {resolved}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    site_url = canonical_site_url(seo)
    root_url = absolute_url(site_url, "")
    zh_url = absolute_url(site_url, "zh/")
    en_url = absolute_url(site_url, "us/")
    write(output / "index.html", render_app(data, seo))
    write(output / "zh/index.html", render_page(data, seo, "zh"))
    write(output / "us/index.html", render_page(data, seo, "en"))
    write(output / "assets/site.css", read(SOURCE_DIR / "static/site.css"))
    write(output / "data/ai-free-quotas.json", json.dumps(data, ensure_ascii=False, indent=2))
    write(output / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {absolute_url(site_url, 'sitemap.xml')}")
    write(output / "sitemap.xml", (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{escape(root_url)}</loc><lastmod>{data['updated_at']}</lastmod></url>\n"
        f"  <url><loc>{escape(zh_url)}</loc><lastmod>{data['updated_at']}</lastmod></url>\n"
        f"  <url><loc>{escape(en_url)}</loc><lastmod>{data['updated_at']}</lastmod></url>\n"
        "</urlset>"
    ))
    write(output / "llms.txt", (
        f"# {seo['title_en']}\n\n"
        f"> {seo['description_en']}\n\n"
        f"- Updated: {data['updated_at']}\n"
        f"- Chinese list: {zh_url}\n"
        f"- English list: {en_url}\n"
        f"- Structured dataset: {absolute_url(site_url, 'data/ai-free-quotas.json')}\n"
        "- Every listing includes an official reference and verification date.\n"
    ))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the static AI free quota site.")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build(args.output)
    print(f"built site: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
