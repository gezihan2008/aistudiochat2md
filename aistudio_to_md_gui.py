#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Aistudio 聊天记录转 Markdown 文档工具 (GUI版)
功能：解析 Aistudio 导出的 JSON 格式聊天记录，转换为可读的 Markdown 文档
支持：多文件选择、目录选择、拖放操作
"""

import json
import os
import sys
import threading
from pathlib import Path
from datetime import datetime
from tkinter import (
    Tk, Frame, Label, Button, Listbox, Scrollbar, Text, 
    filedialog, messagebox, ttk, END, SINGLE, VERTICAL, HORIZONTAL
)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DRAG_DROP = True
except ImportError:
    HAS_DRAG_DROP = False
    print("提示: tkinterdnd2 未安装，拖放功能不可用")


class AistudioChatParser:
    """Aistudio 聊天记录解析器"""

    def __init__(self):
        self.role_map = {
            'user': ('用户', '👤'),
            'model': ('AI助手', '🤖')
        }

    def load_chat_file(self, file_path: str) -> dict:
        """加载并解析 JSON 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_chunks(self, data: dict) -> list:
        """提取对话内容块"""
        if 'chunkedPrompt' in data and 'chunks' in data['chunkedPrompt']:
            return data['chunkedPrompt']['chunks']
        return []

    def clean_text(self, text: str) -> str:
        """清理文本中的特殊字符"""
        if not text:
            return ''
        text = text.strip()
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        return text

    def format_message(self, chunk: dict) -> str:
        """格式化单条消息"""
        role = chunk.get('role', 'unknown')
        role_name, role_icon = self.role_map.get(role, ('未知', '❓'))

        text = self.clean_text(chunk.get('text', ''))
        token_count = chunk.get('tokenCount', 0)
        finish_reason = chunk.get('finishReason', '')

        parts = chunk.get('parts', [])
        if parts and len(parts) > 1:
            main_text = ''
            for part in parts:
                if isinstance(part, dict):
                    part_text = part.get('text', '')
                    if part.get('thought', False):
                        continue
                    main_text += part_text
                else:
                    main_text += str(part)
            if main_text.strip():
                text = self.clean_text(main_text)

        if not text:
            return ''

        lines = [
            f'### {role_icon} {role_name}',
            '',
            text,
            ''
        ]

        metadata = []
        if token_count > 0:
            metadata.append(f'Tokens: {token_count}')
        if finish_reason:
            metadata.append(f'结束原因: {finish_reason}')

        if metadata:
            lines.append(f'<details><summary>元数据</summary>')
            lines.append('')
            lines.append(' | '.join(metadata))
            lines.append('')
            lines.append('</details>')
            lines.append('')

        return '\n'.join(lines)

    def convert_to_markdown(self, data: dict, title: str = "聊天记录") -> str:
        """转换为 Markdown 格式"""
        chunks = self.extract_chunks(data)
        if not chunks:
            return "# 聊天记录\n\n> 无对话内容"

        lines = [
            f'# {title}',
            '',
            f'> 导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            '---',
            ''
        ]

        model_thought_buffer = []

        for chunk in chunks:
            is_thought = chunk.get('isThought', False)
            role = chunk.get('role', '')

            if is_thought and role == 'model':
                thought_text = self.clean_text(chunk.get('text', ''))
                if thought_text:
                    model_thought_buffer.append(thought_text)
                continue

            if model_thought_buffer and not is_thought:
                lines.append('> **🤔 AI 思考过程：**')
                lines.append('>')
                for thought in model_thought_buffer:
                    thought_lines = thought.split('\n')
                    for tline in thought_lines:
                        lines.append(f'> {tline}')
                    lines.append('>')
                lines.append('')
                model_thought_buffer = []

            message = self.format_message(chunk)
            if message:
                lines.append(message)
                lines.append('---')
                lines.append('')

        return '\n'.join(lines)

    def process_file(self, input_path: str) -> tuple:
        """处理单个文件，返回 (成功, 输出路径, 错误信息)"""
        input_file = Path(input_path)
        if not input_file.exists():
            return False, None, f"文件不存在: {input_path}"

        try:
            data = self.load_chat_file(input_path)
            title = input_file.stem
            markdown_content = self.convert_to_markdown(data, title)

            output_path = input_file.parent / f"{input_file.stem}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return True, str(output_path), None
        except json.JSONDecodeError as e:
            return False, None, f"JSON解析错误: {str(e)}"
        except Exception as e:
            return False, None, f"处理错误: {str(e)}"


