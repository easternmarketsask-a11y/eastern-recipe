# -*- coding: utf-8 -*-
"""抓合法配图：维基词条首图优先 + Commons 兜底；下载带大小校验(<30KB视为坏图,换下一个)。"""
import json, re, sys, time, urllib.parse, os
import requests
S=requests.Session(); S.headers['User-Agent']='EasternMarketRecipe/1.0 (easternmarketsask@gmail.com; recipe site)'
CAND={
 'hotpot':['en:Hot pot','commons:火鍋 料理'],
 'red-braised-pork':['en:Red braised pork belly','commons:紅燒肉'],
 'braised-beef-brisket':['commons:柱侯牛腩','commons:紅燒牛腩','commons:牛腩 料理'],
 'soy-braised-beef-shank':['commons:醬牛肉','commons:酱牛肉'],
 'white-cut-chicken':['en:White cut chicken','commons:白切雞'],
 'twice-cooked-pork':['en:Twice-cooked pork','commons:回鍋肉'],
 'cumin-lamb':['commons:孜然羊肉','commons:孜然羊肉串'],
 'tomato-beef-brisket':['commons:番茄牛腩','commons:番茄燉牛肉'],
 'beef-chow-fun':['en:Beef chow fun','commons:乾炒牛河'],
 'soy-sauce-cheung-fun':['commons:豉油皇炒麵','commons:炒河粉'],
 'beef-brisket-noodle-soup':['zh:牛腩麵','commons:牛腩麵'],
 'cheung-fun-ready':['en:Rice noodle roll','commons:腸粉'],
 'youtiao-ready':['en:Youtiao','commons:油條'],
 'nai-huang-bao-ready':['commons:奶黄包','commons:奶皇包'],
 'shouzhuabing-ready':['commons:手抓饼','commons:蔥油餅'],
 'huajuan-ready':['commons:花卷 饅頭','commons:花卷'],
 'hei-jin-liusha-bao-ready':['zh:流沙包','commons:流沙包','commons:奶黄包'],
 'cha-shao-bao-ready':['en:Cha siu bao','commons:叉燒包'],
 'xian-rou-dabao-ready':['commons:鮮肉包','commons:肉包子','en:Baozi'],
 'mapo-tofu':['commons:麻婆豆腐','en:Mapo tofu'],
 'tomato-egg':['commons:番茄炒蛋','commons:番茄炒蛋 料理'],
 'pork-green-pepper':['commons:青椒肉絲','commons:青椒肉丝'],
 'blanched-choy-sum':['commons:菜心 料理','commons:白灼菜心','en:Choy sum'],
 'seaweed-egg-soup':['commons:紫菜蛋花湯','en:Egg drop soup'],
 'xiaolongbao-ready':['commons:小籠包','en:Xiaolongbao'],
 'shumai-ready':['commons:燒賣','en:Shumai'],
 'purple-rice-floss-bun':['commons:肉鬆麵包','commons:肉松面包'],
}
def wiki_img(lang,title):
    u='https://%s.wikipedia.org/api/rest_v1/page/summary/%s'%(lang,urllib.parse.quote(title.replace(' ','_')))
    try:
        d=S.get(u,timeout=20).json()
        img=(d.get('originalimage') or d.get('thumbnail') or {}).get('source','')
        if re.search(r'\.(jpg|jpeg|png)$',img,re.I): return {'url':img,'page':u}
    except Exception: pass
    return None
def commons_imgs(q):
    p={'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrlimit':10,
       'gsrsearch':q,'prop':'imageinfo','iiprop':'url','iiurlwidth':1000}
    out=[]
    try: d=S.get('https://commons.wikimedia.org/w/api.php',params=p,timeout=20).json()
    except Exception: return out
    for pg in sorted(((d.get('query') or {}).get('pages') or {}).values(),key=lambda x:x.get('index',99)):
        ii=(pg.get('imageinfo') or [{}])[0]; url=ii.get('thumburl') or ii.get('url') or ''
        if re.search(r'\.(jpg|jpeg|png)$',url,re.I): out.append({'url':url,'page':ii.get('descriptionurl','')})
    return out
def try_download(hit,path):
    try:
        img=S.get(hit['url'],timeout=35).content
        if len(img)<30000: return 0
        open(path,'wb').write(img); return len(img)
    except Exception: return 0
recs=json.load(open('data/recipes.json',encoding='utf-8'))['recipes']
report=[]; creds={}
for r in recs:
    rid=r['id']; path='src/assets/images/%s.jpg'%rid; done=False
    for cand in CAND.get(rid,[]):
        hits=[]
        if cand[:3] in ('en:','zh:'):
            h=wiki_img(cand[:2],cand[3:]); hits=[h] if h else []
        else:
            hits=commons_imgs(cand.split(':',1)[1])
        for h in hits:
            n=try_download(h,path)
            if n:
                creds[rid]={'source':h['page'],'via':cand}; report.append((rid,r['name_cn'],'OK %dKB'%(n//1024),cand)); done=True; break
        if done: break
        time.sleep(0.2)
    if not done: report.append((rid,r['name_cn'],'MISS',''))
json.dump(creds,open('src/assets/images/_credits.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
ok=sum(1 for x in report if x[2].startswith('OK'))
sys.stdout.buffer.write(('重抓(带校验): %d/%d\n'%(ok,len(recs))).encode('utf-8'))
for rid,nm,st,usd in report:
    sys.stdout.buffer.write(('  %-26s [%s] %s\n'%(rid,st,usd)).encode('utf-8'))
