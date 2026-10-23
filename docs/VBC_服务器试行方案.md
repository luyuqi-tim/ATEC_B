# Visual Whole-Body Control：独立服务器试行方案

核查日期：2026-10-23。本文件是一份待执行方案，不代表已经部署或测得抓取成功率。本轮本地工作仅查询公开资料、阅读源码和编写文档。

## 1. 首轮目标与边界

在独立服务器目录与 Python 环境中，复现 VBC 原生 B1＋Z1 抓取测试。先回答两个问题：公开资源是否足以直接推理；如果足够，原生环境中的抓起和持物表现如何。

默认只做推理/评估，即使用已有训练结果执行动作。不启动训练。暂不更换 B2，不移植 Task B，不安装篮子，不修改现有 Task B 环境。

评估通过只能说明 VBC 在对应原生环境中的表现，不能直接说明它已适配 B2、Task B 的夹爪参数、合法观测和投放计分。

## 2. 源码与资料基准

- [作者仓库](https://github.com/Ericonaldo/visual_wholebody)
- 本次读取的提交：`869104c31953718f30ad20675e5291fcb5c5ea23`。
- [作者项目页](https://wholebody-b1.github.io/)
- [高层 README](https://github.com/Ericonaldo/visual_wholebody/blob/869104c31953718f30ad20675e5291fcb5c5ea23/high-level/README.md)
- [底层 README](https://github.com/Ericonaldo/visual_wholebody/blob/869104c31953718f30ad20675e5291fcb5c5ea23/low-level/README.md)

该仓库 README 的克隆示例使用过 `visual_whole_body` 名称。执行时使用本次核实的仓库 URL `https://github.com/Ericonaldo/visual_wholebody.git`，并记录实际提交。

## 3. 最先检查权重，而不是直接开始长任务

权重/checkpoint 是模型训练后保存的参数文件。VBC 的可用性需要分层判断：

| 文件类型 | 作用 | 本次核查状态 |
| --- | --- | --- |
| 底层控制模型 | 根据身体状态、身体速度与机械臂末端目标执行运动 | 作者根 README 提供下载链接；未下载验证内容及兼容性 |
| 高层教师模型 | 根据结构化状态等特权输入决定抓取动作 | 本次未确认现成可下载权重 |
| 高层视觉学生模型 | 根据视觉输入等信息决定抓取动作 | 本次未确认现成可下载权重 |

根 README 中明确提供的是低层模型链接。仓库当前文件树没有发现已提交的 `.pt/.pth/.ckpt` 模型文件。作者 issues 也存在高层权重及复现结果讨论；不能把训练代码和学习曲线等同于现成抓取模型。

底层链接：[作者 README 提供的文件](https://drive.google.com/file/d/1KIfKu77QkrwbK-YllSWclqb6vJknGgjv/view?usp=sharing)。历史 issue 分享过另一低层文件，不能认为不同来源的权重必然对应相同代码和观测。

阶段 0 必须形成资源清单：文件、来源、SHA-256、模型类型、对应代码与参数、是否可严格加载。先查服务器已有文件和作者公开资源。没有高层权重时，说明阻塞并完成不依赖它的环境与底层检查，不用随机模型充当预训练结果，也不自动启动高层训练。

若只有教师权重，可以做教师抓取评估，但不能把它称为视觉抓取复现。学生推理通常需要低层＋学生权重；当前学生 eval 代码在 `args.eval=True` 时跳过教师权重加载，不能无依据增加“推理必须持有教师权重”的条件。

## 4. 服务器选型

以下是首轮工程建议，不是官方最低配置，也没有进行本项目实机性能测量。

| 项目 | 建议 |
| --- | --- |
| 架构与系统 | Linux x86_64，优先 Ubuntu 20.04 |
| GPU | 单张 NVIDIA RTX 3090，24GB 显存 |
| CPU | 8～16 vCPU |
| 内存 | 建议 64GB；资源有限可先尝试 32GB 的短评估 |
| 可用磁盘 | 建议 100GB，留给代码、资源、环境和录像 |
| 图形能力 | NVIDIA 驱动与 Vulkan 图形链路可用；无桌面时采用 headless 渲染 |
| 连接方式 | SSH 用于命令与文件传输；远程桌面可选 |

选择 3090 的依据：作者在 [issue #4](https://github.com/Ericonaldo/visual_wholebody/issues/4#issuecomment-2207791349) 中报告使用 3090 服务器训练高层；同时它适合从仓库较旧的 PyTorch/CUDA 基线开始核对。不要把“能运行 nvidia-smi”直接当作相机渲染已通过。

首次会话建议设定约 2 小时的排障与试行预算，单个评估进程上限 10 分钟。它们是建议的停止点，不是完成时间承诺。到点停止相关进程、保存日志并汇报；服务器租赁计费需另行管理。

## 5. 环境基线

VBC 用 Isaac Gym；Task B 用 Isaac Sim＋Isaac Lab。两套项目应各用各的 Python 环境。

| 组件 | 本次建议基线 | 依据与说明 |
| --- | --- | --- |
| Python | 3.8 | 作者 README 和包的 `python_requires` |
| Isaac Gym | 先核查仓库附带包；其 release notes 首项为 Preview 4 | `setup.py` 元数据仍写 preview3，不能只看 pip 版本字符串判断实际包版本 |
| PyTorch | 先尝试 1.10.0，CUDA 11.3 构建 | 仓库 `rlgpu_conda_env.yml` 写明 pytorch=1.10、cudatoolkit=11.3；是候选起点，不保证所有高层依赖开箱即用 |
| torchvision | 与 PyTorch 对应，例如 0.11.1 | 最终由安装可用性和依赖检查确认 |
| NumPy | 候选 1.23.5 | 兼顾 Python 3.8 和旧代码的初始兼容方案，并非作者锁定版本 |
| setuptools | 59.5.0 | 仓库 conda 配置指定 |
| 项目依赖 | 优先安装仓库内的 rsl_rl、skrl、low-level | 需要检查它们的依赖及 Python 3.8 兼容性，避免无条件升级到最新版 |
| NVIDIA 驱动 | 使用服务器已配置并与 3090 兼容的版本 | NVIDIA 旧版 Gym 文档列出 470+ 要求；不将它解释成应降级到 470 |

依据：[仓库 conda 配置](https://github.com/Ericonaldo/visual_wholebody/blob/869104c31953718f30ad20675e5291fcb5c5ea23/third_party/isaacgym/python/rlgpu_conda_env.yml)、[Gym 发布说明](https://github.com/Ericonaldo/visual_wholebody/blob/869104c31953718f30ad20675e5291fcb5c5ea23/third_party/isaacgym/docs/_sources/release-notes.rst.txt)、[NVIDIA Gym 下载页](https://developer.nvidia.com/isaac-gym/download)。

Isaac Gym 已属旧版软件，下载可能需要 NVIDIA 许可确认。若安装包、驱动或权重无法获取，报告具体缺项，不在原 Task B 环境里盲目替换依赖。

建议目录：

```text
~/vbc-pilot/
  visual_wholebody/   独立检出的源码
  checkpoints/       实际取得的权重及清单
  outputs/           日志、视频、指标、依赖快照
  patches/           必要的最小修复及说明
```

独立 conda 环境建议名 `vbc38`。保留已有驱动和其他项目；系统级修改需要先说明影响。

## 6. 分阶段试行

| 阶段 | 工作 | 通过条件 |
| --- | --- | --- |
| 0：资源审计 | 检查服务器、源码提交、资产与分层权重 | 得到“能测试哪一层”的明确结论 |
| 1：运行环境 | 验证 Isaac Gym 导入、CUDA 计算、图形设备与相机图像 | 仿真和相机链路有实际输出，且无设备错误 |
| 2：底层控制 | 加载作者低层权重，严格核对观测维度与配置 | 关节输出有效，短时站立与末端目标跟踪合理；不是抓取成功证明 |
| 3：教师抓取（有权重时） | 使用 `play_multistate.py` | 原始状态输入下完成抓取抬升，记录官方指标与录像 |
| 4：视觉抓取（有权重时） | 使用 `play_multi_bc_deter.py` | 相机输入有效，正确加载视觉模型，得到真实抓取结果 |
| 5：重复短评估 | 固定原配置后，变更 seed 做重复观察 | 各次尝试、成功、掉落、异常有可追溯记录 |

先保持原生 B1＋Z1、原资产、原相机和默认评估设置。当前脚本评估默认设置 34 个环境。先短时验证原生组合，再考虑筛选物体或缩小环境数，避免同时改变多个条件。

若只能完成前两阶段，报告“环境和低层可运行，高层权重缺失”，这是一项有效可复现结果，但不能称作抓取验证通过。

## 7. 当前源码中会影响启动的细节

1. 当前 `high-level/utils/config.py` 没有定义 `--num_envs` 参数，不能直接附加 `--num_envs 1`。README 对此的文字与当前 parser 不完全一致。
2. 配置里 `low_policy_path` 是作者机器上的绝对路径。需改成实际下载位置，并保留修改记录。
3. 网络观测维度受 `--observe_gait_commands` 等参数影响。作者在 [issue #2](https://github.com/Ericonaldo/visual_wholebody/issues/2#issuecomment-2141990541) 解释过缺 5 维的匹配问题。不能用 `strict=False`、裁剪权重或删除观测掩盖不匹配。
4. 当前代码会从高层 checkpoint 文件名末尾解析整数，例如 `agent_60000.pt`。保留原文件名并检查，不能随意重命名为 `student.pt`。
5. 学生 eval 的 `create_env()` 会开启相机。`--headless` 隐藏窗口，视觉任务仍需 GPU 图形设备，建议显式核对 `--graphics_device_id 0` 对应的设备。
6. 原生学生环境从仿真获取 segmentation 图像，即仿真给出的像素归属标记。需要在报告中注明目标 mask 来源；它不能直接证明模型已解决 Task B 的 RGB 目标分割问题。
7. 录像路径代码会拆分 checkpoint 路径字符串。采用绝对路径或不同目录层级时，可能需要小范围修复路径处理，保存 diff。
8. 教师策略读取结构化物体状态等特权信息；教师成功不能替代视觉学生评估。

这些是静态源码发现，不代表以上问题都将在目标服务器发生。

## 8. 成功判据和输出

保留原环境成功定义，阅读并记录 `b1z1_pickmulti.py` 的抬升高度、物体与末端距离、保持步数等逻辑。不要通过降低阈值、关闭物体碰撞或固定物体到夹爪来获得成功。

短评估至少区分：没接近、没夹住、抬起后掉落、机器人失稳、模型或图形错误。录像与原始成功指标一起看，不能把模型正常输出动作算成抓取成功。

如条件允许，首轮以原生 34 个并行环境进行数轮评估；报告实际完整 episode 数。需要精简物体集合时，先检查分类索引和空集合处理，并将精简后的结果单独标注，不冒充完整官方集合结果。

输出建议：

```text
outputs/
  preflight.md
  checkpoint_manifest.json
  environment.txt
  pip-freeze.txt
  commands.txt
  logs/
  videos/
  metrics.csv
  result.md
```

记录源码提交、依赖、驱动、GPU、实际命令、seed、checkpoint 哈希、完整尝试数、成功数、掉落数、运行时间与峰值显存。

## 9. 条件满足后的启动命令模板

以下不是“现在已可直接运行”的承诺：需要先取得对应权重、替换低层路径，并核对权重训练参数。参数与 checkpoint 必须匹配。

从 `~/vbc-pilot/visual_wholebody/high-level` 执行，先用真实相对路径设置 `VBC_STUDENT_CKPT`，且文件名保留数值步号。

```bash
conda activate vbc38
cd ~/vbc-pilot/visual_wholebody/high-level

# 示例占位路径，必须替换为实际已核对的视觉学生 checkpoint。
VBC_STUDENT_CKPT='../../checkpoints/student_run/checkpoints/agent_60000.pt'

timeout --signal=INT --kill-after=30s 10m python play_multi_bc_deter.py \
  --task B1Z1PickMulti \
  --checkpoint "$VBC_STUDENT_CKPT" \
  --rl_device cuda:0 \
  --sim_device cuda:0 \
  --graphics_device_id 0 \
  --headless \
  --roboinfo \
  --observe_gait_commands \
  --small_value_set_zero \
  --rand_control \
  --stop_pick \
  --timesteps 1500
```

这些 flags 来自作者基线用法；如果实际权重对应其他训练设置，应按权重契约调整，不能盲目使用模板。首轮不添加录像参数，先验证可运行；录像能力再短测并检查实际文件。

有教师 checkpoint 时使用 `play_multistate.py` 对应入口，明确标注为教师评估。缺少权重时不运行随机初始化模型，不把训练入口当测试入口。

## 10. 给服务器编程助手的交接

配套可复制文本见 [VBC_服务器启动Prompt.txt](VBC_服务器启动Prompt.txt)。该 prompt 用来指挥服务器上的编程助手检查和执行本方案；VBC 原生测试本身由 Python 脚本启动，不是通过给机器人一段自然语言指令启动。
