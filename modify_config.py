import os
import re
import random
import string
import glob
import datetime
import json
import urllib.request
import urllib.parse

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'

lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# 🌟 修复点：将历史备份变量直接初始化到最顶层全局域，彻底解决 NameError 报错
old_valid_json_data = {}

# ====================================================================
# 🚫 【新增：自定义黑名单关键词过滤区】
# 在下方列表中填入指定关键词（支持多个），脚本合并时会自动删除包含这些关键词的
# 点播线路与直播源。如果不需要过滤，保持列表为空即可。
# ====================================================================
BLOCK_KEYWORDS = ["羊壳", "弹幕", "不可用"]

# ====================================================================
# ✍️ 【通道一：老杨专属点播手工加线区】
# ====================================================================
MY_CUSTOM_SITES = [
    {
        "key": "山楂影视",
        "name": "山楂影视.py",
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E5%B1%B1%E6%A5%82%E5%BD%B1%E8%A7%86.py",
        "searchable": 1,
        "quickSearch": 1
    },
    {
        "key": "红果短剧",
        "name": "红果短剧.py",
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E7%BA%A2%E6%9E%9C%E7%9F%AD%E5%89%A7.py",
        "searchable": 1,
        "quickSearch": 1
    }
]

# ====================================================================
# 📺 【通道二：老杨专属直播手工加线区】
# ====================================================================
MY_CUSTOM_LIVES = [
    {
        "name": "乡村电视 ｜Tg：@huliys9",
        "type": 0,
        "playerType": 2,
        "ua": "okhttp/5.3.2",
        "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
    },
    {
      "name": "锋云直播｜Tg：@huliys9",
      "type": 3,
      "url": "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/suale.txt",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
        "name": "最新电影｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u"
    },
    {
        "name": "Kimentanm",
        "type": 0,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
        "playerType": 2
    },
    {
      "name": "综合直播",
      "type": 0,
      "playerType": 2,
      "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt",
      "ua": "bingcha/1.1 (mianfeifenxiang) "
    },
    {
        "name": "央卫TV｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "http://47.120.41.246:8025/vip/jar/zb.php"
    },
    {
        "name": "超稳定流畅｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt"
    },
    {
        "name": "咪咕｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://develop202.github.io/migu_video/interface.txt"
    },
    {
      "name": "Gather「IPTV」｜Tg：@huliys9",
      "type": 3,
      "url": "https://iptv.yang-1989.xyz/playlist.m3u",
      "epg":"https://material.yang-1989.xyz/epg.xml.gz",
      "ua": "okhttp/3.8.1",
      "timeout": 10,
      "playerType": 2
    },
    {
      "name": "Live「直播」｜Tg：@huliys9",
      "type": 3,
      "url": "https://live.yang-1989.eu.org/Live.m3u",
      "ua": "okhttp/3.8.1",
      "timeout": 10,
      "playerType": 2
    },
    {
      "name": "myTV「香港」｜Tg：@huliys9",
      "type": 3,
      "url": "https://iptv.yang-1989.xyz/myTV/playlist.m3u",
      "epg":"https://material.yang-1989.xyz/epg.xml.gz",
      "ua": "okhttp/3.8.1",
      "timeout": 10,
      "playerType": 2
    }
]

today = datetime.datetime.now()
current_month = str(today.month)
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

# 新增：新密码锁生成触发标记，默认关闭
is_new_token_generated = False

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

if is_reset_day and saved_month != current_month:
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1号洗牌】生成本月新密锁: {current_token}")
    # 🎯 触发核心改动点：满足1号且月份不一致，证明重新生成了新密码
    is_new_token_generated = True
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 保持原暗号: {current_token}")
else:
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密锁: {current_token}")

if current_token in ["全量版", "纯净版"]:
    output_filename = "蝴蝶影视纯净版.json"
else:
    output_filename = f"蝴蝶影视纯净版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出：{output_filename}")

# ==================== [ 核心逻辑：在覆盖老配置前备份旧数据 ] ====================
try:
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r', encoding='utf-8') as f_track:
            last_active_filename = f_track.read().strip()
            last_active_filepath = f"datas/{last_active_filename}"
            if os.path.exists(last_active_filepath):
                with open(last_active_filepath, 'r', encoding='utf-8') as f_last_json:
                    temp_data = json.load(f_last_json)
                    if "sites" in temp_data and len(temp_data["sites"]) > 2:
                        old_valid_json_data = temp_data
                        print(f"📑 成功捕获上一次真实的历史接口: {last_active_filename}")
