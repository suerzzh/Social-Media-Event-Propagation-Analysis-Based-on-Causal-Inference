# PCMCI分析说明（重要改进）

## 🎯 关键问题发现

你的原始代码和参考文献结果差距很大的主要原因：

### **问题：使用了错误的独立性检验方法**

#### 原始代码的问题
```python
# ❌ 错误：使用ParCorr（只适合线性关系）
cond_ind_test = ParCorr(significance='analytic')
```

#### B1C数据集的特点
- **B1C是非线性数据**（包含多项式关系，如 X^2, X^3）
- **ParCorr（偏相关检验）只适合线性关系**
- **结果**：无法正确识别非线性因果关系

---

## ✅ 解决方案

### 新代码使用GPDC（非线性检验方法）

```python
# ✅ 正确：使用GPDC（适合非线性关系）
cond_ind_test = GPDC(significance='analytic', gp_params=None)
```

### GPDC vs ParCorr

| 检验方法 | 适用场景 | B1C数据集 |
|---------|---------|----------|
| **ParCorr** | 线性关系 | ❌ 不适合 |
| **GPDC** | 非线性关系 | ✅ **推荐** |
| **CMIknn** | 非线性关系（基于kNN） | ✅ 可选 |

---

## 📝 新代码特点

### 1. **正确的检验方法**
- 使用GPDC处理非线性数据
- 自动识别多项式因果关系

### 2. **标准可视化**
- 使用`tp.plot_time_series_graph`（tigramite标准方法）
- 与参考文献的可视化方式一致

### 3. **完整的输出**
- 因果图（PNG格式）
- 详细结果（CSV格式）
- 数据集信息（CSV格式）

### 4. **自动目录分类**
- 结果自动保存到`run_data/数据集类型/噪声类型/配置/`
- 便于管理和对比

---

## 🔄 代码对比

### 原始代码（pcmci_validation.py）
```python
# 问题1: 使用ParCorr（线性检验）
cond_ind_test = ParCorr(significance='analytic')

# 问题2: 可视化方法可能不标准
plot_graph(...)  # 自定义可视化
```

### 新代码（pcmci_analysis_b1c.py）
```python
# 改进1: 使用GPDC（非线性检验）
cond_ind_test = GPDC(significance='analytic', gp_params=None)

# 改进2: 使用标准可视化方法
tp.plot_time_series_graph(...)  # tigramite标准方法
```

---

## 🚀 使用新代码

### 运行新代码
```bash
python pcmci_analysis_b1c.py
```

### 预期改进
1. ✅ **能正确识别非线性因果关系**
2. ✅ **结果更接近ground truth**
3. ✅ **可视化更标准**
4. ✅ **结果更可靠**

---

## ⚠️ 注意事项

### 1. 计算时间
- GPDC比ParCorr计算时间更长
- 这是正常的，因为非线性检验更复杂

### 2. 参数调整
如果结果仍不理想，可以尝试：
- 调整`alpha_level`（显著性水平）
- 调整`tau_max`（最大滞后）
- 尝试`CMIknn`作为替代方法

### 3. 对比验证
- 对比ground truth图（`_graph.png`文件）
- 评估发现的因果关系是否准确

---

## 📊 预期结果

使用新代码后，你应该能看到：

1. **更多显著的因果关系**
   - 因为GPDC能识别非线性关系

2. **更准确的结果**
   - 更接近ground truth

3. **标准格式的因果图**
   - 与tigramite官方示例一致

---

## 🔍 如果结果仍不理想

### 可能原因
1. **样本量太小**：尝试n3000或n5000
2. **参数设置**：调整alpha_level或tau_max
3. **数据质量**：检查数据是否正确加载

### 建议
1. 先用小数据集测试（4变量，n1000）
2. 对比ground truth图
3. 逐步增加复杂度

---

## 💡 总结

**关键改进：**
- ✅ 使用GPDC（非线性检验）代替ParCorr（线性检验）
- ✅ 使用标准可视化方法
- ✅ 代码结构更清晰

**这应该能显著改善你的结果！** 🎉

