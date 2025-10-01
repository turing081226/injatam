# app.py
import os
import json
from typing import List, Dict, Tuple, Optional

import numpy as np
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_chat import message
from streamlit_folium import st_folium
import folium
import base64
import matplotlib.pyplot as plt
import heapq

# ========== Page Setup ==========
st.set_page_config(page_title="부여 시장 맞춤 안내", page_icon="🛍️", layout="wide")

SAMPLE_MARKET = {
    "nodes": {
        "용우동": {"latlon": [36.282783, 126.911339], "desc": "우동/국수 전문", "tags": ["면", "한식", "분식"], "rating": 4.3},
        "로얄카페": {"latlon": [36.282655, 126.911349], "desc": "커피/디저트", "tags": ["카페", "디저트", "시원"], "rating": 4.2},
        "한스델리": {"latlon": [36.281437, 126.911173], "desc": "샌드위치/양식", "tags": ["양식", "스테이크"], "rating": 4.1},
        "탕화쿵푸": {"latlon": [36.281437, 126.911173], "desc": "중국식 마라탕/훠궈", "tags": ["중식", "매운맛"], "rating": 4.4},
        "역전할머니맥주": {"latlon": [36.280365, 126.911149], "desc": "호프/안주", "tags": ["주점", "안주", "야식"], "rating": 4.0},
        "60계치킨": {"latlon": [36.279695, 126.911150], "desc": "치킨 전문", "tags": ["치킨", "한식", "야식"], "rating": 4.2},
        "병천순대국밥": {"latlon": [36.279310, 126.911175], "desc": "순대국밥/돼지국밥", "tags": ["국밥", "한식", "뜨끈"], "rating": 4.5},
        "옛날통닭": {"latlon": [36.278896, 126.911157], "desc": "전통 통닭", "tags": ["치킨", "한식", "간식"], "rating": 4.1},
        "컴포즈커피": {"latlon": [36.280710, 126.912536], "desc": "카페/커피", "tags": ["카페","커피","디저트"], "rating": 4.2},
        "빽다방": {"latlon": [36.280888, 126.912588], "desc": "카페/커피", "tags": ["카페","커피","저가"], "rating": 4.1},
        "김가네냉면": {"latlon": [36.280942, 126.912772], "desc": "냉면 전문점", "tags": ["냉면","면","한식"], "rating": 4.3},
        "뚜레쥬르": {"latlon": [36.281026, 126.912589], "desc": "빵/케이크/디저트", "tags": ["빵","케이크","디저트"], "rating": 4.2},
        "흑돈": {"latlon": [36.281102, 126.912828], "desc": "제주흑돼지/이베리코", "tags": ["고기","제주흑돼지","이베리코"], "rating": 4.5},
        "붉닭발동대문엽기떡볶이": {"latlon": [36.281230, 126.912588], "desc": "닭발/떡볶이", "tags": ["매운맛","닭발","떡볶이"], "rating": 4.3},
        "아라치": {"latlon": [36.281615, 126.912596], "desc": "치킨 전문점", "tags": ["치킨","안주","야식"], "rating": 4.2},
        "만만닭강정": {"latlon": [36.281633, 126.912566], "desc": "닭강정 전문점", "tags": ["닭강정","분식","간식"], "rating": 4.1},
        "bhc치킨": {"latlon": [36.281342, 126.912798], "desc": "치킨 전문점", "tags": ["치킨","프랜차이즈","야식"], "rating": 4.0},
        "화랑회수산": {"latlon": [36.280742, 126.912146], "desc": "회/해산물", "tags": ["회", "해산물", "모둠회"], "rating": 4.3},
        "시장순대": {"latlon": [36.281270, 126.912004], "desc": "순대/국밥", "tags": ["순대", "국밥", "분식"], "rating": 4.2},
        "토속 가마솥 통닭&분식": {"latlon": [36.281599, 126.911963], "desc": "통닭/분식", "tags": ["통닭", "튀김", "분식"], "rating": 4.1},
        "자갈치 회센터": {"latlon": [36.281585, 126.912213], "desc": "회센터", "tags": ["회", "해산물", "초장집"], "rating": 4.2},
        "버드나무집": {"latlon": [36.281603, 126.912311], "desc": "한식/고기", "tags": ["한식", "백반", "고기"], "rating": 4.2},
        "해미칼국수": {"latlon": [36.281478, 126.912322], "desc": "칼국수/분식", "tags": ["칼국수", "만두", "국물"], "rating": 4.3},
        "들마루": {"latlon": [36.281986, 126.911989], "desc": "가정식 한식", "tags": ["백반", "찌개", "한식"], "rating": 4.2},
        "부뚜막식당": {"latlon": [36.282031, 126.912122], "desc": "가정식 한식", "tags": ["백반", "찌개", "제철"], "rating": 4.2},
        "제일통닭": {"latlon": [36.282129, 126.912123], "desc": "치킨 전문", "tags": ["치킨", "후라이드", "양념"], "rating": 4.1},
        "팻버거슬림": {"latlon": [36.282199, 126.911987], "desc": "수제버거", "tags": ["버거", "패티", "감자튀김"], "rating": 4.2},
        "아궁이칼국수": {"latlon": [36.282210, 126.912309], "desc": "칼국수/수제비", "tags": ["칼국수", "수제비", "만두"], "rating": 4.3},
        "엄마네": {"latlon": [36.282310, 126.912312], "desc": "가정식 한식", "tags": ["백반", "반찬", "집밥"], "rating": 4.2},
        "인생건어물맥주": {"latlon": [36.282309, 126.912386], "desc": "호프/포차", "tags": ["맥주", "건어물", "안주"], "rating": 4.1},
        "왕곰탕": {"latlon": [36.282317, 126.911966], "desc": "곰탕/국밥", "tags": ["곰탕", "사골", "국밥"], "rating": 4.3},
        "장터한우국밥": {"latlon": [36.282326, 126.912150], "desc": "한우국밥", "tags": ["한우", "국밥", "수육"], "rating": 4.3},
        "쪼물쪼물 엄만손맛전집": {"latlon": [36.282444, 126.912120], "desc": "전/막걸리", "tags": ["전", "부침개", "막걸리"], "rating": 4.2},
        "부여칼국수": {"latlon": [36.282839, 126.912121], "desc": "칼국수 전문", "tags": ["칼국수", "보쌈", "만두"], "rating": 4.3},
        "교촌치킨": {"latlon": [36.282942, 126.912835], "desc": "치킨 프랜차이즈", "tags": ["치킨", "간장", "허니"], "rating": 4.2},
        "엄마밥상": {"latlon": [36.282949, 126.912516], "desc": "백반/가정식", "tags": ["백반", "반찬", "집밥"], "rating": 4.1},
        "고려홍삼": {"latlon": [36.282846, 126.912491], "desc": "건강식품 매장", "tags": ["홍삼", "건강식품", "선물"], "rating": 4.0},
        "만다린": {"latlon": [36.282685, 126.912844], "desc": "중식당", "tags": ["짜장", "짬뽕", "탕수육"], "rating": 4.2},
        "청주본가 왕갈비탕": {"latlon": [36.282672, 126.912518], "desc": "갈비탕 전문", "tags": ["갈비탕", "탕", "한식"], "rating": 4.2},
        "돈까스백반": {"latlon": [36.282476, 126.912613], "desc": "돈까스/정식", "tags": ["돈까스", "정식", "한식"], "rating": 4.2},
        "명인만두": {"latlon": [36.282231, 126.912840], "desc": "만두/분식", "tags": ["만두", "라면", "분식"], "rating": 4.2},
        "노브랜드 버거": {"latlon": [36.281961, 126.912515], "desc": "버거 프랜차이즈", "tags": ["버거", "패스트푸드", "세트"], "rating": 4.1},
        "설빙": {"latlon": [36.281961, 126.912515], "desc": "디저트 카페", "tags": ["빙수", "디저트", "카페"], "rating": 4.2},
        "족발신선생": {"latlon": [36.281976, 126.912842], "desc": "족발/보쌈", "tags": ["족발", "보쌈", "야식"], "rating": 4.2},
        "대원식당 보신탕": {"latlon": [36.281115, 126.912866], "desc": "전통 탕/한식", "tags": ["탕", "한식", "전통"], "rating": 3.9},
        "만랩 커피": {"latlon": [36.282968, 126.911653], "desc": "카페", "tags": ["커피","프랜차이즈"], "rating": 4.5},
        "해운달 숯불갈비&풍천장어참숯구이": {"latlon": [36.282518, 126.911653], "desc": "음식점", "tags": ["장어","고기"], "rating": 3.9},
        "파스쿠찌": {"latlon": [36.282155, 126.910742], "desc": "카페", "tags": ["커피","프랜차이즈"], "rating": 3.7},
        "올리브영": {"latlon": [36.281213, 126.910333], "desc": "화장품", "tags": ["화장품","프랜차이즈"], "rating": 4.3},
        "공차": {"latlon": [36.281213, 126.910333], "desc": "카페", "tags": ["버블티","프랜차이즈"], "rating": 4.0},
        "베라": {"latlon": [36.281213, 126.910333], "desc": "아이스크림", "tags": ["아이스크림","프랜차이즈"], "rating": 4.3},
        "에펠제과": {"latlon": [36.280733, 126.910716], "desc": "베이커리", "tags": ["빵"], "rating": 3.8},
        "스마일 찹쌀 꽈배기": {"latlon": [36.280672, 126.909696], "desc": "꽈배기집", "tags": ["가성비","간식"], "rating": 4.7},
        "터미널 분식": {"latlon": [36.280649, 126.909695], "desc": "분식점", "tags": ["분식","복권판매점"], "rating": 4.5},
        "뚱땡이 부대찌개 감자탕": {"latlon": [36.280888, 126.909652], "desc": "부대찌개집", "tags": ["부대찌개","찌개류"], "rating": 4.0},
        "남쉐프독도복국": {"latlon": [36.281408, 126.909360], "desc": "복국", "tags": ["복어","고급음식"], "rating": 4.2},
        "백강문화관": {"latlon": [36.280722, 126.910146], "desc": "카페", "tags": ["카페","쉼터"], "rating": 4.7},
        "맘스터치": {"latlon": [36.280573, 126.911671], "desc": "햄버거집", "tags": ["햄버거","치킨","프랜차이즈"], "rating": 4.0},
        "신전떡볶이": {"latlon": [36.280573, 126.911671], "desc": "떡볶이집", "tags": ["떡볶이","프랜차이즈"], "rating": 4.0},
        "김밥천국": {"latlon": [36.280573, 126.911671], "desc": "분식점", "tags": ["프랜차이즈","김밥","가성비"], "rating": 4.1},
        "헌터 PC": {"latlon": [36.280495, 126.911261], "desc": "PC방", "tags": ["게임","고성능 컴퓨터"], "rating": 4.3},
    },
    "edges": [
        ["터미널 분식", "스마일 찹쌀 꽈배기"],
        ["스마일 찹쌀 꽈배기", "뚱땡이 부대찌개 감자탕"],
        ["뚱땡이 부대찌개 감자탕", "남쉐프독도복국"],
        ["백강문화관", "올리브영"],
        ["올리브영", "공차"],
        ["공차", "베라"],
        ["에펠제과", "파스쿠찌"],
        ["옛날통닭", "병천순대국밥"],
        ["병천순대국밥", "60계치킨"],
        ["60계치킨", "역전할머니맥주"],
        ["역전할머니맥주", "헌터 PC"],
        ["헌터 PC", "한스델리"],
        ["한스델리", "탕화쿵푸"],
        ["탕화쿵푸", "로얄카페"],
        ["로얄카페", "용우동"],
        ["맘스터치", "신전떡볶이"],
        ["신전떡볶이", "김밥천국"],
        ["김밥천국", "해운달 숯불갈비&풍천장어참숯구이"],
        ["해운달 숯불갈비&풍천장어참숯구이", "만랩 커피"],
        ["컴포즈커피", "화랑회수산"],
        ["화랑회수산", "빽다방"],
        ["빽다방", "자갈치 회센터"],
        ["자갈치 회센터", "시장순대"],
        ["시장순대", "해미칼국수"],
        ["해미칼국수", "버드나무집"],
        ["버드나무집", "토속 가마솥 통닭&분식"],
        ["토속 가마솥 통닭&분식", "들마루"],
        ["들마루", "팻버거슬림"],
        ["팻버거슬림", "왕곰탕"],
        ["왕곰탕", "장터한우국밥"],
        ["장터한우국밥", "부뚜막식당"],
        ["부뚜막식당", "제일통닭"],
        ["제일통닭", "쪼물쪼물 엄만손맛전집"],
        ["쪼물쪼물 엄만손맛전집", "아궁이칼국수"],
        ["아궁이칼국수", "엄마네"],
        ["엄마네", "인생건어물맥주"],
        ["인생건어물맥주", "돈까스백반"],
        ["돈까스백반", "청주본가 왕갈비탕"],
        ["청주본가 왕갈비탕", "만다린"],
        ["만다린", "부여칼국수"],
        ["부여칼국수", "고려홍삼"],
        ["고려홍삼", "교촌치킨"],
        ["교촌치킨", "엄마밥상"],
        ["노브랜드 버거", "설빙"],
        ["설빙", "족발신선생"],
        ["족발신선생", "명인만두"],
        ["명인만두", "흑돈"],
        ["흑돈", "bhc치킨"],
        ["bhc치킨", "김가네냉면"],
        ["김가네냉면", "돈까스백반"],
        ["돈까스백반", "뚜레쥬르"],
        ["뚜레쥬르", "붉닭발동대문엽기떡볶이"],
        ["붉닭발동대문엽기떡볶이", "아라치"],
        ["아라치", "만만닭강정"],
        ["만만닭강정", "청주본가 왕갈비탕"],
        ["청주본가 왕갈비탕", "컴포즈커피"],
        ["터미널 분식", "백강문화관"],
        ["스마일 찹쌀 꽈배기", "에펠제과"],
        ["파스쿠찌", "한스델리"],
        ["용우동", "왕곰탕"],
        ["로얄카페", "왕곰탕"],
        ["해운달 숯불갈비&풍천장어참숯구이", "왕곰탕"],
        ["만랩 커피", "부여칼국수"],
        ["역전할머니맥주", "화랑회수산"],
        ["맘스터치", "화랑회수산"],
        ["신전떡볶이", "화랑회수산"],
        ["김밥천국", "화랑회수산"],
        ["헌터 PC", "화랑회수산"],
        ["맘스터치", "김밥천국"],
        ["빽다방", "뚜레쥬르"],
        ["들마루", "부뚜막식당"],
        ["제일통닭", "팻버거슬림"],
        ["엄마네", "장터한우국밥"],
        ["김가네냉면", "흑돈"],
        ["고려홍삼", "청주본가 왕갈비탕"],
        ["컴포즈커피", "빽다방"],
        ["빽다방", "김가네냉면"],
        ["bhc치킨", "대원식당 보신탕"],
        ["토속 가마솥 통닭&분식", "자갈치 회센터"],
        ["만만닭강정", "버드나무집"],
        ["교촌치킨", "만다린"],
        ["만다린", "돈까스백반"],
        ["아궁이칼국수", "노브랜드 버거"],
        ["노브랜드 버거", "족발신선생"],
        ["시장순대", "토속 가마솥 통닭&분식"],
        ["만만닭강정", "노브랜드 버거"],
        ["로얄카페", "해운달 숯불갈비&풍천장어참숯구이"],
        ["아라치", "bhc치킨"],
        ["용우동", "만랩 커피"],
        ["자갈치 회센터", "버드나무집"],
        ["엄마밥상", "고려홍삼"],
        ["빽다방", "자갈치 회센터"],
        ["김밥천국", "헌터 PC"],
        ["스마일 찹쌀 꽈배기", "백강문화관"],
        ["화랑회수산", "김밥천국"],
        ["공차", "백강문화관"],
        ["역전할머니맥주", "에펠제과"],
        ["에펠제과", "백강문화관"],
        ["로얄카페", "파스쿠찌"],
        ["탕화쿵푸", "토속 가마솥 통닭&분식"]
    ]
}



