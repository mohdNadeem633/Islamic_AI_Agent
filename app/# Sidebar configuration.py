# Sidebar configuration
st.sidebar.header("⚙️ Settings")

col1, col2 = st.sidebar.columns(2)

with col1:
    surah_number = st.selectbox(
        "Surah Number",
        options=list(surah_info.keys()),
        format_func=lambda x: f"{x}. {surah_info[x]['surah_name_en']}",
        help="Select the Surah you want to generate a video for"
    )

with col2:
    ayah_number = st.selectbox(
        "Ayah Number",
        options=list(range(1, surah_info[surah_number]["number_of_ayahs"] + 1)),
        help="Select the Ayah number within the selected Surah"
    )

# Voice selection
voice_options = {
    "AbdulBaset": "AbdulBaset AbdulSamad",
    "AbdullahBasfar": "Abdullah Basfar",
    "AbdurrahmaanAsSudais": "Abdurrahmaan As-Sudais",
    "AbuBakrShatri": "Abu Bakr Ash-Shatri",
    "AhmedNeana": "Ahmed Neana",
    "AhmedAlAjmi": "Ahmed Al Ajmi",
    "AkramAlAlaqmi": "Akram Al Alaqmi",
    "AliHajjajAlsouasi": "Ali Hajjaj Alsouasi",
    "AsimAbdullahAlHakeem": "Asim Abdullah Al Hakeem",
    "FaresAbbad": "Fares Abbad",
    "HaniArRifai": "Hani Ar Rifai",
    "KhalidAbdullahAlqurashi": "Khalid Abdullah Alqurashi",
    "MahmoudAliAlBanna": "Mahmoud Ali Al Banna",
    "MahmoudKhalilAlHusary": "Mahmoud Khalil Al Husary",
    "Minshawi": "Minshawi",
    "MohamedAyoub": "Mohamed Ayoub",
    "MohamedRashadAlTabbakh": "Mohamed Rashad Al Tabbakh",
    "MuhammadAyyub": "Muhammad Ayyub",
    "MuhammadJibreel": "Muhammad Jibreel",
    "SaadAlGhamdi": "Saad Al Ghamdi",
    "SahlYassin": "Sahl Yassin",
    "SalahAbdulRahmanBukhatir": "Salah Abdul Rahman Bukhatir",
    "SalahBukhatir": "Salah Bukhatir",
    "TawfeeqAsSayegh": "Tawfeeq As Sayegh",
    "YasserAdDussary": "Yasser Ad Dussary",
    "YasserQurashi": "Yasser Qurashi",
    "YasserSalahuddin": "Yasser Salahuddin"
}

voice = st.sidebar.selectbox(
    "Voice",
    options=list(voice_options.keys()),
    format_func=lambda x: voice_options[x],
    help="Select the reciter voice"
)

# Background selection
background_options = {
    "mosque": "Mosque Background",
    "nature": "Nature Background",
    "space": "Space Background",
    "ocean": "Ocean Background",
    "desert": "Desert Background",
    "custom": "Custom Background"
}

background = st.sidebar.selectbox(
    "Background",
    options=list(background_options.keys()),
    format_func=lambda x: background_options[x],
    help="Select the background for the video"
)

# Custom background upload
if background == "custom":
    custom_background = st.sidebar.file_uploader(
        "Upload Custom Background",
        type=["jpg", "jpeg", "png", "mp4"],
        help="Upload a custom background image or video"
    )

# Video length options
video_length_options = {
    "short": "Short (15-30 seconds)",
    "medium": "Medium (30-60 seconds)",
    "long": "Long (60-90 seconds)"
}

video_length = st.sidebar.selectbox(
    "Video Length",
    options=list(video_length_options.keys()),
    format_func=lambda x: video_length_options[x],
    help="Select the desired video length"
)

# Generate button
if st.sidebar.button("🎬 Generate Video", type="primary"):
    with st.spinner("Generating video... This may take a few minutes."):
        try:
            # Call the main generation function
            result = generate_videos(
                surah_number=surah_number,
                ayah_number=ayah_number,
                voice=voice,
                background=background,
                custom_background=custom_background,
                video_length=video_length
            )
            
            if result["success"]:
                st.success("✅ Video generated successfully!")
                st.video(result["video_path"])
                
                # Download button
                with open(result["video_path"], "rb") as file:
                    st.download_button(
                        label="📥 Download Video",
                        data=file,
                        file_name=f"Quran_S{surah_number}_A{ayah_number}_{voice}.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error(f"❌ Error: {result['error']}")
                
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for the Muslim community")