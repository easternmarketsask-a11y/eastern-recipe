# 东方超市菜谱搜索引擎 — 设计文档

- **日期**：2026-06-14
- **项目**：eastern-recipe（独立 GitHub Pages 静态站，沿用 eastern-farm 套路）
- **状态**：已通过方向评审，待写实施计划

## 1. 目标与定位

把东方超市的**进货 + 销售数据**变成顾客的"想吃什么 → 我们这都有"的入口，同时反过来帮店里清库存。两个一体的用途：

- **A. 顾客端引流**：顾客搜一道菜（如"麻婆豆腐"），系统给出菜谱 + 所需食材清单，每样标注东方超市的价格 / 分类货架 / 是否在售，引导顾客"我想做这道菜"→"来东方买齐"。
- **B. 库存反推促销**：根据当季 / 在售 / 店主手动主推的食材，反查"用到这些食材、且其余配料店里也都有"的菜谱，排序推荐，可导出成促销海报推给会员、清库存、提客单价。

**非目标（YAGNI，v1 不做）**：会员登录、个性化、购物车结算、实时库存数量显示、AI 实时生成菜谱。

## 2. 关键决策与约束

- **菜谱来源 = 自建精选库（手工绑定 SKU）**。准确性优先：每道菜的每样食材都绑定到真实在售商品，保证引流精准、可反推促销。搜不到的菜暂不兜底（未来可加 AI 兜底，非 v1）。
- **平台 = 独立静态网页**（vanilla JS，无 build，GitHub Pages 托管），与 eastern-farm 同构。顾客端不暴露 StockWise 后台。
- **⚠️ 库存数量不可信**：StockWise `products.stock_quantity` 已知不准。因此本项目**不显示"还剩几份"**，只绑定可靠字段：商品身份（`code`）、价格、分类、图片。B 的"可做"判断基于"该商品是否在售 + 店主主推标记"，不依赖库存数字。
- **商品权威源 = Firestore `products`（stockwise-486801），经 StockWise API 读取**，不直连 Firestore、不读原始 Clover 明细。现成字段：`name`（中英双语混排，如 "LH Mushroom Seasoning 香菇调味料 500g"）、`price`（**单位为加元，如 8.99，非分**）、`category`（中文单字符串）、`code`（= itemCode 主键，如 "0333zjzj"）、`imageUrl`（商品图，可复用作食材缩略图）、`latest_cost`（进货成本，仅内部用）。已有工具 `firebase_product_manager.py` / `api_handler.fetch_full_inventory()` 可复用，导出器不从零写。
- **分类对齐 9 大标准类**：`category` 必须落在 StockWise `categories` 集合的 9 类规范内（新鲜蔬菜/水果/冷冻/豆腐蛋品/米面粮油/干货调料/零食饮料/日用杂货/中成药品），经 `GET /api/firebase/categories` 取，**不硬编码**。
- **销售数据的角色**：Clover 销售明细（中英双语商品名 + `clover_item_id`）用于**给菜谱排序**——v1 先做哪些招牌菜、B 优先推哪些，由"所含食材的真实动销"驱动，呼应"基于进货+销售数据"。注意 `sales.product_doc_id` 多为空，销售↔商品 join 用 `clover_item_id`（见 CLAUDE.md 采购待补段）。
- **币种 = 加元 `$`**（萨斯卡通），全站不用 `¥`。

## 3. 架构总览

```
StockWise API (Firestore products) ──(每日导出脚本)──▶ products.json ─┐
Clover 销售明细 (动销，给菜谱排序) ─────────────────────────────────┐  │
                                                                  ├──┼─▶ 静态网页（vanilla JS）
店主手工精选菜谱 ──(半自动绑定脚本)──▶ recipes.json ───────────────┘  │      ├─ A: 搜菜找货
店主主推食材清单 ──(手填，push 即生效)──▶ featured.json ──────────────┘      └─ B: 今天做什么菜
```

三个隔离的单元，各自单一职责、接口清晰、可独立理解和测试：

1. **导出器（export script）** — 经 StockWise API 拉 Firestore 在售商品 + 近 90 天 Clover 动销，产出 `products.json`。
2. **绑定器（binding script）** — 半自动把菜谱食材匹配到商品中英双语名，产出候选绑定供店主确认，沉淀进 `recipes.json`。
3. **前端站点（static site）** — 读 `products.json` / `recipes.json` / `featured.json`，提供 A / B 两个体验。