# ------------------------------------------------------------
# 유틸
# ------------------------------------------------------------
def euclid(a, b):
    return float(np.hypot(a[0]-b[0], a[1]-b[1]))

import numpy as np

def haversine_m(a, b):
    # a, b: [lat, lon] in degrees
    lat1, lon1 = np.deg2rad(a[0]), np.deg2rad(a[1])
    lat2, lon2 = np.deg2rad(b[0]), np.deg2rad(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 6371000.0 * 2.0 * np.arcsin(np.sqrt(h))  # meters

def build_graph(market, crowd_zones: Optional[List[Tuple[float,float,float]]] = None):
    nodes, edges = market["nodes"], market["edges"]
    G = {k: {} for k in nodes}
    for u, v in edges:
        pu, pv = nodes[u]["latlon"], nodes[v]["latlon"]
        w = haversine_m(pu, pv)  # ← 도 단위 유클리드 → 미터
        # 0 길이 간선 보정(동일 좌표 간 연결)
        if w < 0.5:  # 최소 0.5m
            w = 0.5

        # 혼잡 가중 (crowd_zones가 lat/lon/반경(미터)일 때만 의미 있음)
        boost = 1.0
        # crowd_zones 좌표가 위경도라면, 반경 비교시에도 haversine_m을 써야 합니다.
        # 여기선 crowd_zones를 생략하거나, 이미 미터 기반 좌표를 쓰는 경우만 반영하세요.
        w *= boost

        G[u][v] = w
        G[v][u] = w
    return G
    
# ---- KMP ----
def kmp_build_lps(p):
    lps = [0]*len(p); j=0
    for i in range(1,len(p)):
        while j>0 and p[i]!=p[j]: j=lps[j-1]
        if p[i]==p[j]: j+=1; lps[i]=j
    return lps

def kmp_search(text, pattern):
    if not pattern: return True
    t, p = text.lower(), pattern.lower()
    lps = kmp_build_lps(p); j=0
    for ch in t:
        while j>0 and ch!=p[j]: j=lps[j-1]
        if ch==p[j]:
            j+=1
            if j==len(p): return True
    return False


def cosine_sim(a, b, eps=1e-9):
    an = a/ (np.linalg.norm(a)+eps)
    bn = b/ (np.linalg.norm(b)+eps)
    return float(np.dot(an, bn))

# --- Gemini 모델 자동 선택 유틸 ---
def _list_supported_models():
    import google.generativeai as genai
    try:
        models = list(genai.list_models())
    except Exception:
        return []
    out = []
    for m in models:
        name = getattr(m, "name", "")
        short = name.split("/")[-1] if name else ""
        methods = set(getattr(m, "supported_generation_methods", []) or [])
        out.append({"full": name, "short": short, "methods": methods})
    return out

def resolve_model(preferred_order):
    ms = _list_supported_models()
    if not ms:
        return None
    def ok(m):
        methods = m["methods"]
        return ("generateContent" in methods) or ("generateText" in methods)
    names = {m["short"]: m for m in ms}
    for cand in preferred_order:
        if cand in names and ok(names[cand]):
            return cand
    for m in ms:
        if ok(m):
            return m["short"]
    return None

# ---- A* / Dijkstra ----
def dijkstra(G, start, goal):
    pq=[(0.0,start)]; dist={start:0.0}; parent={start:None}
    while pq:
        d,u=heapq.heappop(pq)
        if u==goal: break
        if d>dist.get(u,1e18): continue
        for v,w in G[u].items():
            nd=d+w
            if nd<dist.get(v,1e18):
                dist[v]=nd; parent[v]=u; heapq.heappush(pq,(nd,v))
    if goal not in parent: return float("inf"),[]
    path=[]; cur=goal
    while cur is not None: path.append(cur); cur=parent[cur]
    return dist[goal], list(reversed(path))

def astar(G, coords, start, goal):
    def h(a,b): return euclid(coords[a], coords[b])
    openpq=[(h(start,goal),0.0,start)]
    g={start:0.0}; parent={start:None}; closed=set()
    while openpq:
        f,_,u = heapq.heappop(openpq)
        if u in closed: continue
        if u==goal: break
        closed.add(u)
        for v,w in G[u].items():
            ng=g[u]+w
            if ng<g.get(v,1e18):
                g[v]=ng; parent[v]=u; heapq.heappush(openpq,(ng+h(v,goal),ng,v))
    if goal not in parent: return float("inf"),[]
    path=[]; cur=goal
    while cur is not None: path.append(cur); cur=parent[cur]
    return g[goal], list(reversed(path))

def nearest_neighbor_order(coords, start, targets):
    rem=set(targets); order=[]; cur=start
    while rem:
        nxt=min(rem, key=lambda t: euclid(coords[cur], coords[t]))
        order.append(nxt); rem.remove(nxt); cur=nxt
    return order

# ---- Fallback plotting ----
def plot_market(market, path=None):
    nodes, edges = market["nodes"], market["edges"]
    fig, ax = plt.subplots()
    for u,v in edges:
        x1,y1=nodes[u]["latlon"]; x2,y2=nodes[v]["latlon"]
        ax.plot([x1,x2],[y1,y2], linewidth=1, alpha=0.5)
    xs=[v["latlon"][0] for v in nodes.values()]
    ys=[v["latlon"][1] for v in nodes.values()]
    ax.scatter(xs,ys,s=80)
    for name,meta in nodes.items():
        ax.text(meta["latlon"][0]+0.05, meta["latlon"][1]+0.05, name, fontsize=9)
    if path and len(path)>=2:
        px=[nodes[n]["latlon"][0] for n in path]
        py=[nodes[n]["latlon"][1] for n in path]
        ax.plot(px,py,linewidth=3)
    ax.set_aspect("equal","box")
    ax.set_title("시장 그래프 & 경로")
    st.pyplot(fig)

# ------------------------------------------------------------
# 저장/설정 파일
# ------------------------------------------------------------
DATA_DIR = ".local_store"
os.makedirs(DATA_DIR, exist_ok=True)
USERS_JSON = os.path.join(DATA_DIR, "profiles.json")
CFG_PATH = os.path.join(DATA_DIR, "auth_config.yaml")

def load_auth_config():
    if not os.path.exists(CFG_PATH):
        cfg = {
            "credentials": {"usernames": {}},
            "cookie": {"expiry_days": 30, "key": "buyeo_secret_key", "name": "buyeo_market_cookie"},
            "preauthorized": {"emails": []},
        }
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, allow_unicode=True)
        return cfg
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=SafeLoader)

