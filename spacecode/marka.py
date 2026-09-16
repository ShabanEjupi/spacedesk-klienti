# -*- coding: utf-8 -*-
"""Ngul serverin, çelësin dhe markën SpaceDesk te degëzimi i klientit.

🚨 Kjo NUK është zbukurim. Pa dy konstantet e para, app-i i ndërtuar do të flasë
me `rs-ny.rustdesk.com` — pra me infrastrukturën e tyre publike — dhe i tërë
kuptimi i një serveri tonë humbet pa asnjë gabim që të vihet re.

🚨 Ndryshohet VETËM `applicationId`, jo hapësira e emrave Kotlin. Ato janë dy
gjëra të ndryshme te Gradle: `applicationId` është identiteti te dyqani,
hapësira e emrave është ku rrinë klasat. Riemërtimi i së dytës prek qindra
skedarë dhe s'jep asgjë.
"""
import io, os, re, sys

# Rrënja nxirret si mjedis që i NJËJTI skedar të xhirojë edhe te Ampere edhe te
# CI-ja e GitHub-it. Pa këtë, tubacioni i pamjeve ndërtonte pa markë — dhe
# askush nuk e mattte ([[vegla-nje-burim-i-vetem]]).
RRENJA = os.getenv("SPACEDESK_RRENJA", "/home/opc/build/spacedesk-klienti")
SERVERI = "desk.spacecode.tech"
CELESI = "HW2q7sVEYR6XHphts+Bad7Mkw9n12qVYxfB666HDAYs="
ID_APP = "tech.spacecode.desk"
EMRI = "SpaceDesk"

ndryshime = []
# 🚨 Çdo model që nuk gjendet regjistrohet KËTU dhe e vret skriptin në fund.
# Deri më 10-09-2026 `redakto` shtypte vetëm një ⚠️ mes dhjetëra rreshtave dhe
# vazhdonte me dalje 0 — pra një ndryshim te rrjedha kryesore e linte markën
# gjysmake dhe ndërtimi dilte i gjelbër me app-in ende «RustDesk». Roja shkon
# te NYJA, jo te secili vend.
deshtime = []

def redakto(shtegu, ndreqjet):
    p = os.path.join(RRENJA, shtegu)
    if not os.path.exists(p):
        deshtime.append("mungon skedari: " + shtegu)
        return
    t = io.open(p, encoding="utf-8").read()
    fillestar = t
    for vjeter, i_ri in ndreqjet:
        # 🚨 «Pa ndryshim» NUK është dështim: skripti xhirohet mbi një degë që
        #    mund të jetë e markuar tashmë. Dështim është vetëm kur MUNGON edhe
        #    modeli i vjetër edhe vlera e re — atëherë rrjedha kryesore e ka
        #    ndryshuar burimin dhe marka do të mbetej gjysmake në heshtje.
        if vjeter not in t:
            if i_ri not in t:
                deshtime.append("%s: %s" % (shtegu, vjeter[:70]))
            continue
        t = t.replace(vjeter, i_ri)
    if t != fillestar:
        io.open(p, "w", encoding="utf-8").write(t)
        ndryshime.append(shtegu)
        print("  ✅", shtegu)

print("1) Serveri dhe çelësi (hbb_common)")
redakto("libs/hbb_common/src/config.rs", [
    ('pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
     'pub const RENDEZVOUS_SERVERS: &[&str] = &["%s"];' % SERVERI),
    ('pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
     'pub const RS_PUB_KEY: &str = "%s";' % CELESI),
    # 🚨🏷️ EMRI QË SHEH NJERIU BRENDA APP-IT. Matur 10-09-2026: header-i i
    # app-it thërret `bind.mainGetAppNameSync()` → `config::APP_NAME`, dhe kjo
    # mbetej "RustDesk". Pra app-i i botuar te Play si **SpaceDesk** shkruante
    # **RustDesk** te shiriti i vet i sipërm — pikërisht kategoria «metadata që
    # nuk përputhet me app-in» që rrëzoi Hartën.
    #
    # ⚠️ `APP_NAME` emërton edhe dosjen e konfigurimit dhe shtigjet e regjistrave
    #    (config.rs: `directories_next::ProjectDirs::from(…, &APP_NAME)`), dhe
    #    `is_rustdesk()` te `src/common.rs` kthehet false. Të dyja janë sjellja e
    #    duhur për një klient me markë tonën; kostoja e vetme është që një
    #    instalim EKZISTUES i nis cilësimet nga e para. SpaceDesk-u nuk ka ende
    #    përdorues te prodhimi, ndaj ky është momenti i vetëm pa kosto.
    ('pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
     'pub static ref APP_NAME: RwLock<String> = RwLock::new("%s".to_owned());' % EMRI),
])

