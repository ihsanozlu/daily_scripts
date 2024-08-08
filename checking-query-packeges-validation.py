import requests
import xml.etree.ElementTree as ET

xml_string = '''
  <queries xmlns:android="http://schemas.android.com/apk/res/android">
     <package android:name="org.findmykids.app"/>
    <package android:name="tr.gov.eba.hesap"/>
    <package android:name="com.meb.vbsmobil"/>
    <package android:name="com.kidslox.app"/>
    <package android:name="com.google.android.apps.kids.familylink"/>
    <package android:name="kz.sirius.kidssecurity"/>
    <package android:name="com.sand.airdroidkidp"/>
    <package android:name="com.qustodio.qustodioapp"/>
    <package android:name="relax.sleep.relaxation.sleepingsounds"/>
    <package android:name="com.kidokit.kidokitapp"/>
    <package android:name="com.xogrp.thebump"/>
    <package android:name="com.ovuline.pregnancy"/>
    <package android:name="com.dreamstudio.babysleepsounds"/>
    <package android:name="com.premiumsoftware.gotosleepbaby"/>
    <package android:name="com.babycenter.pregnancytracker"/>
    <package android:name="com.easymobs.pregnancy"/>
    <package android:name="com.wte.view"/>
    <package android:name="com.grupanya.android"/>
    <package android:name="com.cimrimobilevoyager"/>
    <package android:name="com.akakce.akakce"/>
    <package android:name="com.fbf.firsatbufirsat"/>
    <package android:name="net.btpro.client.koctas"/>
    <package android:name="tr.com.tekzen.android"/>
    <package android:name="com.ingka.ikea.app"/>
    <package android:name="com.inditex.ecommerce.zarahome.android"/>
    <package android:name="tr.com.englishhome"/>
    <package android:name="com.evidea.android"/>
    <package android:name="com.yemeksepeti.yemekcom"/>
    <package android:name="com.nytimes.cooking"/>
    <package android:name="com.nefisyemektarifleri.android"/>
    <package android:name="com.strava"/>
    <package android:name="com.runtastic.android"/>
    <package android:name="com.fitnesskeeper.runkeeper.pro"/>
    <package android:name="com.mapmyrun.android2"/>
    <package android:name="com.nike.plusgps"/>
    <package android:name="com.doggoapp.owner"/>
    <package android:name="com.doggoapp.walker"/>
    <package android:name="com.mytoursapp.android.app3427"/>
    <package android:name="tr.gov.ibb.semtpati"/>
    <package android:name="com.tsoft.kolaymama"/>
    <package android:name="com.fiton.android"/>
    <package android:name="pilatesworkouts.loseweight.dailyyoga"/>
    <package android:name="com.fourtechnologies.mynetdiary.ad"/>
    <package android:name="loseweight.weightloss.workout.fitness"/>
    <package android:name="bodyfast.zero.fastingtracker.weightloss"/>
    <package android:name="com.myfitnesspal.android"/>
    <package android:name="com.fatsecret.android"/>
    <package android:name="com.inomera.sm"/>
    <package android:name="com.carrefoursa.ecommerce"/>
    <package android:name="com.file.filemarket"/>
    <package android:name="com.positive.ceptesok"/>
    <package android:name="trendyol.com"/>
    <package android:name="com.getir"/>
    <package android:name="com.pozitron.hepsiburada"/>
    <package android:name="com.alibaba.aliexpresshd"/>
    <package android:name="com.amazon.mShop.android.shopping"/>
    <package android:name="com.offerup"/>
    <package android:name="com.dmall.mfandroid"/>
    <package android:name="com.ebay.mobile"/>
    <package android:name="com.inovel.app.yemeksepeti"/>
    <package android:name="com.mcdonalds.mobileapp"/>
    <package android:name="tr.com.dominos"/>
    <package android:name="com.kfcturkiye.app"/>
    <package android:name="com.ataexpress.tiklagelsin"/>
    <package android:name="com.gratis.android"/>
    <package android:name="de.rossmann.app.android"/>
    <package android:name="com.mobular.watsons"/>
    <package android:name="com.inditex.ecommerce.bershka"/>
    <package android:name="com.inditex.zara"/>
    <package android:name="com.hm.goe"/>
    <package android:name="com.dylvian.mango.activities"/>
    <package android:name="com.inditex.massimodutti"/>
    <package android:name="com.inditex.pullandbear"/>
    <package android:name="com.inditex.stradivarius"/>
    <package android:name="com.inditex.oysho"/>
    <package android:name="com.ipekyol"/>
    <package android:name="com.vakko.android"/>
    <package android:name="com.sephora"/>
    <package android:name="com.mtelnet.watson.ph"/>
    <package android:name="com.cosmetica.app"/>
    <package android:name="com.ecosia.android"/>
    <package android:name="com.sst.panda"/>
    <package android:name="com.earthheroorg.earthhero"/>
    <package android:name="com.cleanbit.joulebug"/>
    <package android:name="com.readabl.paperkarma"/>
    <package android:name="au.org.goodonyou.goodonyou"/>
    <package android:name="com.khcreations.nowaste"/>
    <package android:name="com.ifpen.gecoair"/>
    <package android:name="app.ecohero"/>
    <package android:name="com.tfkb"/>
    <package android:name="com.ingbanktr.ingmobil"/>
    <package android:name="com.vakifbank.mobile"/>
    <package android:name="com.tmobtech.halkbank"/>
    <package android:name="com.kuveytturk.mobil"/>
    <package android:name="com.teb"/>
    <package android:name="com.finansbank.mobile.cepsube"/>
    <package android:name="com.denizbank.mobildeniz"/>
    <package android:name="com.amazon.avod.thirdpartyclient"/>
    <package android:name="com.netflix.mediaclient"/>
    <package android:name="com.disney.disneyplus"/>
</queries>
'''

root = ET.fromstring(xml_string)
package_counts = {}

print("List Size: ",len(root.findall('package')))
for package in root.findall('package'):
    package_name = package.attrib['{http://schemas.android.com/apk/res/android}name']
    try:
        response = requests.get(f"https://play.google.com/store/apps/details?id={package_name}")
        if package_name in package_counts:
            package_counts[package_name] += 1
        else:
            package_counts[package_name] = 1

        if response.status_code != 200:
            print(f"{package_name}: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"{package_name}: Hata - {e}")

print("Duplicated")
for package_name, count in package_counts.items():
    if count > 1:
        print(f"{package_name} count is: {count}")
