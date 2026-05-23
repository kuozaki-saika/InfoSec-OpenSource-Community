# 基于神经网络的图像分类实验

## 环境要求
- Python 3.8+
- TensorFlow 2.10+
- matplotlib
- numpy
- seaborn
- scikit-learn


pip install tensorflow matplotlib numpy seaborn scikit-learn


文件	说明
实验一：基于神经网络的图像分类.py	主程序，包含数据加载、模型构建、训练、评估全流程
best_model.h5	训练过程中保存的最佳模型
*_training_history.png	训练曲线图
*_confusion_matrix.png	混淆矩阵图

运行方式
python 实验一：基于神经网络的图像分类.py

配置说明
默认使用 MNIST 数据集，修改 DATASET = 'mnist' 为 'cifar10' 可切换
超参数（学习率、批次大小、轮次等）已提取为顶部常量，便于统一调整

注意事项
首次运行会自动下载数据集，请保持网络畅通
运行产生的 .h5、.png 文件已被 .gitignore 排除，无需手动清理