print("2) Identiteti te Android")
gradle = "flutter/android/app/build.gradle"
p = os.path.join(RRENJA, gradle)
if not os.path.exists(p):
    gradle = "flutter/android/app/build.gradle.kts"
    p = os.path.join(RRENJA, gradle)
if os.path.exists(p):
    t = io.open(p, encoding="utf-8").read()
    t2 = re.sub(r'applicationId\s*[= ]\s*"[^"]+"', 'applicationId "%s"' % ID_APP, t, count=1)
    if t2 != t:
        io.open(p, "w", encoding="utf-8").write(t2)
        ndryshime.append(gradle)
        print("  ✅ applicationId →", ID_APP)
    elif 'applicationId "%s"' % ID_APP in t:
        print("  ℹ️  applicationId ishte tashmë", ID_APP)
    else:
        deshtime.append("%s: applicationId s'u gjet fare" % gradle)
else:
    deshtime.append("mungon build.gradle(.kts)")

print("3) Emri që sheh njeriu")
for sh in ("flutter/android/app/src/main/AndroidManifest.xml",
           "flutter/ios/Runner/Info.plist"):
    p = os.path.join(RRENJA, sh)
    if not os.path.exists(p):
        deshtime.append("mungon skedari: " + sh)
        continue
    t = io.open(p, encoding="utf-8").read()
    t2 = t.replace('android:label="RustDesk"', 'android:label="%s"' % EMRI)
    t2 = t2.replace("<string>RustDesk</string>", "<string>%s</string>" % EMRI)
    if t2 != t:
        io.open(p, "w", encoding="utf-8").write(t2)
        ndryshime.append(sh)
        print("  ✅", sh)
    # 🚨 Kontrolli i «ishte tashmë» duhet i NGUSHTË. Një `EMRI in t` i thjeshtë
    #    kalonte edhe kur `android:label` ishte bërë `@string/app_name`, sepse
    #    fjala «SpaceDesk» del gjetkë te manifesti (`android:label="SpaceDesk
    #    Input"`). Pra roja do të flinte pikërisht kur burimi ndryshon.
    elif ('android:label="%s"' % EMRI) in t or ("<string>%s</string>" % EMRI) in t:
        print("  ℹ️  emri ishte tashmë", EMRI, "te", sh)
    else:
        deshtime.append("%s: as RustDesk as %s — burimi ndryshoi" % (sh, EMRI))

print()
print("U ndryshuan %d skedarë:" % len(ndryshime))
for x in ndryshime:
    print("  ·", x)


# ═══════════════════════════════════════════════════════════════════════════
#  SHTRESA 2: src/lang/*.rs — teksti qe e sheh VERTET perdoruesi
#
#  🚨 MATUR 16-09-2026. Deri sot marka.py ndryshonte PESE gjera (serveri,
#  celesi, APP_NAME, gradle, nje skript). Ndersa te 52 skedaret e gjuheve
#  rrinin 1338 dalje te fjales "RustDesk" — mes tyre ekrani i PARE:
#      ("connecting_status", "Connecting to the RustDesk network...")
#  Pra app-i shpallej "i markuar" dhe shqyrtuesi i Play-it lexonte RustDesk
#  te sekonda e pare. Kjo eshte pikerisht ankesa e Shabanit.
#
#  🔑 Dy kurthe qe e bejne ndreqjen jo-triviale:
#
#  1. QELESAT NUK PREKEN. Disa celesa E PERMBAJNE fjalen ("About RustDesk").
#     Nje zevendesim i verber do t'i prishte kerkimet te Dart-i, ku thirret
#     translate('Keep RustDesk background service'). Prandaj ndryshohet VETEM
#     vlera (vargu i dyte i cdo tuple-i).
#
#  2. ANGLISHTJA BIE MBI VETE QELESIN. `en.rs` NUK ka hyrje per "About
#     RustDesk" — RustDesk-u e shfaq celesin ashtu si eshte kur mungon
#     perkthimi. Pra vlerat e ndreqara nuk mjaftojne: per cdo celes qe permban
#     marken e vjeter i SHTOHET en.rs-se nje hyrje e markuar. Celesi mbetet i
#     paprekur, ekrani del i yni.
# ═══════════════════════════════════════════════════════════════════════════
import re, glob

E_VJETER = "RustDesk"
E_RE = EMRI if "EMRI" in dir() else "SpaceDesk"

LANG = os.path.join(RRENJA, "src", "lang")
RRESHTI = re.compile(r'^(\s*\(")((?:[^"\\]|\\.)*)(",\s*")((?:[^"\\]|\\.)*)("\s*\),?\s*)$')

celesat_me_marke = set()
prekur = 0

