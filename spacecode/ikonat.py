# -*- coding: utf-8 -*-
"""Ikonat e SpaceDesk-ut për iOS dhe Android — nga NJË SVG, jo me dorë.

🚨 25-09-2026: deri sot app-i i botuar te Play dhe ndërtimi iOS mbanin
logon e RustDesk-ut (unaza blu) — te launcher-i, te ikona e njoftimit dhe te
`assets/icon.svg`. `marka.py` ndërronte tekstin, serverin dhe çelësin, po asnjë
piksel. Apple e sheh si markë të huaj (4.1 / 2.3.8); Shabani e do markën E TËRA
([[marka-nderrohet-plotesisht-pa-perjashtim]]).

Burimi i vetëm: `store/ikona.svg` te depoja Gitea `shaban/spacedesk`
(te Ampere: /mnt/data/workspace/spacedesk/store/ikona.svg). Këtu nuk mbahet
kopje e tij ([[vegla-nje-burim-i-vetem]]); dalja (PNG-të) commit-ohet, sepse
GitHub-i s'e sheh dot Gitea-n.

    python3 spacecode/ikonat.py [shtegu/i/ikona.svg]

Kërkon `rsvg-convert` dhe Pillow (të dyja te hosti).

🚨 Tri kushte që s'duken te pamja, po i bien dyqanit:
  · iOS: ikona pa kanal ALFA — ndryshe ITMS-90717 PAS ngarkimit. Prandaj
    konvertohet në RGB, jo vetëm me sfond të errët.
  · iOS: katror i plotë, pa qoshe të rrumbullakosura — sistemi i rrumbullakos
    vetë; qoshet tona do dilnin si cepa të zinj.
  · Android adaptive: përmbajtja duhet brenda 66/108 të qendrës, ndryshe
    maska e launcher-it ia pret monitorin.
"""
import io, json, os, re, subprocess, sys
from PIL import Image, ImageDraw

RRENJA = os.environ.get("SPACEDESK_RRENJA", os.getcwd())
BURIMI = sys.argv[1] if len(sys.argv) > 1 else "/mnt/data/workspace/spacedesk/store/ikona.svg"
svg = io.open(BURIMI, encoding="utf-8").read()

SFONDI = '<rect width="512" height="512" rx="112" fill="url(#sfondi)"/>'
assert SFONDI in svg, "⛔ s'u gjet sfondi te ikona.svg — ndryshoi burimi?"
KATROR = svg.replace(SFONDI, SFONDI.replace(' rx="112"', ""))
PA_SFOND = svg.replace(SFONDI, "")
NGJYRA_SFONDI = "#0f2c52"  # mesi i gradientit #0b1e3a → #123a6b


def vizato(teksti, madhesia):
    r = subprocess.run(["rsvg-convert", "-w", str(madhesia), "-h", str(madhesia)],
                       input=teksti.encode("utf-8"), stdout=subprocess.PIPE, check=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGBA")


def ruaj(img, shtegu):
    img.save(os.path.join(RRENJA, shtegu), optimize=True)


# ── iOS: çdo skedar që kërkon Contents.json, në madhësinë që thotë ai ──────
IOS = "flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset"
iosi = 0
for im in json.load(io.open(os.path.join(RRENJA, IOS, "Contents.json")))["images"]:
    if "filename" not in im:
        continue
    px = round(float(im["size"].split("x")[0]) * int(im["scale"].rstrip("x")))
    ruaj(vizato(KATROR, px).convert("RGB"), os.path.join(IOS, im["filename"]))
    iosi += 1

# ── Android ────────────────────────────────────────────────────────────────
RES = "flutter/android/app/src/main/res"
DENDESITE = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
permbajtja = vizato(PA_SFOND, 1024)
for d, k in DENDESITE.items():
    dosja = "%s/mipmap-%s" % (RES, d)
    n = round(48 * k)
    ruaj(vizato(svg, n), dosja + "/ic_launcher.png")

    rrethi = vizato(KATROR, n)
    maska = Image.new("L", (n * 4, n * 4), 0)
    ImageDraw.Draw(maska).ellipse((0, 0, n * 4 - 1, n * 4 - 1), fill=255)
    rrethi.putalpha(maska.resize((n, n), Image.LANCZOS))
    ruaj(rrethi, dosja + "/ic_launcher_round.png")

    # adaptive: kanavacë 108dp, përmbajtja në 80% të saj → ~55% e kanavacës
    # (skaji i monitorit), brenda zonës së sigurt 61%.
    f = round(108 * k)
    s = round(f * 0.80)
    kanavaca = Image.new("RGBA", (f, f), (0, 0, 0, 0))
    kanavaca.paste(permbajtja.resize((s, s), Image.LANCZOS), ((f - s) // 2, (f - s) // 2))
    ruaj(kanavaca, dosja + "/ic_launcher_foreground.png")

    # njoftimi: siluetë e bardhë — Android-i e ngjyros vetë, sipas alfës
    m = round(24 * k)
    alfa = permbajtja.resize((m, m), Image.LANCZOS).getchannel("A")
    silueta = Image.new("RGBA", (m, m), (255, 255, 255, 0))
    silueta.putalpha(alfa)
    ruaj(silueta, dosja + "/ic_stat_logo.png")

# Sfondi i ikonës adaptive: ishte i BARDHË, për unazën blu të tyre.
ngjyrat = 0
for emri in os.listdir(os.path.join(RRENJA, RES)):
    if not emri.startswith("values"):
        continue
    for sk in os.listdir(os.path.join(RRENJA, RES, emri)):
        p = os.path.join(RRENJA, RES, emri, sk)
        t = io.open(p, encoding="utf-8").read()
        t2 = re.sub(r'(<color name="ic_launcher_background">)[^<]*(</color>)',
                    r"\g<1>%s\g<2>" % NGJYRA_SFONDI, t)
        if t2 != t:
            io.open(p, "w", encoding="utf-8").write(t2)
        ngjyrat += t2.count('name="ic_launcher_background"')

# Brenda app-it (faqet e desktopit, `loadIcon`): logoja e tyre si SVG.
io.open(os.path.join(RRENJA, "flutter/assets/icon.svg"), "w", encoding="utf-8").write(svg)

# ── Matja, jo besimi ───────────────────────────────────────────────────────
deshtime = []
i1024 = Image.open(os.path.join(RRENJA, IOS, "Icon-App-1024x1024@1x.png"))
if i1024.mode != "RGB" or i1024.size != (1024, 1024):
    deshtime.append("ikona iOS 1024: %s %s (pritej RGB 1024x1024)" % (i1024.mode, i1024.size))
# Ngjyra e qendrës së unazës së RustDesk-ut ishte E BARDHË; e jona është sfond i errët.
if sum(i1024.getpixel((20, 20))) > 200:
    deshtime.append("cepi i ikonës iOS është i çelët — sfondi s'u vizatua?")
if iosi < 10:
    deshtime.append("vetëm %d ikona iOS" % iosi)
if ngjyrat < 1:
    deshtime.append("ic_launcher_background s'u gjet te values*")
if "rustdesk" in io.open(os.path.join(RRENJA, "flutter/assets/icon.svg"), encoding="utf-8").read().lower():
    deshtime.append("assets/icon.svg ende përmend rustdesk")
if deshtime:
    print("⛔ " + "\n⛔ ".join(deshtime))
    sys.exit(1)
print("✅ ikonat: %d iOS (RGB, pa alfa), %d dendësi Android × 4, sfondi %s"
      % (iosi, len(DENDESITE), NGJYRA_SFONDI))
