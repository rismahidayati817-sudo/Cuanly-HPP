
import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cuanly HPP",
    page_icon="💸",
    layout="wide"
)

BIRU = "#417bb8"
BIRU_TUA = "#2563eb"


def rupiah(nilai):
    return "Rp " + f"{nilai:,.0f}".replace(",", ".")


# COVER WEBSITE
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, {BIRU}, {BIRU_TUA});
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;">
        <h4 style="color:white;text-align:left;">
            💸 CUANLY HPP
        </h4>
        <h1 style="color:white;">
            Biar jualan bukan cuma rame, tapi cuan.
        </h1>
        <p>
            Hitung modal produksi, HPP, harga jual,
            keuntungan, dan titik impas dengan mudah.
        </p>
        <b>KALKULATOR HPP & BEP UMKM</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("🧮 Kalkulator Modal Produksi")

st.write(
    "Masukkan total biaya satu kali produksi dan "
    "jumlah produk yang berhasil dibuat."
)

with st.expander("💡 Petunjuk pengisian", expanded=True):
    st.markdown("""
    - **Total modal:** seluruh biaya untuk satu batch produksi.
    - **Biaya tetap:** bagian biaya tetap yang sudah termasuk
      dalam total modal, misalnya alokasi sewa atau penyusutan alat.
    - **Jumlah produk:** jumlah produk jadi yang layak dijual.
    - **Margin:** target laba sebagai persentase dari harga jual.
    - Biaya tetap jangan ditambahkan lagi ke total modal.
    """)

kolom1, kolom2 = st.columns(2)

with kolom1:
    total_modal = st.number_input(
        "Total modal satu batch (Rp)",
        min_value=0,
        value=600000,
        step=10000
    )

    biaya_tetap = st.number_input(
        "Biaya tetap yang termasuk dalam modal (Rp)",
        min_value=0,
        value=200000,
        step=10000
    )

with kolom2:
    jumlah_produk = st.number_input(
        "Jumlah produk jadi (pcs/cup)",
        min_value=1,
        value=50,
        step=1
    )

    margin_persen = st.slider(
        "Target margin keuntungan (%)",
        min_value=5,
        max_value=60,
        value=20,
        step=5
    )

if biaya_tetap > total_modal:
    st.error("Biaya tetap tidak boleh melebihi total modal.")

else:
    if st.button(
        "🚀 Hitung Hasil Produksi",
        type="primary",
        use_container_width=True
    ):
        # PERHITUNGAN HPP
        hpp = total_modal / jumlah_produk

        # Pisahkan biaya tetap dan variabel
        biaya_variabel_total = total_modal - biaya_tetap
        biaya_variabel_unit = (
            biaya_variabel_total / jumlah_produk
        )

        # Harga jual berdasarkan target margin
        margin = margin_persen / 100
        harga_dasar = hpp / (1 - margin)

        # Pembulatan harga ke atas kelipatan Rp500
        harga_jual = math.ceil(harga_dasar / 500) * 500

        laba_unit = harga_jual - hpp
        omzet = harga_jual * jumlah_produk
        laba_total = omzet - total_modal

        # PERHITUNGAN BEP
        kontribusi = harga_jual - biaya_variabel_unit

        if biaya_tetap == 0:
            bep = 0
        elif kontribusi > 0:
            bep = math.ceil(biaya_tetap / kontribusi)
        else:
            bep = None

        st.divider()

        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,{BIRU},{BIRU_TUA});
                color:white;
                text-align:center;
                padding:22px;
                border-radius:15px;">
                <p style="color:white;">TOTAL MODAL PRODUKSI</p>
                <h1 style="color:white;">{rupiah(total_modal)}</h1>
                <p style="color:white;">
                    Untuk {jumlah_produk} produk
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📊 Hasil Perhitungan")

        a, b, c = st.columns(3)
        a.metric("HPP per produk", rupiah(hpp))
        b.metric("Saran harga jual", rupiah(harga_jual))
        c.metric("Laba per produk", rupiah(laba_unit))

        d, e, f = st.columns(3)

        d.metric(
            "BEP estimasi",
            "Tidak tersedia" if bep is None
            else f"{bep} produk"
        )
        e.metric("Estimasi omzet", rupiah(omzet))
        f.metric("Estimasi laba total", rupiah(laba_total))

        st.caption(
            "Harga jual dibulatkan ke atas ke kelipatan Rp500."
        )

        if bep == 0:
            st.info(
                "Biaya tetap Rp0. Berdasarkan biaya tetap, "
                "tidak ada biaya tetap yang perlu ditutup."
            )
        elif bep is not None:
            st.success(
                f"Titik impas diperkirakan tercapai saat "
                f"{bep} produk terjual."
            )
            st.write(
                "Nilai penjualan pada titik tersebut: "
                f"**{rupiah(bep * harga_jual)}**"
            )
        else:
            st.warning("BEP tidak dapat dihitung dari input ini.")

        # GRAFIK KOMPOSISI MODAL
        st.subheader("📊 Komposisi Modal Produksi")

        grafik_biaya = pd.DataFrame({
            "Jenis biaya": ["Biaya variabel", "Biaya tetap"],
            "Total biaya (Rp)": [
                biaya_variabel_total,
                biaya_tetap
            ]
        }).set_index("Jenis biaya")

        st.bar_chart(grafik_biaya)

        # GRAFIK PENDAPATAN DAN BIAYA
        st.subheader("📈 Pendapatan dan Total Biaya")

        batas = max(int(jumlah_produk), int(bep or 0), 10)
        batas = math.ceil(batas * 1.2)
        langkah = max(1, batas // 40)

        kuantitas = list(range(0, batas + 1, langkah))
        if kuantitas[-1] != batas:
            kuantitas.append(batas)

        grafik_bep = pd.DataFrame({
            "Jumlah produk terjual": kuantitas,
            "Pendapatan": [
                q * harga_jual for q in kuantitas
            ],
            "Total biaya": [
                biaya_tetap + q * biaya_variabel_unit
                for q in kuantitas
            ]
        }).set_index("Jumlah produk terjual")

        st.line_chart(grafik_bep)

        st.caption(
            "Catatan: hasil merupakan estimasi berdasarkan data "
            "yang dimasukkan. Ketepatan BEP bergantung pada "
            "pemisahan biaya tetap dan variabel yang benar."
        )

st.divider()
st.caption("Cuanly HPP | Biar jualan bukan cuma rame, tapi cuan.")
