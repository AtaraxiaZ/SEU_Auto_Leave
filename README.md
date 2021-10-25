# SEU_Auto_Leave
东南大学自动请假 研究生和本科生

![Stars](https://img.shields.io/github/stars/quzard/SEU_Auto_Leave.svg)
![Forks](https://img.shields.io/github/forks/quzard/SEU_Auto_Leave.svg)

## 已实现

- [x] 研究生销假
- [x] 研究生请假
- [x] 研究生撤回
- [x] 研究生删除草稿
- [x] 本科生撤回
- [x] 本科生删除草稿
- [x] 本科生销假
- [ ] 本科生请假未验证 应该也可以

## 使用步骤

1. 首先 fork 本项目到自己的仓库

2. 去 Actions 那 Enable Workflow

3. 进入自己 fork 的仓库，点击 Settings -> Secrets -> New repository secret，它们将作为配置项，在应用启动时传入程序。

**所有的可用 Secrets 及说明**

| Secret     | 解释                                                         |
| ---------- | ------------------------------------------------------------ |
| USERNAME   | 一卡通号                                                     |
| PASSWORD   | 一卡通密码                                                   |

4. 如果需要修改上报时间，修改 `.github/workflows/auto_temperature.yml`