except Exception as backup_err:
    print(f"⚠️ 读取历史备份失败: {backup_err}")

# 往下执行金蝉脱壳
old_configs = glob.glob('datas/蝴蝶影视纯净版*.json') + glob.glob('datas/老杨TV纯净版*.json') + glob.glob('datas/老杨TV无18*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "",
                "notice": "⚠️ 警告：当前“蝴蝶影视”绿色专线密码已过期断流！老链接已彻底作废！\n\n最新密码前往Tg频道（@huliys9）获取！",
                "sites": [
                    {"key": "蝴蝶影视绿色纯文字提示", "name": "➡️ 请前往Tg频道（@huliys9）获取最新密码🚨 ➡️ 请前往Tg频道（@huliys9）获取最新密码", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "蝴蝶影视绿色纯文字提示2", "name": "🚨 不要看这里了 ➡️ 请前往Tg频道（@huliys9）获取最新密码", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 当前线路已过期 ➡️  请前往Tg频道（@huliys9）获取最新密码", "urls": ["http://127.0.0.1"]}]}
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蝉脱壳】已将过期旧线调包为大轰炸: {old_file}")
        except:
            pass

for garbage in ['datas/local_config.json', *glob.glob('datas/config_*.json')]:
    try: os.remove(garbage)
    except: pass

def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"❌ 错误：{path} JSON 格式不正确。")
            return {}

json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)

haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])

for item in haitun_sites:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

combined_parses = json_haitun.get("parses", []) + json_cnb.get("parses", [])

custom_keys = {site.get("key") for site in MY_CUSTOM_SITES if site.get("key")}
upstream_sites = haitun_sites + cnb_sites
clean_upstream_sites = [site for site in upstream_sites if site.get("key") not in custom_keys]

# ------------------------------------------------------------------
# 🎯 【过滤点播区核心注入】：从源头过滤包含指定黑名单关键词的点播线路
# ------------------------------------------------------------------
if BLOCK_KEYWORDS:
    filtered_upstream_sites = []
    for site in clean_upstream_sites:
        s_name = site.get("name", "")
        if any(kw.lower() in s_name.lower() for kw in BLOCK_KEYWORDS if kw):
            continue
        filtered_upstream_sites.append(site)
    clean_upstream_sites = filtered_upstream_sites

json_cnb["sites"] = clean_upstream_sites + MY_CUSTOM_SITES

custom_live_names = {live.get("name") for live in MY_CUSTOM_LIVES if live.get("name")}
base_lives = haitun_lives + cnb_lives
clean_base_lives = [live for live in base_lives if live.get("name") not in custom_live_names]

# ------------------------------------------------------------------
# 🎯 【过滤直播区核心注入】：同步过滤包含指定黑名单关键词的直播源
# ------------------------------------------------------------------
if BLOCK_KEYWORDS:
    filtered_base_lives = []
    for live in clean_base_lives:
        l_name = live.get("name", "")
        if any(kw.lower() in l_name.lower() for kw in BLOCK_KEYWORDS if kw):
            continue
        filtered_base_lives.append(live)
    clean_base_lives = filtered_base_lives

for i, custom_live in enumerate(MY_CUSTOM_LIVES):
    live_name = custom_live.get("name", "")
    
    # 手工定制区同样执行黑名单拦截
    if BLOCK_KEYWORDS and any(kw.lower() in live_name.lower() for kw in BLOCK_KEYWORDS if kw):
        continue

    if len(clean_base_lives) >= (5 + i):
        clean_base_lives.insert(5 + i, custom_live)
    else:
        clean_base_lives.append(custom_live)
json_cnb["lives"] = clean_base_lives

final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)

final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')

final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

path_replacements = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': 'https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg'
}
for src, dst in path_replacements.items():
    final_json_text = final_json_text.replace(src, dst)