for f in sorted(glob.glob(os.path.join(LANG, "*.rs"))):
    rreshtat = open(f, encoding="utf-8").read().split("\n")
    dal = []
    ndryshuar = False
    for r in rreshtat:
        m = RRESHTI.match(r)
        if not m:
            dal.append(r); continue
        celesi, vlera = m.group(2), m.group(4)
        if E_VJETER in celesi:
            celesat_me_marke.add(celesi)
        if E_VJETER in vlera:
            vlera = vlera.replace(E_VJETER, E_RE)
            ndryshuar = True
            r = m.group(1) + celesi + m.group(3) + vlera + m.group(5)
        dal.append(r)
    if ndryshuar:
        open(f, "w", encoding="utf-8").write("\n".join(dal))
        prekur += 1

print("📐 skedarë gjuhësh të ndryshuar: %d" % prekur)

# ── en.rs: hyrje e markuar për çdo çelës që e mban markën e vjetër ──────────
EN = os.path.join(LANG, "en.rs")
if not os.path.exists(EN):
    deshtime.append("src/lang/en.rs mungon — anglishtja do të binte mbi çelësat")
else:
    teksti = open(EN, encoding="utf-8").read()
    ekzistuese = set(re.findall(r'^\s*\("((?:[^"\\]|\\.)*)"\s*,', teksti, re.M))
    shtuar = []
    for c in sorted(celesat_me_marke):
        if c in ekzistuese:
            continue
        shtuar.append('        ("%s", "%s"),' % (c, c.replace(E_VJETER, E_RE)))
    if shtuar:
        # futen menjëherë pas hapjes së vargut `[`
        ankor = "    [\n"
        if ankor not in teksti:
            deshtime.append("en.rs: ankori `[` nuk u gjet — struktura ndryshoi")
        else:
            teksti = teksti.replace(ankor, ankor + "\n".join(shtuar) + "\n", 1)
            open(EN, "w", encoding="utf-8").write(teksti)
            print("📐 hyrje të reja te en.rs (anglishtja binte mbi çelësin): %d" % len(shtuar))

# ── 🛡️ PORTA: asnjë vlerë e dukshme nuk guxon të mbajë markën e vjetër ─────
mbeten = []
for f in sorted(glob.glob(os.path.join(LANG, "*.rs"))):
    for nr, r in enumerate(open(f, encoding="utf-8"), 1):
        m = RRESHTI.match(r.rstrip("\n"))
        if m and E_VJETER in m.group(4):
            mbeten.append("%s:%d" % (os.path.basename(f), nr))
if mbeten:
    deshtime.append("src/lang: %d vlera ende mbajnë '%s' (%s…)"
                    % (len(mbeten), E_VJETER, ", ".join(mbeten[:3])))
else:
    print("✅ src/lang: asnjë vlerë e dukshme nuk mban markën e vjetër")


# ═══════════════════════════════════════════════════════════════════════════
#  SHTRESA 3: URL-të — lidhjet që e çojnë njeriun te faqja e HUAJ
#
#  🚨 MATUR 16-09-2026. Marka e tekstit u ndreq te shtresa 2, po çdo lidhje
#  «Website», «Privacy», «Download», «Pricing» dhe çdo lidhje ndihme te
#  gabimet e Linux-it/macOS-it hapte ende `rustdesk.com`. Te MOBILI gjithashtu
#  (`flutter/lib/mobile/pages/settings_page.dart`) — pra te app-i i BOTUAR,
#  jo vetëm te desktopi.
#
#  🔑 Nuk u ndryshuan më parë sepse s'kishim faqe barasvlerëse dhe një URL e re
#  do të jepte 404 në vend të ndihmës. Faqet u shkruan sot dhe u matën 200 PARA
#  se lidhjet të ndërroheshin:
#      https://spacedesk.spacecode.tech/ndihma.html   (#mac #x11 #ekrani-kycjes #lejet-linux #cmimi)
#      https://spacedesk.spacecode.tech/privatesia.html
#      https://spacedesk.spacecode.tech/api/version/latest  → {"url":""}
#
#  🚨🚨 ZËVENDËSIMI NUK BËHET ME `str.replace` TE PREFIKSI. Provuar me
#  kundërshembull: me një model të shkurtër "https://rustdesk.com" te lista,
#  një URL KRESJE e panjohur nga rrjedha kryesore (p.sh. `/blog/i-ri`) bëhej
#  `spacedesk.spacecode.tech/blog/i-ri` — pra 404 te faqja jonë, dhe porta
#  dilte e gjelbër sepse fjala «rustdesk.com» ishte zhdukur. Roja nuk kishte si
#  të binte kurrë ([[provat-qe-nuk-bien-kurre]]).
#  Kura: kapet URL-ja E PLOTË me regex dhe kërkohet te tabela. Ç'nuk gjendet aty
#  NUK preket dhe e vret ndërtimin — njeriu vendos ku duhet të çojë.
#
#  🚨 Tri vende NUK preken, me qëllim:
#   · rreshtat-KOMENT — askush s'i sheh, dhe ato shpjegojnë prejardhjen e forkut;
#   · `is_public()` te src/common.rs dhe provat e saj — ajo mat nëse një adresë
#     i takon infrastrukturës PUBLIKE të RustDesk-ut; serveri ynë nuk i takon,
#     pra `false` është përgjigjja e saktë. Një zëvendësim do ta bënte të gënjejë;
#   · provat te `libs/hbb_common/src/{websocket,socket_client}.rs`.
# ═══════════════════════════════════════════════════════════════════════════

