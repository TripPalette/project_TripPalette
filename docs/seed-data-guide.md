# TripPalette 개발용 Seed Data 안내

## 구성

- `app/data/destinations.json`: 여행지 42개
- `app/data/accommodations.json`: 여행지별 숙소 3개, 총 126개

계절별 여행지 수는 다음과 같습니다.

| 계절 | 여행지 수 |
|---|---:|
| 봄 | 4 |
| 여름 | 4 |
| 가을 | 4 |
| 겨울 | 4 |
| 사계절 | 26 |

모든 여행지 이름은 중복되지 않으며, 모든 숙소의 `destination_name`은
`destinations.json`의 `name`과 정확하게 일치합니다.

## 지역 자료 반영 기준

지역별 엑셀 자료에는 경기·강원·충북·충남·경북·경남·전북·전남·제주의
27개 후보 지역이 들어 있었습니다.

- 기존 데이터와 겹친 정선·보령·여수·구례는 새 여행지로 추가하지 않았습니다.
- 중복 4개 지역은 기존 숙소 3개를 그대로 유지했습니다.
- 나머지 23개 지역만 `사계절` 여행지로 추가했습니다.
- 엑셀에 숙소 후보가 4개인 지역은 작성 순서상 앞의 3개만 사용했습니다.
- `가평균`은 `가평`으로, `브라운도트호텔`과 다음 행의 `완주봉동점`은
  `브라운도트호텔 완주 봉동점`으로 정규화했습니다.
- 행정구역 표기는 `강원특별자치도`, `전북특별자치도`,
  `제주특별자치도`처럼 현재 명칭으로 통일했습니다.
- 제주 지역은 이름 충돌을 피하고 위치를 분명히 하기 위해 `제주 조천`,
  `제주 애월`, `서귀포`로 구분했습니다.

## 가격 기준

`price_per_night`은 2026-09-21~22에 공식 사이트와 국내외 숙박 가격 비교
사이트에서 확인한 공개 가격, 최저가 또는 평균가를 참고해 정한 개발용 1박
대표가격입니다.

- 성수기·비수기, 평일·주말, 객실 등급은 구분하지 않습니다.
- 원 단위 정수로 저장합니다.
- 할인, 세금, 조식과 부대시설 포함 여부를 별도로 계산하지 않습니다.
- 공개 가격을 명확히 확인하기 어려운 일부 소규모 펜션과 호텔은 같은 지역의
  유사 숙소 공개 가격을 참고해 대표가격을 정했습니다.
- 실시간 예약 가격이나 최종 결제 금액으로 사용하지 않습니다.
- 실제 PG사, 카드사 또는 숙소 예약 시스템과 연결하지 않습니다.

이 데이터는 개발·화면·테스트용이며 실제 판매 정보가 아닙니다.

## 평점과 이미지

- 평점은 시점에 따라 달라지므로 `rating`을 `null`로 저장합니다.
- 출처와 사용 권한이 확인된 이미지를 확보하기 전까지 `image_url`은 `null`로 저장합니다.
- 개인정보, 실제 예약정보, 결제정보를 포함하지 않습니다.

### TourAPI 이미지 수집

`scripts/collect_tour_images.py`는 한국관광공사의 관광사진 정보와 국문 관광정보
API를 사용해 여행지와 숙소별로 최대 3장의 이미지 URL을 수집합니다.

- 인증키는 `.env`의 `TOUR_API_KEY`에서만 읽습니다.
- 여행지는 관광사진 검색 결과에서 최대 3장을 선택합니다.
- 관광사진 API 권한이 없으면 국문 관광정보의 관광지 대표 이미지로 자동 대체합니다.
- 숙소는 이름과 주소를 대조한 뒤 상세 이미지를 최대 3장 선택합니다.
- 정확하게 일치하지 않는 숙소는 자동 반영하지 않고 검토 대상으로 분리합니다.
- 3장은 `matched`, 1~2장은 `partial`, 0장은 `review`로 보고서에 기록합니다.
- 각 이미지의 URL, 대체 텍스트, 출처, 저작권 유형과 콘텐츠 ID를 함께 저장합니다.
- `image_url`에는 목록 화면용 첫 번째 이미지를, `images`에는 상세 화면용 전체
  이미지를 저장합니다.
- 외부 이미지가 없거나 불확실하면 공통 기본 이미지를 사용합니다.

먼저 한 항목만 미리보기로 확인합니다.

```powershell
.\venv\Scripts\python.exe scripts\collect_tour_images.py --target destinations --limit 1
```

보고서를 확인한 뒤 전체 결과를 JSON에 반영합니다.

```powershell
.\venv\Scripts\python.exe scripts\collect_tour_images.py --write
```

결과 보고서는 `app/data/tour-image-report.json`에 생성됩니다. API 호출 제한과
장애의 영향을 줄이기 위해 사용자 요청 때마다 API를 호출하지 않고, 수집 시점에
확정한 URL을 seed JSON에 저장합니다.