def save_auth_config(cfg: dict):
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)

config = load_auth_config()

def load_users():
    if os.path.exists(USERS_JSON):
        with open(USERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(store):
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

USER_STORE = load_users()

# ------------------------------------------------------------
# 태그 벡터
# ------------------------------------------------------------
ALL_TAGS = sorted({t for n in SAMPLE_MARKET["nodes"].values() for t in n.get("tags",[])})
TAG_INDEX = {t:i for i,t in enumerate(ALL_TAGS)}
D = len(ALL_TAGS)

def restaurant_vector(meta):
    v = np.zeros(D, dtype=float)
    for t in meta.get("tags", []):
        if t in TAG_INDEX: v[TAG_INDEX[t]] += 1.0
    if v.sum()>0: v = v / np.linalg.norm(v)
    return v

RESTAURANT_VECS = {name: restaurant_vector(meta) for name, meta in SAMPLE_MARKET["nodes"].items()}

# ------------------------------------------------------------
# Auth (최신 버전 전용)
# ------------------------------------------------------------
authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
)

# ------------------------------------------------------------
# 사용자 프로필
# ------------------------------------------------------------
def get_user_profile(uid: Optional[str]):
    prof = {
        "vec": np.ones(D)/np.sqrt(D),
        "favorites": [],
        "eta": 0.25,
        "weights": {"alpha":0.55, "beta":0.30, "gamma":0.15},
        "metric": "cosine",
        "home": "입구",
    }
    if uid and uid in USER_STORE:
        q = USER_STORE[uid]
        prof["vec"] = np.array(q.get("vec",[1]*D), dtype=float)
        prof["favorites"] = q.get("favorites",[])
        prof["eta"] = float(q.get("eta",0.25))
        prof["weights"] = q.get("weights", prof["weights"])
        prof["metric"] = q.get("metric","cosine")
        prof["home"] = q.get("home","입구")
    return prof