FAQJA = "https://spacedesk.spacecode.tech"
NDIHMA = FAQJA + "/ndihma.html"

URLAT = {
    "https://rustdesk.com/docs/en/manual/linux/#x11-required":      NDIHMA + "#x11",
    "https://rustdesk.com/docs/en/client/linux/#x11-required":      NDIHMA + "#x11",
    "https://rustdesk.com/docs/en/manual/linux/#login-screen":      NDIHMA + "#ekrani-kycjes",
    "https://rustdesk.com/docs/en/client/linux/#login-screen":      NDIHMA + "#ekrani-kycjes",
    "https://rustdesk.com/docs/en/client/linux/#permissions-issue": NDIHMA + "#lejet-linux",
    "https://rustdesk.com/docs/en/client/mac/#enable-permissions":  NDIHMA + "#mac",
    "https://rustdesk.com/docs/en/":                                NDIHMA,
    "https://rustdesk.com/privacy.html":                            FAQJA + "/privatesia.html",
    "https://rustdesk.com/download":                                FAQJA + "/",
    "https://rustdesk.com/pricing":                                 NDIHMA + "#cmimi",
    "https://rustdesk.com/":                                        FAQJA + "/",
    "https://rustdesk.com":                                         FAQJA,
    # 🚨 KJO NUK ËSHTË MARKË, ËSHTË RRJEDHJE: kontrolli i versionit i dërgonte
    #    RustDesk-ut sistemin, versionin dhe arkitekturën e çdo pajisjeje —
    #    ndërsa politika jonë e privatësisë thotë «asnjë palë e tretë».
    "https://api.rustdesk.com/version/latest":                      FAQJA + "/api/version/latest",
    # Rrugëdalja e fundit e `get_api_server()`: pa të, hyrja me llogari i
    # dërgonte emrin dhe fjalëkalimin serverit të tyre admin.
    "https://admin.rustdesk.com":                                   "http://desk.spacecode.tech:21114",
}

# Jo çdo markë te lidhjet është URL: te «Settings → About» i MOBILIT adresa
# shfaqet si ETIKETË e dukshme, dhe ajo s'përputhet me asnjë model «https://…».
# Pra lidhja do të hapte faqen tonë ndërsa njeriu lexonte emrin e tyre.
ETIKETAT = {
    "Text('rustdesk.com'": "Text('spacedesk.spacecode.tech'",
}

SKEDARET_URL = [
    "src/client.rs",
    "src/lang/en.rs",
    "libs/hbb_common/src/lib.rs",
    "libs/hbb_common/src/config.rs",
    "flutter/lib/common.dart",
    "flutter/lib/desktop/pages/connection_page.dart",
    "flutter/lib/desktop/pages/desktop_home_page.dart",
    "flutter/lib/desktop/pages/desktop_setting_page.dart",
    "flutter/lib/desktop/pages/install_page.dart",
    "flutter/lib/mobile/pages/connection_page.dart",
    "flutter/lib/mobile/pages/settings_page.dart",
]

RE_URL = re.compile(r'https?://[A-Za-z0-9.-]*rustdesk\.com[^\s"\'`)\];,]*')

def eshte_koment(r):
    r = r.lstrip()
    return r.startswith("//") or r.startswith("#") or r.startswith("* ") or r.startswith("/*")

print()
print("4) URL-të e dukshme")
te_panjohura = []
ndryshuar_url = 0
for sh in SKEDARET_URL:
    p = os.path.join(RRENJA, sh)
    if not os.path.exists(p):
        deshtime.append("mungon skedari: " + sh)
        continue
    rreshtat = io.open(p, encoding="utf-8").read().split("\n")
    dal = []
    ndryshuar = False
    for nr, r in enumerate(rreshtat, 1):
        if eshte_koment(r):
            dal.append(r); continue
        i_ri = r
        for m in RE_URL.findall(r):
            if m in URLAT:
                i_ri = i_ri.replace(m, URLAT[m])
            else:
                te_panjohura.append("%s:%d  %s" % (sh, nr, m))
        for vjeter, zev in ETIKETAT.items():
            i_ri = i_ri.replace(vjeter, zev)
        if i_ri != r:
            ndryshuar = True
        dal.append(i_ri)
    if ndryshuar:
        io.open(p, "w", encoding="utf-8").write("\n".join(dal))
        ndryshuar_url += 1
        print("  ✅", sh)

