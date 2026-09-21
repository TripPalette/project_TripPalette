# TripPalette 개발용 Seed Data 안내

## 구성

- `app/data/destinations.json`: 계절별 여행지 19개
- `app/data/accommodations.json`: 여행지별 숙소 3개, 총 57개

계절별 여행지 수는 다음과 같습니다.

| 계절 | 여행지 수 |
|---|---:|
| 봄 | 4 |
| 여름 | 4 |
| 가을 | 4 |
| 겨울 | 4 |
| 사계절 | 3 |

여행지 이름은 중복되지 않으며, 모든 숙소의 `destination_name`은
`destinations.json`의 `name`과 정확하게 일치합니다.

## 가격 기준

`price_per_night`는 2026-09-21에 공식 사이트와 국내외 숙박 예약·가격 비교
사이트에서 확인한 공개 가격, 최저가, 평균가 또는 공개 가격대를 참고해 정한
1박 기준 개발용 대표 가격입니다.

- 성수기·비수기, 평일·주말, 객실 등급은 구분하지 않습니다.
- 원 단위 정수로 저장합니다.
- 할인, 세금, 조식과 부대시설 포함 여부를 별도로 계산하지 않습니다.
- 실시간 예약 가격이나 최종 결제 금액으로 사용하지 않습니다.
- 실제 예약 기능을 구현할 때는 서버가 숙박 일수와 DB의 고정 가격으로 모의 금액만 계산합니다.
- 실제 PG사, 카드사 또는 숙소 예약 시스템과 연결하지 않습니다.

가격이 공개 검색 결과에서 명확하게 확인되지 않는 일부 소규모 펜션·글램핑은
동일 지역과 동일 유형 숙소의 공개 가격대를 참고해 대표 가격을 정했습니다.
따라서 모든 가격은 실제 판매를 위한 정보가 아니라 개발·화면 테스트용입니다.

## 평점과 이미지

- 평점은 시점에 따라 달라지므로 `null`로 저장합니다.
- 출처가 명확한 이미지를 확보하기 전까지 `image_url`은 `null`로 저장합니다.
- 실제 사용자 개인정보, 리뷰, 예약정보와 결제정보는 포함하지 않습니다.

## 주요 가격 확인 출처

가격은 조회 날짜와 객실 조건에 따라 달라질 수 있습니다.

- 창원 진해 깨끗한 호텔 외인촌: https://nol.yanolja.com/stay/domestic/1000101230
- 창원 글로리아글램핑: https://nol.yanolja.com/stay/domestic/10059700
- 삼척 산티아고펜션: https://rev.yapen.co.kr/externalV2?ypIdx=27330
- 쏠비치 삼척: https://kr.hotels.com/ho625826/ssolbichi-samcheog-samcheog-hangug/
- 소노캄 여수: https://www.expedia.co.kr/Suncheon-Hotels-Sono-Calm-Yeosu.h5699310.Hotel-Information
- 씨크루즈호텔 속초: https://www.hotelscombined.co.kr/Hotel/Sea_Cruise_Hotel.htm
- 롯데리조트 속초: https://www.lotteresort.com/main/ko/reservation/room-list?urlLang=ko
- 무주 나오스펜션: https://kr.hotels.com/ho1456368544/muju-naoseupensyeon-muju-hangug/
- 무주 랜드글램핑: https://www.gocamping.or.kr/bsite/camp/info/read.do?c_no=101358
- 태백호텔: https://www.hotelscombined.co.kr/Hotel/Taebaek_Hotel.htm
- 보령 지역 숙소: https://www.hotelscombined.co.kr/Place/Boryeong.htm
- 담양메타펜션: https://www.google.com/travel/hotels/
- 안동 전통리조트 구름에: https://www.waug.com/ko/accommodations/31214
- 순천 에코그라드호텔: https://www.hotelscombined.co.kr/Hotel/Ecograd_Hotel.htm
- 라카이 샌드파인: https://lakaisandpine.com/package
- 라한셀렉트 경주: https://lahanhotels.com/gyeongju/ko/main.do
- 아난티 앳 부산 코브: https://ananti.kr/ko/busan

## JSON 검증

PowerShell에서 다음 명령으로 JSON 문법을 확인합니다.

```powershell
.\venv\Scripts\python.exe -m json.tool app\data\destinations.json
.\venv\Scripts\python.exe -m json.tool app\data\accommodations.json
```

추가 검증 항목은 다음과 같습니다.

- 여행지 이름 중복 여부
- 계절별 여행지 개수
- 여행지별 숙소 개수
- 숙소가 참조하는 여행지의 존재 여부
- 가격과 수용 인원이 양의 정수인지 여부
- 허용된 계절·목적·분위기·예산 값만 사용했는지 여부

## Seed 적용 순서

1. `destinations.json`을 읽어 여행지를 먼저 저장합니다.
2. 여행지 이름으로 기존 데이터를 확인해 중복 삽입을 방지합니다.
3. `accommodations.json`을 읽습니다.
4. `destination_name`으로 저장된 여행지를 조회합니다.
5. 여행지와 숙소 이름 조합으로 기존 숙소를 확인해 중복 삽입을 방지합니다.
6. 여러 번 실행해도 같은 결과가 나오도록 구현합니다.

