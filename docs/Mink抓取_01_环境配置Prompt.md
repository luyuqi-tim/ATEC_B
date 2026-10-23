# 指令 1：配置 B2＋Z1 的 Mink 单物体抓取环境

你是负责执行的服务器端工程师。请在已连接的 Linux GPU 服务器上实际检查、安装和验收环境，不要只给安装建议。用户的本地电脑只用于远程连接，不在本地运行仿真、模型推理或数值 IK。

本轮最终实验是：B2＋Z1 真实站立，面前固定摆放一个物体，用 Mink 控制 Z1 抓起并保持。没有篮子，不做背部放置、导航、视觉识别、大模型或 RL 训练。已知目标抓取属于独立机械动作诊断，不是完整 Task B 评测。

如果同时收到《Mink抓取_02_执行目标与策略Prompt.md》，完成本文件的必要环境验收后直接继续第二份指令，无需再次询问是否开始。若只收到本文件，则交付环境结果和下一步启动方式。

## 1. 工程与环境事实

用户选择的平台镜像：**Isaac Sim 5.1＋Isaac Lab 2.3.2 workstation＋ROS2 Jazzy**。先核实实际安装版本和路径，不把镜像名称当作安装成功的证据。

工程 README 的已验证组合是 Sim 5.0＋Lab 2.2.1＋Python 3.11＋PyTorch 2.7。Lab 2.3.X 官方支持 Sim 5.1，因此当前镜像可以作为兼容性验证候选，但尚未在用户服务器实测。不因版本差异就重装镜像。

从服务器当前工作目录定位用户上传的 Task B 工程，读取适用的 AGENTS.md，以及以下文件：

- README.md、pyproject.toml、THIRD_PARTY_NOTICES.md；
- taskb_student/constants.py、robot.py、low_level.py、env_cfg.py；
- scripts/check_package.py、run_taskb.sh、play_taskb.py；
- models/locomotion/deployment_manifest.json；
- docs/BinWalker_一周复用审计.md，如存在。

工程特征：assets/b2z1/b2z1_0815.urdf、models/locomotion/policy.pt、任务 Student-TaskB-B2Z1-v0、19 个可控关节。若工程没上传或路径不明，请指出这个必要输入；不要下载另一个比赛仓库代替它，也不要把用户本地的 Windows 路径用在服务器上。

## 2. 安装边界和候选版本

实际物理与相机渲染使用 Isaac Sim；Mink＋MuJoCo 仅用于运动学计算，不把抓取实验迁移到 MuJoCo 仿真。

- 复用镜像配套的 Python 3.11、Isaac、PyTorch、CUDA 和驱动。
- 候选组合为 **mink==1.0.0、mujoco==3.3.7**，另需 qpsolvers 的 DAQP 后端、SciPy、NumPy；视频输出可按需补 imageio、imageio-ffmpeg。
- 这组候选的依据是 Mink v1.0.0 的官方包声明：Python >=3.10,<3.14、MuJoCo >=3.3.6、qpsolvers[daqp] >=4.3.1，并支持 BinWalker 使用的 constraints 参数。该组合尚未在本镜像实测，不要把它写成已验证配置。
- 优先使用镜像已有的兼容依赖，尤其 NumPy、SciPy 和 PyTorch；记录实际选用版本。若已有 MuJoCo 版本兼容且数值检查通过，可以保留并说明。
- 不执行全局 pip upgrade，不主动升级 NumPy、PyTorch 或 CUDA，不修改驱动。不安装 Isaac Gym、完整 BinWalker 训练环境、ROS Humble、VBC、Unitree Python 3.8 二进制 SDK。
- ROS2 Jazzy 本轮无需参与；不主动 source ROS2，不将 ROS2 的 Python 路径混进 Isaac 环境。

先保存 python/pip 路径、pip freeze、pip check 基线和必要的 Isaac/动态库路径。只记录任务需要的环境变量，不输出密钥和令牌。对已有共享环境产生冲突时，优先创建隔离环境或最小覆盖层，避免强行改变镜像基础包。

## 3. 执行步骤

### A. 核实运行时

记录 GPU 型号、显存、驱动、CPU、内存、可用磁盘、操作系统以及 Isaac Sim/Lab 实装版本。单卡 RTX 4090 24GB 可作为本次候选；参考官方基础要求，内存至少 32GB。这里不承诺渲染帧率。