# `get_api_server()` te src/common.rs: VETËM rreshti i rrugëdaljes, kurrë
# `is_public()` dhe kurrë provat e saj.
p = os.path.join(RRENJA, "src", "common.rs")
t = io.open(p, encoding="utf-8").read()
vjeter = '"https://admin.rustdesk.com".to_owned()'
i_ri = '"http://desk.spacecode.tech:21114".to_owned()'
if vjeter in t:
    if t.count(vjeter) != 1:
        deshtime.append("src/common.rs: %d dalje te rrugëdaljes — pritej 1" % t.count(vjeter))
    else:
        io.open(p, "w", encoding="utf-8").write(t.replace(vjeter, i_ri))
        ndryshuar_url += 1
        print("  ✅ src/common.rs (rrugëdalja e get_api_server)")
elif i_ri not in t:
    deshtime.append("src/common.rs: as rrugëdalja e vjetër, as e reja — burimi ndryshoi")

print("📐 skedarë me URL të ndryshuar: %d" % ndryshuar_url)

if te_panjohura:
    deshtime.append("URL të panjohura (vendos ku duhet të çojnë, te URLAT): "
                    + " | ".join(te_panjohura[:5]))

# ── 🛡️ PORTA E DYTË: asnjë rresht kodi me markën e vjetër, as si etiketë ────
mbeten_url = []
for sh in SKEDARET_URL:
    p = os.path.join(RRENJA, sh)
    if not os.path.exists(p):
        continue
    for nr, r in enumerate(io.open(p, encoding="utf-8"), 1):
        if "rustdesk.com" in r and not eshte_koment(r):
            mbeten_url.append("%s:%d" % (sh, nr))
if mbeten_url:
    deshtime.append("URL: %d rreshta kodi ende mbajnë rustdesk.com (%s)"
                    % (len(mbeten_url), ", ".join(mbeten_url[:4])))
else:
    print("✅ URL: asnjë rresht kodi nuk çon e nuk shkruan më rustdesk.com")


# ═══════════════════════════════════════════════════════════════════════════
#  SHTRESA 4: versionCode-i — një numër i përdorur një herë e vret ngarkimin
#
#  🚨 MATUR 16-09-2026. AAB-ja e parë me URL-të e reja u ndërtua e plotë, u
#  nënshkrua, u shkarkua — dhe Play-i e ktheu me `403 Version code 67 has
#  already been used`. Sepse `flutter/pubspec.yaml` e mban të ngulitur
#  `version: 1.4.9+67`: ÇDO ndërtim i rrjedhës kryesore prodhon të njëjtin numër.
#  Kostoja: ~40 minuta ndërtimi, dhe gabimi del vetëm në fund, te ngarkimi.
#
#  Kura: numri nxirret nga ORA UTC — `YYMMDDHH`. Rritet vetvetiu, s'përsëritet
#  brenda ditës, dhe lexohet me sy (26091608 = 16-09-2026, ora 08 UTC). I njëjti
#  stil si te AAB-të e Hartës (26091401).
# ═══════════════════════════════════════════════════════════════════════════
import time as _koha

VERZIONI_KOD = _koha.strftime("%y%m%d%H", _koha.gmtime())
_pub = os.path.join(RRENJA, "flutter", "pubspec.yaml")
if not os.path.exists(_pub):
    deshtime.append("mungon flutter/pubspec.yaml — versionCode-i do të mbetej i ngulitur")
else:
    _t = io.open(_pub, encoding="utf-8").read()
    _i_ri, _sa = re.subn(r"(?m)^version:[ \t]*([0-9]+\.[0-9]+\.[0-9]+)\+[0-9]+[ \t]*$",
                         lambda m: "version: " + m.group(1) + "+" + VERZIONI_KOD,
                         _t, count=1)
    if _sa != 1:
        deshtime.append("pubspec.yaml: rreshti `version: x.y.z+N` nuk u gjet")
    else:
        io.open(_pub, "w", encoding="utf-8").write(_i_ri)
        print("  ✅ versionCode →", VERZIONI_KOD)




