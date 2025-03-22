# 基于电解CO2制CO结合费托合成生产SAF的生命周期评价(LCA)模型

## 1. 模型概述

本LCA模型评估基于CO2电解合成一氧化碳(CO)及水电解制氢(H2)，再通过费托合成制备可持续航空燃料(SAF)的全生命周期环境影响。模型依据IATA《可持续航空燃料(SAF)核算与报告方法》，遵循ISO 14040/44标准，采用"从摇篮到坟墓"的全生命周期评价方法。

### 1.1 系统边界

```
               ┌────────────────── 系统边界 ──────────────────┐
               │                                              │
CO2捕获/获取 ──┼──> CO2运输 ──> CO2电解 ──> CO生产             │
               │                                 ↘            │
               │                                   ──> 费托合成 ──> SAF产品升级 ──> SAF运输 ──> 航空发动机燃烧
               │                                 ↗            │
水处理/提取 ───┼──> 水电解 ──> H2生产                          │
               │                                              │
电力供应 ─────┼──────────────────────────────────────────────┘
(可再生/常规)   │
```

### 1.2 功能单位

- 主要功能单位: 1 MJ 最终使用的SAF能量
- 替代功能单位: 1 kg SAF或1升SAF（用于特定分析场景）

## 2. 生命周期阶段与计算方法

### 2.1 原料获取与运输阶段

#### 2.1.1 CO2捕获/获取
CO2可来自三种来源，其碳强度各不相同：
1. **工业点源捕获**: 如水泥厂、钢铁厂和发电厂的烟气
2. **生物质来源CO2**: 如发酵、沼气提纯过程
3. **直接空气捕获(DAC)**: 从大气中直接捕获CO2

计算公式:
```
CO2_capture_emissions = CO2_capture_energy * energy_emission_factor + capture_process_emissions
```

其中:
- `CO2_capture_energy`: 捕获每吨CO2所需能源(MJ/t CO2)
- `energy_emission_factor`: 使用能源的排放因子(kg CO2e/MJ)
- `capture_process_emissions`: 捕获过程直接排放(kg CO2e/t CO2)

#### 2.1.2 CO2运输
根据运输距离和方式(管道、卡车、船舶)计算:
```
CO2_transport_emissions = transport_distance * transport_mode_factor * CO2_amount
```

#### 2.1.3 水资源获取与处理
包括水提取和纯化处理:
```
water_emissions = water_amount * (extraction_ef + purification_ef)
```

其中:
- `water_amount`: 所需水量(kg)
- `extraction_ef`: 水提取排放因子(kg CO2e/kg)
- `purification_ef`: 水纯化排放因子(kg CO2e/kg)

### 2.2 转化阶段

#### 2.2.1 CO2电解过程
计算CO2电解为CO的排放:
```
CO2_electrolysis_emissions = electricity_consumption * electricity_ef + 
                           direct_process_emissions - biogenic_carbon_credit
```

其中:
- `electricity_consumption`: 电力消耗(kWh/kg CO)
- `electricity_ef`: 电力排放因子(kg CO2e/kWh)
- `direct_process_emissions`: 工艺直接排放
- `biogenic_carbon_credit`: 若使用生物质来源CO2，可计入碳减排

#### 2.2.2 水电解过程
计算水电解为H2的排放:
```
water_electrolysis_emissions = electricity_consumption_h2 * electricity_ef + 
                             process_emissions
```

#### 2.2.3 费托合成与升级
计算合成气转化为SAF的排放:
```
FT_synthesis_emissions = process_energy * energy_ef + 
                        catalyst_emissions + other_process_emissions
```

其中:
- `process_energy`: 费托过程能耗(MJ/kg SAF)
- `energy_ef`: 能源排放因子(kg CO2e/MJ)
- `catalyst_emissions`: 催化剂生产和更换的归一化排放
- `other_process_emissions`: 其他工艺排放

#### 2.2.4 SAF产品升级
计算产品精制和加氢过程排放:
```
upgrading_emissions = upgrading_energy * energy_ef + upgrading_hydrogen * h2_ef
```

