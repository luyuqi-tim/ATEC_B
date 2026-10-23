# ATEC_B：Mink 全身协调抓取

B2 机器狗原地下蹲，Z1 机械臂接近、闭爪，再起身配合抬臂。Mink 同时协调机身、四条腿和机械臂。物理仿真使用 Isaac，MuJoCo 只做运动学求解。

## 本轮结果

按要求只做 **3 个物体 × 3 个朝向 × 每个一次，共 9 次**，不重试、不测距离。九个组合中实际夹持抬升成功 **6/9**，连同保守路径检查确认 **6/9**。

| 物体 | -45 度 | 0 度 | +45 度 |
| --- | --- | --- | --- |
| 芥末瓶 | 成功 | 成功 | 成功 |
| 糖盒 | 成功 | 成功 | 成功 |
| 香蕉 | 失败 | 失败 | 失败 |

成功要求物体抬升至少 10 cm、最低点离地至少 2 cm、双指真实夹持且连续保持至少 3 s，同时机身稳定。失败按失败保留；IK 可达或程序正常结束不算抓取成功。

完整录像、逐次表格和报告在 [results/mink_multiclass_9](results/mink_multiclass_9)，重点看 [测试报告](results/mink_multiclass_9/nine_report.md) 和 [九次结果](results/mink_multiclass_9/nine_trials.csv)。此前芥末瓶同姿态 5/5 的历史复验保留在 [results/mink_ik1](results/mink_ik1)，不混入本轮。

当前不会主动走近或后退来调距离；走到可抓范围属于后续导航。本轮物体初始中心固定在前方 0.55 m，只改变 -45、0、+45 度朝向。使用已知目标位姿，不包含视觉定位，完整 Task B 的感知、导航和收集投放尚未完成。

## 怎么运行

在已安装 Isaac Sim 5.1、Isaac Lab 2.3.2、Python 3.11 的 Linux GPU 服务器上运行；已验证 GPU 为 RTX 4090，CPU PhysX、GPU 渲染。

~~bash
git clone https://github.com/luyuqi-tim/ATEC_B.git
cd ATEC_B
git switch branch-Mink_IK1
~~

原服务器依赖已装好，直接运行下面的九次测试。新环境先使用配套 Isaac 镜像，再安装工程及 Mink 依赖：

~~bash
source experiments/mink_wholebody/runtime.sh
/isaac-sim/python.sh -m pip install -e . --no-deps
/isaac-sim/python.sh -m pip install -c experiments/mink_wholebody/constraints.txt -r requirements-mink.txt
/isaac-sim/python.sh scripts/check_package.py
~~

上述路径对应当前镜像的 /isaac-sim 和 /workspace/isaaclab；换镜像时需调整 runtime.sh 和 supervise.py 的路径。仓库包含原始资产和老师模型，不包含 Isaac 安装包。完整 requirements.lock.txt 是环境快照，不要整体覆盖另一套镜像。

一条命令运行九个组合，每个只执行一次：

~~bash
bash scripts/run_mink_multiclass.sh --output runs/mink_multiclass/my_nine
~~

输出目录必须不存在。summary.json、trials.csv 是本次结果；各 case/trial_01/continuous.mp4 是完整录像；controller.jsonl 和 evaluation.jsonl 分开记录控制与物理评价。进一步审计和归档见 [实验说明](experiments/mink_multiclass/README.md)。

## 从哪里改

- experiments/mink_multiclass/configs/：九个已锁定的物体、朝向、夹持点和下蹲高度。
- experiments/mink_wholebody/controller.py：下蹲、开爪、接近、闭爪、抬升和保持。
- experiments/mink_wholebody/wholebody_ik.py：Mink 全身 IK 与支撑补偿。
- experiments/mink_wholebody/bench.py、evaluator.py：Isaac 执行与独立评价。

原始 Task B 说明见 [docs/TaskB_original_README.md](docs/TaskB_original_README.md)，第三方声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本轮没有修改原机器人、老师权重、质量、夹爪限力或正式计分。正式环境 LiDAR 的版本兼容问题仍保留。
