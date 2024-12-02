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
    
    # 计算实际宽度
    actual_width = calculate_width(lines, max_width) if flexible_width else max_width

    for line in lines:
        line = line.strip()
        if not line:
            process_paragraph(paragraph, formatted_lines, actual_width, align_mode, justify_mode)
            formatted_lines.append('')  # 保持空行
            continue

        if line.startswith('#'):
            process_paragraph(paragraph, formatted_lines, actual_width, align_mode, justify_mode)
            process_title(line, formatted_lines, actual_width, align_mode)
        else:
            paragraph.append(line.strip())

    # 处理最后一个段落
    process_paragraph(paragraph, formatted_lines, actual_width, align_mode, justify_mode)

    # 写入文件
    write_output(output_file, formatted_lines)
            
    # 打印结果信息
    print_results(input_file, output_file, actual_width, align_mode, justify_mode, flexible_width)

def calculate_width(lines, max_width):
    """计算弹性宽度"""
    widths = []
    temp_para = []
    current_section = None
    section_widths = {}
    
    for line in lines:
        line = line.strip()
        if not line and temp_para:
            widths.append(calculate_paragraph_width(temp_para, max_width, current_section, section_widths))
            temp_para = []
            continue
            
        if line.startswith('#'):
            if temp_para:
                widths.append(calculate_paragraph_width(temp_para, max_width, current_section, section_widths))
                temp_para = []
            current_section = line.lstrip('#').strip()
            widths.append(get_string_width(current_section.upper()))
        else:
            temp_para.append(line.strip())
    
    if not widths:
        return max_width
        
    min_width = min(widths)
    max_needed = max(widths)
    
    if min_width <= max_width <= max_needed:
        return max_width
    elif max_width > max_needed:
        return max_needed
    else:
        return min_width

def calculate_paragraph_width(para, max_width, section, section_widths):
    """计算段落宽度"""
    total_length = sum(get_string_width(name) for name in para)
    avg_length = total_length / len(para)
    names_per_line = max(1, int(max_width / (avg_length + 1)))
    width = total_length // names_per_line + (len(para) - 1)
    
    if section:
        if section not in section_widths:
            section_widths[section] = []
        section_widths[section].append(width)
    return width

def process_paragraph(paragraph, formatted_lines, max_width, align_mode, justify_mode):
    """处理段落"""
    if not paragraph:
        return
        
    format_paragraph(paragraph, formatted_lines, max_width, align_mode, justify_mode)
    paragraph.clear()

def process_title(line, formatted_lines, max_width, align_mode):
    """处理标题"""
    level = line.count('#')
    title = line.lstrip('#').strip().upper()
    title_width = get_string_width(title)
    
    formatted_lines.append('\n' if level == 2 else '\n\n' if level == 1 else '')
    
    if align_mode == 2:  # 居中对齐
        padding = (max_width - title_width) // 2
        formatted_lines.append(' ' * padding + title)
    elif align_mode == 3:  # 右对齐
        padding = max_width - title_width
        formatted_lines.append(' ' * padding + title)
    else:  # 左对齐
        formatted_lines.append(title)
        
    formatted_lines.append('')

def write_output(output_file, formatted_lines):
    """写入输出文件"""
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w', encoding='utf-8') as file:
        for line in formatted_lines:
            file.write(line + '\n')

def print_results(input_file, output_file, actual_width, align_mode, justify_mode, flexible_width):
    """打印处理结果"""
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
    
    # 将名字分组并格式化每一行
    for i in range(0, len(names), names_per_line):
        line_names = names[i:i + names_per_line]
        line_text = format_line(line_names, max_width, align_mode, justify_mode)
        formatted_lines.append(line_text)

def format_line(line_names, max_width, align_mode, justify_mode):
    """格式化单行文本"""
    if len(line_names) == 1:
        line_text = format_single_name(line_names[0], max_width, align_mode, justify_mode)
    else:
        line_text = format_multiple_names(line_names, max_width, align_mode, justify_mode)
    return line_text

def format_single_name(name, max_width, align_mode, justify_mode):
    """格式化单个名字"""
    line_text = name
    current_width = get_string_width(line_text)
    
    if justify_mode:
        if align_mode == 2:  # 居中对齐
            padding = (max_width - current_width) // 2
            line_text = ' ' * padding + line_text
            # 补齐右侧空格以达到max_width
            right_padding = max_width - (padding + current_width)
            line_text += ' ' * right_padding
        elif align_mode == 3:  # 右对齐
            padding = max_width - current_width
            line_text = ' ' * padding + line_text
        else:  # 左对齐
            line_text += ' ' * (max_width - current_width)
    
    return line_text

def format_multiple_names(names, max_width, align_mode, justify_mode):
    """格式化多个名字"""
    total_name_width = sum(get_string_width(name) for name in names)
    available_space = max_width - total_name_width
    
    if justify_mode:
        line_text = format_justified(names, available_space, max_width)
    else:
        space_between = max(1, available_space // (len(names) - 1))
        line_text = (' ' * space_between).join(names)
        
        if not justify_mode:
            line_width = get_string_width(line_text)
            if align_mode == 2:
                padding = (max_width - line_width) // 2
                line_text = ' ' * padding + line_text
            elif align_mode == 3:
                padding = max_width - line_width
                line_text = ' ' * padding + line_text
                
    return line_text

def format_justified(names, available_space, max_width):
    """格式化左右对齐文本"""
    gaps = len(names) - 1
    min_spaces = gaps
    remaining_spaces = available_space - min_spaces
    
    space_counts = []
    if remaining_spaces > 0:
        for j in range(gaps):
            if remaining_spaces > 0:
                space = remaining_spaces // (gaps - j)
                space_counts.append(space + 1)
                remaining_spaces -= space
            else:
                space_counts.append(1)
    else:
        space_counts = [1] * gaps
    
    line_text = ''
    for j, name in enumerate(names[:-1]):
        line_text += name + ' ' * space_counts[j]
    line_text += names[-1]
    
    current_width = get_string_width(line_text)
    if current_width < max_width:
        padding = max_width - current_width
        line_text += ' ' * padding
        
    return line_text

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