# ═══════════════════════════════════════════════════════════════════════════
#  SHTRESA 5: v1 = VETËM DALJE — pa Accessibility, pa shërbime në plan të
#  parë, pa hyrje me llogari
#
#  🚨 MATUR 16-09-2026. AAB-ja 26091608 u ndërtua e plotë dhe Play-i e refuzoi
#  te KONFIRMIMI, jo te ngarkimi:
#      ⛔ 403 Your accessibility permission declaration needs to be updated.
#  Derisa ajo deklaratë të mbushet, ASNJË ndryshim nuk konfirmohet dot te ky
#  app. Dhe e njëjta pritë rri një hap më tutje: manifesti deklaron TRE
#  `foregroundServiceType` (specialUse|mediaProjection|microphone), dhe ajo
#  faqe kërkon një VIDEO për secilin ([[play-sherbimet-ne-plan-te-pare]]).
#
#  🔨 VENDIMI i Shabanit: të dyja hiqen nga v1 dhe kthehen te v2 — e njëjta
#  rrugë si [[publikimi-i-lehte-pastaj-verzioni-i-plote]]. Ç'humbet: telefoni
#  nuk KONTROLLOHET më nga larg. Ç'mbetet: telefoni KONTROLLON kompjuterin —
#  vetë veçoria e app-it, dhe e vetmja që listimi premton.
#
#  🚨 HEQJA E DEKLARATËS PA HEQJEN E UI-SË ËSHTË REFUZIM TJETËR. Një buton
#  «Share screen» që nuk nis dot më asnjë shërbim është pikërisht ankesa
#  «Unresponsive UI elements» me të cilën Play-i rrëzoi SpaceRent-in
#  ([[spacerent-refuzimi-broken-functionality]]). Prandaj UI-ja nuk fshihet me
#  dorë nga dhjetë vende: ndizet flamuri I VETË rrjedhës kryesore —
#  `is_outgoing_only()` — dhe ajo i heq vetvetiu skedën «Share Screen», lejet
#  e ekranit dhe çdo cilësim hyrës. Roja shkon te NYJA
#  ([[nje-roje-globale-jo-njeqind-ndreqje]]).
#
#  🚨 `tools:node="remove"`, jo fshirje rreshti: bashkuesi i manifesteve i
#  rikthen lejet nga çdo bibliotekë e varur — burimi duket i pastër, AAB-ja jo.
#
#  ⚠️ Kodi Kotlin i `InputService`/`MainService` MBETET te burimi; vetëm
#  manifesti nuk i deklaron. Kështu ndërtimi nuk bie, dhe v2 i rikthen me një
#  rresht. Asgjë nuk i nis: `MainActivity` i lidhet MainService-it vetëm kur
#  `MainService.isReady`, dhe atë e bën true vetëm ana hyrëse e UI-së.
# ═══════════════════════════════════════════════════════════════════════════

print()
print("5) v1: pa Accessibility, pa FGS, pa llogari")

MANIFESTI = "flutter/android/app/src/main/AndroidManifest.xml"
_pm = os.path.join(RRENJA, MANIFESTI)

# (tag, android:name, pse hiqet)
ELEMENTET_JASHTE = [
    ("service", ".InputService",
     "BIND_ACCESSIBILITY_SERVICE — deklarata që ktheu 403-shin"),
    ("service", ".MainService",
     "foregroundServiceType specialUse|mediaProjection|microphone"),
    ("service", ".FloatingWindowService",
     "dritarja pluskuese — vetëm kur TELEFONI kontrollohet"),
    ("receiver", ".BootReceiver",
     "nisja te ndezja — nis MainService-in, pra s'ka më ç'nis"),
]

# Lejet nuk fshihen: shënohen `tools:node="remove"`, që bashkuesi të mos i kthejë.
LEJET_JASHTE = [
    "android.permission.FOREGROUND_SERVICE",
    "android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION",
    "android.permission.FOREGROUND_SERVICE_MICROPHONE",
    "android.permission.FOREGROUND_SERVICE_SPECIAL_USE",
    "android.permission.RECORD_AUDIO",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
]

# 🛡️ KUNDËRSHEMBULLI ([[kundershembulli-mat-ndreqjen]]): këto NUK guxojnë të
# preken. Pa to porta do të kalonte edhe mbi një manifest të zbrazur krejt.
LEJET_BRENDA = [
    "android.permission.INTERNET",
    "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.WAKE_LOCK",
    "android.permission.POST_NOTIFICATIONS",
]

if not os.path.exists(_pm):
    deshtime.append("mungon " + MANIFESTI)
else:
    _t = io.open(_pm, encoding="utf-8").read()
    _fillestar = _t

    for _tag, _emri, _pse in ELEMENTET_JASHTE:
        # `[^>]*` s'e kapërcen dot një `>`, pra ndalon te fundi i etiketës
        # hapëse edhe kur atributet shtrihen në disa rreshta.
        _rx = re.compile(
            r'\n[ \t]*<%s\b[^>]*android:name="%s"[^>]*(?:/>|>.*?</%s>)\n'
            % (_tag, re.escape(_emri), _tag), re.S)
        _t2, _sa = _rx.subn("\n", _t)
        if _sa == 1:
            _t = _t2
            print("  ✅ hoqi <%s %s> — %s" % (_tag, _emri, _pse))
        elif _sa > 1:
            deshtime.append("%s: %d dalje të <%s %s> — pritej 1"
                            % (MANIFESTI, _sa, _tag, _emri))
        elif ('android:name="%s"' % _emri) in _t:
            deshtime.append("%s: <%s %s> ekziston po s'u kap nga modeli"
                            % (MANIFESTI, _tag, _emri))
        else:
            print("  ℹ️  <%s %s> s'ishte më aty" % (_tag, _emri))

    for _leje in LEJET_JASHTE:
        _plot = '<uses-permission android:name="%s" tools:node="remove" />' % _leje
        if _plot in _t:
            continue
        _vjeter = '<uses-permission android:name="%s" />' % _leje
        if _vjeter in _t:
            _t = _t.replace(_vjeter, _plot)
            print("  ✅ tools:node=remove →", _leje.rsplit(".", 1)[1])
        else:
            deshtime.append("%s: leja %s as e deklaruar as e hequr — burimi ndryshoi"
                            % (MANIFESTI, _leje))

    if _t != _fillestar:
        io.open(_pm, "w", encoding="utf-8").write(_t)
        ndryshime.append(MANIFESTI)

