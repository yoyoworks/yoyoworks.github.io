# AI Free Quota

AI 免费额度清单是 YOYOworks 统一网站中的独立模块。

## 构建

在仓库根目录运行：

```bash
python3 -m unittest discover -s ai_free_quota/tests -v
python3 ai_free_quota/scripts/build.py --output _site/ai_free_quota
```

生成页面包括：

- `/ai_free_quota/`：根据浏览器语言直接显示中文或英文内容，并记住手动选择；
- `/ai_free_quota/zh/`：中文预渲染页面；
- `/ai_free_quota/us/`：英文预渲染页面；
- JSON、robots、sitemap、llms.txt 等公开产物。

正文始终预渲染；浏览器脚本只负责统一入口的语言显示和偏好保存。
