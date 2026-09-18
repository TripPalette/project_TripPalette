# TripPalette 협업 가이드

TripPalette는 GitHub Fork와 Pull Request 방식으로 협업합니다. 모든 참여자는 작업을 시작하기 전에 이 문서를 확인합니다.

## 1. 저장소 구조

### 팀원

- `origin`: 팀원 개인 계정으로 Fork한 저장소
- `upstream`: `TripPalette/project_TripPalette` Organization 원본 저장소

```text
origin    https://github.com/<본인계정>/project_TripPalette.git
upstream  https://github.com/TripPalette/project_TripPalette.git
```

다음 명령으로 설정을 확인합니다.

```bash
git remote -v
```

`upstream`이 없다면 추가합니다.

```bash
git remote add upstream https://github.com/TripPalette/project_TripPalette.git
```

### 팀장

팀장은 Organization 원본 저장소를 관리하므로 `origin`이 `TripPalette/project_TripPalette`를 가리킵니다. 별도의 `upstream`은 필요하지 않습니다.

## 2. 작업 시작 전 동기화

팀원은 새 작업을 시작하기 전에 개인 Fork의 `main`을 Organization의 최신 `main`과 동기화합니다.

```bash
git switch main
git fetch upstream
git merge upstream/main
git push origin main
```

GitHub의 개인 Fork 페이지에서 `Sync fork`와 `Update branch`를 사용한 경우에는 다음 명령으로 로컬에 반영합니다.

```bash
git switch main
git pull origin main
```

## 3. 브랜치 규칙

`main` 브랜치에서 직접 개발하지 않습니다. 기능이나 작업 단위로 브랜치를 생성합니다.

```bash
git switch main
git switch -c feature/기능이름
```

브랜치 이름은 소문자 영문과 하이픈을 사용합니다.

- `feature/login`
- `feature/destination-list`
- `fix/login-validation`
- `docs/readme-update`
- `chore/project-settings`

## 4. 커밋 규칙

커밋 메시지는 `타입: 작업 내용` 형식으로 작성합니다.

| 타입 | 용도 | 예시 |
|---|---|---|
| `feat` | 새로운 기능 | `feat: 이메일 로그인 구현` |
| `fix` | 오류 수정 | `fix: 예약 인원 검증 오류 수정` |
| `docs` | 문서 수정 | `docs: 실행 방법 추가` |
| `style` | 기능 변화 없는 형식 수정 | `style: 템플릿 들여쓰기 정리` |
| `refactor` | 코드 구조 개선 | `refactor: 인증 로직 분리` |
| `test` | 테스트 추가·수정 | `test: 로그인 테스트 추가` |
| `chore` | 설정 및 기타 작업 | `chore: 패키지 의존성 추가` |

한 커밋에는 가능한 한 하나의 작업 목적만 포함합니다.

## 5. 작업 브랜치 Push

팀원은 작업 브랜치를 개인 Fork인 `origin`에 Push합니다.

```bash
git add .
git commit -m "feat: 작업 내용"
git push -u origin feature/기능이름
```

팀원은 Organization 원본인 `upstream`에 직접 Push하지 않습니다.

## 6. Pull Request

팀원은 개인 Fork의 작업 브랜치에서 Organization 원본의 `main`으로 Pull Request를 생성합니다.

```text
base repository: TripPalette/project_TripPalette
base branch: main

head repository: <본인계정>/project_TripPalette
compare branch: feature/기능이름
```

PR에는 다음 내용을 작성합니다.

- 구현하거나 수정한 내용
- 주요 변경 파일
- 실행 및 테스트 방법
- 관련 Issue
- 화면 변경이 있다면 스크린샷
- 팀원이 알아야 할 참고사항

PR 생성 후에는 팀장 또는 리뷰어의 검토를 기다립니다. 임의로 `main`에 병합하지 않습니다.

## 7. 리뷰와 수정

리뷰어는 PR의 `Files changed`에서 변경사항을 확인한 뒤 다음 중 하나를 선택합니다.

- `Comment`: 일반적인 의견
- `Approve`: 병합 가능
- `Request changes`: 수정 필요

수정 요청을 받은 팀원은 기존 작업 브랜치에서 수정하고 다시 Push합니다. 기존 PR에 자동으로 반영되므로 새 PR을 만들지 않습니다.

```bash
git add .
git commit -m "fix: 리뷰 내용 반영"
git push
```

## 8. Merge 후 동기화

PR이 Organization의 `main`에 병합되면 개인 Fork와 로컬 저장소를 다시 동기화합니다.

```bash
git switch main
git fetch upstream
git merge upstream/main
git push origin main
```

기존 작업 브랜치를 계속 사용해야 한다면 최신 `main`을 반영합니다.

```bash
git switch feature/기능이름
git merge main
```

작업이 끝난 브랜치는 삭제합니다.

```bash
git switch main
git branch -d feature/기능이름
git push origin --delete feature/기능이름
```

## 9. 공유 파일 담당 원칙

다음 파일은 여러 기능에서 함께 사용하므로 수정하기 전에 팀에 알립니다.

- `app/models.py`
- `app/__init__.py`
- `app/templates/base.html`
- `config.py`
- `requirements.txt`
- `migrations/`

`models.py`와 Migration은 지정된 담당자가 관리합니다. 새 패키지를 설치했다면 `requirements.txt`도 함께 수정합니다.

## 10. 커밋 금지 파일

다음 파일과 폴더는 Git에 올리지 않습니다.

- `.env`
- `venv/`
- `instance/`
- 로컬 데이터베이스 파일
- 비밀번호, API 키, 토큰
- Python 캐시와 로그

환경변수 항목을 추가해야 할 때는 실제 값을 제외하고 `.env.example`만 수정합니다.

## 11. 작업 완료 기준

PR을 만들기 전에 다음 사항을 확인합니다.

- 로컬에서 애플리케이션이 실행되는가
- 맡은 기능이 정상적으로 동작하는가
- 기존 기능이 깨지지 않았는가
- `.env`나 민감정보가 포함되지 않았는가
- 불필요한 파일을 함께 수정하지 않았는가
- 개발 사양서의 URL, 모델, 템플릿 경로와 일치하는가

