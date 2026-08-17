#!/usr/bin/env python3
import subprocess, time, base64, sys, re, os

# 可通过环境变量覆盖：ADB_PATH / ANDROID_SERIAL / OCR_SCRIPT
ADB=os.environ.get('ADB_PATH', '/Users/edy/Downloads/platform-tools/adb')
SERIAL=os.environ.get('ANDROID_SERIAL', 'ZTQCJJ7DKVZHFMRS')
OCR_SCRIPT=os.environ.get('OCR_SCRIPT', '/Users/edy/ideaProjects/my-skills/skills/wechat-account-bookmarks/scripts/ocr_wechat.swift')
TMP='/tmp/batch_wechat'

os.makedirs(TMP, exist_ok=True)

def sh(args):
    return subprocess.run([ADB,'-s',SERIAL]+args, capture_output=True, text=True)

def shell(cmd):
    return sh(['shell', cmd])

def tap(x,y):
    sh(['shell','input','tap',str(x),str(y)])

def swipe(x1,y1,x2,y2,d=200):
    sh(['shell','input','swipe',str(x1),str(y1),str(x2),str(y2),str(d)])

def screencap(path):
    with open(path,'wb') as f:
        subprocess.run([ADB,'-s',SERIAL,'exec-out','screencap','-p'], stdout=f, check=False)
    return path

def ocr(path):
    r = subprocess.run(['swift', OCR_SCRIPT, path], capture_output=True, text=True)
    items=[]
    for line in r.stdout.splitlines():
        m=re.match(r'([\d.]+),([\d.]+) ([\d.]+)x([\d.]+)\t(.*)', line)
        if m:
            x=float(m.group(1)); y=float(m.group(2)); w=float(m.group(3)); h=float(m.group(4)); text=m.group(5).strip()
            items.append({'x':x,'y':y,'w':w,'h':h,'text':text})
    return items

def find(items, *subs, ymin=0, ymax=99999, xmin=0, xmax=99999):
    for it in items:
        if ymin <= it['y'] <= ymax and xmin <= it['x'] <= xmax:
            for s in subs:
                if s in it['text']:
                    return it
    return None

def center(it):
    return (it['x']+it['w']/2, it['y']+it['h']/2)

def tap_item(it):
    x,y=center(it)
    tap(int(x),int(y))

def broadcast(action, extra_key=None, extra_val=None):
    cmd=[ADB,'-s',SERIAL,'shell','am','broadcast','-a',action]
    if extra_key:
        cmd += ['--es', extra_key, extra_val]
    subprocess.run(cmd, capture_output=True, text=True)

def matches_search(text, name):
    """搜索/候选匹配：
    - 名称长度 <= 6：要求完整名称出现
    - 名称长度 > 6：默认匹配前 6 个字
    仅用于找候选，不能作为最终确认。"""
    compact_text = text.replace('-','').replace(' ','')
    compact_name = name.replace('-','').replace(' ','')
    if len(compact_name) <= 6:
        return name in text or compact_name in compact_text
    prefix6 = compact_name[:6]
    return prefix6 in compact_text or name[:6] in text

def matches_full(text, name):
    """资料页最终校验：必须完整匹配目标公众号名称。
    允许去掉名称中的连接符/空格后做完整匹配。"""
    if name in text:
        return True
    compact_name = name.replace('-','').replace(' ','')
    compact_text = text.replace('-','').replace(' ','')
    return compact_name and compact_name in compact_text

def matches_confirm(text, name):
    """小程序确认（简介页不显示完整名时）：信任搜索列表选中的名称文本。
    - 全名/compact 全名命中（matches_full）→ 通过
    - 候选文本被截断（含“…”或长度不足）→ 要求包含目标名称前 7 个字，
      用于区分“中国银行保险报”（无第7字“电”）和“中国银行保险报电…”（有“电”）
    - 未截断 → 要求完整名或特征后缀
    """
    if matches_full(text, name):
        return True
    compact_text = text.replace('-','').replace(' ','').replace('…','')
    compact_name = name.replace('-','').replace(' ','')
    truncated = '…' in text or len(compact_text) < len(compact_name)
    if truncated:
        # 要求比公共前缀再多 1 个字，避免“中国银行保险报”（7字）命中“中国银行保险报电子报”
        # 目标 10 字时，前 8 字包含“电”，能区分
        min_prefix = min(8, len(compact_name))
        return compact_name[:min_prefix] in compact_text
    if len(compact_name) > 6:
        suffix = compact_name[-3:] if len(compact_name) >= 9 else compact_name[-2:]
        return suffix in compact_text
    return False