## 주요 가격 확인 출처

가격은 조회일과 객실 조건에 따라 달라질 수 있습니다.

- 창원 진해 김해공항 호텔 브라운도트: https://nol.yanolja.com/stay/domestic/1000101230
- 창원 그랜드시티호텔: https://nol.yanolja.com/stay/domestic/10059700
- 삼척 씨티앤고펜션: https://rev.yapen.co.kr/externalV2?ypIdx=27330
- 쏠비치 삼척: https://kr.hotels.com/ho625826/ssolbichi-samcheog-samcheog-hangug/
- 소노캄 여수: https://www.expedia.co.kr/Suncheon-Hotels-Sono-Calm-Yeosu.h5699310.Hotel-Information
- 씨크루즈호텔 속초: https://www.hotelscombined.co.kr/Hotel/Sea_Cruise_Hotel.htm
- 롯데리조트 속초: https://www.lotteresort.com/main/ko/reservation/room-list?urlLang=ko
- 무주 나오스펜션: https://kr.hotels.com/ho1456368544/muju-naoseupensyeon-muju-hangug/
- 무주 하늘길캠핑장: https://www.gocamping.or.kr/bsite/camp/info/read.do?c_no=101358
- 태백호텔: https://www.hotelscombined.co.kr/Hotel/Taebaek_Hotel.htm
- 보령 지역 숙소: https://www.hotelscombined.co.kr/Place/Boryeong.htm
- 안동 전통리조트 구름에: https://www.waug.com/ko/accommodations/31214
- 순천 에코그라드호텔: https://www.hotelscombined.co.kr/Hotel/Ecograd_Hotel.htm
- 라카이 샌드파인: https://lakaisandpine.com/package
- 라한셀렉트 경주: https://lahanhotels.com/gyeongju/ko/main.do
- 아난티 앳 부산 코브: https://ananti.kr/ko/busan
- 포천 지역 숙소: https://www.hotelscombined.co.kr/Place/Pocheon.htm
- 쏠비치 양양 등 양양 지역 숙소: https://kr.trip.com/hotels/yangyang-osan-ri-beach/hotels-c6430m60881709/
- 제천 지역 숙소: https://www.hotelscombined.co.kr/Place/Jecheon.htm
- 소노문 단양: https://kr.hotels.com/ho370556/sonomun-dan-yang-gu-daemyeonglijoteu-dan-yang-dan-yang-hangug/
- 켄싱턴리조트 충주: https://www.kensington.co.kr/rcj/room_info/detail?idx=201
- 라한호텔 포항: https://lahanhotels.com/pohang/ko/main.do
- 청송 한옥호텔 안: https://booking.kakao.com/detail/accommodation/285202
- 소노벨 청송: https://www.hotelscombined.co.kr/Hotel/Sono_Belle_Cheongsong.htm
- 주왕산 온천관광호텔: https://nol.yanolja.com/stay/domestic/10041107
- 바다호텔: https://nol.yanolja.com/stay/domestic/10045714
- 남해 스포츠파크 호텔: https://www.hotelscombined.co.kr/Hotel/Namhae_Sportpark_Hotel.htm
- 남해 지역 숙소: https://www.traveloka.com/ko-kr/hotel/south-korea/landmark/namhae-sports-park-91744080058754
- 에코랜드 호텔: https://www.kayak.co.kr/%EC%A0%9C%EC%A3%BC%EC%8B%9C-%ED%98%B8%ED%85%94-%EC%97%90%EC%BD%94%EB%9E%9C%EB%93%9C-%ED%98%B8%ED%85%94.8651584.ksp
- 유니호텔 제주: https://www.jeju.to/CS/Goods/Lodge/detail.aspx?cid=9760
- 켄싱턴리조트 서귀포: https://kensington.co.kr/rsw/room_info/detail?idx=193

## JSON 검증

PowerShell에서 다음 명령으로 JSON 문법을 확인합니다.

```powershell
.\venv\Scripts\python.exe -m json.tool app\data\destinations.json
.\venv\Scripts\python.exe -m json.tool app\data\accommodations.json
```

추가 검증 항목은 다음과 같습니다.

- 여행지 이름 중복 여부
- 계절별 여행지 개수
- 여행지별 숙소가 정확히 3개인지 여부
- 숙소가 참조하는 여행지가 존재하는지 여부
- 가격과 수용 인원이 양의 정수인지 여부
- 허용된 계절·목적·분위기·예산 값만 사용하는지 여부

## Seed 적용 순서

1. `destinations.json`을 읽어 여행지를 먼저 저장합니다.
2. 여행지 이름으로 기존 데이터를 확인해 중복 삽입을 방지합니다.
3. `accommodations.json`을 읽습니다.
4. `destination_name`으로 저장된 여행지를 조회합니다.
5. 여행지와 숙소 이름 조합으로 기존 숙소를 확인해 중복 삽입을 방지합니다.
6. 여러 번 실행해도 같은 결과가 나오도록 구현합니다.
