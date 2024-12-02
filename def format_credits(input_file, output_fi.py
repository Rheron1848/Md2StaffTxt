import os
import unicodedata

def format_credits(input_file, output_file, max_width, align_mode, justify_mode=False, flexible_width=False):
    # 检查文件路径是否合法
    if not os.path.isfile(input_file):
        raise ValueError(f"输入文件路径无效: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    formatted_lines = []
    paragraph = []
    
    # 如果启用弹性宽度,先计算最佳宽度
    actual_width = max_width
    if flexible_width:
        # 收集所有段落和标题的宽度
        widths = []
        temp_para = []
        current_section = None
        section_widths = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if temp_para:
                    # 计算段落可能的宽度
                    total_length = sum(get_string_width(name) for name in temp_para)
                    avg_length = total_length / len(temp_para)
                    names_per_line = max(1, int(max_width / (avg_length + 1)))
                    para_width = total_length // names_per_line + (len(temp_para) - 1)
                    if current_section:
                        if current_section not in section_widths:
                            section_widths[current_section] = []
                        section_widths[current_section].append(para_width)
                    widths.append(para_width)
                    temp_para = []
                continue
            if line.startswith('#'):
                if temp_para:
                    total_length = sum(get_string_width(name) for name in temp_para)
                    avg_length = total_length / len(temp_para)
                    names_per_line = max(1, int(max_width / (avg_length + 1)))
                    para_width = total_length // names_per_line + (len(temp_para) - 1)
                    if current_section:
                        if current_section not in section_widths:
                            section_widths[current_section] = []
                        section_widths[current_section].append(para_width)
                    widths.append(para_width)
                    temp_para = []
                line = line.lstrip('#').strip()
                current_section = line
                widths.append(get_string_width(line.upper()))
            else:
                temp_para.append(line.strip())
        
        # 找到最接近max_width的宽度,同时确保每个段落的宽度都合适
        if widths:
            min_width = min(widths)
            max_needed = max(widths)
            
            # 确保每个段落的宽度都适当
            section_max_widths = {}
            for section, section_width_list in section_widths.items():
                section_max_widths[section] = max(section_width_list)
            
            # 调整宽度以确保段落间的宽度关系合适
            if len(section_max_widths) > 1:
                for section1, width1 in section_max_widths.items():
                    for section2, width2 in section_max_widths.items():
                        if section1 != section2:
                            max_needed = max(max_needed, max(width1, width2))
            
            if min_width <= max_width <= max_needed:
                actual_width = max_width
            elif max_width > max_needed:
                actual_width = max_needed
            else:
                actual_width = min_width
            print(f"\n使用弹性宽度: {actual_width} (原始宽度: {max_width})")

    for line in lines:
        line = line.strip()
        if not line:
            # 处理段落结束
            if paragraph:
                format_paragraph(paragraph, formatted_lines, actual_width, align_mode, justify_mode)
                paragraph = []
            formatted_lines.append('')  # 保持空行
            continue

        # 处理Markdown标题
        if line.startswith('#'):
            # 处理未完成的段落
            if paragraph:
                format_paragraph(paragraph, formatted_lines, actual_width, align_mode, justify_mode)
                paragraph = []
            
            level = line.count('#')
            line = line.lstrip('#').strip()
            # 根据对齐模式处理标题
            title = line.upper()
            title_width = get_string_width(title)
            if align_mode == 1:  # 左对齐
                formatted_lines.append('\n' if level == 2 else '\n\n' if level == 1 else '')
                formatted_lines.append(title)
            elif align_mode == 2:  # 居中对齐
                formatted_lines.append('\n' if level == 2 else '\n\n' if level == 1 else '')
                padding = (actual_width - title_width) // 2
                formatted_lines.append(' ' * padding + title)
            else:  # 右对齐
                formatted_lines.append('\n' if level == 2 else '\n\n' if level == 1 else '')
                padding = actual_width - title_width
                formatted_lines.append(' ' * padding + title)
            formatted_lines.append('')  # 标题后添加一个空行
        else:
            # 收集段落中的名字
            paragraph.append(line.strip())

    # 处理最后一个段落
    if paragraph:
        format_paragraph(paragraph, formatted_lines, actual_width, align_mode, justify_mode)

    # 检查输出路径是否合法
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w', encoding='utf-8') as file:
        for formatted_line in formatted_lines:
            file.write(formatted_line + '\n')
            
    print(f"\n格式化完成!")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"实际宽度: {actual_width}")
    print(f"对齐方式: {'左对齐' if align_mode == 1 else '居中对齐' if align_mode == 2 else '右对齐'}")
    print(f"左右拉齐: {'是' if justify_mode else '否'}")
    print(f"弹性宽度: {'是' if flexible_width else '否'}")

def get_string_width(text):
    """计算字符串的实际显示宽度,汉字算2个宽度,其他字符算1个宽度"""
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
            width += 2
        else:
            width += 1
    return width

def format_paragraph(names, formatted_lines, max_width, align_mode, justify_mode):
    """格式化一个段落的名字列表"""
    if not names:
        return
        
    # 计算所有名字的总长度和平均长度
    total_length = sum(get_string_width(name) for name in names)
    avg_length = total_length / len(names)
    
    # 估算每行可以放置的名字数量
    names_per_line = max(1, int(max_width / (avg_length + 1)))
    
    # 将名字分组
    lines = []
    for i in range(0, len(names), names_per_line):
        line_names = names[i:i + names_per_line]
        
        # 计算名字之间的间距
        if len(line_names) > 1:
            total_name_width = sum(get_string_width(name) for name in line_names)
            available_space = max_width - total_name_width
            
            if justify_mode:  # 左右拉齐模式
                # 计算不均匀的空格分配
                spaces = available_space
                gaps = len(line_names) - 1
                space_counts = []
                
                # 确保每个间隔至少有一个空格
                min_spaces = gaps
                remaining_spaces = spaces - min_spaces
                
                if remaining_spaces > 0:
                    for j in range(gaps):
                        if remaining_spaces > 0:
                            space = remaining_spaces // (gaps - j)
                            space_counts.append(space + 1)  # 加1是因为要保证最小间隔
                            remaining_spaces -= space
                        else:
                            space_counts.append(1)  # 至少保留一个空格
                else:
                    space_counts = [1] * gaps  # 每个间隔都使用一个空格
                
                # 使用计算好的空格数连接名字
                line_text = ''
                for j, name in enumerate(line_names[:-1]):
                    line_text += name + ' ' * space_counts[j]
                line_text += line_names[-1]
                
                # 确保每行都达到最大宽度
                current_width = get_string_width(line_text)
                if current_width < max_width:
                    padding = max_width - current_width
                    line_text += ' ' * padding
            else:  # 等间距模式
                space_between = max(1, available_space // (len(line_names) - 1))
                line_text = (' ' * space_between).join(line_names)
        else:
            line_text = line_names[0]
            if justify_mode:  # 单个名字时也需要填充到最大宽度
                current_width = get_string_width(line_text)
                padding = max_width - current_width
                line_text += ' ' * padding
            
        # 根据对齐模式添加缩进
        if not justify_mode:  # 只在非左右拉齐模式下应用对齐
            line_width = get_string_width(line_text)
            if align_mode == 2:  # 居中对齐
                padding = (max_width - line_width) // 2
                line_text = ' ' * padding + line_text
            elif align_mode == 3:  # 右对齐
                padding = max_width - line_width
                line_text = ' ' * padding + line_text
            
        lines.append(line_text)
    
    formatted_lines.extend(lines)

try:
    print("\n=== 文本格式化工具 ===\n")
    # 使用示例
    input_file = input("请输入要格式化的文件路径: ").strip().strip('"').strip("'")
    if not os.path.isfile(input_file):
        raise ValueError("请输入有效的文件路径")
    output_file = input_file.rsplit('.', 1)[0] + '_formatted.' + input_file.rsplit('.', 1)[1]
    max_width = int(input("请输入每行的最大字符宽度(汉字算2个宽度): "))
    align_mode = int(input("请选择对齐方式(1:左对齐, 2:居中对齐, 3:右对齐): "))
    if align_mode not in [1, 2, 3]:
        raise ValueError("对齐方式必须是1、2或3")
    justify_mode = input("是否启用左右拉齐模式? (y/n): ").lower() == 'y'
    flexible_width = input("是否启用弹性宽度? (y/n): ").lower() == 'y'
    format_credits(input_file, output_file, max_width, align_mode, justify_mode, flexible_width)
except Exception as e:
    print(f"\n发生错误: {str(e)}")
    print("程序已终止")