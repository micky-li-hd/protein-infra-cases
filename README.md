# Protein infrastructure acceleration cases

蛋白质研究代码的基础设施优化实验：保持任务工作量，修改执行方式，同时检查性能和数值行为。组织方式参考 [ResearchBoost-Agent](https://github.com/AI4AI-for-Anything/ResearchBoost-Agent) 与 [Faster-RAE](https://github.com/AI4AI-for-Anything/Faster-RAE)。这里提供候选补丁、实测结果和验证范围，尚非一键复现完整训练的发行版。

## 实测结果

每项结果均来自单张 A100 上同配置的原版和候选版比较；各项计时范围不同，不计算跨项目平均加速比。

| 案例 | 计时范围 | 原版 → 候选版 | 加速比 | 验证范围 |
| --- | --- | --- | --- | --- |
| ProteinMPNN 训练 | 预热后的训练循环 | 99.59 → 46.83 ms/update | **2.13×** | 3 组 R-C-R 测速；3 × 128 次更新的数值比较 |
| ProteinMPNN 推理 | 32 条序列生成阶段 | 代表组约 10.40 → 8.72 s | **1.19×** | 输出与最终 RNG 精确一致，补充 seed、batch 和缺失 mask 检查 |
| RFdiffusion 推理 | 完整 50 步设计阶段 | 28.19 → 27.02 s | **1.043×** | 原始轨迹、RNG、PDB/TRB 一致 |

**训练 2.13× 仅指稳态。** 包含冷编译的短 160-update 进程从 27.17 s 增至 192.96 s，实际更慢约 7.10 倍；峰值 allocated 显存从 3.208 增至 4.160 GiB。没有完成收敛验证，也没有获得 ResearchBoost 四关认证。RFdiffusion 的整进程收益没有通过噪声阈值，不能将 1.043× 写成端到端加速。

## 怎么优化

ProteinMPNN 训练将按 dtype 分组的数据传输合并，使用解码顺序的逆排列比较构造邻居可见性，减少稠密排列矩阵计算；移除 activation checkpoint 重算并启用动态形状编译。编译设置保留随机行为和低精度舍入边界。这里包含显存换算力的取舍，且使用 PyTorch 内部配置，不能假设跨版本直接兼容。

ProteinMPNN 推理将索引 `repeat` 换为 `expand` 视图，提前计算不变的 padding 分支，并减少解码层间重复的 mask gather。32 条序列、106 residues、batch 1、temperature 0.1、seed 37，精度与采样任务不变。

RFdiffusion 将模型前向的 `torch.no_grad()` 换为 `torch.inference_mode()`，减少推理中的 autograd 元数据开销。测试为 100 residues、seed 0、完整 50 步的无条件生成，保留所有轨迹输出。

## 如何判断收益可信

先固定源代码、数据、checkpoint、随机控制、精度、优化器与原始工作量，再运行 reference–candidate–reference。多个独立进程重复测量，性能收益必须超过预设噪声阈值。检查输出、梯度或参数、优化器状态和随机状态；失败候选保留记录。冷启动、稳态、显存和数值证据分开报告。

训练测速是 3 组 R-C-R、共 9 个进程，每个进程预热 40 updates，再计时 3 个 35-update 窗口。**轮次编号不代表独立候选数量。** 当前训练证据属于 development 结果，`n1_pass=false`、`four_gate_certified=false`；短轨迹检查不等于完整训练收敛一致。

## 文件

- `*.patch`：三个候选的源代码差异；训练补丁基于 ProteinMPNN commit `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57` 的参考快照。RFdiffusion 基于 `86507b6538f51fce57b5a72477165f03999ed7ae`。
- `*.json`：从本地实验记录导出的结果摘要及补丁哈希；移除了服务器路径和进程标识。这些摘要不是完整原始轨迹。
- [发布范围与复现缺口](reproduction.md)：完整训练复现仍需补齐的环境与数据材料。

## 使用推理补丁

先准备一个独立的上游 checkout。以下命令从本案例仓库根目录执行，应用 ProteinMPNN 推理补丁；不会启动 GPU 任务。

```bash
git clone https://github.com/dauparas/ProteinMPNN.git ../ProteinMPNN-inference
git -C ../ProteinMPNN-inference checkout 8907e6671bfbfc92303b5f79c4b5e6ce47cdef57
python apply_case.py proteinmpnn-inference ../ProteinMPNN-inference --check-only
python apply_case.py proteinmpnn-inference ../ProteinMPNN-inference
```

按照上游说明安装依赖后，可运行原始测试工作量：

```bash
cd ../ProteinMPNN-inference
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 python protein_mpnn_run.py \
  --pdb_path inputs/PDB_monomers/pdbs/5L33.pdb --pdb_path_chains A \
  --path_to_model_weights vanilla_model_weights --model_name v_48_020 \
  --seed 37 --num_seq_per_target 32 --batch_size 1 --sampling_temp 0.1 \
  --backbone_noise 0.0 --out_folder outputs-case --save_score 1 --save_probs 1
```

原实验使用 PyTorch `2.5.1+cu121`。上面的单次运行用于执行工作量，不会自动重现三组测速或数值验收。比较收益时，应在另一份未修改的 checkout 中运行相同任务，并执行完整 R-C-R 和输出比较，不能只取最快的一次。

RFdiffusion 使用独立 checkout 的 `86507b6538f51fce57b5a72477165f03999ed7ae`，对应命令为 `python apply_case.py rfdiffusion-inference <checkout>`。训练补丁使用另一份 ProteinMPNN checkout，命令为 `python apply_case.py proteinmpnn-training <checkout>`；须先阅读训练兼容性与复现限制。

## 未计入成功案例的实验

Protenix 尚无验收通过的加速结果；OpenFold 的探索性测速未通过完整数值验收；FrameFlow 编译遇到重编译限制和超时；PAR-Protein 编译候选没有测速收益。它们不能放入成功结果表。

## 致谢

原始项目：[ProteinMPNN](https://github.com/dauparas/ProteinMPNN)、[RFdiffusion](https://github.com/RosettaCommons/RFdiffusion)。方法参考 ResearchBoost-Agent。上游代码及衍生补丁受各自许可证约束；本文不代表上游项目或 ResearchBoost 官方认证。

## 独立训练运行包

已补充[完整训练代码与运行入口](TRAINING_RUNTIME.md)，包含锁定的原版与候选代码、依赖、官方完整数据训练配置、共享 GPU 锁和进程所有权清理。新入口目前通过 CPU 检查，尚待空闲 GPU 做启动验证及后续完整训练；这不是新增加速或收敛结果。