def persist_user_profile(uid: str, prof):
    USER_STORE[uid] = {
        "vec": list(map(float, prof["vec"])),
        "favorites": prof["favorites"],
        "eta": prof["eta"],
        "weights": prof["weights"],
        "metric": prof["metric"],
        "home": prof["home"],
    }
    save_users(USER_STORE)

# ------------------------------------------------------------
# 사이드바: 데이터/혼잡/개인화
# ------------------------------------------------------------
st.sidebar.header("설정")
market_json = st.sidebar.text_area("시장 데이터(JSON)", json.dumps(SAMPLE_MARKET, ensure_ascii=False, indent=2), height=240)
crowd_str = st.sidebar.text_input("혼잡 구역 (cx,cy,r) ; 로 구분. 예: 4,2,1.5; 6,1,1")
crowd_zones=[]
if crowd_str.strip():
    try:
        for chunk in crowd_str.split(";"):
            cx,cy,r = map(float, chunk.strip().split(","))
            crowd_zones.append((cx,cy,r))
    except Exception as e:
        st.sidebar.error(f"혼잡 파싱 오류: {e}")

try:
    MARKET = json.loads(market_json)
    assert "nodes" in MARKET and "edges" in MARKET
except Exception:
    MARKET = SAMPLE_MARKET

