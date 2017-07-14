# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from ulakbus.models import KurumIciGorevlendirmeBilgileri, KurumDisiGorevlendirmeBilgileri
from ulakbus.models import HizmetKayitlari
from zengine.lib.test_utils import BaseTestCase
from dateutil.relativedelta import relativedelta
import datetime
from ulakbus.lib.role import AbsRole
import time

__author__ = 'Mithat Raşit Özçıkrıkcı'


class TestCase(BaseTestCase):
    """
        Personel görevlendirme işlemine görevlendirme türü seçilerek başlanır.
        Görevlendirme Türleri:
        1- Kurum içi görevlendirme
        2- Kurum dışı görevlendirme
        Seçilen görevlendirme türüne göre görüntülenen formda gereken
        bilgiler girilir ve kaydedilir.
    """

    def test_kurum_ici_gorevlendirme_standart(self):
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user=user)
        personel_id = "ShW15GBQCCUAuk64ZrK9myA470y"

        # Görevlendirilecek birim
        birim_id = "PNrGNyS35dmw9WHKPyl9Er0CiWN"
        # birim = Unit.objects.get(birim_id)

        # Görevlendirilecek personel veritabanından çekilir.
        # personel = Personel.objects.get(personel_id)

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id, model="Personel", param="personel_id", wf="gorevlendirme")

        # Veritabanındaki görevlendirme bilgileri test
        # sonunda kontrol edebilmek amacıyla silinir.
        KurumIciGorevlendirmeBilgileri.objects.delete()
        KurumDisiGorevlendirmeBilgileri.objects.delete()

        self.client.post(cmd='tur_sec', wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme",
                         form=dict(gorevlendirme_tur=2))

        # Görevlendirmesi yapılacak soyut rol
        soyut_rol_id = AbsRole.DAIRE_PERSONELI.name
        # soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet",
                         wf="gorevlendirme",
                         form=dict(baslama_tarihi=baslangic.strftime("%d.%m.%Y"),
                                   bitis_tarihi=bitis.strftime("%d.%m.%Y"),
                                   birim_id=birim_id,
                                   soyut_rol_id=soyut_rol_id,
                                   aciklama="Test Öğrenci İşleri Daire Başkanlığı Görevlendirme",
                                   resmi_yazi_sayi="123123",
                                   resmi_yazi_tarih=resmi_yazi_tarih.strftime("%d.%m.%Y")))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        gorevlendirme = KurumIciGorevlendirmeBilgileri.objects.all()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.baslama_tarihi == baslangic

        assert gorevlendirme.bitis_tarihi == bitis

        assert gorevlendirme.birim.key == birim_id

    def test_kurum_ici_gorevlendirme_dekan(self):
        """
            Bir personelin kurum içerisinde herhangi bir fakülteye dekan olarak
            görevlendirilmesi durumunu içeren test metodudur.
            Standart görevlendirmeden farkı, görevlendirmenin hizmet cetvelini etkiliyor olmasıdır.
        """

        # Dekan Soyut Rol
        soyut_rol_id = AbsRole.FAKULTE_DEKANI.name
        # soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirme yapılacak personel
        personel_id = "OFrnc32AYZou8KcZjKFZGD7gOj3"
        # personel = Personel.objects.get(personel_id)

        # Görevlendirilecek birim
        birim_id = "ZDfRAEBXkRwVd5g8FpTYNsfhqgR"
        # birim = Unit.objects.get(birim_id)

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        # Veritabanındaki görevlendirme bilgileri test sonunda kontrol edebilmek amacıyla silinir.
        KurumIciGorevlendirmeBilgileri.objects.delete()
        KurumDisiGorevlendirmeBilgileri.objects.delete()

        # Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user=user)

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id, model="Personel", param="personel_id", wf="gorevlendirme")

        self.client.post(cmd='tur_sec', wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme",
                         form=dict(gorevlendirme_tur=2))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            baslama_tarihi=baslangic.strftime("%d.%m.%Y"),
            bitis_tarihi=bitis.strftime("%d.%m.%Y"),
            birim_id=birim_id,
            soyut_rol_id=soyut_rol_id,
            aciklama="Dekan olarak görevlendirme",
            resmi_yazi_sayi="123123",
            resmi_yazi_tarih=resmi_yazi_tarih.strftime("%d.%m.%Y")
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        gorevlendirme = KurumIciGorevlendirmeBilgileri.objects.all()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.baslama_tarihi == baslangic

        assert gorevlendirme.bitis_tarihi == bitis

        assert gorevlendirme.birim.key == birim_id

        self.client.post(cmd="hizmet_cetveli_giris", wf="gorevlendirme", form=dict(
            baslama_tarihi="23.03.2017",
            bitis_tarihi="28.09.2017"
        ))

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.count() > 0

    def test_kurum_disi_gorevlendirme_rektor(self):
        """
            Bir personelin kurum dışına rektör olarak görevlendirilmesi durumudur.
        """

        # Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user=user)

        # Rektör Soyut Rol
        soyut_rol_id = AbsRole.REKTOR.name
        # soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirilecek personel
        personel_id = "XFLlsTdqyOV07kgQCbJiIGIvC0v"
        # personel = Personel.objects.get(personel_id)

        # Kurum dışı görevlendirme bilgilerinin test sonunda kontrol
        # edilebilmesi için önceki kayıtlar siliniyor
        KurumDisiGorevlendirmeBilgileri.objects.delete()
        KurumIciGorevlendirmeBilgileri.objects.delete()

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        time.sleep(1)

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id, model="Personel", param="personel_id", wf="gorevlendirme")

        self.client.post(cmd='tur_sec', wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme",
                         form=dict(gorevlendirme_tur=1))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            baslama_tarihi=baslangic.strftime("%d.%m.%Y"),
            bitis_tarihi=bitis.strftime("%d.%m.%Y"),
            aciklama="Rektör kurum dışı görevlendirme",
            resmi_yazi_sayi="234234",
            resmi_yazi_tarih=resmi_yazi_tarih.strftime("%d.%m.%Y"),
            maas=False,
            yevmiye=False,
            yolluk=True,
            ulke=90,
            soyut_rol_id=soyut_rol_id
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        assert KurumDisiGorevlendirmeBilgileri.objects.count() > 0
        gorevlendirme = KurumDisiGorevlendirmeBilgileri.objects.all()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.baslama_tarihi == baslangic

        assert gorevlendirme.bitis_tarihi == bitis

        self.client.post(cmd="hizmet_cetveli_giris", wf="gorevlendirme", form=dict(
            baslama_tarihi="23.03.2017",
            bitis_tarihi="28.09.2017"
        ))

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.count() > 0

    def test_kurum_disi_gorevlendirme_dekan(self):
        """
            Bir personelin kurum dışına dekan olarak görevlendirilmesi durumudur.
        """

        # Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user=user)

        # Dekan Soyut Rol
        soyut_rol_id = AbsRole.FAKULTE_DEKANI.name
        # soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirilecek personel
        personel_id = "XFLlsTdqyOV07kgQCbJiIGIvC0v"
        # personel = Personel.objects.get(personel_id)

        # Kurum dışı görevlendirme bilgilerinin test sonunda
        # kontrol edilebilmesi için önceki kayıtlar siliniyor
        KurumDisiGorevlendirmeBilgileri.objects.delete()
        KurumIciGorevlendirmeBilgileri.objects.delete()

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        time.sleep(1)

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id, model="Personel", param="personel_id", wf="gorevlendirme")

        self.client.post(cmd='tur_sec', wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme",
                         form=dict(gorevlendirme_tur=1))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            baslama_tarihi=baslangic.strftime("%d.%m.%Y"),
            bitis_tarihi=bitis.strftime("%d.%m.%Y"),
            aciklama="Rektör kurum dışı görevlendirme",
            resmi_yazi_sayi="234234",
            resmi_yazi_tarih=resmi_yazi_tarih.strftime("%d.%m.%Y"),
            maas=False,
            yevmiye=False,
            yolluk=True,
            ulke=90,
            soyut_rol_id=soyut_rol_id
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        assert KurumDisiGorevlendirmeBilgileri.objects.count() > 0
        gorevlendirme = KurumDisiGorevlendirmeBilgileri.objects.all()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.baslama_tarihi == baslangic

        assert gorevlendirme.bitis_tarihi == bitis

        self.client.post(cmd="hizmet_cetveli_giris", wf="gorevlendirme", form=dict(
            baslama_tarihi="23.03.2017",
            bitis_tarihi="28.09.2017"
        ))

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.count() > 0
