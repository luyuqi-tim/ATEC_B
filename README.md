# ATEC_B：Mink 全身协调抓取

B2 机器狗先下蹲，Z1 机械臂夹住面前的芥末瓶，再起身配合抬臂。Mink 同时协调机身、四条腿和机械臂。

**服务器 Isaac 仿真已完成 5 次独立重置，5/5 抓取成功。** 物体抬升约 14.8 cm，连续有效夹持约 5.9 s，完整保持阶段为 4 s。这是固定已知目标的单物体诊断，完整 Task B 的导航、感知和收集投放尚未完成。

## 1. 获取代码

```bash
git clone https://github.com/luyuqi-tim/ATEC_B.git
cd ATEC_B
git switch branch-Mink_IK1
```

`main` 和 `branch-Mink_IK1` 保存同一套本次验收版本。

## 2. 配置环境

在 Linux GPU 服务器上运行。已验证环境：Isaac Sim 5.1、Isaac Lab 2.3.2、Python 3.11、RTX 4090；物理使用 CPU，图像使用 GPU。仓库包含机器人资产、物体和行走模型，不包含 Isaac 安装包。

以下命令对应当前服务器的 `/isaac-sim` 和 `/workspace/isaaclab`。原服务器依赖已装好，可直接跳到第 3 步；换服务器时先准备相同 Isaac 环境，再执行：

```bash
source experiments/mink_wholebody/runtime.sh
/isaac-sim/python.sh -m pip install -e . --no-deps
/isaac-sim/python.sh -m pip install \
  -c experiments/mink_wholebody/constraints.txt \
  -r requirements-mink.txt
/isaac-sim/python.sh scripts/check_package.py
```

镜像路径不同时，需调整 `runtime.sh` 与 `supervise.py` 中的解释器路径。`requirements.lock.txt` 是已有镜像的完整快照，不要用它整体覆盖另一套环境。

## 3. 运行抓取

在仓库根目录执行，无需打开远程桌面：

```bash
bash scripts/run_mink_wholebody.sh \
  --mode grasp --trials 5 \
  --headless --enable_cameras --record-video \
  --output runs/mink_wholebody/my_run
```

只试一次时，把 `--trials 5` 改成 `--trials 1`。输出目录重名时自动另存，保留旧结果。五次运行在当前服务器约需 11 分钟。

## 4. 查看结果

新运行的结果在 `runs/mink_wholebody/my_run/`：

- `summary.json`、`trials.csv`：是否抓起、抬升高度、保持时长。
- `trial_01/continuous.mp4` 等：每次从站稳到保持结束的完整录像。
- `controller.jsonl`、`evaluation.jsonl`：各次目录内的控制与物理评价记录。
- `process_status.json`：进程结束状态；原生清理若挂起会单独记录。

已经验收的五次结果在 [results/mink_ik1](results/mink_ik1)：[录像 1](results/mink_ik1/wholebody_trial_01.mp4)、[录像 2](results/mink_ik1/wholebody_trial_02.mp4)、[录像 3](results/mink_ik1/wholebody_trial_03.mp4)、[录像 4](results/mink_ik1/wholebody_trial_04.mp4)、[录像 5](results/mink_ik1/wholebody_trial_05.mp4)，以及[逐次结果](results/mink_ik1/wholebody_trials.csv)和[详细报告](results/mink_ik1/wholebody_report.md)。原始轨迹以 `.jsonl.gz` 保存在 `raw/`。

## 5. 修改入口

- `experiments/mink_wholebody/config.json`：物体位置、抓取点、下蹲高度和验收阈值。
- `controller.py`：下蹲、开爪、接近、闭爪、抬升与保持。
- `wholebody_ik.py`：Mink 全身运动学求解与站立支撑补偿。
- `bench.py`、`evaluator.py`：Isaac 场景执行与独立评价。

上述源码均在 `experiments/mink_wholebody/`。物体真值只用于评价，不反馈给控制器。旧的臂抓取失败版本保留在 `experiments/mink_grasp/`，此次请使用 `run_mink_wholebody.sh`。

原 Task B 说明见 [docs/TaskB_original_README.md](docs/TaskB_original_README.md)。第三方来源与许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 [Mink 参考声明](experiments/mink_wholebody/THIRD_PARTY.md)。正式 Task B 的 LiDAR 在当前镜像仍有兼容问题，不影响这个独立抓取场景。
