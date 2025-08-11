# Tobii Eye Tracker 数据采集与分析工具

用于 Tobii Eye Tracker 4C/5 眼动追踪设备数据获取和实时分析的完整解决方案。

## 项目概述

由于 Tobii 眼动追踪设备的 SDK 只提供 C/C++ 版本，本项目采用以下架构：
- **C++ 客户端**：使用 Tobii Stream Engine API 获取眼动数据
- **UDP 通信**：通过 Socket 将数据实时传输到 Python 端
- **Python 分析端**：提供数据记录、可视化和分析功能

**官方 SDK 文档**: https://developer.tobii.com/product-integration/stream-engine/

**测试环境**: Windows 11

## 项目结构

```
├── README.md                     # 项目说明文档
├── C++客户端/                    # 编译好的可执行文件
│   ├── eye_tracking.exe          # 主程序（眼动数据采集）
│   ├── tobii_stream_engine.dll   # Tobii 运行库
│   └── *.csv                     # 示例输出数据文件
├── eye_tracking_C++/             # C++ 源代码项目
│   ├── GazeTrackWithTobii.sln    # Visual Studio 解决方案
│   └── src/                      # 源代码目录
├── PythonExamples/               # Python 示例程序
    ├── base.py                   # 基础 UDP 接收示例
    ├── record_csv.py             # 数据记录到 CSV 文件
    ├── visualize.py              # 实时眼动可视化
    └── requirements.txt          # Python 依赖包
```

## 快速开始 

### 1. 环境准备

#### 硬件要求
- Tobii Eye Tracker 4C 或 5
- Windows 10/11 系统
- USB 3.0 接口

#### 驱动安装

1. 访问 https://gaming.tobii.com/zh/getstarted/
2. 下载并安装 Tobii Experience 驱动
3. 在微软商店下载 Tobii Experience 应用
4. 连接设备到 USB 3.0 端口，启动 Tobii Experience 应用，按提示进行校准
5. 运行 `../C++客户端/eye_tracking.exe` 测试是否能正常输出眼动数据

### 2. 使用方法

#### 方法一：基础数据接收
```powershell
# 1. 启动 C++ 数据采集程序
.\C++客户端\eye_tracking.exe

# 2. 在新终端运行 Python 接收程序
python PythonExamples\base.py
```

#### 方法二：数据记录到 CSV
```powershell
# 1. 启动数据采集
.\C++客户端\eye_tracking.exe

# 2. 记录数据到文件（按 Ctrl+C 停止并保存）
python PythonExamples\record_csv.py
```

#### 方法三：实时可视化
```powershell
# 1. 启动数据采集
.\C++客户端\eye_tracking.exe

# 2. 启动实时可视化界面
python PythonExamples\visualize.py
```

## 功能特性

### C++ 数据采集端
- ✅ 实时眼动点坐标获取
- ✅ 双眼位置数据记录
- ✅ 头部姿态追踪
- ✅ 数据时间戳同步
- ✅ CSV 文件自动保存
- ✅ UDP 实时数据传输

### Python 分析端
- **base.py**: 基础 UDP 数据接收和打印
- **record_csv.py**: 数据记录到 CSV 文件，支持时间戳转换
- **visualize.py**: 高级实时可视化功能
  - 🎯 实时眼动点显示
  - 📊 网格参考线
  - ⭕ 多层可视化指示器
  - 📝 实时数据信息显示
  - ⌨️ 快捷键控制

### 数据格式

**UDP 传输格式**: `timestamp_micros,x_coordinate,y_coordinate`
- `timestamp_micros`: 微秒级时间戳
- `x_coordinate`: 屏幕 X 坐标 (0.0-1.0)
- `y_coordinate`: 屏幕 Y 坐标 (0.0-1.0)

**CSV 文件格式**:
```csv
timestamp [micros],x,y
1628123456789000,0.512,0.345
1628123456799000,0.508,0.352
```

## 开发指南

### C++ 项目编译

如需修改 C++ 代码：

1. **环境要求**
   - Visual Studio 2019/2022
   - Tobii Stream Engine SDK

2. **编译步骤**
   ```powershell
   # 打开 Visual Studio 解决方案
   .\eye_tracking_C++\GazeTrackWithTobii.sln
   
   # 或使用命令行编译
   msbuild .\eye_tracking_C++\GazeTrackWithTobii.sln /p:Configuration=Release
   ```

### Python 开发

**扩展功能建议**:
- 数据滤波和平滑处理
- 眼动轨迹分析算法
- 注视点热力图生成
- 多屏幕坐标映射
- 数据库存储支持

**自定义可视化参数**:
```python
# 在 visualize.py 中修改 GazeVisualizationConfig 类
class GazeVisualizationConfig:
    BACKGROUND_WIDTH = 1920      # 背景宽度
    BACKGROUND_HEIGHT = 1080     # 背景高度
    GAZE_OUTER_CIRCLE_RADIUS = 20  # 外圈半径
    # ... 更多配置选项
```

## 故障排除

### 常见问题

**1. 设备未检测到**
- 确认 Tobii 设备已正确连接
- 检查 USB 3.0 接口连接
- 重新安装驱动程序

**2. 数据接收异常**
- 确认防火墙未阻止 UDP 通信
- 检查端口 1235 是否被占用
- 验证 IP 地址 127.0.0.1 可访问

**3. Python 依赖问题**
```powershell
# 重新安装依赖
pip install --upgrade mss numpy opencv-python
```

**4. 可视化窗口不显示**
- 检查显示器分辨率设置
- 尝试修改 `GazeVisualizationConfig` 中的分辨率参数

### 性能优化

- **数据采样频率**: 默认为设备最大频率（通常 60-90 Hz）
- **网络延迟**: UDP 传输延迟通常 < 1ms
- **内存使用**: 长时间运行建议定期清理数据缓存

## 技术细节

### 坐标系统
- **Tobii 坐标系**: 左上角为原点 (0,0)，右下角为 (1,1)
- **屏幕坐标系**: 像素坐标，需要根据屏幕分辨率进行转换

### 数据精度
- **时间精度**: 微秒级 (μs)
- **空间精度**: 通常 0.5-1.0 度视角
- **采样频率**: 60-90 Hz（取决于设备型号）

### 通信协议
```
C++ Client ←→ Python Server
    ↓ UDP (127.0.0.1:1235)
[timestamp,x,y] 格式数据流
```

## 许可证与引用

本项目基于原始参考项目开发，遵循相应的开源协议。

**参考引用**:
```bibtex
@misc{tobii_eyetracker_python,
  title={TobiiEyeTracker.py},
  author={DigitalNatureGroup},
  url={https://github.com/DigitalNatureGroup/TobiiEyeTracker.py},
  year={2023}
}
```

---

**联系方式**: 如有问题请提交 Issue 或联系项目维护者。
