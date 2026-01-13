#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Aistudio 聊天记录转 Markdown 文档工具
功能：解析 Aistudio 导出的 JSON 格式聊天记录，转换为可读的 Markdown 文档
"""

import json
import os
from pathlib import Path
from datetime import datetime


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
        """清理文本中的特殊字符和格式问题"""
        if not text:
            return ''
        text = text.strip()
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        return text

    def format_message(self, chunk: dict, index: int) -> str:
        """格式化单条消息为 Markdown 格式"""
        role = chunk.get('role', 'unknown')
        role_name, role_icon = self.role_map.get(role, ('未知', '❓'))

        text = self.clean_text(chunk.get('text', ''))
        token_count = chunk.get('tokenCount', 0)

        is_thought = chunk.get('isThought', False)
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
        """将解析后的数据转换为 Markdown 格式"""
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
        last_was_model_thought = False

        for i, chunk in enumerate(chunks):
            role = chunk.get('role', 'unknown')
            is_thought = chunk.get('isThought', False)

            if is_thought and role == 'model':
                thought_text = self.clean_text(chunk.get('text', ''))
                if thought_text:
                    model_thought_buffer.append(thought_text)
                last_was_model_thought = True
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
                last_was_model_thought = False

            message = self.format_message(chunk, i)
            if message:
                lines.append(message)
                lines.append('---')
                lines.append('')

        return '\n'.join(lines)

    def process_file(self, input_path: str, output_dir: str = None) -> str:
        """处理单个文件"""
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")

        if output_dir is None:
            output_dir = input_file.parent

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        data = self.load_chat_file(input_path)

        title = input_file.stem
        markdown_content = self.convert_to_markdown(data, title)

        output_path = output_dir / f"{input_file.stem}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(output_path)

    def process_multiple_files(self, file_paths: list, output_dir: str = None) -> list:
        """批量处理多个文件"""
        results = []
        for file_path in file_paths:
            try:
                output = self.process_file(file_path, output_dir)
                results.append((file_path, output, True, None))
                print(f"✅ 成功转换: {file_path} -> {output}")
            except Exception as e:
                results.append((file_path, None, False, str(e)))
                print(f"❌ 转换失败: {file_path} - {str(e)}")
        return results


def main():
    """主函数"""
    parser = AistudioChatParser()

    input_files = [
        r"d:\202508\开发\aisuidiochat2md\aisuidiochat2md\Husband's Wife's Emotional Distress",
        r"d:\202508\开发\aisuidiochat2md\aisuidiochat2md\Mind Quadrant_ Inner World Assessment"
    ]

    output_directory = r"d:\202508\开发\aisuidiochat2md\aisuidiochat2md\output"

    print("=" * 60)
    print("Google Aistudio 聊天记录转 Markdown 工具")
    print("=" * 60)
    print()

    results = parser.process_multiple_files(input_files, output_directory)

    print()
    print("=" * 60)
    print("处理结果汇总:")
    print("=" * 60)
    for input_path, output_path, success, error in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {input_path}")
        if output_path:
            print(f"   输出: {output_path}")
        if error:
            print(f"   错误: {error}")

    print()
    print("✨ 所有文件处理完成！")


if __name__ == "__main__":
    main()
