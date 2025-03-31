import subprocess
import json
import os
import sys
import re
import shlex

def sanitize_filename(filename):
    """清理字符串，使其成为有效的文件名。"""
    # 移除或替换非法字符
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 替换空格（可选，有时用下划线更好）
    # sanitized = sanitized.replace(" ", "_")
    # 限制长度（可选）
    # max_len = 200
    # sanitized = sanitized[:max_len]
    # 移除开头或结尾的点或空格
    sanitized = sanitized.strip('. ')
    if not sanitized:
        sanitized = "untitled" # 如果清理后为空，则提供默认名称
    return sanitized

def get_chapters(filepath):
    """使用 ffprobe 获取音频文件的章节信息。"""
    command = [
        "ffprobe",
        "-v", "quiet",        # 只输出错误信息
        "-print_format", "json", # 输出格式为 JSON
        "-show_chapters",     # 显示章节信息
        "-i", filepath
    ]
    print(f"[*] 正在运行 ffprobe 获取章节信息: {' '.join(map(shlex.quote, command))}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        metadata = json.loads(result.stdout)
        if "chapters" in metadata and metadata["chapters"]:
            print(f"[+] 成功找到 {len(metadata['chapters'])} 个章节。")
            return metadata["chapters"]
        else:
            print("[-] 未在该文件中找到章节信息。")
            return None
    except FileNotFoundError:
        print("[!] 错误：找不到 'ffprobe' 命令。请确保 FFmpeg 已正确安装并在系统 PATH 中。")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[!] ffprobe 执行出错:")
        print(f"    命令: {' '.join(map(shlex.quote, e.cmd))}")
        print(f"    返回码: {e.returncode}")
        print(f"    标准输出: {e.stdout}")
        print(f"    标准错误: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print("[!] 错误：解析 ffprobe 输出的 JSON 时出错。")
        return None
    except Exception as e:
        print(f"[!] 获取章节信息时发生未知错误: {e}")
        return None


def split_audio_by_chapters(filepath, chapters):
    """使用 ffmpeg 按章节分割音频。"""
    if not chapters:
        print("[-] 没有章节信息，无法进行分割。")
        return

    base_name = os.path.splitext(os.path.basename(filepath))[0]
    input_dir = os.path.dirname(os.path.abspath(filepath))
    output_dir = os.path.join(input_dir, base_name + "_章节")

    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"[*] 输出目录: {output_dir}")
    except OSError as e:
        print(f"[!] 创建输出目录 '{output_dir}' 时出错: {e}")
        return

    file_extension = os.path.splitext(filepath)[1]
    if not file_extension:
        print("[!] 警告：无法确定原始文件扩展名，将使用 '.mp3' 作为默认扩展名。")
        file_extension = ".mp3" # 或其他合适的默认值

    total_chapters = len(chapters)
    for i, chapter in enumerate(chapters):
        try:
            start_time = float(chapter.get('start_time', 0))
            end_time = float(chapter.get('end_time', 0))
            title = chapter.get('tags', {}).get('title', f'Chapter_{i+1:02d}')

            # 清理标题作为文件名
            sanitized_title = sanitize_filename(title)
            # 添加序号前缀以保证顺序
            output_filename = f"{i+1:02d}_{sanitized_title}{file_extension}"
            output_path = os.path.join(output_dir, output_filename)

            print(f"\n[*] 正在处理章节 {i+1}/{total_chapters}: {title}")
            print(f"    开始时间: {start_time}, 结束时间: {end_time}")
            print(f"    输出文件: {output_path}")

            # 构建 ffmpeg 命令
            command = [
                "ffmpeg",
                "-i", filepath,      # 输入文件
                "-ss", str(start_time), # 起始时间
                "-to", str(end_time),   # 结束时间 (注意: ffmpeg 的 -to 是绝对时间点)
                "-c", "copy",         # 直接复制流，不重新编码，速度快且无损
                "-map_metadata", "0", # 复制全局元数据
                "-metadata", f"title={title}", # 设置分割后文件的标题元数据
                "-vn",                # 忽略视频流（如果源文件包含视频）
                "-y",                 # 如果文件已存在，则覆盖
                output_path
            ]

            print(f"[*] 正在运行 ffmpeg 命令: {' '.join(map(shlex.quote, command))}")

            result = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8') # check=False 以便检查 stderr

            if result.returncode != 0:
                print(f"[!] ffmpeg 执行出错 (章节: {title}):")
                print(f"    返回码: {result.returncode}")
                # ffmpeg 通常将进度信息输出到 stderr
                print(f"    标准错误/输出: \n{result.stderr or result.stdout}")
            else:
                print(f"[+] 成功创建文件: {output_filename}")

        except KeyError as e:
            print(f"[!] 错误：章节 {i+1} 缺少必要的键: {e}")
            continue # 跳过这个章节，继续处理下一个
        except ValueError as e:
            print(f"[!] 错误：转换章节 {i+1} 的时间戳时出错: {e}")
            continue
        except FileNotFoundError:
            print("[!] 错误：找不到 'ffmpeg' 命令。请确保 FFmpeg 已正确安装并在系统 PATH 中。")
            sys.exit(1)
        except Exception as e:
             print(f"[!] 处理章节 {i+1} ('{title}') 时发生未知错误: {e}")
             continue

    print("\n[*] 所有章节处理完毕。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python split_audiobook.py <audiobook_filepath>")
        sys.exit(1)

    input_filepath = sys.argv[1]

    if not os.path.isfile(input_filepath):
        print(f"[!] 错误：文件 '{input_filepath}' 不存在或不是一个文件。")
        sys.exit(1)

    print(f"[*] 开始处理文件: {input_filepath}")
    chapters_data = get_chapters(input_filepath)

    if chapters_data:
        split_audio_by_chapters(input_filepath, chapters_data)
    else:
        print("[*] 文件不包含章节信息或获取失败，脚本结束。")