其中:
- `upgrading_energy`: 升级能耗(MJ/kg SAF)
- `upgrading_hydrogen`: 产品升级所需氢气(kg/kg SAF)
- `h2_ef`: 氢气排放因子(kg CO2e/kg H2)

### 2.3 产品配送与使用阶段

#### 2.3.1 SAF运输与配送
```
distribution_emissions = distribution_distance * transport_mode_factor
```

#### 2.3.2 燃烧阶段排放
对于生物质碳源或DAC捕获的CO2制造的SAF:
```
combustion_emissions = 0 (生物质碳为中性)
```

对于工业点源CO2制造的SAF:
```
combustion_emissions = direct_CO2_emissions * allocation_factor
```

### 2.4 能源与辅助投入

#### 2.4.1 电力排放计算
对使用的电力，根据其来源计算排放:
```
electricity_emissions = electricity_consumption_total * grid_mix_factor
```

对于可再生电力:
```
renewable_electricity_emissions = renewable_electricity * renewable_ef
```

#### 2.4.2 催化剂与化学品
```
catalyst_emissions = (catalyst_amount / catalyst_lifetime) * catalyst_production_ef
```

## 3. 排放计算与分配

### 3.1 总排放计算
对各阶段排放进行累加:
```
total_emissions = CO2_capture_emissions + transport_emissions + 
                 CO2_electrolysis_emissions + water_electrolysis_emissions +
                 FT_synthesis_emissions + upgrading_emissions +
                 distribution_emissions + combustion_emissions
```

### 3.2 排放强度计算
1. **按能量计算**: emissions_intensity_MJ = total_emissions / energy_content (g CO2e/MJ)
2. **按质量计算**: emissions_intensity_kg = total_emissions / mass (kg CO2e/kg SAF)
3. **按体积计算**: emissions_intensity_L = total_emissions / volume (kg CO2e/L SAF)

### 3.3 减排效益计算
与传统航空燃料的比较:
```
emission_reduction = (fossil_jet_fuel_emissions - saf_emissions) / fossil_jet_fuel_emissions * 100%
```

其中:
- `fossil_jet_fuel_emissions`: 常规航煤排放强度(89 g CO2e/MJ，按CORSIA标准)
- `saf_emissions`: 计算所得SAF排放强度(g CO2e/MJ)

## 4. 不确定性分析与敏感性分析

### 4.1 蒙特卡罗不确定性分析
对关键参数进行概率分布假设，如:
- CO2捕获效率: N(μ, σ²)
- 电解效率: N(μ, σ²)
- 费托转化选择性: N(μ, σ²)
- 电力排放因子: N(μ, σ²)

运行1000-10000次蒙特卡罗模拟，得到结果分布。

### 4.2 敏感性分析
对以下关键参数进行±20%敏感性分析:
1. 电力排放强度
2. CO2捕获能耗
3. 电解效率
4. 费托转化率
5. 可再生电力比例
6. 运输距离

## 5. 数据需求与默认参数

### 5.1 关键数据需求
| 参数名称 | 单位 | 典型值范围 | 数据来源 |
|---------|------|-----------|---------|
| CO2捕获能耗 | MJ/t CO2 | 4000-7000 | 工艺数据 |
| 点源CO2捕获效率 | % | 85-95 | 工艺数据 |
| DAC能耗 | MJ/t CO2 | 5000-10000 | 文献 |
| CO2电解能耗 | kWh/kg CO | 2.5-5.0 | 工艺数据 |
| 水电解能耗 | kWh/kg H2 | 45-55 | 工艺数据 |
| 费托转化效率 | % | 70-85 | 工艺数据 |
| 费托产物选择性 | % | 60-80 | 工艺数据 |
| 电网排放因子 | kg CO2e/kWh | 0.1-0.8 | 地区数据 |
| SAF能量密度 | MJ/kg | 43.5-44.1 | 产品规格 |
| H2/CO比例 | mol/mol | 2.0-2.2 | 工艺参数 |