找到镜像正确的启动方法：可能是 conda 激活后 Python，也可能是 Isaac Lab 的 isaaclab.sh -p 或预装二进制的 Python 包装器。不要用系统 Python 的导入失败判断 Isaac 缺失；Kit/Omni 模块按 AppLauncher 的正确顺序加载。

后续每条命令都使用同一套已确认解释器/包装器。建立可重复使用的启动环境脚本，记录完整命令，不能仅在某个临时终端中碰巧成功。

### B. 最小安装

在工程根目录，用正确解释器检查项目依赖。依赖齐全时执行：

```bash
python -m pip install -e . --no-deps
python scripts/check_package.py
```

这里的 python 表示已确认的 Isaac 环境解释器；如果需要包装器，请替换为实际命令。check_package.py 包含 CPU 模型推理，必须在服务器执行。

安装 Mink 前先预览依赖变更，并用当前 NumPy、SciPy、PyTorch 等版本建立约束。下面是候选安装请求，不是要求不经检查直接执行：

```bash
python -m pip install --dry-run "mink==1.0.0" "mujoco==3.3.7" "qpsolvers[daqp]>=4.3.1"
```

使用生成的约束文件执行实际安装。只补缺失且兼容的依赖；安装后对照 pip check 基线，解释新增问题。若候选冲突，先定位具体依赖并选择最小调整，不盲升最新版 Mink。验证通过后保存完整 lock/freeze 和安装命令。

### C. 分开验收

1. 工程资产、19 关节契约和原始行走权重检查通过。
2. Mink、MuJoCo、SciPy 可导入，qpsolvers 的可用后端包含 daqp；用一个小型已知可达目标做有限次 IK 数值检查，确认结果有限且误差下降。无需启动 MuJoCo viewer；该检查不证明 B2 抓取成功。
3. Isaac Sim 可以启动，加载实际 B2＋Z1，零底盘速度、收臂站立；CPU PhysX 物理计算、GPU 图像渲染。
4. 至少一台 Isaac 相机生成可辨认的 RGB 帧，能够保存连续帧或短视频；确认不是全黑画面或仅 GUI 能打开。
5. Mink 与 Isaac 同进程导入/计算可以共存。若图形库冲突，先避免导入 mujoco.viewer、避免创建第二个渲染器；必要时用独立 IK 工作进程传递关节角和目标，而不是重装图形驱动。

可以先利用原工程进行短时验证：

```bash
bash scripts/run_taskb.sh --headless --steps 300 --max-walltime-s 120 --debug
bash scripts/run_taskb.sh --headless --enable_cameras --steps 300 --max-walltime-s 120 --sensor-output runs/mink_envcheck/sensors --debug
```

注意：原启动脚本使用 TASKB_PYTHON 指定解释器并补充 PyTorch 动态库路径；按实际安装方式正确设置。项目要求 --device cpu，不传 --device cuda:0。原工程 LiDAR 需要在 AppLauncher 启动时启用 isaacsim.sensors.physx。

原工程雷达若出现版本故障，应记录完整异常；第二份指令的独立抓取场景不需要 LiDAR，可以只搭建机器人、单物体、地面和观察相机。不要修改正式雷达代码来掩盖问题，也不要把本轮抓取环境通过报告成完整 Task B 已通过。

每次进程设置有限外部超时，首次着色器编译单独记录。--max-walltime-s 在 reset 后才开始计时，不能代替启动超时。不得让僵死进程、重复启动或无限重试消耗租用时间。

## 4. 交付与继续条件

在 runs/mink_envcheck/<时间戳>/ 保存：

- environment_report.md：实际版本、硬件、解释器、执行命令、变更以及通过/失败/未验证项；
- 安装前依赖快照、最终依赖锁定文件、pip check 结果；
- 可复用的启动环境脚本/命令；
- 包检查、Mink 数值检查、站立、相机的原始日志和图片/视频。

若同名目录已存在，保留旧结果，创建新目录。必要环境检查通过后继续第 2 份指令，实际实现并运行抓取；不要把“环境配置完成”当成“抓取完成”。如果缺少服务器、工程或可用 GPU，指出缺项，不编造运行结果。

## 官方参考

- Isaac Lab v2.3.2 兼容表：https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/README.md#isaac-sim-version-dependency
- 安装要求：https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/installation/index.html
- Mink v1.0.0 依赖：https://github.com/kevinzakka/mink/blob/v1.0.0/pyproject.toml
- Mink v1.0.0 求解 API：https://github.com/kevinzakka/mink/blob/v1.0.0/src/mink/solve_ik.py
- MuJoCo 3.3.7：https://pypi.org/project/mujoco/3.3.7/