coords = {k: tuple(v["latlon"]) for k,v in MARKET["nodes"].items()}
G = build_graph(MARKET, crowd_zones)
NAMES = list(MARKET["nodes"].keys())

# ------------------------------------------------------------
# 상단바: 로그인 + 회원가입 (우측)
# ------------------------------------------------------------
colL, colR = st.columns([0.8,0.2])
with colL:
    st.title("🛍️ 부여 중앙시장 맞춤 탐색")
with colR:
    with st.popover("🔐 계정", use_container_width=True):
        # 로그인 (최신 시그니처)
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

        if auth_status:
            st.success(f"{name} 님 환영합니다!")
            authenticator.logout(
                button_name="로그아웃",
                location="main",
                key="logout_btn",
            )
        elif auth_status is False:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
        else:
            st.info("로그인해 주세요.")

        st.divider()
        st.subheader("회원가입")

        # 회원가입 (최신 시그니처: 이메일/아이디/이름 반환)
        reg_email, reg_user, reg_name = authenticator.register_user(
            location="main",
            fields={
                "Form name": "회원가입",
                "Email": "이메일",
                "Username": "아이디",
                "Name": "이름",
                "Password": "비밀번호",
                "Repeat password": "비밀번호 확인",
                "Register": "가입",
            },
            captcha=False,
            password_hint=True,
            key="register_form",
        ) or (None, None, None)

        if reg_email and reg_user and reg_name:
            # config가 내부에서 갱신되므로 저장
            save_auth_config(config)
            st.success("회원가입이 완료되었습니다. 로그인해 주세요.")

UID = username if 'auth_status' in locals() and auth_status else None
PROFILE = get_user_profile(UID)