### 5.2 默认排放因子
| 活动 | 排放因子 | 单位 | 来源 |
|------|----------|------|------|
| 电网电力(全球平均) | 0.475 | kg CO2e/kWh | IEA 2021 |
| 电网电力(欧盟) | 0.253 | kg CO2e/kWh | EEA 2020 |
| 电网电力(中国) | 0.638 | kg CO2e/kWh | IEA 2021 |
| 太阳能光伏电力 | 0.048 | kg CO2e/kWh | IPCC 2014 |
| 风能 | 0.011 | kg CO2e/kWh | IPCC 2014 |
| 水力 | 0.024 | kg CO2e/kWh | IPCC 2014 |
| 天然气 | 56.1 | kg CO2e/GJ | IPCC 2006 |
| 生物质热能 | 0-36 | kg CO2e/GJ | 取决于原料 |
| 铁催化剂生产 | 3.5 | kg CO2e/kg | 文献 |
| 水提取与处理 | 0.3-1.5 | kg CO2e/m³ | 地区数据 |
| 卡车运输 | 0.062 | kg CO2e/t·km | GLEC 2019 |
| 铁路运输 | 0.022 | kg CO2e/t·km | GLEC 2019 |
| 船舶运输 | 0.008 | kg CO2e/t·km | GLEC 2019 |

## 6. 可持续性标准与认证

### 6.1 符合标准
本LCA评估方法设计满足以下主要标准与框架:
- ISO 14040/44: 生命周期评价原则与框架
- CORSIA: 国际民航组织碳抵消和减排计划
- RED II: 欧盟可再生能源指令II
- ASTM D7566: 合成液体燃料规范
- RSB: 可持续生物材料圆桌会议标准

### 6.2 认证路径
SAF认证流程应包括:
1. 系统边界定义与功能单位确认
2. 数据收集与验证
3. LCA计算与第三方审核
4. 符合性声明与认证报告
5. 持续监控与更新

## 7. 案例分析

### 7.1 电力来源情景分析

| 电力情景 | 描述 | 预期排放强度 (g CO2e/MJ) | 减排比例 |
|---------|------|-------------------------|---------|
| 基准情景 | 全球平均电网(475 g CO2e/kWh) | 60-75 | 15-30% |
| 低碳情景 | 50%可再生+50%电网 | 30-45 | 50-65% |
| 全可再生情景 | 100%可再生电力 | 5-15 | 83-95% |

### 7.2 CO2来源情景分析

| CO2来源 | 描述 | 预期排放强度 (g CO2e/MJ) | 减排比例 |
|--------|------|-------------------------|---------|
| 工业点源 | 水泥厂捕获 | 40-50 | 43-55% |
| 生物质CO2 | 乙醇发酵源 | 10-20 | 77-89% |
| DAC | 直接空气捕获 | 15-30 | 66-83% |

### 7.3 完整案例计算
基于以下假设计算示例:
- CO2来源: 生物质发酵(乙醇厂)
- 电力: 80%可再生+20%电网
- 产能: 5000吨SAF/年
- 运输距离: CO2 50km, SAF 300km

每阶段排放与最终强度详细计算过程与结果。

## 8. 持续改进与数据更新机制

### 8.1 数据管理计划
- 初始LCA计算基于设计参数
- 运行数据收集与定期更新
- 每年重新计算排放强度
- 外部因素变化(如电网强度)的定期更新

### 8.2 技术路线改进
- 持续识别碳足迹热点
- 定义减排机会排序
- 评估新技术整合可能性
- 扩大项目规模的阶段性计划

## 9. 附录

### 9.1 计算工具与资源
- 推荐LCA软件工具
- 数据来源清单
- 排放因子数据库

### 9.2 术语与缩略语
- LCA: 生命周期评价
- GWP: 全球变暖潜能值
- CORSIA: 国际航空碳抵消和减排计划
- SAF: 可持续航空燃料
- DAC: 直接空气捕获
- FT: 费托合成
