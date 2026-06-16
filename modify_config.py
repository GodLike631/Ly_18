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
# 5. 🌟 智能字数判定引流模块：剥离老杨字眼 + 5字以内精准挂载 🌟
# ====================================================================

def clean_and_append_tg(match):
    full_line = match.group(0)
    original_name = match.group(1)
    
    # 1. 拔除全部海豚相关词汇和特殊符号
    clean = original_name.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
    clean = clean.replace('｜', '').replace('丨', '').replace('|', '').strip()
    
    # 2. 如果被剥离后成了空名字或默认APP，给个通用干净名字兜底
    if not clean or clean == "APP":
        clean = "全能影视"
        
    # 3. 🎯 核心逻辑：判断清洗后的原名长度是否不超过 5 个字
    if len(clean) <= 5:
        new_name = f"{clean} [Tg频道：@huliys9]"
    else:
        new_name = clean  # 超过 5 个字就老老实实保留原有个性名，不加后缀
        
    return full_line.replace(f'"name": "{original_name}"', f'"name": "{new_name}"')

# 精准拦截带有海豚标志的数据行
final_json_text = re.sub(r'.*"name": "([^"]*(?:🐬|海豚)[^"]*)".*', clean_and_append_tg, final_json_text)

# 全局基础广告和群组链接强洗
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

print("🎉 【5字内精准引流版】已经无缝生成，未包含任何老杨字眼！")
