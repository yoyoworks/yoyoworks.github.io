# YOYOworks

YOYOworks 的统一网站仓库，包含个人主页与 AI 免费额度清单。

## 目录结构

```text
index.html             # 统一入口
assets/                # 主页资源
ai_free_quota/         # AI 免费额度数据、模板、构建脚本和测试
```

`assets/theme.css` 是 YOYOworks 全渠道品牌主题的唯一来源。共享变量统一使用
`--yw-*` 前缀；主页与 AI Free Quota 直接引用，微信公众号生成器从公仓读取后
转换为兼容的内联样式。

## 本地构建

```bash
python3 -m unittest discover -s ai_free_quota/tests -v
python3 ai_free_quota/scripts/build.py --output _site/ai_free_quota
cp index.html .nojekyll _site/
cp -R assets _site/assets
python3 -m http.server 8000 --directory _site
```

浏览器打开 `http://localhost:8000`。免费额度页面位于
`http://localhost:8000/ai_free_quota/`。

## 部署

推送到 `main` 后，由 GitHub Actions 构建并统一部署到 GitHub Pages。