# ── Flamujt e vetë rrjedhës kryesore: një ndryshim, dhjetë ekrane ──────────
#
# 🚨 Pse te Rust-i e jo te Dart-i: të njëjtat tri funksione i lexojnë EDHE
# desktopi, EDHE mobili, EDHE tubacioni i pamjeve. Nëse UI-ja fshihet me dorë
# te Dart-i, pamjet e dyqanit do të nxirreshin nga një ndërtim që ende i
# tregon ato ekrane — pra pamje që nuk përputhen me app-in
# ([[pershkrimi-matet-kunder-ekraneve]]).
#
# ⚠️ Kompjuteri demo i shqyrtuesit (ID 468543837) NUK preket: ai xhiron .deb-in
# e RustDesk-ut nga rrjedha kryesore, jo këtë degëzim (demo/Dockerfile). Pra
# «vetëm dalje» këtu nuk e prish anën që PRANON lidhjen atje.
KONF = "libs/hbb_common/src/config.rs"
_pc = os.path.join(RRENJA, KONF)

FLAMUJT = [
    ("is_outgoing_only",
     'pub fn is_outgoing_only() -> bool {\n'
     '    HARD_SETTINGS\n'
     '        .read()\n'
     '        .unwrap()\n'
     '        .get("conn-type")\n'
     '        .map_or(false, |x| x == ("outgoing"))\n'
     '}',
     'pub fn is_outgoing_only() -> bool {\n'
     '    // SpaceDesk v1: vetëm DALJE. Kjo fsheh skedën «Share Screen», lejet e\n'
     '    // ekranit dhe çdo cilësim hyrës — sepse manifesti nuk i deklaron më\n'
     '    // AccessibilityService-in dhe shërbimet në plan të parë, dhe një buton\n'
     '    // pa pasojë është refuzim më vete. Kthehet te v2 bashkë me to.\n'
     '    true\n'
     '}'),
    ("is_disable_account",
     'pub fn is_disable_account() -> bool {\n'
     '    is_some_hard_opton("disable-account")\n'
     '}',
     'pub fn is_disable_account() -> bool {\n'
     '    // SpaceDesk v1: pa hyrje me llogari. Fsheh butonin Login, skedën e\n'
     '    // librit të adresave dhe panelin e grupit te TË GJITHA ndërfaqet.\n'
     '    true\n'
     '}'),
    ("is_disable_ab",
     'pub fn is_disable_ab() -> bool {\n'
     '    is_some_hard_opton("disable-ab")\n'
     '}',
     'pub fn is_disable_ab() -> bool {\n'
     '    // Libri i adresave rri te llogaria; pa llogari s\'ka ç\'sinkronizohet.\n'
     '    true\n'
     '}'),
]

if not os.path.exists(_pc):
    deshtime.append("mungon " + KONF)
else:
    _t = io.open(_pc, encoding="utf-8").read()
    _fillestar = _t
    for _emri, _vjeter, _ri in FLAMUJT:
        if _ri in _t:
            print("  ℹ️  %s() ishte tashmë i ngulur" % _emri)
            continue
        if _vjeter not in _t:
            deshtime.append("%s: trupi i %s() ndryshoi — mos e ngul verbërisht"
                            % (KONF, _emri))
            continue
        if _t.count(_vjeter) != 1:
            deshtime.append("%s: %d dalje të %s() — pritej 1"
                            % (KONF, _t.count(_vjeter), _emri))
            continue
        _t = _t.replace(_vjeter, _ri)
        print("  ✅ %s() → true" % _emri)
    if _t != _fillestar:
        io.open(_pc, "w", encoding="utf-8").write(_t)
        ndryshime.append(KONF)