with st.sidebar.expander("개인화/가중치"):
    PROFILE["metric"] = st.radio("유사도", ["cosine","dot"], index=0 if PROFILE["metric"]=="cosine" else 1, horizontal=True)
    a = st.slider("α 취향 유사도 가중", 0.0,1.0, float(PROFILE["weights"]["alpha"]), 0.05)
    b = st.slider("β 평점 가중",       0.0,1.0, float(PROFILE["weights"]["beta"]), 0.05)
    g = st.slider("γ 거리 페널티",     0.0,1.0, float(PROFILE["weights"]["gamma"]), 0.05)
    tot = max(a+b+g, 1e-9)
    PROFILE["weights"] = {"alpha":a/tot, "beta":b/tot, "gamma":g/tot}
    PROFILE["eta"] = st.slider("학습률(좋아요/방문 반영)", 0.05, 0.9, float(PROFILE["eta"]), 0.05)
    PROFILE["home"] = st.selectbox("현재 위치(노드)", NAMES, index=NAMES.index(PROFILE["home"]) if PROFILE["home"] in NAMES else 0)

if UID and st.sidebar.button("프로필 저장", use_container_width=True):
    persist_user_profile(UID, PROFILE)
    st.sidebar.success("저장됨")

# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------
tab_rec, tab_search, tab_chat, tab_path = st.tabs(["🍽️ 추천", "🔎 검색", "💬 챗봇", "🗺️ 경로"])