## 4. 数据模型

### products.json（每日自动导出，机器生成，勿手改）
```json
{
  "generated_at": "2026-06-14T21:00:00-06:00",
  "items": [
    {
      "code": "10588",
      "name_cn": "芫荽",
      "name_en": "Cilantro",
      "price": 0.99,
      "price_unit": "each",
      "category": "新鲜蔬菜",
      "image_url": "https://.../cilantro.jpg",
      "on_sale": true,
      "sold_90d": 142
    }
  ]
}
```
- `code` 为主键（Firestore `products.code`，= Clover itemCode）。
- `price` 加元；`price_unit` ∈ `each` / `lb`（称重商品按 lb 标价，影响总价计算，见 §5）。
- `category` 为 9 大标准类之一（导出时把商品 `category` 归一到规范名）。
- `image_url` 复用 Firestore `imageUrl`，前端用作食材缩略图，可空。
- `on_sale` = 商品当前在售（available 且未 deleted），**不代表剩余数量**。
- `sold_90d` = 近 90 天 Clover 动销件数（按 `clover_item_id` join），仅供菜谱排序，可为 0。
- 不导出 `latest_cost` / `stock_quantity` 等内部/不可信字段到公开站。

### recipes.json（手工精选 + 半自动绑定，人审）
```json
{
  "recipes": [
    {
      "id": "mapo-tofu",
      "name_cn": "麻婆豆腐",
      "name_en": "Mapo Tofu",
      "aliases": ["麻婆豆腐", "mapo", "麻辣豆腐", "mapodoufu"],
      "image": "images/mapo-tofu.jpg",
      "image_credit": "self",
      "tags": ["川菜", "下饭", "快手"],
      "steps": ["豆腐切块焯水", "..."],
      "ingredients": [
        { "label": "嫩豆腐", "qty": "1 盒", "code": "4011tofu", "required": true },
        { "label": "郫县豆瓣酱", "qty": "2 勺", "code": "ddbanjiang", "required": true },
        { "label": "牛肉末", "qty": "200g", "code": null, "required": false }
      ]
    }
  ]
}
```
- `code: null` = 暂未绑定 / 店里没有对应商品（前端标"暂缺"，不阻断）。
- `required` = 是否核心食材；B 的"可做"判断只看 `required` 的食材是否都在售。
- `aliases` 含中文、英文、拼音（无空格小写），覆盖顾客可能的输入。
- `image_credit` ∈ `self`（自拍）/ `ai`（生成）/ `licensed`（授权）——见 §7 版权约束，**禁止**直接扒网图。

### 关联逻辑（前端启动时）
对每道菜的每个 ingredient，用 `code` 去 `products.json` 查：在售→带出价格/分类/缩略图；未在售或 `code:null`→标"暂缺"。

## 5. 功能流程

### A. 顾客搜菜（引流）
1. 顾客输入菜名（支持中文 / 英文 / 拼音、`aliases` 模糊匹配）。
2. 命中菜谱 → 展示图 + 标签 + 步骤 + 食材清单。
3. 每样食材一行：`【食材名 · 用量】` → `【$价格 · 分类 · 缩略图】` 或 `【暂缺】`。
4. 底部汇总：「X/Y 样我们都有」+「生成购物清单」（可截图/二维码到店找货）。
   - ⚠️ **总价只做"参考价"**：称重商品（`price_unit: lb`）标价是每磅，菜谱用量是"一把/200g"，**不能直接加总**。规则：只对 `each` 定量商品给"约 $XX 起"，称重项单列每磅价 + 标注"按需称重"，避免给顾客算错总价的负体验。

### B. 今天做什么菜（清库存/促销）
1. 输入 = `featured.json`（店主主推食材清单，手填一个文本/JSON、push 即生效，沿用 eastern-farm 改数据文件的工作流；无后台、无登录）。
2. 反查：所有 `required` 食材都在售、且至少用到 ≥1 个主推食材的菜谱。
3. 排序：用到主推食材数量 → 食材齐全度 → `sold_90d` 动销，综合排序。
4. 选中可一键导出促销海报素材（菜名 + 图 + 主推食材 + 价格）。**复用现有促销海报管线**（`stockwise_promo` / promo-poster 项目，见 memory `project_promo_poster_r2_resume`），不另造轮子，导出后接入会员推送。

