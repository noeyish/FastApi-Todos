# FastAPI 0.135.1 이상 버전 요구사항에 맞춰 Python 3.10-slim 사용
FROM python:3.10-slim

# 환경 변수 설정
# PYTHONDONTWRITEBYTECODE: .pyc 파일 생성을 방지하여 디스크 공간 절약
# PYTHONUNBUFFERED: 로그가 버퍼링 없이 즉시 출력되도록 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
# bcrypt(v4.0+)와 python-jose(cryptography) 빌드를 위해 gcc, libffi-dev, cargo 등이 필요할 수 있습니다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python3-dev \
    cargo \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일만 먼저 복사하여 레이어 캐싱 활용
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 프로젝트 파일 복사
COPY . .

# 포트 노출
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
