# 每周更新（食谱站）

每周一次，保持“菜谱绑的货店里真有卖”。

## 跑什么（按顺序）

```bash
cd D:/easternmarket.ca/eastern-recipe
python scripts/mark_pantry.py --check   # 免购标记完整，无新增缺口才过
python scripts/weekly_refresh.py        # 定向核验 152 个条码，刷新快照
python scripts/build_static_pages.py    # 重写 data/catalog.json + r/*.html
python -m pytest scripts/ -q            # 44 项
npm test                                # 28 项
```

`weekly_refresh.py` 只认肯定证据：精确命中才刷新名字/上架态，
无命中、多档未固定的一律只报告不改文件，未知的新增缺口退出码为 1。
已知待办（9735 下架、LXLX 无码、Hhlo 一码两档、肉松紫米包成品无货）
记在脚本里的 KNOWN 表中，处理完就从表里删掉。

## 发布

验证全绿后走分支 + PR + 合并（main 受保护），回 main 同步，
轮询线上 sitemap 确认发布。和以往食谱上线流程一致，不另起炉灶。
