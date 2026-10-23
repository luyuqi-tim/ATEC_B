# BinWalker：一周开发约束下的复用审计

审查日期：2026-10-23。范围：读取公开源码、仓库文件清单、论文与本地机器人描述；未安装外部依赖、下载二进制权重、运行 IK、仿真或训练。服务器上的兼容性与抓取效果尚未验证。

## 结论

**BinWalker 不是已验证适配本作业的完整交付包，不能承诺下载后直接让 B2 抓取。能确认的是：有可复用的 Z1 求解器封装、动作流程代码和 Aliengo 相关策略权重；未在已查公开材料中找到可直接用于本作业的抓取示范数据集或完整视觉抓取发布包。**

一周开发不应复制整套 BinWalker 仿真、ROS 和训练系统。候选方案是保留作业环境和老师的 B2 控制，只提取 BinWalker 的 Mink 求解器封装及必要动作流程；先做有时间上限的 Z1 适配验收，再决定是否作为主线。

“复用现成 IK”不等于“从头开发 IK”。Mink 已实现数值求解，项目也已写好 Z1 封装。但坐标、关节零位、夹爪工作点和实际动作结果不能跳过核对。

## 查了什么

- 仓库：[iit-DLSLab/trash-collection-isaaclab](https://github.com/iit-DLSLab/trash-collection-isaaclab)。
- 当前 main 与前次审查一致，固定提交：`76c51c4c08e5762d00c75f36cb07aa3e525d6990`。
- 递归树返回完整的 226 个条目，未截断；检查了权重、配置、数据扩展名及感知相关路径。
- [论文](https://arxiv.org/html/2603.10529v1)、README、README_DEPLOY、部署依赖、IK、状态机、ROS 控制器、操作策略封装、Z1 模型与操作策略训练配置。
- GitHub Releases 列表为空。此结论仅覆盖审查当时该公开仓库，不代表作者没有未公开资源。
- 本地 `assets/b2z1/b2z1_0815.urdf`、`taskb_student/constants.py`、控制接口。

## 资源能复用到什么程度

| 资源 | 确认存在的内容 | 对本任务的判断 |
| --- | --- | --- |
| IK 代码 | `deploy/ik_mink.py`，含 Z1 模型、位置和朝向目标、关节限制、冻结机身自由度选项 | 最值得提取的候选；需做下述适配，尚未实跑 |
| 动作流程 | `deploy/state_machine.py`，预抓取、接近、闭爪、篮口等动作 | 可复用阶段划分和部分逻辑；阻塞循环不能原样接进 `predicts` |
| 操作策略权重 | `tested_policies/arm/aliengo_with_z1/exported/policy.pt`、`policy.onnx` 和训练检查点 | 文件存在；不是与 B2 接口匹配的即用抓取模型 |
| 行走权重 | `tested_policies/locomotion/rough/exported/` | 对应其平台，保留老师的 B2 权重，不替换 |
| 抓取示范数据 | 未在已查代码树、README、论文链接中找到可下载的完整示范轨迹集 | 不把它计入已有资源；训练检查点和 TensorBoard 日志不能当作示范数据集 |
| 视觉链路 | ROS 控制器订阅外部 `detections3d/grasp_poses` | 当前仓库未提供该链路的完整检测发布实现与对应视觉专用权重，不能声称视觉模块已经齐全 |
| 篮子模型 | 有模型及动作关键点 | 依赖其安装与机械设计；不是本作业现成可承接物体的篮子 |
| 自主导航 | 论文实验使用手柄，自动导航不在研究范围 | 仍需我们实现 |

权重文件路径来自 Git 文件树，本次没有下载、加载或验证二进制。操作权重的运行封装读取腿、臂和身体状态，输出六个臂动作及两个身体姿态指令，并依赖自己的底层行走控制；不能只因它使用 Z1 就当作独立抓取策略套用。

## 为什么 IK 有复用价值，但不能照搬

### 臂的基本运动链对得上

本地 URDF 与 BinWalker 的 Z1 模型中，六个关节的局部平移和转轴如下，静态源码比对一致：

| 关节 | 平移 xyz，米 | 转轴 xyz |
| --- | --- | --- |
| joint1 | 0, 0, 0.0585 | 0, 0, 1 |
| joint2 | 0, 0, 0.045 | 0, 1, 0 |
| joint3 | -0.35, 0, 0 | 0, 1, 0 |
| joint4 | 0.218, 0, 0.057 | 0, 1, 0 |
| joint5 | 0.07, 0, 0 | 0, 0, 1 |
| joint6 | 0.0492, 0, 0 | 1, 0, 0 |

这支持“复用其现成求解实现”的判断，不代表工作空间、姿态或夹持效果已经验证。

### 必须适配的地方

1. **安装和零位。** 实际 IK 加载的是 `z1_floating.xml`：臂基座位置为 `(0.22,0,0.055)`，首臂节另有绕 z 轴约 90 度的固定旋转。我们的挂载为 `(0.2,0,0.09)`，首关节原点没有该旋转。状态机还含首关节 `1.57` 的实验编码器偏移，应统一以本地 URDF 为准，避免漏补或重复补偿。
2. **夹爪工作点。** 其求解目标 `attachment_site` 位于 `link06` 的 x 方向 0.15 米处。必须核对我们夹爪实际夹持中心的位置，不能把腕部原点直接当作抓取点。
3. **关节范围。** 两份模型的 joint2–joint5 限制不同，执行侧以本项目约束为准。
4. **身体控制。** 原抓取流程第一次求解开启 `optimize_height=True, optimize_pitch=True`，而本作业老师的低层接口只提供前后速度与转向。独立机械臂候选必须冻结这两个自由度，并验证地面目标是否可达；不能求出“需要弯腰”的解却不执行身体动作。
5. **求解验收。** 当前 `pos_threshold=1e-1`，即允许 10 厘米位置误差；虽计算朝向误差，但返回成功只检查位置。需收紧任务精度并同时检查朝向，不能直接把返回 True 当成可抓取。
6. **路径与碰撞。** 当前封装创建了碰撞约束，但在启用的 limits 中将其注释掉。求出终点不表示中途避开机身、腿和地面；至少要检查预抓取与接近路径。
7. **执行方式。** 状态机用 `time.sleep` 推进真实时间。本项目在 `predicts` 返回后推进仿真，应按控制步更新状态和插值，不能直接复制等待循环。
8. **夹爪端点。** 其闭爪目标为 `0.1`；本项目上限和闭合端为 `0`，速度与力矩也不同。抓住后还需验证物体是否随夹爪抬升。

以上是已定位的适配项，不承诺只改这些就能成功。不要为沿用动作数据去修改指定机器人或计分规则。

## 一周方案与停止条件

### 环境通过后的首个半天：只验收复用接口

范围限于 Mink、MuJoCo 数值求解和最薄适配层，不导入 BinWalker 的 ROS 系统、Aliengo 控制器或训练工程。MuJoCo 在这里作为运动学计算工具，Task B 的实际物理仿真仍由 Isaac Sim 执行。

- 将目标和当前关节角统一到本项目 URDF 的坐标与零位，冻结求解器的机身高度和俯仰。
- 先验证求解模型的正运动学与实际 URDF 一致，再做可达目标的求解与执行检查。
- 建议首轮验收目标：已知可达目标的末端位置误差不超过 5 毫米、朝向误差不超过 5 度；这是拟定验收标准，尚无实验结果，最终仍由实际夹持容差决定。
- 在服务器核对预抓取、接近和抬升轨迹。目标点由规定传感器与已知几何得到，不从场景对象读取物体真实位姿。
- 半天仍未通过时，记录原因并停止继续扩展这一适配路线；不让环境迁移或通用 IK 优化占满一周。

### 按验收结果推进

| 时间 | 首要交付 |
| --- | --- |
| 第 1 天 | 环境与传感器通过；复用 IK 接口和地面可达性有明确结论 |
| 第 2 天 | 一种物体完成视觉定位、闭爪、抬起、保持与释放；未通过则暂停多物体、篮子和大模型扩展 |
| 第 3–4 天 | 单物体运输到目标区并真实得分，加入最基本的搜索和返回 |
| 第 5–6 天 | 扩展类别、布局、重试和连续收集；按剩余时间决定篮子是否值得加入 |
| 第 7 天 | 固定依赖和种子、回归检查、整理提交 |

时间表是资源分配建议，不是成功保证。首先保证一个物体真实得分，再争取数量与泛化。

### 受限后备路线

若求解器集成成本过高，但已验证存在可达抓取姿态，可采用“固定抓取窗口＋预设关节动作”：底盘将物体对准一个固定的相对区域，机械臂重复执行已经验证的动作。这能减少在线 IK 的依赖，但仍需在本机器人上验证至少一套轨迹，对物体姿态和位置的容忍度较低。它也不能解决机身过高、机械臂物理上够不到的问题。

本周不新增大模型作为主依赖，不开始重训步态、迁移整套 VBC 或训练 Aliengo 权重。

## 来源

- [IK 封装](https://github.com/iit-DLSLab/trash-collection-isaaclab/blob/76c51c4c08e5762d00c75f36cb07aa3e525d6990/deploy/ik_mink.py)
- [实际求解模型](https://github.com/iit-DLSLab/trash-collection-isaaclab/blob/76c51c4c08e5762d00c75f36cb07aa3e525d6990/deploy/mujoco/models/z1/z1_floating.xml)
- [状态机](https://github.com/iit-DLSLab/trash-collection-isaaclab/blob/76c51c4c08e5762d00c75f36cb07aa3e525d6990/deploy/state_machine.py)
- [操作策略运行封装](https://github.com/iit-DLSLab/trash-collection-isaaclab/blob/76c51c4c08e5762d00c75f36cb07aa3e525d6990/deploy/manipulation_policy_wrapper.py)
- [ROS 控制器与外部检测订阅](https://github.com/iit-DLSLab/trash-collection-isaaclab/blob/76c51c4c08e5762d00c75f36cb07aa3e525d6990/deploy/run_controller_ros2.py)
- [公开操作策略文件目录](https://github.com/iit-DLSLab/trash-collection-isaaclab/tree/76c51c4c08e5762d00c75f36cb07aa3e525d6990/tested_policies/arm/aliengo_with_z1)
- [仓库完整文件树 API](https://api.github.com/repos/iit-DLSLab/trash-collection-isaaclab/git/trees/76c51c4c08e5762d00c75f36cb07aa3e525d6990?recursive=1)
- [论文：手柄导航、操作流程与视觉方法](https://arxiv.org/html/2603.10529v1)
- [BSD-3-Clause 许可证](https://github.com/iit-DLSLab/trash-collection-isaaclab/blob/76c51c4c08e5762d00c75f36cb07aa3e525d6990/LICENSE)：复制代码时保留声明；资产与第三方依赖分别遵守各自许可证。

另外核查了 [Unitree Z1 SDK 模型示例](https://github.com/unitreerobotics/z1_sdk/blob/f1af2b42f2a39a5010946e049ad3fe324e2e6f06/examples_py/example_model.py)，确认有现成 FK/IK 接口。但该提交自带 Python 扩展为 CPython 3.8 二进制，不能当作本项目 Python 3.11 下直接可导入的替代品；本周不据此另开一条未经验证的集成主线。
