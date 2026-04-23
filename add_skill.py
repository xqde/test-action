import sys
import os
import logging

# =========================
# logging
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =========================
# 常量区（统一管理语义）
# =========================
START_LINE = 4
MD_FILE = "README.md"

NAV_TITLE = "## 导航"
NAV_NAME = "导航"   


# =========================
# IO
# =========================
def ensure_file():
    if not os.path.exists(MD_FILE):
        open(MD_FILE, "w", encoding="utf-8").close()
        logger.info("创建文件")


def read_lines():
    logger.info("读取文件")
    with open(MD_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


def write_lines(lines):
    logger.info("写入文件")
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def slugify(text):
    return text.strip().lower().replace(" ", "-")


# =========================
# 解析结构（忽略 NAV）
# =========================
def parse_structure(lines):
    logger.info("解析结构")

    structure = {}
    current = None

    for line in lines:
        # ===== 跳过导航块 =====
        if line.strip() == NAV_TITLE:
            current = None
            continue

        if line.startswith("## "):
            title = line.replace("## ", "").strip()

            # 防止误识别导航
            if title == NAV_NAME:
                current = None
                continue

            current = title
            structure.setdefault(current, [])

        elif current and line.strip().startswith("- ["):
            structure[current].append(line)

    logger.info(f"解析完成：{len(structure)} 个目录")
    return structure


# =========================
# 写入数据（去重）
# =========================
def add_entry(structure, directory, short_desc, url, desc):
    structure.setdefault(directory, [])

    new_item = f"- [{short_desc}]({url}) - {desc}\n"

    for x in structure[directory]:
        if f"]({url})" in x:
            logger.info("重复 URL，跳过")
            return

    structure[directory].append(new_item)
    logger.info(f"写入目录：{directory}")


# =========================
# 构建 Markdown
# =========================
def build_md(structure):
    logger.info("重建 Markdown")

    lines = []

    # ===== TOC =====
    lines.append(f"{NAV_TITLE}\n")

    for k in sorted(structure.keys()):
        lines.append(f"- [{k}](#{slugify(k)})\n")

    lines.append("\n")

    # ===== content =====
    for k in sorted(structure.keys()):
        lines.append(f"## {k}\n\n")
        lines.extend(structure[k])
        lines.append("\n")

    logger.info("构建完成")
    return lines


# =========================
# main
# =========================
def main():
    if len(sys.argv) != 5:
        logger.error("参数错误")
        print("用法: python add_skill.py <目录> <地址> <简短描述> <描述>")
        return

    directory = sys.argv[1]
    url = sys.argv[2]
    short_desc = sys.argv[3]
    desc = sys.argv[4]

    logger.info("===== START =====")
    logger.info(f"目录: {directory}")
    logger.info(f"地址: {url}")
    logger.info(f"简短描述: {short_desc}")
    logger.info(f"描述: {desc}")

    ensure_file()

    lines = read_lines()

    head = lines[:START_LINE]
    body = lines[START_LINE:]

    structure = parse_structure(body)

    add_entry(structure, directory, short_desc, url, desc)

    new_body = build_md(structure)

    write_lines(head + new_body)

    logger.info("===== DONE =====")


if __name__ == "__main__":
    main()