def pick_candidates(items, name):
    """在账号列表中按"条目聚类"返回候选列表：
    1. 用 matches_search（≤6 全匹配，>6 前 6 字）找匹配行
    2. y 范围放宽到 2600，小程序也能进候选（不再只限 1800）
    3. 同一实体的多行（主标题/副标题/简介）按 y 聚类合并为一条，只取主标题行，
       避免同一号被当成多个候选（去重 key 用整行文本挡不住不同行）
    4. 按标签优先级排序：公众号 > 服务号 > 媒体 > 视频号 > 小程序
    """
    priority = ['公众号','服务号','媒体','视频号','小程序']
    matched = [it for it in items if 500 <= it['y'] <= 2600 and matches_search(it['text'], name)]
    # 按 y 聚类：与上一组最后一行 y 差 <150 视为同一条目
    matched.sort(key=lambda it: it['y'])
    groups = []
    for it in matched:
        if groups and it['y'] - groups[-1][-1]['y'] < 150:
            groups[-1].append(it)
        else:
            groups.append([it])
    cands=[]
    seen=set()
    for g in groups:
        main = g[0]  # 主标题行（最上方）
        ymin = main['y'] - 120
        ymax = g[-1]['y'] + 250
        label = None
        pri = len(priority)
        for i, lbl in enumerate(priority):
            if find(items, lbl, ymin=ymin, ymax=ymax, xmin=0, xmax=1200):
                label = lbl
                pri = i
                break
        if not label:
            continue
        key = (main['text'].strip(), label)
        if key not in seen:
            seen.add(key)
            cands.append((pri, main, label))
    cands.sort(key=lambda x: x[0])
    return [(it,label) for _,it,label in cands]

def tap_search_icon():
    """定位右上角放大镜。
    优先从 OCR 文本里找“Q”：
    - 如果是一个独立的小 Q（宽度较小），点它的中心；
    - 如果 Q 和“直播中/•••”混在同一行，点该行右端偏左的位置（放大镜在 ••• 左侧）。
    避免把“直播中”当成放大镜。"""
    shot=screencap(f'{TMP}/nav.png')
    items=ocr(shot)
    qitem=None
    for it in items:
        if it['y'] <= 350 and 'q' in it['text'].lower() and it['x'] >= 500:
            qitem=it
            break
    if qitem:
        if qitem['w'] <= 160:
            x = qitem['x'] + qitem['w']/2
        else:
            # 混合行（如“◎ 直播中>Q…”），放大镜在行尾 ••• 的左侧约 180px
            x = qitem['x'] + qitem['w'] - 180
        y = qitem['y'] + qitem['h']/2
        print(f'  tap magnifier at ({x:.0f},{y:.0f})', flush=True)
        tap(int(x), int(y))
    else:
        print('  Q not found by OCR, fallback tap (972,210)', flush=True)
        tap(972,210)
    time.sleep(0.8)

def is_mini_program():
    """通过当前 top/resumed Activity 判断是否进入小程序页面。
    注意：不能检查整个 dumpsys 输出——微信进程历史栈里残留的 appbrand
    Activity 会导致误判恒 True（公众号页面也被当成小程序）。"""
    r = sh(['shell','dumpsys','activity','activities']).stdout
    for line in r.splitlines():
        low = line.lower()
        if 'appbrand' in low and ('resumedactivity' in low or 'topresumedactivity' in low or 'mcurrentfocus' in low):
            return True
    return False

def handle_mini_program_add():
    """小程序添加到桌面流程：
    右上角“...” → 底部“转发到朋友”那一行 → 向左滑 → 右侧出现“添加到桌面” → 点击 → 右下角返回。
    """
    print('  handle_mini_program_add', flush=True)
    # 点右上角“...”
    tap(1100,210)
    time.sleep(2)
    shot=screencap(f'{TMP}/mini_menu.png')
    items=ocr(shot)
    row=find(items, '转发到朋友', ymin=1500, ymax=2500)
    if not row:
        print('  !! 转发到朋友 not found', flush=True)
        return False
    y = row['y'] + row['h']/2
    # 向左滑动该行，露出“添加到桌面”
    swipe(1000, int(y), 300, int(y), 300)
    time.sleep(1)
    shot=screencap(f'{TMP}/mini_add.png')
    items=ocr(shot)
    add=find(items, '添加到桌面', ymin=1000, ymax=2500)
    if not add:
        print('  !! 添加到桌面 not found in mini menu', flush=True)
        return False
    tap_item(add)
    time.sleep(1.5)
    # 点击右下角返回，继续下一个
    shell('input keyevent 4')
    time.sleep(1)
    return True

