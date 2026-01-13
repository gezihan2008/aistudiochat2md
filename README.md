# AI Studio 聊天记录转 Markdown 工具

一个简单易用的工具，用于将 Google AI Studio 聊天记录转换为清晰易读的 Markdown 文档。

## 📋 项目概述

该工具可以帮助您将 Google AI Studio 导出的聊天记录 JSON 文件转换为结构清晰、格式美观的 Markdown 文档，方便阅读、分享和归档。

## ✨ 功能特性

### 🎯 核心功能
- **批量转换**：支持同时转换多个 AI Studio 聊天记录文件
- **自动识别**：智能识别聊天记录中的用户和 AI 消息
- **格式优化**：生成结构清晰、美观易读的 Markdown 文档
- **完整保留**：保留聊天记录中的所有内容，包括 AI 思考过程
- **多种输出**：支持命令行和图形界面两种使用方式

### 🖥️ 图形界面特性
- **直观操作**：简洁友好的图形界面，无需命令行知识
- **拖放支持**：支持直接拖放文件到窗口进行转换
- **批量处理**：可从目录批量导入文件
- **进度显示**：实时显示转换进度
- **结果反馈**：清晰的转换结果反馈

### 📁 支持的文件格式
- **输入**：Google AI Studio 导出的聊天记录 JSON 文件
- **输出**：标准 Markdown (.md) 文件

## � 如何获取 AI Studio 聊天记录

### 从 Google AI Studio 直接导出
1. 打开 [Google AI Studio](https://aistudio.google.com/)
2. 选择您想要导出的聊天记录会话
3. 点击右上角的 **分享** 按钮
4. 在弹出的菜单中选择 **导出**
5. 选择 **JSON** 格式，点击 **导出**
6. 保存下载的 JSON 文件到您的电脑

### 从谷歌云盘下载
1. 打开 [谷歌云盘](https://drive.google.com/)
2. 导航到 AI Studio 聊天记录存储文件夹（通常位于 `Google AI Studio` 文件夹下）
3. 找到您想要下载的聊天记录 JSON 文件
4. 右键点击该文件，选择 **下载**
5. 保存文件到您的电脑

### 批量下载提示
- 如果您有多个聊天记录文件需要下载，可以按住 `Ctrl` (Windows) 或 `Command` (Mac) 键选择多个文件，然后右键点击并选择 **下载**
- 下载的文件会被压缩成 ZIP 格式，您需要先解压才能使用本工具转换

## �🚀 快速开始

### 方法一：使用可执行文件（推荐）

1. 直接下载或从项目 `dist` 目录获取 `AI Studio转Markdown工具.exe`
2. 双击运行该文件
3. 在弹出的界面中：
   - 点击「➕ 添加文件」选择要转换的 AI Studio 聊天记录文件
   - 或点击「📁 从目录添加」批量导入文件
   - 或直接将文件拖放到窗口中
4. 点击「🚀 开始转换」
5. 转换完成后，Markdown 文件将保存在源文件同一目录下

### 方法二：使用 Python 脚本

#### 环境要求
- Python 3.7 或更高版本

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 使用命令行工具
```bash
python AI Studio_to_md.py <input_file1> <input_file2> ...
```

例如：
```bash
python AI Studio_to_md.py "Husband's Wife's Emotional Distress" "Mind Quadrant_ Inner World Assessment"
```

#### 使用图形界面脚本
```bash
python AI Studio_to_md_gui.py
```

## 📦 项目结构

```
.
├── AI Studio_to_md.py          # 核心转换脚本（命令行版）
├── AI Studio_to_md_gui.py      # 图形界面版本
├── requirements.txt           # 依赖列表
├── README.md                  # 项目说明文档
├── dist/                      # 打包后的可执行文件目录
│   └── AI Studio转Markdown工具.exe
├── output/                    # 转换结果示例目录
└── build/                     # 打包临时目录
```

## 📄 转换示例

### 输入：AI Studio 聊天记录 JSON
```json
{
  "chunkedPrompt": {
    "chunks": [
      {
        "parts": [
          {
            "text": "你好",
            "role": "user"
          }
        ]
      },
      {
        "parts": [
          {
            "text": "你好！我是你的AI助手，有什么可以帮助你的吗？",
            "role": "model"
          }
        ]
      }
    ]
  }
}
```

### 输出：Markdown 文档
```markdown
# 聊天记录

> 导出时间: 2026-01-13 15:51:45

---

### 👤 用户

你好

<details><summary>元数据</summary>

Tokens: 3

</details>

---

### 🤖 AI助手

你好！我是你的AI助手，有什么可以帮助你的吗？

<details><summary>元数据</summary>

Tokens: 15

</details>

---
```

## 🛠️ 核心代码说明

### AI StudioChatParser 类

```python
class AI StudioChatParser:
    """AI Studio 聊天记录解析器"""
    
    def load_chat_file(self, file_path: str) -> dict:
        """加载并解析 JSON 文件"""
        pass
    
    def extract_chunks(self, data: dict) -> list:
        """提取聊天记录块"""
        pass
    
    def format_message(self, chunk: dict) -> str:
        """格式化单条消息"""
        pass
    
    def convert_to_markdown(self, data: dict, title: str = "聊天记录") -> str:
        """将解析后的数据转换为 Markdown 格式"""
        pass
    
    def process_file(self, input_path: str, output_dir: str = None) -> tuple:
        """处理单个文件"""
        pass
    
    def process_multiple_files(self, file_paths: list, output_dir: str = None) -> list:
        """批量处理多个文件"""
        pass
```

## 📝 自定义配置

您可以根据需要修改以下配置：

1. **输出目录**：默认输出到源文件同一目录，可在代码中修改
2. **Markdown 模板**：可修改 `convert_to_markdown` 方法中的模板
3. **角色映射**：可修改 `role_map` 字典来自定义角色显示

## 🔧 常见问题

### Q: 转换失败怎么办？
A: 请检查：
   - 输入文件是否为有效的 AI Studio 聊天记录 JSON 文件
   - 文件是否完整，没有损坏
   - 如果使用命令行，是否有足够的权限

### Q: 转换后的 Markdown 文件在哪里？
A: 默认保存在源文件同一目录下，文件名与源文件相同，后缀为 `.md`

### Q: 支持 Linux 或 macOS 吗？
A: 当前提供的可执行文件仅支持 Windows 系统。Linux 和 macOS 用户可以使用 Python 脚本版本。

### Q: 可以转换其他平台的聊天记录吗？
A: 目前仅支持 Google AI Studio 导出的聊天记录格式。

## 📋 更新日志

### v1.0.0 (2026-01-13)
- ✨ 初始版本
- 🎯 支持 AI Studio 聊天记录转换为 Markdown
- 🖥️ 提供图形界面和命令行两种使用方式
- 📦 支持批量转换
- 🎨 美观的 Markdown 输出格式
- 🔄 完整保留聊天记录内容

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：[gezihan2008@gmail.com]

---

**祝您使用愉快！** 🎉
