**已知目标位姿的抓取诊断：环境配置报告**

日期：2026-10-23（北京时间）。工程：/root/Desktop/TaskB。所有模型推理、IK、物理和渲染均在服务器运行。

**结论：独立单物体诊断环境通过功能验收；正式 Task B 的 LiDAR 启动仍有兼容问题。抓取结果另见抓取报告。**

| 项目 | 实测 |
| --- | --- |
| 系统 | Ubuntu 24.04.5 LTS，x86_64 |
| GPU | RTX 4090，24564 MiB，驱动 580.126.09 |
| 容器资源 | CPU 配额 14 核，内存上限 50 GiB |
| 磁盘初始可用 | 系统盘约 29 GiB，数据盘约 49 GiB |
| Isaac Sim | /isaac-sim/VERSION：5.1.0-rc.19+release.26219.9c81211b.gl |
| Isaac Lab | /workspace/isaaclab/VERSION：2.3.2；Python 包元数据 0.54.2 |
| Python | /isaac-sim/kit/python/bin/python3，3.11.13 |
| 启动包装器 | /isaac-sim/python.sh |
| 保留的核心依赖 | PyTorch 2.7.0+cu128、NumPy 1.26.0、SciPy 1.15.3 |
| 新安装 | mink 1.0.0、mujoco 3.3.7、etils 1.14.0、glfw 2.11.0、PyOpenGL 3.1.10 |
| 已有求解依赖 | qpsolvers 4.8.2、daqp 0.7.2，可用后端 daqp |
| 视频依赖 | imageio 2.37.0、imageio-ffmpeg 0.6.0 |

安装前保存 pip_freeze_before.txt、pip_check_before.txt、runtime_before.json。先用 constraints.txt 锁定已有核心依赖，预览安装，再安装缺失包。没有升级 NumPy、PyTorch、CUDA 或驱动。工程采用 editable 安装，安装命令和输出保存在安装日志中。最终锁定文件为 requirements.lock.txt。

镜像原有 pip check 的 7 条依赖问题保持不变，详见 before/final 和空的 diff 文件：缺 quadprog、docstring-parser、usd-core（两个包）、pyjwt，以及 lxml、starlette 版本不匹配。未为本实验修改这些无关包，不能把当前镜像描述为 pip check 全绿。

**验收证据**

- 原始 URDF、行走权重 SHA256、19 关节契约及真实 TorchScript 推理通过；最终原项目测试 **22 passed**。
- Mink 与 MuJoCo、SciPy 可导入，DAQP 可求解。URDF 独立 FK 与 MuJoCo FK 三个姿态的误差约 10^-16 m；最终 IK 往返数值检查通过。
- 独立 Isaac 场景使用原 B2Z1_CFG、浮动机身、CPU PhysX、GPU 渲染、0.005 s 物理步、0.02 s 控制步。实际站姿高度约 0.539 m、倾角约 1.1°。
- 已生成连续 640×480 RGB 录像。显式启用 CPU 物理到 USD 的位姿更新后，USD/PhysX 位置差为 0；实际腕部与 URDF FK 差小于 1 微米。
- Mink 在 Isaac 同进程中实际参与运算，运行阶段共存通过。原生退出阶段会挂起，现用独立 supervisor 在输出完整落盘后给 5 秒清理时间，随后回收该进程组，状态单独写入 process_status.json。外部启动上限 180 秒、总上限 480 秒，各试验还保留内部真实时间和仿真时间上限。

**发现及处理**

首次独立场景未显式写入默认关节状态，随后修正为每次 reset 都写入默认 root/joint 状态。按老师 deployment_manifest 的站立历史初始化要求，使用 100 次重复的初始实测本体观测填充策略历史；没有替换权重。启动位移从未初始化历史时约 0.4 m 降至约 0.023 m。夹持阶段不执行完整 controller.reset()。

原镜像 /physics/updateToUsd 和 /physics/updateVelocitiesToUsd 为 false；独立场景中设为 true，并关闭 Fabric。此修复仅用于独立诊断启动，不修改正式环境或传感器代码。

正式 scripts/run_taskb.sh 在 LiDAR Prim 上报错：“not a xformable prim with standard transform operations”。原始 standing.log 和退出码均保留。按授权文档采用无 LiDAR 的独立抓取场景；这不代表完整 Task B 环境已经通过。

复用启动环境为 experiments/mink_grasp/runtime.sh。复现入口：
bash scripts/run_mink_grasp.sh --mode env-check --headless --enable_cameras --record-video --output runs/mink_envcheck/reproduce

最终实际验证目录为本目录的 final/，功能返回码为 0，原生清理回收标记为 true。

官方接口依据：[Isaac Lab v2.3.2 兼容表](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/README.md#isaac-sim-version-dependency)、[Mink v1.0.0 依赖](https://github.com/kevinzakka/mink/blob/v1.0.0/pyproject.toml)、[Mink solve_ik](https://github.com/kevinzakka/mink/blob/v1.0.0/src/mink/solve_ik.py)。本报告的通过结论来自服务器实测日志。