# ---- Recommendation Tab ----
with tab_rec:
    st.subheader("개인화 추천")

    if "_max_dist" not in st.session_state:
        coords_all = [m["latlon"] for m in MARKET["nodes"].values()]
        md = 0.0
        for i in range(len(coords_all)):
            for j in range(i+1, len(coords_all)):
                md = max(md, haversine_m(coords_all[i], coords_all[j]))  # 미터
        st.session_state._max_dist = max(md, 1.0)

    current_xy = MARKET["nodes"][PROFILE["home"]]["latlon"]
    items = []
    for name in NAMES:
        if name in ["입구","출구"]: continue
        sim = cosine_sim(PROFILE["vec"], RESTAURANT_VECS[name]) if PROFILE["metric"]=="cosine" else float(np.dot(PROFILE["vec"], RESTAURANT_VECS[name]))
        rating01 = MARKET['nodes'][name].get('rating',4.0)/5.0
        distn = euclid(current_xy, MARKET['nodes'][name]["latlon"]) / st.session_state._max_dist
        sc = PROFILE["weights"]["alpha"]*sim + PROFILE["weights"]["beta"]*rating01 - PROFILE["weights"]["gamma"]*distn
        items.append((sc, name, {"sim":sim,"rating":rating01,"dist":distn}))

    items.sort(reverse=True, key=lambda x:x[0])

    K = st.slider("표시 수", 3, min(12, len(items)), 6, 1)
    cols_per_row = 3
    for row_start in range(0, min(K, len(items)), cols_per_row):
        cols = st.columns(cols_per_row, vertical_alignment="top")
        for col, data in zip(cols, items[row_start:row_start+cols_per_row]):
            sc, name, meta = data
            with col.container(border=True):
                node = MARKET["nodes"][name]
                st.markdown(f"### {name}")
                st.caption(node.get("desc",""))
                st.write("태그:", ", ".join(node.get("tags",[])))
                st.metric("개인화 점수", f"{sc:.3f}", help=f"sim={meta['sim']:.3f}, rating={meta['rating']:.2f}, dist={meta['dist']:.2f}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("👍 좋아요", key=f"like_{name}"):
                        i = RESTAURANT_VECS[name]; eta = PROFILE["eta"]
                        nv = (1-eta)*PROFILE["vec"] + eta*(i/(np.linalg.norm(i)+1e-9))
                        PROFILE["vec"] = nv/(np.linalg.norm(nv) if np.linalg.norm(nv)>0 else 1.0)
                        if UID: persist_user_profile(UID, PROFILE)
                        st.success("취향이 업데이트 되었어요.")
                        st.rerun()
                with c2:
                    if st.button("✅ 방문", key=f"visit_{name}"):
                        i = RESTAURANT_VECS[name]; eta = PROFILE["eta"]*0.5
                        nv = (1-eta)*PROFILE["vec"] + eta*(i/(np.linalg.norm(i)+1e-9))
                        PROFILE["vec"] = nv/(np.linalg.norm(nv) if np.linalg.norm(nv)>0 else 1.0)
                        if UID: persist_user_profile(UID, PROFILE)
                        st.info("방문 반영 완료.")
                        st.rerun()
                with c3:
                    fav = name in PROFILE["favorites"]
                    lab = "★ 즐겨찾기" if not fav else "☆ 해제"
                    if st.button(lab, key=f"fav_{name}"):
                        if not fav: PROFILE["favorites"].append(name)
                        else: PROFILE["favorites"] = [x for x in PROFILE["favorites"] if x!=name]
                        if UID: persist_user_profile(UID, PROFILE)
                        st.toast("즐겨찾기 업데이트")

    if PROFILE["favorites"]:
        st.write("**즐겨찾기:** ", ", ".join(PROFILE["favorites"]))

# ---- Search Tab ----
with tab_search:
    st.subheader("키워드 검색")
    q = st.text_input("검색어", key="search_q")

    if st.button("검색", key="search_btn"):
        if not q.strip():
            st.warning("검색어를 입력하세요.")
        else:
            docs = [
                f"{n} {MARKET['nodes'][n].get('desc','')} "
                f"{' '.join(MARKET['nodes'][n].get('tags',[]))}"
                for n in NAMES
            ]
            hits = [i for i, doc in enumerate(docs) if kmp_search(doc, q)]

            if not hits:
                st.info("검색 결과가 없습니다.")
            else:
                st.success(f"{len(hits)}건 발견")
                # 필요하면 개인화 점수 등으로 재정렬 가능
                for i in hits:
                    name = NAMES[i]
                    node = MARKET["nodes"][name]
                    with st.container(border=True):
                        st.markdown(f"**{name}** — {node.get('desc','')}")
                        st.caption("태그: " + ", ".join(node.get("tags", [])))

# ---- Chatbot Tab ----
with tab_chat:
    st.subheader("부여 중앙시장 캐릭터 챗봇 (streamlit-chat)")

    PERSONAS = {
        "Sunny":  {"emoji":"🌞","desc":"명랑한 길잡이 — 밝고 친절, 추천 위주.","model":"gemini-1.5-flash","temperature":1.0,"max_tokens":512,
                   "system":"You are Sunny, a bright, friendly market guide for Bujeo Central Market. 답변은 자연스럽고 간결한 한국어로 하세요. 사용자 취향을 존중하고, 추천과 이유(대표 메뉴, 대략 거리/시간)를 짧게 덧붙이세요."},
        "Charles":{"emoji":"🧭","desc":"분석형 플래너 — 경로/최적화 중심, 근거 제시.","model":"gemini-1.5-pro","temperature":0.6,"max_tokens":640,
                   "system":"You are Charles, an analytical trip planner for Bujeo Central Market. 격식 있는 간결한 한국어로 말하고, 선택지·거리·예상 소요시간을 불릿으로 정리하세요."},
        "son":    {"emoji":"🧒","desc":"귀여운 꼬마 가이드 — 쉬운 말, 라이트 톤.","model":"gemini-1.5-flash","temperature":1.1,"max_tokens":384,
                   "system":"You are Son, a cute kid guide for Bujeo Central Market. 친근하고 쉬운 한국어로, 짧고 명료하게 대답하세요. 어린 이용자도 이해할 수 있도록 설명하세요."},
        "Becky":  {"emoji":"🍰","desc":"디저트/카페 전문가 — 감성 톤, 사진 스폿 제안.","model":"gemini-1.5-flash","temperature":0.9,"max_tokens":512,
                   "system":"You are Becky, a dessert & cafe expert around Bujeo Central Market. 상냥한 한국어로, 디저트/음료 추천과 사진 스폿, 분위기 포인트를 짧게 알려주세요."},
        "Aggie":  {"emoji":"🛒","desc":"시장 상인 감성 — 실속/가격/행사 정보 중시.","model":"gemini-1.5-flash","temperature":0.8,"max_tokens":512,
                   "system":"You are Aggie, a friendly market vendor persona. 반말은 자제하되 친근한 한국어로, 실속/가격/행사/혼잡 팁을 우선으로 알려주세요."},
    }

    colL, colR = st.columns([2, 1], vertical_alignment="top")

    with colR:
        persona = st.radio("답변자", list(PERSONAS.keys()), index=0)
        cfg = PERSONAS[persona]
        st.markdown(f"**{cfg['emoji']} {persona}**")
        st.caption(cfg["desc"])
        clear = st.button("🧹 이 캐릭터 대화 초기화", use_container_width=True)

    if "_chat_by_persona" not in st.session_state:
        st.session_state._chat_by_persona = {}
    history = st.session_state._chat_by_persona.setdefault(persona, [])

    if clear:
        st.session_state._chat_by_persona[persona] = []

    with colL:
        for i, turn in enumerate(history):
            if turn["role"] == "user":
                message(turn["content"], is_user=True, key=f"{persona}_user_{i}")
            else:
                message(f"{persona}: {turn['content']}", key=f"{persona}_bot_{i}")

        user_msg = st.chat_input(f"{cfg['emoji']} {persona}에게 메시지를 보내세요…", key=f"chat_in_{persona}")
        if user_msg and user_msg.strip():
            # 사용자 push (재할당)
            hist = st.session_state._chat_by_persona.get(persona, [])
            hist = hist + [{"role": "user", "content": user_msg}]
            st.session_state._chat_by_persona[persona] = hist

            # 기본 폴백
            fallback = f"(임시 답변 · {persona}) 좋은 질문이에요! 시장 지도를 기준으로 경로와 추천을 알려드릴 수 있어요."
            reply = fallback

            # Gemini 호출 (키 없으면 폴백)
            try:
                import google.generativeai as genai
                api = st.secrets.get("GEMINI_API_KEY","")
                print(api)
                if not api:
                    st.info("Gemini API 키가 없어 임시 응답을 사용합니다.", icon="🔑")
                else:
                    genai.configure(api_key=api)
                    preferred = [
                        cfg.get("model", "gemini-1.5-flash"),
                        "gemini-1.5-flash-latest",
                        "gemini-1.5-flash-8b",
                        "gemini-1.5-pro",
                        "gemini-1.5-pro-latest",
                        "gemini-pro",
                        "gemini-1.0-pro",
                    ]
                    model_name = resolve_model(preferred) or cfg.get("model", "gemini-pro")

                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=cfg["system"],
                        generation_config={
                            "temperature": cfg["temperature"],
                            "max_output_tokens": cfg["max_tokens"],
                        },
                    )
                    hist_for_llm = st.session_state._chat_by_persona[persona][:-1]
                    gem_hist = [{"role": ("user" if t["role"] == "user" else "model"), "parts": [{"text": t["content"]}]} for t in hist_for_llm]
                    chat = model.start_chat(history=gem_hist)
                    with st.spinner("답변 작성 중…"):
                        resp = chat.send_message(user_msg)
                    reply = (getattr(resp, "text", None) or "").strip() or fallback
            except Exception:
                pass

            # 봇 push (재할당) + 즉시 갱신
            hist = st.session_state._chat_by_persona.get(persona, [])
            hist = hist + [{"role": "assistant", "content": reply}]
            st.session_state._chat_by_persona[persona] = hist
            st.rerun()

