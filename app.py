from flask import Flask, render_template, request
import sqlite3

from datetime import date

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def pocetna():

    upozorenje = []
    danas = date.today()
    poruka = ""
    servisi = []
    troskovi = []
    vozila = []
    ukupni_troskovi = 0
    conn = sqlite3.connect("evidencija_servisa_vozila.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vozila (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marka_vozila TEXT,
        model_vozila TEXT,
        godiste_vozila INTEGER,
        registarska_oznaka TEXT,
        broj_sasije_vin TEXT,
        trenutna_kilometraza INTEGER
    )
    """)
    conn.close()

    conn = sqlite3.connect("evidencija_servisa_vozila.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servisi(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vozilo_id INTEGER,
        datum_servisa TEXT,
        kilometraza_vozila INTEGER,
        vrsta_servisa TEXT,
        opis_servisa TEXT,
        zamijenjeni_dijelovi TEXT,
        naziv_servisa TEXT,
        cijena_servisa INTEGER,
        dodatna_napomena TEXT
    )
    """)
    conn.close()

    if request.method == "POST":
        akcija = request.form.get("akcija")

        if akcija == "dodaj_vozilo":
            marka_vozila = request.form.get("marka_vozila")
            model_vozila = request.form.get("model_vozila")
            godiste_vozila = request.form.get("godiste")
            registarska_oznaka = request.form.get("registarska_oznaka")
            broj_sasije_vin = request.form.get("broj_sasije_vin")
            trenutna_kilometraza = request.form.get("trenutna_kilometraza")
            
            if not marka_vozila or not model_vozila or not godiste_vozila or not registarska_oznaka or not trenutna_kilometraza:
                poruka = "Popunite sva obavezna polja"

            else:
                try:
                    godiste_vozila = int(godiste_vozila)
                    trenutna_kilometraza = int(trenutna_kilometraza)

                except ValueError:
                    poruka = "Godiste i kilometraza moraju biti brojevi"

                else:
                    if godiste_vozila < 1900:
                        poruka = "Godiste vozila ne moze biti manje od 1900"

                    elif godiste_vozila > danas.year:
                        poruka = "Godiste vozila ne moze biti u buducnosti"

                    elif trenutna_kilometraza < 0:
                        poruka = "Kilometraza ne moze biti negativna"

                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                            INSERT INTO vozila (
                                marka_vozila,
                                model_vozila,
                                godiste_vozila,
                                registarska_oznaka,
                                broj_sasije_vin,
                                trenutna_kilometraza
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            marka_vozila,
                            model_vozila,
                            godiste_vozila,
                            registarska_oznaka,
                            broj_sasije_vin,
                            trenutna_kilometraza
                        ))

                        conn.commit()
                        conn.close()

                        poruka = "Uspjesno dodavanje vozila"
            
        if akcija == "dodaj_servis":
            unesite_id_vozila = request.form.get("unesite_id_vozila")
            datum_servisa = request.form.get("datum_servisa")
            kilometraza_na_kojoj_je_servis_uradjen = request.form.get("kilometraza_na_kojoj_je_servis_uradjen")
            vrsta_servisa = request.form.get("vrsta_servisa")
            opis_sta_je_uradjeno = request.form.get("opis_sta_je_uradjeno")
            koji_dio_dijelovi_su_zamijenjeni = request.form.get("koji_dio_dijelovi_su_zamijenjeni")
            naziv_servisa = request.form.get("naziv_servisa")
            cijena_servisa = request.form.get("cijena_servisa")
            dodatna_napomena = request.form.get("dodatna_napomena")
            
            if not unesite_id_vozila or not datum_servisa or not kilometraza_na_kojoj_je_servis_uradjen or not vrsta_servisa or not opis_sta_je_uradjeno or not naziv_servisa or not cijena_servisa:
                poruka = "Popunite sva obavezna polja"

            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)
                    kilometraza_na_kojoj_je_servis_uradjen = int(kilometraza_na_kojoj_je_servis_uradjen)
                    cijena_servisa = float(cijena_servisa)
                    datum_servisa_date = date.fromisoformat(datum_servisa)
                
                except ValueError:
                    poruka = "ID, kilometraza, cijena ili datum nisu ispravni"                          
                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"

                    elif kilometraza_na_kojoj_je_servis_uradjen < 0:
                        poruka = "Kilometraza ne moze biti negativna"

                    elif cijena_servisa < 0:
                        poruka = "Cijena servisa ne moze biti negativna"
                    
                    elif datum_servisa_date > danas:
                        poruka = "Datum servisa ne moze biti u buducnosti"
                    
                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()

                        if vozilo:

                            cursor.execute("""
                            INSERT INTO servisi (
                                vozilo_id,
                                datum_servisa,
                                kilometraza_vozila,
                                vrsta_servisa,
                                opis_servisa,
                                zamijenjeni_dijelovi,
                                naziv_servisa,
                                cijena_servisa,
                                dodatna_napomena
                                )
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                unesite_id_vozila,
                                datum_servisa,
                                kilometraza_na_kojoj_je_servis_uradjen,
                                vrsta_servisa,
                                opis_sta_je_uradjeno,
                                koji_dio_dijelovi_su_zamijenjeni,
                                naziv_servisa,
                                cijena_servisa,
                                dodatna_napomena
                            ))
                            poruka = "Servis je uspjesno dodat"

                            conn.commit()
                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"
                                    
                        conn.close()

        if akcija == "prikazati_servise":
            unesite_id_vozila = request.form.get("unesite_id_vozila")
            
            if not unesite_id_vozila:
                poruka = "Unesite ID vozila"
            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)

                except ValueError:
                    poruka = "ID vozila mora biti broj"

                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"
                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()

                        if vozilo:
                            cursor.execute("""
                            SELECT servisi.*, vozila.marka_vozila, vozila.model_vozila
                            FROM servisi
                            JOIN vozila ON servisi.vozilo_id = vozila.id
                            WHERE servisi.vozilo_id = ?
                            """, (unesite_id_vozila,))

                            servisi = cursor.fetchall()

                            if servisi == []:
                                poruka = "Nema evidentiranih servisa za ovo vozilo"
                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"
                        conn.close()

        conn = sqlite3.connect("evidencija_servisa_vozila.db")
        cursor = conn.cursor()
        cursor.execute (""" 
        CREATE TABLE IF NOT EXISTS sljedeci_servis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vozilo_id INTEGER,
            sljedeci_datum TEXT,
            sljedeca_kilometraza INTEGER
        )
        """)
        conn.close()

        if akcija == "sacuvaj_sljedeci_servis":

            unesite_id_vozila = request.form.get("unesite_id_vozila")
            sljedeci_datum = request.form.get("sljedeci_datum")
            sljedeca_kilometraza = request.form.get("sljedeca_kilometraza")

            if not unesite_id_vozila or not sljedeci_datum or not sljedeca_kilometraza:
                poruka = "Popunite sva obavezna polja"

            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)
                    sljedeca_kilometraza = int(sljedeca_kilometraza)
                    sljedeci_datum_date = date.fromisoformat(sljedeci_datum)
                
                except ValueError:
                    poruka = "ID, kilometraza ili datum nisu ispravni"            
                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"

                    elif sljedeca_kilometraza < 0:
                        poruka = "Sljedeca kilometraza ne moze biti negativna"

                    elif sljedeci_datum_date < danas:
                        poruka = "Datum sljedeceg servisa ne moze biti u proslosti"

                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()

                        if vozilo:

                            cursor.execute("""
                            SELECT * FROM sljedeci_servis
                            WHERE vozilo_id = ?
                            """, (unesite_id_vozila,))

                            postojeci_servis = cursor.fetchone()

                            if postojeci_servis:
                                cursor.execute("""
                                UPDATE sljedeci_servis
                                SET sljedeci_datum = ?,
                                    sljedeca_kilometraza = ?
                                WHERE vozilo_id = ?
                                """, (
                                    sljedeci_datum,
                                    sljedeca_kilometraza,
                                    unesite_id_vozila
                                ))

                                poruka = "Sljedeći servis je uspješno izmijenjen"

                            else:
                                cursor.execute("""
                                INSERT INTO sljedeci_servis (
                                    vozilo_id,
                                    sljedeci_datum,
                                    sljedeca_kilometraza
                                )
                                VALUES (?, ?, ?)
                                """, (
                                    unesite_id_vozila,
                                    sljedeci_datum,
                                    sljedeca_kilometraza
                                ))

                                poruka = "Sljedeći servis je uspješno sačuvan"

                            conn.commit()
                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"

                        conn.close()

        conn = sqlite3.connect("evidencija_servisa_vozila.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT sljedeci_servis.*, vozila.marka_vozila, vozila.trenutna_kilometraza
        FROM sljedeci_servis
        JOIN vozila ON sljedeci_servis.vozilo_id = vozila.id
        """)
        sljedeci_servisi = cursor.fetchall()

        for sljedeci_servis in sljedeci_servisi:
            sljedeci_datum = sljedeci_servis[2]
            sljedeci_datum_date = date.fromisoformat(sljedeci_datum)
            preostalo_dana = (sljedeci_datum_date - danas).days

            if sljedeci_datum_date < danas:
                upozorenje.append(
                    f"{sljedeci_servis[4]} (ID {sljedeci_servis[1]}): servis je istekao"
                )

            elif sljedeci_datum_date == danas:
                upozorenje.append(
                    f"{sljedeci_servis[4]} (ID {sljedeci_servis[1]}): servis je danas"
                )

            elif preostalo_dana <= 7:
                upozorenje.append(
                    f"{sljedeci_servis[4]} (ID {sljedeci_servis[1]}): servis {sljedeci_servis[2]} je za {preostalo_dana} dana"
                )

            sljedeca_kilometraza = sljedeci_servis[3]
            trenutna_kilometraza = sljedeci_servis[5]

            preostalo_km = sljedeca_kilometraza - trenutna_kilometraza

            if preostalo_km < 0:
                upozorenje.append(
                    f"{sljedeci_servis[4]} (ID {sljedeci_servis[1]}): servis je prekoračen za {abs(preostalo_km)} km"
                )

            elif preostalo_km <= 500:
                upozorenje.append(
                    f"{sljedeci_servis[4]} (ID {sljedeci_servis[1]}): do sljedećeg servisa preostalo je {preostalo_km} km"
                )
        conn.close() 

        conn = sqlite3.connect("evidencija_servisa_vozila.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS troskovi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vozilo_id INTEGER,
            vrsta_usluge TEXT,
            cijena_dijelova REAL,
            cijena_rada REAL,
            ukupna_cijena REAL
        )
        """)

        conn.commit()
        conn.close()

        if akcija == "sacuvaj_troskove":
            unesite_id_vozila = request.form.get("unesite_id_vozila")
            vrsta_usluge = request.form.get("vrsta_usluge")
            cijena_dijelova = request.form.get("cijena_dijelova")
            cijena_rada = request.form.get("cijena_rada")

            if not unesite_id_vozila or not vrsta_usluge or not cijena_dijelova or not cijena_rada:
                poruka = "Popunite sva obavezna polja"

            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)
                    cijena_dijelova = float(cijena_dijelova)
                    cijena_rada = float(cijena_rada)

                except ValueError:
                    poruka = "ID vozila i cijene moraju biti brojevi"

                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"

                    elif cijena_dijelova < 0:
                        poruka = "Cijena dijelova ne moze biti negativna"

                    elif cijena_rada < 0:
                        poruka = "Cijena rada ne moze biti negativna"

                    
                    else:
                        ukupna_cijena = cijena_dijelova + cijena_rada

                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()

                        if vozilo:

                            cursor.execute("""
                            INSERT INTO troskovi (
                                vozilo_id,
                                vrsta_usluge,
                                cijena_dijelova,
                                cijena_rada,
                                ukupna_cijena
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """, (
                                unesite_id_vozila,
                                vrsta_usluge,
                                cijena_dijelova,
                                cijena_rada,
                                ukupna_cijena
                            ))
                            conn.commit()
                            poruka = "Trosak uspjesno sacuvan"

                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"

                        conn.close()

        if akcija == "prikazi_troskove":
            unesite_id_vozila = request.form.get("unesite_id_vozila")

            if not unesite_id_vozila:
                poruka = "Unesite ID vozila"

            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)

                except ValueError:
                    poruka = "ID vozila mora biti broj"

                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"
                
                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()
                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()

                        if vozilo:
                            cursor.execute("""
                            SELECT * FROM troskovi
                            WHERE vozilo_id = ?
                            """, (unesite_id_vozila,))

                            troskovi = cursor.fetchall()
                            if not troskovi:
                                poruka = "Nema evidentiranih troskova za ovo vozilo"
                            
                            for trosak in troskovi:
                                ukupni_troskovi = ukupni_troskovi + trosak[5]
                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"
                        conn.close()

        if akcija == "pretrazi_vozila":
            unesite_marku_vozila = request.form.get("unesite_marku_vozila")
            
            if not unesite_marku_vozila:
                poruka = "Unesite marku vozila"

            else:
                conn = sqlite3.connect("evidencija_servisa_vozila.db")
                cursor = conn.cursor()
                cursor.execute("""
                SELECT * FROM vozila
                WHERE marka_vozila = ?
                """, (unesite_marku_vozila,))

                vozila = cursor.fetchall()

                if vozila == []:
                    poruka = "Vozilo nije pronadjeno"
                conn.close()

        if akcija == "prikazi_sva_vozila":
            conn = sqlite3.connect("evidencija_servisa_vozila.db")
            cursor = conn.cursor()

            cursor.execute("""
            SELECT * FROM vozila
            """)
            vozila = cursor.fetchall()
            conn.close()

        if akcija == "sacuvaj_izmjene":
            unesite_id_vozila = request.form.get("unesite_id_vozila")
            nova_marka_vozila = request.form.get("nova_marka_vozila")
            novi_model_vozila = request.form.get("novi_model_vozila")
            novo_godiste = request.form.get("novo_godiste")
            nova_registarska_oznaka = request.form.get("nova_registarska_oznaka")
            novi_broj_sasije_vin = request.form.get("novi_broj_sasije_vin")
            nova_kilometraza = request.form.get("nova_kilometraza")

            if not unesite_id_vozila or not nova_marka_vozila or not novi_model_vozila or not novo_godiste or not nova_registarska_oznaka or not nova_kilometraza:
                poruka = "Popunite sva obavezna polja"

            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)
                    novo_godiste = int(novo_godiste)
                    nova_kilometraza = int(nova_kilometraza)

                except ValueError:
                    poruka = "ID, godiste i kilometraza moraju biti brojevi"

                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"

                    elif novo_godiste < 1900:
                        poruka = "Godiste vozila ne moze biti manje od 1900"

                    elif novo_godiste > danas.year:
                        poruka = "Godiste vozila ne moze biti u buducnosti"

                    elif nova_kilometraza < 0:
                        poruka = "Kilometraza ne moze biti negativna"

                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()
                    
                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()
                        
                        if vozilo:
                            cursor.execute("""
                            UPDATE vozila
                            SET marka_vozila = ?,
                                model_vozila = ?,
                                godiste_vozila = ?,
                                registarska_oznaka = ?,
                                broj_sasije_vin = ?,
                                trenutna_kilometraza = ?
                            WHERE id = ?
                            """, (nova_marka_vozila,
                                novi_model_vozila,
                                novo_godiste,
                                nova_registarska_oznaka,
                                novi_broj_sasije_vin,
                                nova_kilometraza,
                                unesite_id_vozila 
                            ))

                            conn.commit()
                            poruka = "Podaci o vozilu uspjesno izmijenjeni"
                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"
                        conn.close()
                                    
        
        if akcija == "obrisi_vozilo":
            unesite_id_vozila = request.form.get("unesite_id_vozila")

            if not unesite_id_vozila:
                poruka = "Unesite ID vozila"

            else:
                try:
                    unesite_id_vozila = int(unesite_id_vozila)

                except ValueError:
                    poruka = "ID vozila mora biti broj"
                 
                else:
                    if unesite_id_vozila < 1:
                        poruka = "ID vozila mora biti veci od 0"
                
                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM vozila
                        WHERE id = ?
                        """, (unesite_id_vozila,))

                        vozilo = cursor.fetchone()

                        if vozilo:
                            cursor.execute("""
                            DELETE FROM servisi
                            WHERE vozilo_id = ?
                            """, (unesite_id_vozila,))

                            cursor.execute("""
                            DELETE FROM troskovi
                            WHERE vozilo_id = ?
                            """, (unesite_id_vozila,))

                            cursor.execute("""
                            DELETE FROM sljedeci_servis
                            WHERE vozilo_id = ?
                            """, (unesite_id_vozila,))

                            cursor.execute("""
                            DELETE FROM vozila
                            WHERE id = ?
                            """, (unesite_id_vozila,))

                            conn.commit()
                            poruka = "Vozilo uspjesno obrisano"
                        else:
                            poruka = "Vozilo sa unesenim ID-em ne postoji"

                        conn.close()
        
        if akcija == "izmijeni_servis":
            id_servisa_izmjena = request.form.get("id_servisa_izmjena")
            novi_datum_servisa = request.form.get("novi_datum_servisa")
            nova_kilometraza_servisa = request.form.get("nova_kilometraza_servisa")
            nova_vrsta_servisa = request.form.get("nova_vrsta_servisa")
            novi_opis_servisa = request.form.get("novi_opis_servisa")
            novi_zamijenjeni_dijelovi = request.form.get("novi_zamijenjeni_dijelovi")
            novi_naziv_servisa = request.form.get("novi_naziv_servisa")
            nova_cijena_servisa = request.form.get("nova_cijena_servisa")
            nova_dodatna_napomena = request.form.get("nova_dodatna_napomena")

            if not id_servisa_izmjena or not novi_datum_servisa or not nova_kilometraza_servisa or not nova_vrsta_servisa or not novi_opis_servisa or not novi_naziv_servisa or not nova_cijena_servisa:
                poruka = "Popunite sva obavezna polja"

            else:
                try:
                    id_servisa_izmjena = int(id_servisa_izmjena)
                    nova_kilometraza_servisa = int(nova_kilometraza_servisa)
                    nova_cijena_servisa = float(nova_cijena_servisa)
                    novi_datum_servisa_date = date.fromisoformat(novi_datum_servisa)

                except ValueError:
                    poruka = "ID, kilometraza, cijena ili datum nisu ispravni"

                else:
                    if id_servisa_izmjena < 1:
                        poruka = "ID servisa mora biti veci od 0"

                    elif nova_kilometraza_servisa < 0:
                        poruka = "Kilometraza ne moze biti negativna"

                    elif nova_cijena_servisa < 0:
                        poruka = "Cijena servisa ne moze biti negativna"
                    elif novi_datum_servisa_date > danas:
                        poruka = "Datum servisa ne moze biti u buducnosti"
                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM servisi
                        WHERE id = ?
                        """, (id_servisa_izmjena,))

                        servis = cursor.fetchone()

                        if servis:
                            cursor.execute("""
                                UPDATE servisi
                                SET datum_servisa = ?,
                                    kilometraza_vozila = ?,
                                    vrsta_servisa = ?,
                                    opis_servisa = ?,
                                    zamijenjeni_dijelovi = ?,
                                    naziv_servisa = ?,
                                    cijena_servisa = ?,
                                    dodatna_napomena = ?
                                WHERE id = ?
                                """, (
                                    novi_datum_servisa,
                                    nova_kilometraza_servisa,
                                    nova_vrsta_servisa,
                                    novi_opis_servisa,
                                    novi_zamijenjeni_dijelovi,
                                    novi_naziv_servisa,
                                    nova_cijena_servisa,
                                    nova_dodatna_napomena,
                                    id_servisa_izmjena
                                ))
                            conn.commit()
                            poruka = "Servisni zapis uspjesno izmijenjen"      
                        else:
                            poruka = "Servisni zapis sa unesenim ID-em ne postoji"

                        conn.close()
        
        if akcija == "obrisi_servis":
            id_servisa = request.form.get("id_servisa")

            if not id_servisa:
                poruka = "Unesite ID servisa"

            else:
                try:
                    id_servisa = int(id_servisa)

                except ValueError:
                    poruka = "ID servisa mora biti broj"
               
                else:
                    if id_servisa < 1:
                        poruka = "ID servisa mora biti veci od 0"
                
                    else:
                        conn = sqlite3.connect("evidencija_servisa_vozila.db")
                        cursor = conn.cursor()

                        cursor.execute("""
                        SELECT * FROM servisi
                        WHERE id = ?
                        """, (id_servisa,))
                        servis = cursor.fetchone()
                            
                        if servis: 
                            cursor.execute("""
                            DELETE FROM servisi
                            WHERE id = ?
                            """, (id_servisa,))

                            conn.commit()
                            poruka = "Servisni zapis uspjesno obrisan"
                        else:
                            poruka = "Servisni zapis sa unesenim ID-em ne postoji"

                        conn.close()

        if akcija != "pretrazi_vozila" and akcija != "prikazi_sva_vozila":
            conn = sqlite3.connect("evidencija_servisa_vozila.db")
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM vozila
            """) 
            vozila = cursor.fetchall()
            conn.close()

    return render_template(
        "index.html", 
        poruka=poruka, 
        vozila=vozila, 
        servisi=servisi, 
        upozorenje=upozorenje,
        troskovi=troskovi,
        ukupni_troskovi=ukupni_troskovi
        )

if __name__ == "__main__":
     app.run(debug=True)