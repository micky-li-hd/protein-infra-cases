# 发布范围与复现缺口

本包已包含三个候选补丁和脱敏后的实验摘要，可用于核对发布文案。暂不能宣传为开箱即用的训练复现仓库。

训练补丁改动 `training/model_utils.py`，包含 PyTorch Inductor 内部选项和全局编译 hook。发布可运行版本前，应锁定实验使用的完整 PyTorch、CUDA、驱动及依赖版本，附参考源 SHA256、checkpoint 和数据 fixture 的获取流程、相同 seed 控制与测量入口。不能仅凭补丁推出其他 PyTorch 版本、其他形状或其他显卡也有同等收益。

训练原始配置包括每 epoch 64 examples、最长 512 residues、token budget 4096、原始 FP16 autocast 与 FP32 参数和优化器、Adam + Noam warmup 4000、原始 smoothed loss 和 /2000 归一化。数据通过正常 PDB loader 读取，不使用缓存 toy batch 替换训练工作量。

ProteinMPNN 推理补丁修改 `protein_mpnn_utils.py`；RFdiffusion 补丁修改 `rfdiffusion/inference/model_runners.py`。复现时需分别检出锁定上游版本，在独立 checkout 中检查补丁适用性，再进行原版与候选版对照。

上游 LICENSE 与第三方归属说明已包含在本包中。三个补丁已对锁定上游源文件通过 `git apply --check`。完整训练复现仍需补齐可公开的数据资产来源、环境版本和原始验收输出，并在干净 GPU 环境执行所提供的命令。当前摘要中的通过结论描述原实验，不表示已在这个发布目录重新执行。

三个案例都没有 ResearchBoost 四关认证。不要将完整训练收敛、跨硬件收益或其他蛋白质任务质量改善作为已完成结果。