## 6. 绑定数据怎么攒（解决 B 方案的主要成本）

半自动 `binding script`：
1. 维护一份常见家常菜食材词表（含别名，如"豆瓣酱"="郫县豆瓣"="豆瓣"）。
2. 拿食材名对 `products.json` 商品中英双语名做模糊匹配（中文子串 + 英文 token + 拼音），生成"候选绑定"（食材 → top-N 候选 `code` + 置信度）。商品名本身混排中英（"香菇调味料 500g / LH Mushroom Seasoning"）是匹配的强信号。
3. 店主过一遍：高置信直接采纳，低置信人工选或标"暂缺"。
4. 结果写回 `recipes.json`。新品上架时重跑、补绑。

首批目标：50–100 道东方超市顾客最常做的家常菜。**重质不重量**：优先做顾客真正常做、且本店食材最齐的招牌菜（用 `sold_90d` 动销辅助选），每道图/步骤/价格都精确，绝不为凑数堆一堆"暂缺"。

## 7. 错误处理与边界

- **搜不到菜**：提示"暂无此菜谱"，**不报错、不兜底生成**（v1）。搜索词收集走轻量端：用 Firestore Web SDK 往 `eastern-market-members` 写一个 `recipe_search_misses` 集合（仅 append，匿名），定期回看补菜谱。**不在静态站自建后端**——静态站无服务端，这点必须靠 Firestore 客户端写，否则"记录搜索词"无处落地。若不接 Firestore，则 v1 退化为不记录（二选一，计划阶段定）。
- **菜品图版权（硬约束）**：公开商用站，菜品成品图**只能用**自拍 / AI 生成 / 明确授权（CC0 等），`image_credit` 字段标明来源；**禁止**直接扒百度/小红书等网图。食材缩略图复用本店 `imageUrl`（自有商品图，无版权问题）。
- `products.json` 拉取失败：前端用上一次缓存的 JSON（localStorage），页面顶部提示"价格更新于 X"。
- 食材未绑定/暂缺：正常展示菜谱，该食材标"暂缺"，不影响其他食材引流。
- 价格时效：`products.json` 每日导出，页面标注"价格仅供参考，以店内标价为准"，规避隔夜调价纠纷。
- 中文/微信浏览器兼容：沿用 eastern-farm 已踩过的坑（无 build、纯静态、注意微信内置浏览器对部分 API 的限制，见 memory `project_eastern_farm`）。

## 8. 测试策略

- **导出器**：对样例 Firestore 商品数据跑，断言 `products.json` 字段完整、`code` 唯一、价格为数值（加元）、`category` 落在 9 类内、`price_unit` ∈ {each, lb}。
- **绑定器**：给定食材词 + 商品列表，断言匹配候选与置信度排序符合预期（含中英双语、拼音、别名用例）。
- **前端关联**：给定 products + recipes 夹具，断言每道菜的"齐全度""参考价（称重项不入总价）""暂缺标记"计算正确。
- **B 排序**：给定 `featured.json`，断言推荐集合与排序正确（含"required 缺货则排除""sold_90d 平手时的次级排序"用例）。

## 9. 分期

- **v1（本 spec）**：方案 1 静态站 + A + B + 首批 50–100 菜谱 + 每日导出 + 半自动绑定 + 促销海报复用。
- **v2（未来，另开 spec）**：升级方案 3（React+Firebase 复用 eastern-market-members），加会员登录、保存购物清单、AI 兜底生成搜不到的菜。

## 10. 待计划阶段定的开放项（不阻塞设计）

1. **搜索词收集**：接 Firestore `recipe_search_misses` vs v1 不记录——二选一。
2. **域名**：`recipe.easternmarket.ca` 独立子域 vs 复用现有站点二级路径（注意 easternmarket.ca DNS 已知不稳，见 CLAUDE.md；分享链接可能要用 `*.github.io` 或 web.app 形式）。
3. **每日导出怎么跑**：复用 `D:\easternmarket.ca\routines` 的 Windows 计划任务，还是 GitHub Actions 定时。
4. **首批菜谱清单**：由 `sold_90d` 动销 + 店主经验共同圈定具体 50–100 道。
