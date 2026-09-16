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
