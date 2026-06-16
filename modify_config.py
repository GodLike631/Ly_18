import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/老杨TV.json'  # 🌟 专属后缀文件名

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 物理提取海豚源里的 sites（视频站）和 lives（直播源）内部的纯文本
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    after_key = content.split(split_key, 1)[1]
    if '],' in after_key:
        inner_text = after_key.split('],', 1)[0]
    else:
        inner_text = after_key.split(']', 1)[0]
    return inner_text.strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# ====================================================================
# 2. 逆向注入：把海豚的内容，无缝贴进 CNB 对应的数组最前面
# ====================================================================
final_json_text = text_cnb

# 注入视频站点
if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

# 注入直播源
if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 靶向拦截手术：揪出这两个瘫痪的 4K 线路，强行切断 CNB 依赖，锁死海豚核心
# ====================================================================
final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"spider": "./tvbox.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"spider": "./tvbox.jar",\n        "key": "茫茫"'
)

# ====================================================================
# 【全方位无死角路径清洗】：让 CNB 的其余线路走官方绝对 network 链接
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 4. 定制老杨自用全量缝合专线 brand 头部
# ====================================================================
final_json_text = final_json_text.replace('"warningText": "欢迎使用鱼儿自用缝合专线，完全免费！"', '"warningText": "欢迎使用老杨自用全量缝合专线，本接口完全免费！"')

# ====================================================================
# 5. 🌟 智能语义洗牌：个性重组 + 老杨TV 适时注入 🌟
# ====================================================================

def smart_rename_personality(match):
    full_line = match.group(0)
    original_name = match.group(1)
    
    # 1. 彻底清除破坏美感的垃圾品牌词和符号
    clean = original_name.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
    clean = clean.replace('｜', '').replace('丨', '').replace('|', '').strip()
    
    # 2. 根据原名的含义与关键词，进行个性化定制重组
    if "综合" in clean or "全能" in clean:
        new_name = f"老杨TV专属｜{clean}"
    elif "4K" in clean or "特质" in clean or "高清" in clean or "蓝光" in clean:
        new_name = f"老杨TV·{clean}"
    elif "磁力" in clean or "网盘" in clean or "搜索" in clean:
        new_name = f"老杨影视·{clean}"
    elif "港台" in clean or "国际" in clean or "海外" in clean:
        new_name = f"境外特线｜{clean}专线"
    elif "体育" in clean or "直播" in clean or "看球" in clean:
        new_name = f"老杨体育｜{clean}"
    elif "合集" in clean or "免费" in clean:
        # 类似“各大源合集 永久免费如有收费的都是骗子”的处理
        new_name = f"老杨TV全网通知｜{clean}"
    elif not clean or clean == "APP":
        new_name = "老杨核心｜全能影视"
    else:
        # 其余小众个性名字（如某些特定的App接口名），保留原名并加专线后缀
        new_name = f"{clean}｜老杨专线"
        
    return full_line.replace(f'"name": "{original_name}"', f'"name": "{new_name}"')

# 靶向重命名带海豚标记的行
final_json_text = re.sub(r'.*"name": "([^"]*(?:🐬|海豚)[^"]*)".*', smart_rename_personality, final_json_text)

# 3. 靶向替换特定的广告词、联系方式以及你的新频道链接
final_json_text = final_json_text.replace('@hshsjk9', '@huliys9')
final_json_text = final_json_text.replace('交流群', 'Tg频道')

# ====================================================================
# 6. 安全、高效地消除尾部逗号瑕疵
# ====================================================================
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

# 写入本地文件存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 【老杨TV个性融合版】已闪电生成完毕！")
