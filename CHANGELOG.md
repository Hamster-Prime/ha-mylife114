# Changelog

所有重要变更都会记录在这里。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.0.3] - 2026-04-21

### Added

- 开门失败时自动创建 HA 持久通知(右上角铃铛会亮红点),标题 "🚪 Mylife114 门禁",正文含门名和具体原因(来自服务端 `msg` 字段)
- 同一扇门再次按成功后,旧失败通知会被自动清除,不会堆积

## [1.0.2] - 2026-04-21

### Added

- 识别开门成功/失败:`open_door` 响应里 `ref == 0` 或 `msg` 含 "成功" 视为成功,否则抛 `Mylife114ApiError`,失败原因从 `msg` 里取
- 新增 HA 事件 `mylife114_door_event`:每次按按钮都会广播 `{result: success|failed, door_name, controller_sn, house_id, community_name, msg}`,方便用自动化做通知、推送、记录等

### Fixed

- `api.open_door` 在服务端返回 HTTP 200 但业务失败时不再被静默忽略

## [1.0.1] - 2026-04-21

### Added

- 本地 brand 图标(`icon.png` + `dark_icon.png`),256×256 透明背景
- HA 2026.3+ 自动使用本地图标,优先级高于 brands CDN

## [1.0.0] - 2026-04-21

### Added

- 首个版本
- Config Flow:UI 输入 UID 即可配置,自动发现社区和所有门
- Button 平台:每扇门一个按钮实体,稳定的 `unique_id`,UI 修改持久化
- 按门类型(公共门 / 单元门)自动选择图标
- `mylife114.open_door` 服务,可覆盖 `uid` 供多账号开门
- DataUpdateCoordinator 12 小时自动刷新门列表
- 中文 / 英文 翻译
- 灵活的响应解析(支持 `result` / `data` / `list` / `rows` 等包装)
- 自动去重:同一扇门在多个 `house_id` 下重复出现时只保留一个
