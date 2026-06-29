import streamlit as st
import yt_dlp
import requests

# -------------------------------------------------------------
# [필수] SerpApi 공식 홈페이지에서 무료 가입 후 API Key를 발급받으세요.
# Streamlit Cloud에 배포할 때는 Secret 기능을 사용하는 것이 안전합니다.
# -------------------------------------------------------------
SERPAPI_KEY = "YOUR_SERPAPI_KEY_HERE"  # 여기에 발급받은 API 키를 넣으세요.

def get_youtube_thumbnail(video_url):
    """yt-dlp를 이용해 영상을 다운로드하지 않고 썸네일 주소만 추출합니다."""
    ydl_opts = {'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        # 가장 화질이 좋은 썸네일 URL 반환
        return info_dict.get('thumbnail')

def search_original_video(image_url, api_key):
    """Google Lens API(SerpApi)를 이용해 이미지 역검색을 수행합니다."""
    search_url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": api_key,
        "hl": "ko"  # 결과 언어 설정
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API 요청 실패 (오류 코드: {response.status_code})")
        return None

# --- Streamlit UI 시작 ---
st.set_page_config(page_title="유튜브 원본 찾기 봇", page_icon="🎬", layout="centered")

st.title("🎬 유튜브 영상 원본 찾기 프로그램")
st.caption("쇼츠나 짜깁기 영상의 링크를 넣으면 Google Lens를 통해 진짜 원본 영상을 찾아냅니다.")
st.write("---")

# 사용자 입력
video_input = st.text_input("유튜브 또는 쇼츠 영상 링크를 입력하세요:", placeholder="https://youtube.com/shorts/...")

if video_input:
    if not SERPAPI_KEY or SERPAPI_KEY == "YOUR_SERPAPI_KEY_HERE":
        st.warning("⚠️ 코드가 정상 작동하려면 SerpApi 키가 필요합니다. 코드 상단의 SERPAPI_KEY를 수정해주세요.")
    else:
        with st.spinner("🔄 영상을 분석하고 역검색을 진행 중입니다..."):
            try:
                # 1. 다운로드 없이 썸네일 이미지 주소 따오기
                img_url = get_youtube_thumbnail(video_input)
                
                if img_url:
                    st.image(img_url, caption="분석에 사용된 영상 프레임(썸네일)", use_container_width=True)
                    
                    # 2. SerpApi 구글 렌즈 검색 호출
                    results = search_original_video(img_url, SERPAPI_KEY)
                    
                    # 3. 결과 출력
                    if results and "visual_matches" in results:
                        st.success("✅ 역검색 매칭 결과를 찾았습니다!")
                        st.subheader("🔗 원본 예상 후보 목록")
                        
                        matches = results["visual_matches"]
                        found_any = False
                        
                        for match in matches:
                            title = match.get("title", "제목 없음")
                            link = match.get("link", "#")
                            source = match.get("source", "출처 미상")
                            thumbnail = match.get("thumbnail")
                            
                            # 유튜브 링크인 것들을 최상단에 강조하거나 필터링하여 보여줌
                            if "youtube.com" in link or "youtu.be" in link:
                                found_any = True
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    if thumbnail:
                                        st.image(thumbnail, use_container_width=True)
                                with col2:
                                    st.markdown(f"**[{title}]({link})**")
                                    st.caption(f"출처: {source} | [바로가기]({link})")
                                st.write("---")
                        
                        if not found_any:
                            st.info("유튜브 플랫폼 내에서 정확히 일치하는 원본 링크를 찾지 못했습니다. 다른 웹사이트 검색 결과를 확인해보세요.")
                            for match in matches[:5]:  # 상위 5개 일반 매칭 결과 출력
                                st.write(f"- [{match.get('title')}]({match.get('link')}) ({match.get('source')})")
                    else:
                        st.error("검색 결과를 가져오지 못했습니다.")
                else:
                    st.error("영상에서 이미지를 추출하는 데 실패했습니다.")
                    
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