# ── Një çelës i vetëm te Dart-i që flamuri NUK e mbulon ────────────────────
#
# 🚨 «Keep <marka> background service» rri jashtë çdo `if (!outgoingOnly)`.
# Pa këtë rresht, v1 do të kishte një çelës që kërkon leje për një shërbim që
# manifesti s'e deklaron më — buton pa pasojë, pra pikërisht refuzimi që po
# shmangim.
CILESIMET = "flutter/lib/mobile/pages/settings_page.dart"
_ps = os.path.join(RRENJA, CILESIMET)
_vjeter_bat = "    if (_hasIgnoreBattery) {"
_ri_bat = "    if (_hasIgnoreBattery && !bind.isOutgoingOnly()) {"
if not os.path.exists(_ps):
    deshtime.append("mungon " + CILESIMET)
else:
    _t = io.open(_ps, encoding="utf-8").read()
    if _ri_bat in _t:
        print("  ℹ️  çelësi i baterisë ishte tashmë i kushtëzuar")
    elif _vjeter_bat in _t:
        io.open(_ps, "w", encoding="utf-8").write(_t.replace(_vjeter_bat, _ri_bat, 1))
        ndryshime.append(CILESIMET)
        print("  ✅ çelësi «Keep … background service» fshihet te vetëm-dalje")
    else:
        deshtime.append("%s: `if (_hasIgnoreBattery)` s'u gjet — burimi ndryshoi"
                        % CILESIMET)

# ── 🛡️ PORTA E SHTRESËS 5 ─────────────────────────────────────────────────
#
# 🚨 Matet REZULTATI, jo veprimi. Një `replace` që s'kapi asgjë dhe një
# skedar i shkruar gjysmak duken njësoj te dalja ([[shkrimi-deshtoi-po-porta-kaloi]]).
if os.path.exists(_pm):
    _m = io.open(_pm, encoding="utf-8").read()

    for _fjala, _pse in [
        ("BIND_ACCESSIBILITY_SERVICE", "deklarata që ktheu 403-shin"),
        ("accessibilityservice", "veprimi i AccessibilityService-it"),
        ("foregroundServiceType", "kërkon një VIDEO për çdo lloj"),
        ("PROPERTY_SPECIAL_USE_FGS_SUBTYPE", "specialUse kërkon miratim më vete"),
    ]:
        if _fjala in _m:
            deshtime.append("%s: '%s' ende aty (%s)" % (MANIFESTI, _fjala, _pse))

    for _tag, _emri, _ in ELEMENTET_JASHTE:
        if ('android:name="%s"' % _emri) in _m:
            deshtime.append("%s: <%s %s> ende i deklaruar" % (MANIFESTI, _tag, _emri))

    for _leje in LEJET_JASHTE:
        if ('android:name="%s" tools:node="remove"' % _leje) not in _m:
            deshtime.append("%s: %s pa tools:node=remove — bashkuesi e kthen"
                            % (MANIFESTI, _leje))

    # 🛡️ Kundërshembulli: pa këtë, një manifest i zbrazur krejt do të kalonte.
    for _leje in LEJET_BRENDA:
        if ('android:name="%s" />' % _leje) not in _m:
            deshtime.append("%s: %s u prek — heqja s'ishte e synuar"
                            % (MANIFESTI, _leje))
    if 'android:name=".MainActivity"' not in _m:
        deshtime.append("%s: MainActivity u hoq — app-i s'do të nisej fare" % MANIFESTI)

    # Dhe XML-ja duhet të mbetet XML: një regex mbi etiketa e prish në heshtje.
    try:
        import xml.etree.ElementTree as _ET
        _ET.fromstring(_m)
    except Exception as _e:
        deshtime.append("%s: XML i pavlefshëm pas heqjes — %s" % (MANIFESTI, _e))

if os.path.exists(_pc):
    _c = io.open(_pc, encoding="utf-8").read()
    for _emri, _, _ri in FLAMUJT:
        if _ri not in _c:
            deshtime.append("%s: %s() nuk u ngul" % (KONF, _emri))
    # 🛡️ Kundërshembulli: `is_incoming_only()` ka trup thuajse identik me
    # `is_outgoing_only()`. Nëse edhe ai doli `true`, modeli kapi shumë.
    if 'pub fn is_incoming_only() -> bool {\n    HARD_SETTINGS' not in _c:
        deshtime.append("%s: is_incoming_only() u prek — modeli kapi shumë" % KONF)


# 🛡️ ROJA. Pa të, çdo model i pagjetur ishte vetëm një rresht ⚠️ dhe skripti
# dilte 0 — pra ndërtimi vazhdonte me markë gjysmake. Tani ndërtimi BIE këtu.
if deshtime:
    print()
    print("⛔ %d modele NUK u gjetën — marka është e paplotë:" % len(deshtime))
    for x in deshtime:
        print("  ·", x)
    print()
    print("Rrjedha kryesore e ndryshoi burimin. Përditëso marka.py; MOS e ndërto ashtu.")
    sys.exit(1)

print("✅ marka u ngul e plotë")
