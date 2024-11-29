from fastapi import APIRouter, HTTPException, status
import requests
import json

router = APIRouter()

# 플래그 상태 변수
is_notice_api_unavailable = False

@router.get("/notice", status_code=status.HTTP_200_OK)
def read_notice():
    global is_notice_api_unavailable

    # 503 에러 상태라면 즉시 차단
    if is_notice_api_unavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The notices API server is currently unavailable. Retry later."
        )

    url = "http://localhost:8010/notice/notices"
    try:
        resp = requests.get(url=url)
        resp.raise_for_status()
    except requests.ConnectionError:
        is_notice_api_unavailable = True  # 플래그 설정
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The notices API server is unavailable."
        )
    except requests.Timeout:
        is_notice_api_unavailable = True  # 플래그 설정
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The notices API server timed out."
        )

    if resp.status_code == 200:
        # JSON으로 변환
        try:
            notices = resp.json()
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decode JSON from API response"
            )

        # 데이터 구조 검증
        if not isinstance(notices, list):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid data format received from notices API"
            )

        # 공지가 없을 때 예외 처리
        if not notices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No notices available"
            )

        # `id`를 기준으로 정렬
        try:
            sorted_notices = sorted(
                notices,
                key=lambda x: x['id'],  # `id` 기준으로 정렬
                reverse=True  # 내림차순
            )
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid notice format: Missing 'id' field"
            )

        # 가장 큰 `id`를 가진 공지 반환
        latest_notice = sorted_notices[0].get("title") if sorted_notices else None
        if not latest_notice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid title found in the latest notice"
            )

        return {"message": latest_notice}

    raise HTTPException(status_code=resp.status_code, detail="Failed to fetch notices")
