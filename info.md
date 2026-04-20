# Mylife114 社区门禁

把 `guard.mylife114.com` 平台的门禁接入 Home Assistant。

## 功能

- UID 一键发现所有门,自动去重
- 每扇门一个按钮,公共门和单元门不同图标
- `mylife114.open_door` 服务可用于自动化 / 脚本 / NFC / Siri
- UI 修改名字、图标、区域永久保留

## 配置

添加集成 → 搜 `Mylife114` → 填 UID(从微信抓包里拿)即可。

## ⚠️ 安全提示

接口无鉴权,请**不要**公开自己的 `uid` / `house_id` / `controller_sn`。

更多细节见 [README](README.md)。
