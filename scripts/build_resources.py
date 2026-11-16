#!/usr/bin/env python3
"""Generate Tetrixa gameplay articles and feature detail pages."""
import html, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]; DIST=ROOT/"dist"
APP=json.loads((ROOT/"content/app.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"content/screenshots.json").read_text(encoding="utf-8"))
FEATURES=json.loads((ROOT/"content/features.json").read_text(encoding="utf-8"))
BASE=APP["website_url"].rstrip("/"); PLAY=APP["google_play_url"]

DATA=[
("block-placement-basics","Block placement tips for a cleaner board","نصائح لوضع القطع والحفاظ على لوحة مرتبة","Learn to place falling pieces thoughtfully, preserve open space and avoid filling the board too quickly.","تعلّم وضع القطع الساقطة بعناية والحفاظ على المساحات المفتوحة وتجنب ملء اللوحة بسرعة.",[
("Look at the next piece","راقب القطعة التالية","Use the next-piece preview to think one move ahead and choose a placement that keeps options open.","استخدم معاينة القطعة التالية للتخطيط للحركة المقبلة واختيار موضع يبقي أمامك خيارات."),
("Keep the board flexible","حافظ على مرونة اللوحة","Avoid creating awkward gaps when a simpler placement can keep the board easier to manage.","تجنب إنشاء فراغات صعبة عندما يكون بإمكانك اختيار موضع أبسط يجعل إدارة اللوحة أسهل."),
("Plan before the board gets crowded","خطط قبل ازدحام اللوحة","As the pace increases, take a moment to consider where the piece will land before moving it.","مع ازدياد السرعة، خذ لحظة لتحديد مكان سقوط القطعة قبل تحريكها."),
("Use every move deliberately","اجعل لكل حركة هدفاً","A small adjustment can make the difference between keeping space available and blocking future pieces.","قد يصنع تعديل بسيط الفرق بين إبقاء مساحة متاحة وإعاقة القطع القادمة.")]),
("how-to-clear-rows","How to clear rows in a block puzzle","كيف تكمل الصفوف في لعبة المربعات","Understand the basic goal: arrange pieces to complete horizontal rows and clear space for new pieces.","افهم الهدف الأساسي: رتّب القطع لإكمال الصفوف الأفقية وإخلاء مساحة للقطع الجديدة.",[
("Build complete horizontal rows","كوّن صفوفاً أفقية مكتملة","Place pieces so that a row has no gaps. A completed row clears and opens room on the board.","ضع القطع بحيث يخلو الصف من الفراغات. عند اكتماله يُزال الصف وتُفتح مساحة على اللوحة."),
("Watch for gaps","انتبه إلى الفراغات","Before placing a piece, check whether it leaves a hard-to-fill hole beneath or beside the stack.","قبل وضع القطعة، تحقق مما إذا كانت ستترك فجوة يصعب ملؤها أسفل التكدس أو بجانبه."),
("Balance immediate and future clears","وازن بين الإكمال الفوري واللاحق","Sometimes a safe placement now creates a better opportunity to complete a row on the next move.","قد يتيح وضع آمن الآن فرصة أفضل لإكمال صف في الحركة التالية."),
("Keep space for incoming pieces","اترك مساحة للقطع القادمة","Clearing rows regularly helps prevent the board from becoming crowded as the game speeds up.","يساعد إكمال الصفوف بانتظام على منع ازدحام اللوحة مع تسارع اللعبة.")]),
("improve-your-puzzle-score","Ways to improve your Tetrixa score","طرق لتحسين نتيجتك في Tetrixa","Build a repeatable approach to piece placement, row clearing and adapting as the pace increases.","اتبع أسلوباً ثابتاً في وضع القطع وإكمال الصفوف والتكيف مع ازدياد سرعة اللعب.",[
("Prioritize clean placements","أعطِ الأولوية للمواضع المناسبة","Choose placements that fit the current shape of the board and preserve room for upcoming pieces.","اختر مواضع تناسب شكل اللوحة الحالي وتحافظ على مساحة للقطع القادمة."),
("Use the preview to plan ahead","استخدم المعاينة للتخطيط","Look at the next piece before committing to a move. Thinking ahead can reduce rushed decisions.","انظر إلى القطعة التالية قبل تثبيت الحركة. يساعد التخطيط المسبق على تقليل القرارات المتسرعة."),
("Adapt to the increasing pace","تكيف مع ازدياد السرعة","As the challenge grows, favor clear, reliable moves over last-second corrections.","مع تصاعد التحدي، فضّل الحركات الواضحة والموثوقة على التصحيحات في اللحظة الأخيرة."),
("Learn from each round","تعلّم من كل جولة","Notice which placements created difficult gaps and try a different arrangement in your next attempt.","لاحظ المواضع التي أنشأت فجوات صعبة وجرّب ترتيباً مختلفاً في محاولتك التالية.")]),
("play-puzzle-games-offline","Enjoy a block puzzle game offline","استمتع بلعبة ألغاز المربعات دون اتصال","Tetrixa is described on Google Play as a complete offline game, making it available when you do not have an internet connection.","تصف صفحة Google Play لعبة Tetrixa بأنها لعبة تعمل دون اتصال، لتتمكن من اللعب عندما لا يتوفر الإنترنت.",[
("Start a round when it suits you","ابدأ جولة في الوقت المناسب","Open the game and enjoy a quick puzzle session during a break or whenever you have time.","افتح اللعبة واستمتع بجولة ألغاز قصيرة أثناء الاستراحة أو عندما يتوفر لديك الوقت."),
("Focus on the board","ركز على لوحة اللعب","Move and rotate pieces, complete rows and follow your score without needing an online connection.","حرّك القطع ودوّرها وأكمل الصفوف وتابع نتيجتك دون الحاجة إلى اتصال بالإنترنت."),
("Use touch controls","استخدم أدوات التحكم باللمس","The mobile controls are designed for direct interaction with the game board.","صُممت أدوات التحكم على الهاتف للتفاعل المباشر مع لوحة اللعب."),
("Install from the official listing","ثبّت اللعبة من الصفحة الرسمية","Use the official Google Play page for the current Android installation and app information.","استخدم صفحة Google Play الرسمية للحصول على التثبيت الحالي ومعلومات التطبيق على Android.")])
]

GUIDES={
"guide":("Tetrixa user guide: learn the basics","دليل Tetrixa: تعرّف على أساسيات اللعب","A quick walkthrough of the board, falling pieces, next-piece preview and row clearing.","شرح سريع للوحة اللعب والقطع الساقطة ومعاينة القطعة التالية وإكمال الصفوف.",[
("Start a round","ابدأ جولة","Open Tetrixa and look at the game board before the first pieces begin to fall.","افتح Tetrixa وانظر إلى لوحة اللعب قبل بدء سقوط القطع."),
("Move and rotate pieces","حرّك القطع ودوّرها","Use the on-screen controls to position and rotate pieces so they fit the available space.","استخدم أدوات التحكم على الشاشة لوضع القطع وتدويرها لتناسب المساحة المتاحة."),
("Check the next piece","تحقق من القطعة التالية","Use the preview to anticipate what is coming and plan a better placement.","استخدم المعاينة لمعرفة القطعة القادمة والتخطيط لوضعها بشكل أفضل."),
("Complete rows","أكمل الصفوف","Fill a horizontal row without gaps to clear it and make room on the board.","املأ صفاً أفقياً دون فجوات لإزالته وإخلاء مساحة على اللوحة."),
("Keep improving","واصل التحسن","Follow your score and adapt as the game becomes more challenging.","تابع نتيجتك وتكيف مع ازدياد تحدي اللعبة.")]),
"tips":("Tetrixa tips for smarter block placement","نصائح Tetrixa لوضع القطع بذكاء","Simple ideas for planning moves, keeping the board open and responding to a faster pace.","أفكار بسيطة للتخطيط للحركات والحفاظ على مساحة اللوحة والاستجابة لسرعة اللعب.",[
("Think one move ahead","فكر في الحركة التالية","Check the next-piece preview and consider how it will fit after your current move.","تحقق من معاينة القطعة التالية وفكر في كيفية وضعها بعد حركتك الحالية."),
("Avoid difficult gaps","تجنب الفجوات الصعبة","Try not to leave isolated spaces that are hard to fill with later pieces.","حاول ألا تترك مساحات منعزلة يصعب ملؤها بالقطع اللاحقة."),
("Clear rows regularly","أكمل الصفوف بانتظام","Completed rows free up space and help you manage the board for longer.","تؤدي الصفوف المكتملة إلى إخلاء مساحة وتساعدك على إدارة اللوحة مدة أطول."),
("Stay calm as speed rises","حافظ على هدوئك مع زيادة السرعة","Prefer a deliberate placement over a rushed move when the pace increases.","فضّل وضع القطعة بعناية بدلاً من حركة متسرعة عندما تزداد السرعة.")]),
"comparison":("Block puzzle strategies: plan, place and clear","استراتيجيات ألغاز المربعات: خطط وضع وأكمل","A practical comparison of different ways to approach a crowded board and an upcoming piece.","مقارنة عملية بين طرق التعامل مع لوحة مزدحمة وقطعة قادمة.",[
("Quick placement","الوضع السريع","A fast move can help when the board is open, but check the landing space first.","قد تساعد الحركة السريعة عندما تكون اللوحة مفتوحة، لكن تحقق من مساحة الهبوط أولاً."),
("Plan for the next piece","خطط للقطعة التالية","Looking ahead can preserve more options than focusing only on the current piece.","قد يحافظ النظر إلى الحركة التالية على خيارات أكثر من التركيز على القطعة الحالية فقط."),
("Clear space when possible","أخلِ المساحة عندما تستطيع","Completing rows reduces clutter and gives new pieces room to fit.","يقلل إكمال الصفوف الازدحام ويمنح القطع الجديدة مساحة مناسبة."),
("Choose the safer move","اختر الحركة الأكثر أماناً","A stable board can be more useful than a risky placement that leaves hard-to-fill gaps.","قد تكون اللوحة المستقرة أفضل من وضع محفوف بالمخاطر يترك فجوات يصعب ملؤها.")])
}

def e(v): return html.escape(str(v),quote=True)
def route_url(lang,tail=""): return f'{BASE}/{lang}/'+(f'{tail}/' if tail else "")
def routes():
    tails=["","about","features","download","faq","blog"]+["features/"+f["id"] for f in FEATURES]+["blog/"+a[0] for a in DATA]+list(GUIDES)
    return [(l,t) for l in ("en","ar") for t in tails]
def nav(l,tail=""):
    import build
    primary=[("about","About" if l=="en" else "حول اللعبة"),("features","Features" if l=="en" else "المزايا"),("download","Download" if l=="en" else "التنزيل"),("faq","FAQ" if l=="en" else "الأسئلة")]
    resource=[("tips","Tips" if l=="en" else "نصائح اللعب"),("blog","Blog" if l=="en" else "المدونة"),("guide","User guide" if l=="en" else "دليل اللعب"),("comparison","Strategies" if l=="en" else "استراتيجيات")]
    p="".join(f'<a data-nav-item="{k}" href="{route_url(l,k)}">{v}</a>' for k,v in primary)
    r="".join(f'<a data-nav-item="{k}" href="{route_url(l,k)}">{v}</a>' for k,v in resource)
    return (f'<header class="standard-header"><div class="locale-switch" aria-label="Country and region">{build.render_market_flags(tail)}{build.render_social_links()}</div>'
      f'<div class="header-main"><a class="brand" href="{BASE}/">TETRIXA</a><nav aria-label="Primary navigation">'
      f'<details class="nav-menu" data-nav-group="primary"><summary>{"Explore" if l=="en" else "استكشف"}</summary><div class="nav-dropdown">{p}</div></details>'
      f'<details class="nav-menu" data-nav-group="resources"><summary>{"Play guides" if l=="en" else "أدلة اللعب"}</summary><div class="nav-dropdown">{r}</div></details></nav></div></header>')
def page(l,tail,title,desc,content,typ="WebPage"):
    u=route_url(l,tail); org={"@type":"Organization","@id":f"{BASE}/#organization","name":APP["developer"],"url":BASE+"/","email":APP["support_email"]}
    node={"@type":typ,"name":title,"description":desc,"inLanguage":l,"url":u,"publisher":{"@id":f"{BASE}/#organization"}}
    if typ=="Article": node.update({"headline":title,"mainEntityOfPage":u,"author":{"@id":f"{BASE}/#organization"}})
    schema={"@context":"https://schema.org","@graph":[org,node]}
    return f'''<!doctype html><html lang="{l}" dir="{"rtl" if l=="ar" else "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{u}"><link rel="alternate" hreflang="en" href="{route_url("en",tail)}"><link rel="alternate" hreflang="ar" href="{route_url("ar",tail)}"><link rel="alternate" hreflang="x-default" href="{route_url("en",tail)}"><meta property="og:type" content="article"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{u}"><meta property="og:image" content="{e(SHOTS[0]["src"])}"><meta name="twitter:card" content="summary_large_image"><link rel="preconnect" href="https://play-lh.googleusercontent.com" crossorigin><link rel="stylesheet" href="{BASE}/assets/style.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body data-page-section="{e(tail.split("/")[0] if tail else "home")}"><a class="skip-link" href="#main-content">{"تجاوز إلى المحتوى الرئيسي" if l=="ar" else "Skip to main content"}</a>{nav(l,tail)}<main id="main-content">{content}</main><footer><span>© DevImpact · TETRIXA</span><span><a href="{e(APP["privacy_policy_url"])}">{"سياسة الخصوصية" if l=="ar" else "Privacy policy"}</a> · <a href="mailto:{e(APP["support_email"])}">{"الدعم" if l=="ar" else "Support"}</a></span></footer></body></html>'''
def blog(l):
    title="Tetrixa gameplay blog and puzzle guides" if l=="en" else "مدونة Tetrixa وأدلة اللعب"
    desc="Practical guides to block placement, clearing rows, improving your score and playing offline." if l=="en" else "أدلة عملية لوضع القطع وإكمال الصفوف وتحسين النتيجة واللعب دون اتصال."
    cards=[]
    for slug,et,at,ee,ae,sections in DATA:
        t=et if l=="en" else at; d=ee if l=="en" else ae
        cards.append(f'<article class="item"><h2><a href="{route_url(l,"blog/"+slug)}">{e(t)}</a></h2><p>{e(d)}</p><a href="{route_url(l,"blog/"+slug)}">{"Read guide →" if l=="en" else "اقرأ الدليل ←"}</a></article>')
    content=f'<section class="section"><div class="tag">TETRIXA · {"GAMEPLAY RESOURCES" if l=="en" else "موارد اللعب"}</div><h1>{"Tetrixa gameplay guides" if l=="en" else "أدلة اللعب في Tetrixa"}</h1><p class="lead">{"Tips and explainers to help you plan each move and enjoy every round." if l=="en" else "نصائح وشروحات تساعدك على التخطيط لكل حركة والاستمتاع بكل جولة."}</p><div class="grid">{"".join(cards)}</div></section>'
    return page(l,"blog",title,desc,content)
def article(l,a):
    slug,et,at,ee,ae,sections=a; title=et if l=="en" else at; desc=ee if l=="en" else ae
    blocks="".join(f'<section class="article-section"><h2>{e(h_en if l=="en" else h_ar)}</h2><p>{e(p_en if l=="en" else p_ar)}</p></section>' for h_en,h_ar,p_en,p_ar in sections)
    content=f'<article class="section article"><h1>{e(title)}</h1><p class="lead">{e(desc)}</p>{blocks}<p><a href="{route_url(l,"blog")}">{"← All guides" if l=="en" else "← جميع الأدلة"}</a></p><div class="end"><h2>{"Play Tetrixa on Android" if l=="en" else "العب Tetrixa على Android"}</h2><p>{"Put these ideas into practice in your next round." if l=="en" else "جرّب هذه الأفكار في جولتك القادمة."}</p><a class="btn" href="{PLAY}" target="_blank" rel="noopener noreferrer">{"Open on Google Play" if l=="en" else "افتح على Google Play"}</a></div></article>'
    return page(l,"blog/"+slug,title,desc,content,"Article")
def guide(l,slug,data):
    et,at,ee,ae,steps=data; title=et if l=="en" else at; desc=ee if l=="en" else ae
    blocks=[]
    for i,(h_en,h_ar,p_en,p_ar) in enumerate(steps):
        image=""
        if slug=="guide" and i<len(SHOTS):
            s=SHOTS[i]; image=f'<figure class="guide-shot"><img src="{e(s["src"])}" width="526" height="936" alt="{e(s["alt"]["en" if l=="en" else "ar"])}" loading="lazy" decoding="async"><figcaption>{e(s["caption"]["en" if l=="en" else "ar"])}</figcaption></figure>'
        blocks.append(f'<section class="guide-step"><div class="num">{i+1:02d}</div><div><h2>{e(h_en if l=="en" else h_ar)}</h2><p>{e(p_en if l=="en" else p_ar)}</p>{image}</div></section>')
    content=f'<section class="section"><div class="tag">TETRIXA · {"GAMEPLAY GUIDE" if l=="en" else "دليل اللعب"}</div><h1>{e(title)}</h1><p class="lead">{e(desc)}</p><div class="guide-list">{"".join(blocks)}</div><p><a class="btn" href="{PLAY}" target="_blank" rel="noopener noreferrer">{"Play Tetrixa" if l=="en" else "العب Tetrixa"}</a></p></section>'
    return page(l,slug,title,desc,content)
def feature_page(l,feature):
    index=next(i for i,x in enumerate(FEATURES) if x["id"]==feature["id"]); shot=SHOTS[index]
    title=feature["title"][l]+" | Tetrixa"; desc=feature["description"][l]
    headings=(["Learn the core loop","Make each placement count","Keep the board manageable"] if l=="en" else ["تعرّف على طريقة اللعب","اجعل لكل وضع هدفاً","حافظ على سهولة إدارة اللوحة"])
    paragraphs=([desc,"Use the preview and touch controls to think ahead and position pieces carefully.","Complete rows to create space and adapt as the challenge increases."] if l=="en" else [desc,"استخدم المعاينة وأدوات التحكم باللمس للتخطيط ووضع القطع بعناية.","أكمل الصفوف لإخلاء المساحة وتكيف مع ازدياد التحدي."])
    sections="".join(f'<section class="article-section"><h2>{e(h)}</h2><p>{e(p)}</p></section>' for h,p in zip(headings,paragraphs))
    content=f'<article class="article"><div class="tag">TETRIXA · {"GAME FEATURE" if l=="en" else "ميزة في اللعبة"}</div><h1>{e(feature["title"][l])}</h1><p class="lead">{e(desc)}</p><figure class="guide-shot"><img src="{e(shot["src"])}" width="526" height="936" alt="{e(shot["alt"]["en" if l=="en" else "ar"])}" loading="lazy" decoding="async"><figcaption>{e(shot["caption"]["en" if l=="en" else "ar"])}</figcaption></figure>{sections}<p><a href="{route_url(l,"features")}">{"Explore all features" if l=="en" else "استكشف جميع المزايا"}</a></p><p><a href="{route_url(l,"download")}">{"Download Tetrixa" if l=="en" else "تنزيل Tetrixa"}</a></p></article>'
    return page(l,"features/"+feature["id"],title,desc,content)
def build_extra_pages():
    css=DIST/"assets/style.css"
    css.write_text(css.read_text(encoding="utf-8")+"""
.article{max-width:850px;margin:auto}.article h1{font-size:clamp(2.1rem,5vw,3.5rem);line-height:1.2}.article-section{padding:18px 0;border-bottom:1px solid #ffffff18}.article-section h2{font-size:1.45rem}.article-section p,.guide-step p{color:#c1ccda}.guide-list{display:grid;gap:18px;margin-top:28px}.guide-step{display:grid;grid-template-columns:54px 1fr;gap:16px;padding:22px;background:#111925;border:1px solid #283449;border-radius:16px}.guide-step>.num{font-size:1.4rem}.guide-step h2{margin:0 0 8px}.guide-shot{margin:18px 0 0;padding:12px;background:#080b12;border-radius:12px}.guide-shot img{display:block;width:100%;height:auto;object-fit:contain}.guide-shot figcaption{color:#aab6c8;padding-top:8px}.article .end{margin-top:38px}.item a{color:#00c4df}.item h2{font-size:1.3rem;line-height:1.4}
""",encoding="utf-8")
    for l in ("en","ar"):
        for f in (DIST/l).rglob("index.html"):
            src=f.read_text(encoding="utf-8")
            if "<nav " in src and 'data-nav-group="resources"' not in src:
                resource=[("tips","Tips" if l=="en" else "نصائح اللعب"),("blog","Blog" if l=="en" else "المدونة"),("guide","User guide" if l=="en" else "دليل اللعب"),("comparison","Strategies" if l=="en" else "استراتيجيات")]
                links="".join(f'<a data-nav-item="{k}" href="{route_url(l,k)}">{v}</a>' for k,v in resource)
                extra=f'<details class="nav-menu" data-nav-group="resources"><summary>{"Play guides" if l=="en" else "أدلة اللعب"}</summary><div class="nav-dropdown">{links}</div></details>'
                f.write_text(src.replace("</nav>",extra+"</nav>"),encoding="utf-8")
        p=DIST/l/"blog"/"index.html"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(blog(l),encoding="utf-8")
        for a in DATA:
            p=DIST/l/"blog"/a[0]/"index.html"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(article(l,a),encoding="utf-8")
        for slug,data in GUIDES.items():
            p=DIST/l/slug/"index.html"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(guide(l,slug,data),encoding="utf-8")
        for feature in FEATURES:
            p=DIST/l/"features"/feature["id"]/"index.html"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(feature_page(l,feature),encoding="utf-8")
    entries=[(f"{BASE}/",None)]+[(route_url(l,t),t) for l,t in routes()]
    sm='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    for loc,tail in entries:
        en,ar=(route_url("en"),route_url("ar")) if tail is None else (route_url("en",tail),route_url("ar",tail))
        default=f"{BASE}/" if tail is None else en
        sm+=f'<url><loc>{e(loc)}</loc><xhtml:link rel="alternate" hreflang="en" href="{e(en)}"/><xhtml:link rel="alternate" hreflang="ar" href="{e(ar)}"/><xhtml:link rel="alternate" hreflang="x-default" href="{e(default)}"/></url>'
    sm+="</urlset>"; (DIST/"sitemap.xml").write_text(sm,encoding="utf-8")
    (DIST/"sitemap.txt").write_text("\n".join(x[0] for x in entries)+"\n",encoding="utf-8")
    ll=(DIST/"llms.txt").read_text(encoding="utf-8")+"\n## Tetrixa gameplay resources\n"
    for l in ("en","ar"):
        ll+=f"- {l} gameplay blog: {route_url(l,'blog')}\n"
        for slug in GUIDES: ll+=f"- {l} {slug}: {route_url(l,slug)}\n"
        for feature in FEATURES: ll+=f"- {l} feature {feature['id']}: {route_url(l,'features/'+feature['id'])}\n"
    (DIST/"llms.txt").write_text(ll,encoding="utf-8")
if __name__=="__main__": build_extra_pages()
