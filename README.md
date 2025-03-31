 

如何使用:
安装 FFmpeg:
确保你的系统上安装了 FFmpeg，并且 ffmpeg 和 ffprobe 命令可以在你的终端（命令行）中直接运行。

• Windows: 从 FFmpeg官网 下载，解压并将 bin 目录添加到系统的 PATH 环境变量中。
• macOS: 使用 Homebrew: brew install ffmpeg
• Linux (Debian/Ubuntu): sudo apt update && sudo apt install ffmpeg
• Linux (Fedora): sudo dnf install ffmpeg
保存脚本: 将上面的 Python 代码保存为一个文件，例如 split_audiobook.py。

运行脚本:
打开你的终端或命令行。
使用 cd 命令切换到保存脚本的目录。
运行脚本，并将你的有声书文件路径作为参数传递给它：
Bash

python split_audiobook.py "你的有声书文件路径.m4b"
注意: 如果文件路径包含空格，请务必用引号将其括起来。

脚本说明:
sanitize_filename(filename): 这个辅助函数用于移除或替换章节标题中不适合用作文件名的字符（如 , /, :, *, ?, ", <, >, |），防止创建文件时出错。
get_chapters(filepath): 调用 ffprobe，请求 JSON 格式的章节信息。如果成功且包含章节，则返回章节列表，否则返回 None。它还包含了错误处理，例如 ffprobe 命令未找到或执行出错。
split_audio_by_chapters(filepath, chapters):
创建输出目录（例如，如果输入是 MyBook.m4b，输出目录将是 MyBook_章节）。
遍历 ffprobe 返回的每个章节字典。
提取 start_time、end_time 和 tags['title']。
清理章节标题以用作文件名，并在前面加上两位数的序号（如 01_, 02_）以保证文件按章节顺序排列。
构建 ffmpeg 命令：
-i filepath: 指定输入文件。
-ss start_time: 设置分割开始时间。
-to end_time: 设置分割结束时间点。
-c copy: 关键参数！ 这告诉 ffmpeg 直接复制音频流，不进行重新编码。这样处理速度非常快，并且能保持原始音质。
-map_metadata 0: 尝试从输入文件复制全局元数据到输出文件。
-metadata title="Chapter Title": 将当前章节的标题设置为输出文件的标题元数据。
-vn: 忽略任何视频流。
-y: 自动覆盖同名输出文件（如果存在）。
output_path: 指定输出文件的完整路径和名称。
使用 subprocess.run() 执行 ffmpeg 命令，并检查执行结果。
if name == "main": 这部分是脚本的入口点。它检查是否提供了命令行参数（音频文件路径），然后调用上述函数来完成工作。
shlex.quote: 用于安全地构建命令行字符串，特别是当路径或标题包含特殊字符或空格时。
  

如何使用:
安装 FFmpeg:
确保你的系统上安装了 FFmpeg，并且 ffmpeg 和 ffprobe 命令可以在你的终端（命令行）中直接运行。

• Windows: 从 FFmpeg官网 下载，解压并将 bin 目录添加到系统的 PATH 环境变量中。
• macOS: 使用 Homebrew: brew install ffmpeg
• Linux (Debian/Ubuntu): sudo apt update && sudo apt install ffmpeg
• Linux (Fedora): sudo dnf install ffmpeg
保存脚本: 将上面的 Python 代码保存为一个文件，例如 split_audiobook.py。

运行脚本:
打开你的终端或命令行。
使用 cd 命令切换到保存脚本的目录。
运行脚本，并将你的有声书文件路径作为参数传递给它：
Bash

python split_audiobook.py "你的有声书文件路径.m4b"
注意: 如果文件路径包含空格，请务必用引号将其括起来。

脚本说明:
sanitize_filename(filename): 这个辅助函数用于移除或替换章节标题中不适合用作文件名的字符（如 , /, :, *, ?, ", <, >, |），防止创建文件时出错。
get_chapters(filepath): 调用 ffprobe，请求 JSON 格式的章节信息。如果成功且包含章节，则返回章节列表，否则返回 None。它还包含了错误处理，例如 ffprobe 命令未找到或执行出错。
split_audio_by_chapters(filepath, chapters):
创建输出目录（例如，如果输入是 MyBook.m4b，输出目录将是 MyBook_章节）。
遍历 ffprobe 返回的每个章节字典。
提取 start_time、end_time 和 tags['title']。
清理章节标题以用作文件名，并在前面加上两位数的序号（如 01_, 02_）以保证文件按章节顺序排列。
构建 ffmpeg 命令：
-i filepath: 指定输入文件。
-ss start_time: 设置分割开始时间。
-to end_time: 设置分割结束时间点。
-c copy: 关键参数！ 这告诉 ffmpeg 直接复制音频流，不进行重新编码。这样处理速度非常快，并且能保持原始音质。
-map_metadata 0: 尝试从输入文件复制全局元数据到输出文件。
-metadata title="Chapter Title": 将当前章节的标题设置为输出文件的标题元数据。
-vn: 忽略任何视频流。
-y: 自动覆盖同名输出文件（如果存在）。
output_path: 指定输出文件的完整路径和名称。
使用 subprocess.run() 执行 ffmpeg 命令，并检查执行结果。
if name == "main": 这部分是脚本的入口点。它检查是否提供了命令行参数（音频文件路径），然后调用上述函数来完成工作。
shlex.quote: 用于安全地构建命令行字符串，特别是当路径或标题包含特殊字符或空格时。
 