def process(name, first=False):
    print(f'=== Processing: {name} ===', flush=True)
    b64 = base64.b64encode(name.encode('utf-8')).decode()

    # 1. 导航到搜索输入框：兼容“已停在搜索页”的情况
    act = sh(['shell','dumpsys','activity','activities']).stdout
    m = re.search(r'topResumedActivity=ActivityRecord\{[^ ]+ [^ ]+ ([^ ]+)', act)
    top_act = m.group(1) if m else ''
    if 'FTSMainUI' in top_act or 'MMFTSSOSHomeWebViewUI' in top_act:
        # 已经在搜索页，直接点输入框
        shell("input tap 500 220; sleep 0.3")
    elif 'NewBizInfoSettingUI' in top_act:
        # 在设置页：先返回简介页，再点放大镜
        shell("input keyevent 4; sleep 0.4")
        tap_search_icon()
        shell("input tap 500 220; sleep 0.3")
    elif first:
        tap_search_icon()
        shell("input tap 500 220; sleep 0.3")
    else:
        shell("input keyevent 4; sleep 0.4")
        tap_search_icon()
        shell("input tap 500 220; sleep 0.3")
    time.sleep(1.0)
    broadcast('ADB_CLEAR_TEXT')
    time.sleep(0.5)
    broadcast('ADB_INPUT_B64','msg',b64)
    time.sleep(2.0)
    # 2. 点击下面出现的匹配项（不是顶部“搜索”按钮）
    shot=screencap(f'{TMP}/suggest.png')
    items=ocr(shot)
    sug=None
    # 优先选带 Q 的搜索建议（账号/搜索入口），避免点到左侧头像/联系人
    for it in items:
        if 300 <= it['y'] <= 700 and it['text'].lstrip().startswith('Q') and matches_search(it['text'], name):
            sug=it
            break
    if not sug:
        for it in items:
            if 300 <= it['y'] <= 700 and matches_search(it['text'], name):
                sug=it
                break
    if sug:
        print(f'  tap suggestion at {center(sug)}', flush=True)
        tap_item(sug)
        time.sleep(2.5)
    else:
        print('  !! no suggestion found, skip', flush=True)
        return False
    # 3. Ensure account filter
    shot=screencap(f'{TMP}/result.png')
    items=ocr(shot)
    acct=find(items, '账号', ymin=300, ymax=500)
    attempts=0
    while not acct and attempts < 8:
        print(f'  no 账号 tab, small left swipe #{attempts+1}', flush=True)
        swipe(700,370,500,370,200)
        time.sleep(1)
        shot=screencap(f'{TMP}/result_swipe{attempts}.png')
        items=ocr(shot)
        acct=find(items, '账号', ymin=300, ymax=500)
        attempts += 1
    if acct:
        print(f'  tap 账号 at {center(acct)}', flush=True)
        tap_item(acct)
        time.sleep(2.5)
    else:
        print('  !! 账号 tab not found after swipes, skip', flush=True)
        return False
    # 4-5. 动态查找候选：不匹配返回后重新扫描当前列表，找其他候选，最多尝试 3 个
    tried=set()
    verified=False
    for attempt in range(3):
        # 重新扫描当前账号列表（返回后应回到列表）
        shot=screencap(f'{TMP}/account_try{attempt}.png')
        items=ocr(shot)
        cand=None
        cand_label=None
        for it,label in pick_candidates(items, name):
            key=(it['text'].strip(), label)
            if key not in tried:
                cand=it
                cand_label=label
                break
        # 当前屏没有未试候选，则向下滚动再找一次
        if not cand:
            swipe(600,1800,600,900,400)
            time.sleep(1.5)
            shot=screencap(f'{TMP}/account_try{attempt}_scroll.png')
            items=ocr(shot)
            for it,label in pick_candidates(items, name):
                key=(it['text'].strip(), label)
                if key not in tried:
                    cand=it
                    cand_label=label
                    break
        if not cand:
            print('  !! no more candidates, skip', flush=True)
            return False
        key=(cand['text'].strip(), cand_label)
        tried.add(key)
        print(f'  candidate {attempt+1}/3: tap {center(cand)}', flush=True)
        tap_item(cand)
        time.sleep(3.0)
        # Verify profile; handle video profile with linked 公众号
        shot=screencap(f'{TMP}/profile_verify.png')
        items=ocr(shot)
        # Already on settings page -> add directly
        add_now=find(items, '添加到桌面', ymin=300, ymax=1800)
        if add_now:
            print('  already on settings, tap 添加到桌面', flush=True)
            tap_item(add_now)
            time.sleep(1.5)
            return True
        # Video profile (FinderProfileUI) with linked 公众号 entry
        gzh_link=find(items, '公众号：', ymin=0, ymax=1500)
        is_video_profile = find(items, '视频号', ymin=0, ymax=1500) or find(items, '主页', ymin=0, ymax=1500)
        if gzh_link and is_video_profile:
            print(f'  video profile, tap linked 公众号 at {center(gzh_link)}', flush=True)
            tap_item(gzh_link)
            time.sleep(2.5)
            shot=screencap(f'{TMP}/after_gzh_link.png')
            items=ocr(shot)
            add_now=find(items, '添加到桌面', ymin=300, ymax=1800)
            if add_now:
                print(f'  tap 添加到桌面 at {center(add_now)}', flush=True)
                tap_item(add_now)
                time.sleep(1.5)
                return True
        # 小程序：简介页不显示完整名，按候选文本确认（搜索名确认）后直接走小程序添加流程
        if is_mini_program():
            list_ok = matches_confirm(cand['text'], name)
            page_ok = any(matches_full(it['text'], name) for it in items if it['y'] < 1500)
            if not list_ok and not page_ok:
                print('  mini program name mismatch, back and try next candidate', flush=True)
                shell('input keyevent 4')
                time.sleep(1.5)
                continue
            print('  mini program verified by search name, use mini program add flow', flush=True)
            if handle_mini_program_add():
                return True
            else:
                shell('input keyevent 4')
                time.sleep(1.5)
                continue
        # 资料页必须完整匹配
        name_ok = any(matches_full(it['text'], name) for it in items if it['y'] < 1500)
        if name_ok:
            verified=True
            break
        else:
            print('  profile name mismatch, back and try another candidate', flush=True)
            shell('input keyevent 4')
            time.sleep(1.5)
    if not verified:
        print('  !! profile not verified after candidates, skip', flush=True)
        return False
    # 5. Profile: follow if needed
    shot=screencap(f'{TMP}/profile.png')
    items=ocr(shot)
    followed = find(items, '已关注', ymin=800, ymax=2000, xmin=0, xmax=1200)
    follow = None
    if not followed:
        follow=find(items, '关注服务号', '关注公众号', ymin=800, ymax=2000, xmin=0, xmax=700)
        if not follow:
            follow=find(items, '关注', ymin=800, ymax=2000, xmin=100, xmax=600)
    if followed:
        print('  already followed, skip follow', flush=True)
    elif follow:
        print(f'  tap follow at {center(follow)}', flush=True)
        tap_item(follow)
        time.sleep(2.0)
    # 6. If chat page (no 私信/关注), tap avatar to profile
    shot=screencap(f'{TMP}/after_follow.png')
    items=ocr(shot)
    if not find(items, '私信') and not find(items, '关注'):
        print('  in chat, tap avatar', flush=True)
        tap(1100,210)
        time.sleep(2.5)
    # 7. Open ... menu (try multiple positions; top banner may cover)
    setting=None
    for mx,my in [(1100,210),(1140,210),(1080,250),(1100,260),(1050,220)]:
        tap(mx,my)
        time.sleep(1.5)
        shot=screencap(f'{TMP}/menu_try.png')
        items=ocr(shot)
        setting=find(items, '设置', ymin=1500, ymax=2200)
        if setting:
            print(f'  menu opened with tap ({mx},{my})', flush=True)
            break
    if not setting:
        # maybe a top banner is covering; try to close an X near top-right and retry
        print('  menu not opened, trying to close banner X', flush=True)
        for cx,cy in [(1150,150),(1100,160),(1050,150)]:
            tap(cx,cy)
            time.sleep(0.8)
        for mx,my in [(1100,210),(1140,210)]:
            tap(mx,my)
            time.sleep(1.5)
            shot=screencap(f'{TMP}/menu_try2.png')
            items=ocr(shot)
            setting=find(items, '设置', ymin=1500, ymax=2200)
            if setting:
                break
    if setting:
        print(f'  tap 设置 at {center(setting)}', flush=True)
        tap_item(setting)
        time.sleep(2.0)
    else:
        print('  !! menu not opened (banner may cover), skip', flush=True)
        return False
    # 8. Settings: add to desktop
    shot=screencap(f'{TMP}/settings.png')
    items=ocr(shot)
    add=find(items, '添加到桌面', ymin=300, ymax=1800)
    if add:
        print(f'  tap 添加到桌面 at {center(add)}', flush=True)
        tap_item(add)
        time.sleep(1.5)
        return True
    else:
        print('  !! 添加到桌面 not found', flush=True)
        return False

if __name__=='__main__':
    names = sys.argv[1:] if len(sys.argv)>1 else ['央视网','央视新闻','大众新闻-大众日报']
    # Ensure ADBKeyBoard active
    sh(['shell','ime','set','com.android.adbkeyboard/.AdbIME'])
    for i, n in enumerate(names):
        try:
            ok=process(n, first=(i==0))
            print(f'RESULT {n}: {"OK" if ok else "SKIP/FAIL"}', flush=True)
        except Exception as e:
            print(f'RESULT {n}: ERROR {e}', flush=True)
    # Restore Sogou
    sh(['shell','ime','set','com.sohu.inputmethod.sogou.xiaomi/.SogouIME'])
    print('Batch done, IME restored', flush=True)