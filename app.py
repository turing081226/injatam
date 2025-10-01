# 로그인 및 회원가입 (상단 팝오버 내부)
with st.popover("🔐 계정", use_container_width=True):
    # 로그인
    try:
        name, auth_status, username = authenticator.login(
            location="main",
            fields={
                "Form name": "로그인",
                "Username": "아이디",
                "Password": "비밀번호",
                "Login": "로그인",
            },
            key="login_form",
        ) or (None, None, None)
    except Exception as e:
        st.error(f"로그인 위젯 오류: {e}")
        name, auth_status, username = None, None, None

    # 로그인 결과 안내
    if auth_status is True:
        st.success(f"✅ 로그인 성공: {name} 님 환영합니다!")
        authenticator.logout(button_name="로그아웃", location="main", key="logout_btn")
    elif auth_status is False:
        # 아이디 존재 여부로 구분
        usernames = (config.get("credentials", {}) or {}).get("usernames", {}) or {}
        if username and username not in usernames:
            st.error("❌ 로그인 실패: 존재하지 않는 아이디입니다.")
        else:
            st.error("❌ 로그인 실패: 비밀번호가 올바르지 않습니다.")
    else:
        st.info("로그인해 주세요.")

    st.divider()
    st.subheader("회원가입")

    reg_email = reg_user = reg_name = None
    try:
        reg_out = authenticator.register_user(
            location="main",
            fields={
                "Form name": "회원가입",
                "Email": "이메일",
                "Username": "아이디",
                "Name": "이름",  # 최신 버전에서는 First/Last name 대신 Name 하나를 사용
                "Password": "비밀번호",
                "Repeat password": "비밀번호 확인",
                "Register": "가입",
            },
            captcha=False,
            password_hint=True,
            key="register_form",
        )

        if isinstance(reg_out, tuple):
            # 버전에 따라 3개 또는 4개 반환
            if len(reg_out) == 3:
                reg_email, reg_user, reg_name = reg_out
            elif len(reg_out) == 4:
                reg_email, reg_user, first, last = reg_out
                reg_name = f"{last}{first}".strip()
    except Exception as e:
        st.error(f"❌ 회원가입 실패: {e}")

    if reg_email and reg_user and reg_name:
        save_auth_config(config)
        st.success(f"✅ 회원가입 완료: {reg_name}님, 이제 로그인해 주세요.")

# … (생략) …

# 챗봇 탭 내부 – 입력 처리 및 Gemini 호출 부분
# 기본 폴백
fallback = f"(임시 답변 · {persona}) 좋은 질문이에요! 시장 지도를 기준으로 경로와 추천을 알려드릴 수 있어요."
reply = fallback

# Gemini 호출
try:
    import google.generativeai as genai
    api = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    api = api.strip().strip('"').strip("'")  # 따옴표 제거

    if not api:
        st.info("Gemini API 키가 없어 임시 응답을 사용합니다.", icon="🔑")
    else:
        genai.configure(api_key=api)

        preferred = [
            cfg.get("model", "gemini-1.5-flash"),
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-pro",
        ]
        model_name = cfg.get("model", "gemini-1.5-flash")
        try:
            m2 = resolve_model(preferred)
            if m2:
                model_name = m2
        except Exception:
            pass

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=cfg["system"],
            generation_config={
                "temperature": cfg["temperature"],
                "max_output_tokens": cfg["max_tokens"],
            },
        )

        hist_for_llm = st.session_state._chat_by_persona[persona][:-1]
        gem_hist = [
            {"role": ("user" if t["role"] == "user" else "model"), "parts": [{"text": t["content"]}]}
            for t in hist_for_llm
        ]
        chat = model.start_chat(history=gem_hist)

        with st.spinner("답변 작성 중…"):
            resp = chat.send_message(user_msg)

        # 안전 파싱
        text = getattr(resp, "text", None)
        reply = text.strip() if text else fallback

except Exception as e:
    # API 호출 실패 – 키를 마스킹하여 오류 메시지 표시
    err = str(e)
    if api:
        err = err.replace(api, "***")
    st.error(f"Gemini 호출 실패: {err}")

# 결과 추가 및 rerun
hist = st.session_state._chat_by_persona.get(persona, [])
hist = hist + [{"role": "assistant", "content": reply}]
st.session_state._chat_by_persona[persona] = hist
st.rerun()