class AistudioToMD_GUI:
    """GUI 主窗口"""

    def __init__(self, root):
        self.root = root
        self.parser = AistudioChatParser()
        self.file_list = []
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        self.root.title("Aistudio聊天记录转Markdown - 工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        style = ttk.Style()
        style.configure('TButton', font=('微软雅黑', 10))
        style.configure('TLabel', font=('微软雅黑', 10))
        style.configure('Header.TLabel', font=('微软雅黑', 12, 'bold'))

        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        title_label = Label(
            main_frame, 
            text="📝 Aistudio 聊天记录转 Markdown 工具",
            font=('微软雅黑', 16, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))

        file_frame = Frame(main_frame)
        file_frame.pack(fill='both', expand=True, pady=10)

        file_label = Label(
            file_frame, 
            text="📂 选择要转换的文件 (支持多选):",
            style='Header.TLabel'
        )
        file_label.pack(anchor='w')

        listbox_frame = Frame(file_frame)
        listbox_frame.pack(fill='both', expand=True, pady=10)

        scrollbar_y = Scrollbar(listbox_frame, orient=VERTICAL)
        scrollbar_y.pack(side='right', fill='y')

        scrollbar_x = Scrollbar(listbox_frame, orient=HORIZONTAL)
        scrollbar_x.pack(side='bottom', fill='x')

        self.file_listbox = Listbox(
            listbox_frame,
            selectmode='extended',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=('Consolas', 10),
            height=10,
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        self.file_listbox.pack(side='left', fill='both', expand=True)

        scrollbar_y.config(command=self.file_listbox.yview)
        scrollbar_x.config(command=self.file_listbox.xview)

        if HAS_DRAG_DROP:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.handle_drop)

        btn_frame = Frame(main_frame)
        btn_frame.pack(fill='x', pady=15)

        add_files_btn = Button(
            btn_frame,
            text="➕ 添加文件",
            command=self.add_files,
            width=15,
            height=2,
            bg='#3498db',
            fg='white',
            font=('微软雅黑', 10)
        )
        add_files_btn.pack(side='left', padx=(0, 10))

        add_dir_btn = Button(
            btn_frame,
            text="📁 从目录添加",
            command=self.add_directory,
            width=15,
            height=2,
            bg='#2ecc71',
            fg='white',
            font=('微软雅黑', 10)
        )
        add_dir_btn.pack(side='left', padx=(0, 10))

        clear_btn = Button(
            btn_frame,
            text="🗑️ 清空列表",
            command=self.clear_list,
            width=15,
            height=2,
            bg='#e74c3c',
            fg='white',
            font=('微软雅黑', 10)
        )
        clear_btn.pack(side='left', padx=(0, 10))

        remove_btn = Button(
            btn_frame,
            text="❌ 移除选中",
            command=self.remove_selected,
            width=15,
            height=2,
            bg='#f39c12',
            fg='white',
            font=('微软雅黑', 10)
        )
        remove_btn.pack(side='left', padx=(0, 10))

        convert_btn = Button(
            btn_frame,
            text="🚀 开始转换",
            command=self.start_convert,
            width=20,
            height=2,
            bg='#9b59b6',
            fg='white',
            font=('微软雅黑', 11, 'bold')
        )
        convert_btn.pack(side='right')

        progress_frame = Frame(main_frame)
        progress_frame.pack(fill='x', pady=10)

        self.progress_label = Label(
            progress_frame,
            text="就绪 - 请添加要转换的文件",
            font=('微软雅黑', 10),
            fg='#7f8c8d'
        )
        self.progress_label.pack(anchor='w')

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=100
        )
        self.progress_bar.pack(fill='x', pady=(5, 0))

        status_frame = Frame(main_frame)
        status_frame.pack(fill='x', pady=(10, 0))

        self.status_text = Text(
            status_frame,
            height=8,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            state='disabled'
        )
        self.status_text.pack(fill='both', expand=True)

        self.log_message("欢迎使用 Aistudio 聊天记录转换工具！")
        self.log_message("支持添加多个文件或整个目录")
        if HAS_DRAG_DROP:
            self.log_message("支持拖放文件到列表中")
        self.log_message("-" * 50)

    def log_message(self, message: str):
        """添加日志消息"""
        self.status_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(END, f"[{timestamp}] {message}\n")
        self.status_text.see(END)
        self.status_text.config(state='disabled')

    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择Aistudio聊天记录文件",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        for file in files:
            if file not in self.file_list:
                self.file_list.append(file)
                self.file_listbox.insert(END, file)
        self.update_progress_label()

    def add_directory(self):
        """从目录添加"""
        dir_path = filedialog.askdirectory(
            title="选择包含聊天记录的目录"
        )
        if dir_path:
            dir_path = Path(dir_path)
            json_files = list(dir_path.glob('*.json'))
            added_count = 0
            for json_file in json_files:
                file_str = str(json_file)
                if file_str not in self.file_list:
                    self.file_list.append(file_str)
                    self.file_listbox.insert(END, file_str)
                    added_count += 1
            if added_count > 0:
                self.log_message(f"从目录添加了 {added_count} 个文件")
            else:
                self.log_message("目录中没有新的JSON文件")
        self.update_progress_label()

    def handle_drop(self, event):
        """处理拖放事件"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.endswith('.json') and file not in self.file_list:
                self.file_list.append(file)
                self.file_listbox.insert(END, file)
        self.update_progress_label()
        self.log_message(f"拖放了 {len(files)} 个文件")

    def clear_list(self):
        """清空列表"""
        self.file_list.clear()
        self.file_listbox.delete(0, END)
        self.update_progress_label()
        self.log_message("列表已清空")

    def remove_selected(self):
        """移除选中的项目"""
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            self.file_listbox.delete(index)
            del self.file_list[index]
        self.update_progress_label()

    def update_progress_label(self):
        """更新进度标签"""
        count = len(self.file_list)
        self.progress_label.config(
            text=f"已选择 {count} 个文件 - 输出将保存在源文件所在目录"
        )

    def start_convert(self):
        """开始转换"""
        if not self.file_list:
            messagebox.showwarning("警告", "请先添加要转换的文件！")
            return

        self.log_message("=" * 50)
        self.log_message("开始转换...")

        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()

    def convert_files(self):
        """在后台线程中转换文件"""
        total = len(self.file_list)
        success_count = 0
        fail_count = 0

        for i, file_path in enumerate(self.file_list, 1):
            self.progress_bar['value'] = (i / total) * 100
            self.progress_label.config(text=f"正在处理 ({i}/{total}): {Path(file_path).name}")

            self.log_message(f"处理: {Path(file_path).name}")

            success, output_path, error = self.parser.process_file(file_path)

            if success:
                self.log_message(f"✅ 成功 -> {Path(output_path).name}")
                success_count += 1
            else:
                self.log_message(f"❌ 失败 -> {error}")
                fail_count += 1

        self.progress_bar['value'] = 100
        self.progress_label.config(text=f"转换完成！成功: {success_count}, 失败: {fail_count}")

        self.log_message("=" * 50)
        self.log_message(f"转换完成！成功: {success_count}, 失败: {fail_count}")

        self.root.after(0, lambda: messagebox.showinfo(
            "完成",
            f"转换完成！\n成功: {success_count} 个\n失败: {fail_count} 个"
        ))


def main():
    """主函数"""
    if HAS_DRAG_DROP:
        root = TkinterDnD.Tk()
    else:
        root = Tk()

    app = AistudioToMD_GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
