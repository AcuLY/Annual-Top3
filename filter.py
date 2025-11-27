import json
import re
from datetime import datetime

INPUT_FILE = "subject.jsonlines"
OUTPUT_FILE = "./src/constant/2025.json"

def extract_infobox_names(infobox: str) -> list:
    """从 Infobox 字符串中提取 中文名 与 别名 列表"""
    names = []

    if not isinstance(infobox, str):
        return names

    # 提取 |中文名= xxx
    m = re.search(r"\|中文名\s*=\s*([^\r\n]+)", infobox)
    if m:
        names.append(m.group(1).strip())

    # 提取别名={ ... } 中的 [xxx]
    alias_block = re.search(r"\|别名\s*=\s*\{([\s\S]*?)\}", infobox)
    if alias_block:
        alias_text = alias_block.group(1)
        alias_list = re.findall(r"\[([^\]]+)\]", alias_text)
        names.extend([a.strip() for a in alias_list])
    
    names = [n for n in names if n and not n.startswith("|别名")]

    return names


def date_is_2025(date_str: str) -> bool:
    """判断 date 是否在 2025 年"""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.year == 2025
    except:
        return False


def main():
    results = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            item = json.loads(line)

            # 过滤条件
            if item.get("type") != 2:
                continue
            if not date_is_2025(item.get("date", "")):
                continue
            if item.get("nsfw"):
                continue
            if sum([num for num in item.get("score_details").values()]) < 100:
                continue

            names = []

            # name / name_cn
            if "name_cn" in item and item["name_cn"]:
                names.append(item["name_cn"])
            if "name" in item and item["name"]:
                names.append(item["name"])

            # infobox
            if "infobox" in item and item["infobox"]:
                names.extend(extract_infobox_names(item["infobox"]))

            # 去重
            cleaned = []
            for n in names:
                if not n:
                    continue

                # 去掉 “xx版权译|xxx” 前缀，只保留 | 后面的部分
                if "版权译|" in n:
                    parts = n.split("版权译|", 1)
                    if len(parts) == 2 and parts[1].strip():
                        n = parts[1].strip()
                    else:
                        continue  # 如果右边为空直接丢弃

                cleaned.append(n)

            # 去重
            names = list(dict.fromkeys(cleaned))

            results.append({
                "id": item["id"],
                "names": names,
                "date": item["date"]
            })
    
    results.sort(key=lambda x: x["date"])
    for r in results:
        r.pop("date", None)


    # 输出为 JSON Lines
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Done! {len(results)} records written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