# ---- Path Tab ----
with tab_path:
    st.subheader("최단 경로 / 경유지 (지도)")

    def popup_html(name, meta):
        desc = meta.get("desc", "")
        tags = ", ".join(meta.get("tags", []))
        rating = meta.get("rating", None)
        rating_html = f"<div><b>평점</b>: {rating:.1f}/5.0</div>" if isinstance(rating, (int,float)) else ""
        return f"""
        <div style="width:240px">
          <div style="font-weight:700; font-size:14px; margin-bottom:4px;">{name}</div>
          <div style="font-size:13px; color:#444;">{desc}</div>
          <div style="font-size:12px; color:#666; margin-top:4px;"><b>태그</b>: {tags}</div>
          {rating_html}
        </div>
        """

    def make_map(market, path_names=None, start=None, end=None, via_list=None):
        nodes = market["nodes"]
        coords_ll = {k: tuple(nodes[k]["latlon"]) for k in nodes if "latlon" in nodes[k]}
        lat_center = sum(lat for lat, _ in coords_ll.values()) / max(len(coords_ll), 1)
        lon_center = sum(lon for _, lon in coords_ll.values()) / max(len(coords_ll), 1)
        m = folium.Map(location=[lat_center, lon_center], zoom_start=16, control_scale=True)

        via_set = set(via_list or [])
        for name, meta in nodes.items():
            if "latlon" not in meta:
                continue
            lat, lon = meta["latlon"]
            if name == start:
                color, icon = "green", "play"
            elif name == end:
                color, icon = "red", "stop"
            elif name in via_set:
                color, icon = "purple", "flag"
            else:
                color, icon = "blue", "info-sign"
            popup = folium.Popup(popup_html(name, meta), max_width=260)
            folium.Marker(
                location=[lat, lon],
                popup=popup,
                tooltip=name,
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)

        if path_names and len(path_names) >= 2:
            line = []
            for nm in path_names:
                meta = nodes.get(nm, {})
                if "latlon" in meta:
                    line.append(tuple(meta["latlon"]))
            if len(line) >= 2:
                folium.PolyLine(line, weight=5, color="#1E90FF", opacity=0.8).add_to(m)
        return m

    # 상태 저장용 키 준비
    if "_path_result" not in st.session_state:
        st.session_state._path_result = None  # dict or None

    # ─── UI ───
    colA, colB = st.columns(2)
    with colA:
        start = st.selectbox("출발지", NAMES, index=0, key="path_start")
        end   = st.selectbox("도착지", NAMES, index=min(len(NAMES)-1, 5), key="path_end")
        via   = st.multiselect("경유지", [n for n in NAMES if n not in (start, end)], key="path_via")
    with colB:
        algo2 = st.radio("알고리즘", ["A*", "Dijkstra"], horizontal=True, key="path_algo")
        order_mode = st.radio("경유지 순서", ["선택 순서", "가까운 곳부터(NN)"], horizontal=False, key="path_order")

    # 경유지 순서 결정
    seq = [start]
    tgs = via.copy()
    if order_mode.startswith("가까운"):
        seq += nearest_neighbor_order(coords, start, tgs)
    else:
        seq += tgs
    seq.append(end)

    # 기반 지도: 항상 표시
    st.caption("지도의 마커를 클릭하면 설명 팝업이 뜹니다.")
    base_map = make_map(MARKET, path_names=None, start=start, end=end, via_list=via)
    st_folium(base_map, height=440, width=None)

    # 계산 버튼
    if st.button("경로 계산", key="btn_calc_path"):
        total, full, feasible = 0.0, [], True
        for s, t in zip(seq[:-1], seq[1:]):
            c, path = (astar(G, coords, s, t) if algo2 == "A*" else dijkstra(G, s, t))
            if not path:
                feasible = False
                break
            if full and path and full[-1] == path[0]:
                full.extend(path[1:])
            else:
                full.extend(path)
            total += c
        walk_mps = 1.2  # 보행 1.2 m/s ≈ 72 m/min
        mins = total / 72.0
        st.success(f"총 이동 거리: {total:,.0f} m (약 {mins:.1f}분)")
        # 👉 결과를 세션에 저장 (rerun 후에도 유지)
        st.session_state._path_result = {
            "feasible": feasible,
            "total": total,
            "full": full,
            "start": start,
            "end": end,
            "via": via,
            "algo": algo2,
        }
        # 즉시 피드백
        if feasible:
            st.success(f"총 이동 비용(거리): {total:.2f}")
        else:
            st.error("경로를 찾지 못했습니다. 그래프/혼잡 설정을 확인하세요.")

    # 결과 지우기
    if st.button("🗑 경로 결과 지우기", key="btn_clear_path"):
        st.session_state._path_result = None
        st.toast("경로 결과를 지웠습니다.")

    # 👉 버튼 블록 밖에서 항상 렌더링
    res = st.session_state._path_result
    if res:
        # 입력이 바뀌었는데 예전 결과가 보이는 걸 막고 싶으면 아래 체크로 안내
        if (res["start"], res["end"], res["via"], res["algo"]) != (start, end, via, algo2):
            st.info("선택이 변경되었습니다. [경로 계산]을 다시 눌러 결과를 갱신하세요.")

        if res["feasible"]:
            st.success(f"(저장됨) 총 이동 비용(거리): {res['total']:.2f}")
            result_map = make_map(MARKET, path_names=res["full"], start=res["start"], end=res["end"], via_list=res["via"])
            st_folium(result_map, height=500, width=None)
        else:
            st.error("(저장됨) 경로를 찾지 못했습니다.")
지금까지 했던 이야기 바탕으로 이거 최신으로 바꿔줄래
