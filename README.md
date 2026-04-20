# Mylife114 社区门禁 — Home Assistant 自定义集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![HA min](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5)

把基于 `guard.mylife114.com` 的小区门禁接入 Home Assistant —— 每扇门一个按钮,支持 Lovelace、脚本、NFC、Siri 快捷指令,不用再每次进微信。

---

## ⚠️ 安全提示(请务必先看)

Mylife114 的开门接口**没有任何鉴权**:只要知道你的 `uid` + `house_id` + `controller_sn`,任何人都能开你家的门。因此:

- **不要**把你自己的 `uid` / `house_id` / `controller_sn` / 社区名写进公开仓库、issue、截图、日志。
- 提 issue 前请把日志里的真实参数**全部脱敏**(`uid=1XXXXX`、`D********` 等)。
- 本 README、示例代码里的 UID/SN/房号**均为占位符**,不是可用真值。

平台如果哪天给接口加了 token/签名,本集成会失效,需要重新抓包适配。

---

## 功能

- ✅ 输入 UID 一键发现你**所有**社区 + **所有**门,自动去重
- ✅ 每扇门生成一个 `button.*` 实体,按一下就开
- ✅ 按门类型区分图标(公共门 `mdi:gate`,单元门 `mdi:door-open`)
- ✅ 提供 `mylife114.open_door` 服务,可在自动化/脚本/NFC/语音助手里调用
- ✅ UI 修改名字、图标、区域**永久保留**,重启不还原
- ✅ 12 小时自动重新拉取门列表(搬家/换房时自动出现新门)

---

## 安装

### 方式 A —— HACS(推荐)

1. HACS → 集成 → 右上角三点 → 自定义仓库
2. 仓库 URL 填 `https://github.com/Hamster-Prime/ha-mylife114`,类别选 **Integration**
3. 在 HACS 搜 `Mylife114` 并下载
4. 重启 Home Assistant

### 方式 B —— 手动

把 `custom_components/mylife114/` 整个目录复制到 HA 配置目录下的 `custom_components/`:

```
<ha-config>/
└── custom_components/
    └── mylife114/
        ├── __init__.py
        ├── api.py
        ├── button.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── icons.json
        ├── manifest.json
        ├── services.yaml
        ├── strings.json
        └── translations/
            ├── en.json
            └── zh-Hans.json
```

重启 Home Assistant。

---

## 配置

### 第一步:获取你的 UID

1. 手机上装一个抓包工具:[Reqable](https://reqable.com/)、Charles、mitmproxy 等
2. 在微信里进入小区门禁小程序,走一次**开门**流程
3. 在抓包工具里搜 `open_door`,找到形如下面这条请求:

   ```
   GET https://guard.mylife114.com/api/v1/open_door
       ?controller_sn=D********
       &uid=1XXXXX            ← 这就是你的 UID
       &direction=1
       &house_id=8XXXXX
   ```

4. 记下 `uid` 的值。

### 第二步:添加集成

1. Home Assistant → 设置 → 设备与服务 → **添加集成** → 搜 `Mylife114`
2. 填入刚才抓到的 UID,确认
3. 插件会自动拉取你的社区和所有门,每扇门生成一个按钮实体

---

## 使用

### Lovelace 按钮卡片

```yaml
type: button
name: 开楼道门
icon: mdi:door-open
icon_height: 80px
tap_action:
  action: call-service
  service: button.press
  target:
    entity_id: button.men_xxxxxxxxx
show_state: false
```

### 服务调用

```yaml
service: mylife114.open_door
data:
  controller_sn: D********
  house_id: "8XXXXX"
  direction: 1
```

### NFC 一碰开门

1. HA 手机 App → 设置 → 标签 → 读取一张 NFC 标签 → 写入
2. 动作选"按下" → 选要开的门按钮实体
3. 贴在门口/手机壳上,碰一下即开

### iOS 快捷指令 / Siri

1. 创建"获取 URL 内容"快捷指令
2. URL 填 HA 的 `/api/services/button/press`,方法 POST
3. Header 加 `Authorization: Bearer <长期令牌>`
4. Body 填 `{"entity_id": "button.xxx"}`
5. 绑定 Siri 短语 "开门"

---

## 故障排查

### 打开调试日志

`configuration.yaml` 追加:

```yaml
logger:
  default: warning
  logs:
    custom_components.mylife114: debug
```

重启 HA 后在 **设置 → 系统 → 日志** 里搜 `mylife114`。

### 常见问题

**Q: 集成添加成功但没有按钮出现?**
A: 大概率 API 返回字段名和代码预期不一致。查看 debug 日志里的原始响应,提 issue 时贴出来(记得脱敏)。

**Q: 按下按钮没反应 / 返回错误?**
A: 日志里看 `open_door` 的返回。平台有时会根据 `house_id` 限制——公共门可能挑选了错误的 `house_id`,需要手动指定你自己那个。

**Q: UID 我是自己这栋楼的住户,能开别人单元楼门吗?**
A: 接口现在没有权限校验,API 返回的"门列表"就是平台认为你能开的所有门;如果列表里没有,强开一般会失败。

**Q: 重启后按钮名字被还原?**
A: 不会。`unique_id` 是稳定的,UI 里的重命名存在 entity registry,重启/重新加载都不会丢。

---

## 涉及的 API

| 接口 | 用途 |
|---|---|
| `GET https://guard.mylife114.com/api/v1/get_communitys?uid=` | 列出我所在的社区 |
| `GET https://guard.mylife114.com/api/v1/community_doors?uid=&community_id=` | 列出某社区下所有门 |
| `GET https://guard.mylife114.com/api/v1/open_door?controller_sn=&uid=&direction=&house_id=` | 开门 |

---

## 开发

```
custom_components/mylife114/
├── __init__.py         # 集成入口 + 服务注册
├── manifest.json
├── const.py            # 域名 / API 路径 / UA
├── api.py              # 异步 API 客户端
├── coordinator.py      # DataUpdateCoordinator
├── config_flow.py      # UI 配置流
├── button.py           # 按钮平台
├── services.yaml
├── icons.json
├── strings.json
└── translations/
    ├── en.json
    └── zh-Hans.json
```

## 免责声明

- 本项目**仅供**有合法访问权限的住户本人在自己设备上自动化使用,不承担任何滥用后果。
- 与 Mylife114 / 悦然通 / 相关物业公司**无关联、无授权**,是用户侧的逆向适配。
- 若平台方通知要求下架,本项目将撤回。

## 许可

[MIT](LICENSE) © 2026 Sanite&Ava