thanks_warning = "\n\n👑 【特别致谢与版权声明】\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出 (源码基础: fish2018/webhtv，TG群: https://t.me/webhtv)\n🐬 感谢海豚佬的付出 (核心仓库: FGBLH/GHK，TG群: https://t.me/hshsjk9)"
welcome_notice = "👑 欢迎使用【蝴蝶影视粉丝专属绿色纯净线】！本接口由蝴蝶影视结合海豚佬＆鱼佬的优质绿色资源无损缝合而成，纯净绿色无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）获取当前最新密码锁！"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice + thanks_warning
    if "warningText" in final_obj:
        final_obj.pop("warningText")
    
    ordered_obj = {}
    if "notice" in final_obj:
        ordered_obj["notice"] = final_obj.pop("notice")
        
    ordered_obj.update(final_obj)

    try:
        unique_parses = []
        seen_names = set()
        for p in combined_parses:
            name = p.get("name", "")
            if name and name not in seen_names:
                unique_parses.append(p)
                seen_names.add(name)
        ordered_obj["parses"] = unique_parses

        if "doh" in ordered_obj and isinstance(ordered_obj["doh"], list):
            for doh_item in ordered_obj["doh"]:
                if doh_item.get("url", "").endswith("/dns-quer"):
                    doh_item["url"] = doh_item["url"] + "y"
            
            ali_doh = {
                "name": "AliDNS",
                "url": "https://dns.alidns.com/dns-query",
                "ips": ["223.5.5.5", "223.6.6.6"]
            }
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]):
                ordered_obj["doh"].insert(0, ali_doh)

        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            ordered_obj["lives"] = [live for live in ordered_obj["lives"] if live]

        custom_js_rules = [
            "console.log('蝴蝶影視綠色版高級WebView攔截器啟動');",
            "window.addEventListener('DOMContentLoaded', function() {",
            "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
            "   Function.prototype.__constructor__ = Function.prototype.constructor;",
            "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
            "});",
            "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);"
        ]

        current_rules = ordered_obj.get("rules", [])
        if not isinstance(current_rules, list):
            current_rules = []
             
        ad_hosts = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]
        for rule in current_rules:
            if isinstance(rule, dict) and "hosts" in rule:
                for h in rule["hosts"]:
                    if h not in ad_hosts: ad_hosts.append(h)

        js_injection_rule = {
            "name": "蝴蝶影视·雲端高級去廣告JS注入",
            "hosts": ad_hosts,
            "script": custom_js_rules
        }
        ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "老楊TV·雲端高級去广告JS注入"]

        block_1_rebo = []        
        block_2_yingshi = []     
        block_3_duanju = []      
        block_4_dongman = []     
        block_5_cili = []        
        block_6_tiyu = []        
        block_7_shaoer = []      
        block_8_yinyue = []      
        block_9_fuli = []        

        tg_tail_count = 0 
        for site in ordered_obj.get("sites", []):
            if "name" not in site:
                continue
                
            raw_name = site["name"]
            s_key = site.get("key", "")
            s_genre = site.get("genre", "")
            s_api = site.get("api", "")
            
            for char in ['丨', '┃', ' ']:
                raw_name = raw_name.strip(char)
            raw_name = re.sub(r'\s+', ' ', raw_name)
            
            if "｜Tg：@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg：@huliys9", "").strip()
            elif "｜Tg:@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg:@huliys9", "").strip()

            if "ext" in site and site["ext"] == {}:
                site["ext"] = ""

            if isinstance(s_api, str) and "PanWebShare" in s_api:
                site["api"] = "csp_PanWebShare"
                if "jar" in site:
                    site.pop("jar")

            is_guazi = "瓜子" in raw_name or "GZ" == s_key
            is_target_rebo_main = (s_key == "热播影视")

            if is_target_rebo_main:
                site["name"] = "热播 • APP｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
                site["category"] = "综合"
                block_1_rebo.append(site)

            elif "豆瓣" in raw_name and "首页" in raw_name:
                site["name"] = "🦋 豆瓣 • 首页"
                site["category"] = "综合"
                site["searchable"] = 0
                block_2_yingshi.append(site)
                
            elif "短剧" in raw_name or "剧场" in raw_name:
                if "dj" in raw_name.lower() or "dj" in s_key.lower():
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "音乐"
                    site["searchable"] = 0
                    block_8_yinyue.append(site)
                else:
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "短剧"
                    site["genre"] = "shortdrama"
                    block_3_duanju.append(site)
                    
            elif "动漫" in raw_name or "新番" in raw_name or "anime" in s_key.lower() or "a1" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "动漫"
                block_4_dongman.append(site)
                
            elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower() or "PanWebShare" in str(s_api):
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "网盘/磁力"
                site["searchable"] = 0
                site["quickSearch"] = 0
                site["changeable"] = 1
                block_5_cili.append(site)
                
            elif "体育" in raw_name or "球" in raw_name or "直播" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "体育/直播"
                block_6_tiyu.append(site)
                
            elif "少儿" in raw_name or "课堂" in raw_name or "教学" in raw_name or "教育" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "少儿"
                site["searchable"] = 0
                block_7_shaoer.append(site)
                 
            elif "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "唱会" in raw_name or "fm" in raw_name.lower() or "相声" in raw_name or "小品" in raw_name or "戏曲" in raw_name or "推送" in raw_name or "配置" in raw_name or "版本" in raw_name or "本地" in raw_name or "dj" in raw_name.lower() or "dj" in s_key.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                if "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower():
                    site["category"] = "音乐"
                else:
                    site["category"] = "综合"
                site["searchable"] = 0
                block_8_yinyue.append(site)
                
            else:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "综合"
                block_2_yingshi.append(site)

            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site:
                site["searchable"] = 1

        for site in block_2_yingshi:
            if site.get("key") == "AQY":
                site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9"

        # block_9_fuli 保持彻底悬空清空，确保纯净绿色体验
        ordered_obj["sites"] = (
            block_1_rebo + block_2_yingshi + block_3_duanju + block_4_dongman +
            block_6_tiyu + block_7_shaoer + block_8_yinyue + block_5_cili + block_9_fuli
        )

        # 🛡️ 纯净版硬核物理清洗核心算法：二次清洗合并后的新 sites 与 lives，确保 100% 滤除 18+ 敏感词
        clean_sites = []
        for site in ordered_obj.get("sites", []):
            site_str = json.dumps(site, ensure_ascii=False)
            if "🔞" not in site_str and "18+" not in site_str and "有三级片" not in site_str:
                clean_sites.append(site)
                 
        clean_lives = []
        for live in ordered_obj.get("lives", []):
            live_str = json.dumps(live, ensure_ascii=False)
            if "🔞" not in live_str and "18+" not in live_str and "有三级片" not in live_str:
                if live and isinstance(live, dict):
                    if not live.get("ua") or live.get("ua") == "okhttp":
                        live["ua"] = "okhttp/5.3.2"
                    clean_lives.append(live)
                
        ordered_obj["sites"] = clean_sites
        ordered_obj["lives"] = clean_lives

        print(f"🚀 【洗牌结算】蝴蝶纯净绿色版过滤重排全自动落地！")

    except Exception as inner_e:
        print(f"⚠️ 提示：重排阶段异常跳过: {inner_e}")

    # ====================================================================
    # 🎯 【超高精度对比与推送板块】
    # ====================================================================
    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    github_repo = os.getenv("GITHUB_REPO", "GodLike631/Ly_18")
    
    # 动态抓取及感知当前构建的订阅链接
    subscribe_url = f"https://raw.githubusercontent.com/{github_repo}/refs/heads/main/datas/{output_filename}"

    # ------------------------------------------------------------------
    # 🌟 【新增核心功能：新密码专属推送通道（完全独立解耦）】
    # ------------------------------------------------------------------
    if is_new_token_generated and tg_token and tg_chat_id:
        try:
            pwd_msg = f"🔔 *老杨TV · 蝴蝶纯净版全新月份硬核密码锁发布* 🔔\n\n"
            pwd_msg += f"📅 *生效时间*：{(datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y年%m月01日')} (北京时间)\n"
            pwd_msg += f"🔑 *本月全新蝴蝶纯净版密锁*：`{current_token}`\n\n"
            pwd_msg += f"🚀 *重要提示*：\n旧接口已全线开启【金蝉脱壳】大轰炸提示，原蝴蝶纯净版链接已彻底作废断流！\n\n"
            pwd_msg += f"🔗 *最新蝴蝶纯净版订阅链接 (点击即可自动复制)*：\n`{subscribe_url}`\n\n"
            pwd_msg += f"👑 蝴蝶纯净版链接已在后台全自动换锁，请及时更新电视端接口。若电视端遇到断流请尝试重启软件或前往频道（@huliys9）获取最新支持！"

            pwd_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            pwd_data = urllib.parse.urlencode({"chat_id": tg_chat_id, "parse_mode": "Markdown", "text": pwd_msg}).encode("utf-8")
            pwd_req = urllib.request.Request(pwd_url, data=pwd_data)
            with urllib.request.urlopen(pwd_req, timeout=15) as response:
                print("🚀 [专属密码通道] 蝴蝶纯净版每月1号新密锁独立通知发送成功！")
        except Exception as pwd_err:
            print(f"❌ [专属密码通道] 蝴蝶纯净版发送通知失败: {pwd_err}")

    try:
        old_sites_names, old_lives_names = set(), set()
        if old_valid_json_data:
            old_sites_names = {s.get("name", "").strip() for s in old_valid_json_data.get("sites", []) if s.get("name")}
            old_lives_names = {l.get("name", "").strip() for l in old_valid_json_data.get("lives", []) if l.get("name")}
        elif os.path.exists(tracker_path):
            with open(tracker_path, 'r', encoding='utf-8') as f:
                old_file_name = f.read().strip()
            old_file_path = f"datas/{old_file_name}"
            if os.path.exists(old_file_path):
                with open(old_file_path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    old_sites_names = {s.get("name", "").strip() for s in old_data.get("sites", []) if s.get("name")}
                    old_lives_names = {l.get("name", "").strip() for l in old_data.get("lives", []) if l.get("name")}

        # 抓取本次安全重排并滤除18+后生成的最新名录
        new_sites_names = {s.get("name", "").strip() for s in ordered_obj.get("sites", []) if s.get("name")}
        new_lives_names = {l.get("name", "").strip() for l in ordered_obj.get("lives", []) if l.get("name")}

        # 差分对比，纯中文展示名字，过滤虚假误报
        added_sites = sorted(list(new_sites_names - old_sites_names))
        deleted_sites = sorted(list(old_sites_names - new_sites_names))
        added_lives = sorted(list(new_lives_names - old_lives_names))
        deleted_lives = sorted(list(old_lives_names - new_lives_names))

        if added_sites or deleted_sites or added_lives or deleted_lives:
            msg_lines = ["📝 *【 变动明细预览 】*", "📊 *━━━━━━━━━━━━━━━*"]
            
            # 点播线部分
            if added_sites or deleted_sites:
                msg_lines.append("📺 *【点播线路变动】*")
                if added_sites:
                    msg_lines.append("➕ *新增点播*：")
                    msg_lines.extend([f"🟢 {name}" for name in added_sites])
                if deleted_sites:
                    if added_sites: msg_lines.append("")
                    msg_lines.append("➖ *剔除点播*：")
                    msg_lines.extend([f"🔴 {name}" for name in deleted_sites])
                msg_lines.append("📊 *━━━━━━━━━━━━━━━*")
                
            # 直播源部分
            if added_lives or deleted_lives:
                if len(msg_lines) > 2: msg_lines.append("")
                msg_lines.append("📡 *【直播源站变动】*")
                if added_lives:
                    msg_lines.append("➕ *新增直播*：")
                    msg_lines.extend([f"🟢 {name}" for name in added_lives])
                if deleted_lives:
                    if added_lives: msg_lines.append("")
                    msg_lines.append("➖ *剔除直播*：")
                    msg_lines.extend([f"🔴 {name}" for name in deleted_lives])
                msg_lines.append("📊 *━━━━━━━━━━━━━━━*")

            if tg_token and tg_chat_id:
                current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
                detail_msg = "\n".join(msg_lines)
                
                full_msg = f"🔔 *老杨TV 蝴蝶纯净版接口变更明细通知* 🔔\n\n"
                full_msg += f"📅 *更新时间*：{current_time} (北京时间)\n"
                full_msg += f"🚀 *变动说明*：检测到上游数据源更新或手工区线路调整，新接口配置已全自动编译上链！\n\n"
                full_msg += f"{detail_msg}\n\n"
                full_msg += f"🔗 *【 订阅链接 】* (点击即可自动复制)：\n`{subscribe_url}`\n\n"
                full_msg += f"👑 纯净版链接已在后台无缝更新，更新接口即可，若电视端遇到断流请尝试重启软件或及时前往频道（@huliys9）获取当前最新密码锁！"

                # 🚀 采用底层的 urllib.request 标准流发射，绝对安全
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                data = urllib.parse.urlencode({"chat_id": tg_chat_id, "parse_mode": "Markdown", "text": full_msg}).encode("utf-8")
                req = urllib.request.Request(url, data=data)
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        print("🚀 Telegram 纯净版通知直发成功！")
                except Exception as net_err:
                    print(f"❌ Telegram 发送网络请求失败: {net_err}")
            else:
                print("⚠️ 提示：缺少 TG_TOKEN 或 TG_CHAT_ID，跳过通知发送。")
        else:
            print("⏭️ 点播与直播线路无名称级实质变动，智能拦截冗余推送。")
            
    except Exception as diff_err:
        print(f"⚠️ 对比变动核心发生异常: {diff_err}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
    print(f"🎉 纯净版处理写出成功: {output_path}")
except Exception as e:
    print(f"❌ 运行失败: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
